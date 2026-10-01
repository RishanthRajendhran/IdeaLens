"""OpenAI Batch API, for anything not going through Vertex.

Used for feature discovery, embeddings and the GPT generation arms. Batch is
half price with a 24-hour completion window; the synchronous path exists here
only for single calls (one feature-discovery request over a contrast set, a
smoke test), never for a corpus.
"""
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from .keys import require_key


def _client():
    from openai import OpenAI
    require_key("openai")
    return OpenAI()


def build_request(custom_id: str, model: str, messages: list[dict], *,
                  url: str = "/v1/chat/completions", **params) -> dict:
    """One JSONL row of a batch file."""
    return {"custom_id": str(custom_id), "method": "POST", "url": url,
            "body": {"model": model, "messages": messages, **params}}


def build_embedding_request(custom_id: str, model: str, text: str,
                            dimensions: int | None = None) -> dict:
    body: dict[str, Any] = {"model": model, "input": text}
    if dimensions:
        body["dimensions"] = dimensions
    return {"custom_id": str(custom_id), "method": "POST",
            "url": "/v1/embeddings", "body": body}


def run_batch(rows: list[dict], *, description: str = "", poll_interval: int = 60,
              timeout: int = 86400, log: Callable[[str], None] = print) -> dict:
    """Submit, wait, and return {custom_id: response body}. Errors are reported."""
    client = _client()
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        tmp = fh.name
    try:
        upload = client.files.create(file=open(tmp, "rb"), purpose="batch")
    finally:
        Path(tmp).unlink(missing_ok=True)

    url = rows[0]["url"] if rows else "/v1/chat/completions"
    job = client.batches.create(input_file_id=upload.id, endpoint=url,
                                completion_window="24h",
                                metadata={"description": description})
    log(f"  batch {job.id}: {len(rows):,} requests -> {url}")

    t0 = time.time()
    while True:
        job = client.batches.retrieve(job.id)
        counts = job.request_counts
        log(f"    [{(time.time() - t0) / 60:.1f}m] {job.status}  "
            f"completed={getattr(counts, 'completed', 0)} failed={getattr(counts, 'failed', 0)}")
        if job.status == "completed":
            break
        if job.status in ("failed", "expired", "cancelled"):
            raise RuntimeError(f"batch {job.id} ended {job.status}: {job.errors}")
        if time.time() - t0 > timeout:
            raise TimeoutError(f"batch {job.id} still {job.status} after {timeout}s")
        time.sleep(poll_interval)

    out, errors = {}, []
    if job.output_file_id:
        for line in client.files.content(job.output_file_id).text.splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            resp = (rec.get("response") or {}).get("body")
            if resp is None:
                errors.append((rec.get("custom_id"), rec.get("error")))
            else:
                out[rec["custom_id"]] = resp
    if job.error_file_id:
        for line in client.files.content(job.error_file_id).text.splitlines():
            if line.strip():
                rec = json.loads(line)
                errors.append((rec.get("custom_id"), rec.get("error")))
    if errors:
        log(f"    {len(errors)} failed row(s), e.g. {errors[:2]}")
    return out


def text_of(body: dict) -> str | None:
    """Pull the assistant text out of a chat-completions response body."""
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None


def embedding_of(body: dict) -> list[float] | None:
    try:
        return body["data"][0]["embedding"]
    except (KeyError, IndexError, TypeError):
        return None


def call_once(model: str, messages: list[dict], *, reasoning_effort: str | None = None,
              response_format: dict | None = None, **params) -> tuple[str, dict]:
    """One synchronous call. For single requests only — never loop this over a corpus.

    Returns (text, usage). Bulk work belongs in `run_batch`, which costs half.
    """
    client = _client()
    kwargs: dict[str, Any] = {"model": model, "messages": messages, **params}
    if reasoning_effort:
        kwargs["reasoning_effort"] = reasoning_effort
    if response_format:
        kwargs["response_format"] = response_format
    r = client.chat.completions.create(**kwargs)
    usage = r.usage.model_dump() if hasattr(r.usage, "model_dump") else dict(r.usage or {})
    return r.choices[0].message.content, usage
