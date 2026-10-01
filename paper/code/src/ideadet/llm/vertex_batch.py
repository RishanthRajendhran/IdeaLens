"""Vertex AI batch prediction for Gemini models.

This is the transport for both pipeline stages and for every generated eval
corpus. Batch is half the online price and this project's two bulk stages are
most of its spend, so **nothing bulk should ever go through the online path.**

Five implementation details are deliberate and load-bearing. Each was a real
failure before it was a rule:

1. **Direct REST POST to v1beta1**, not `client.batches.create`. The legacy v1
   surface cannot see preview models, and the SDK's config object cannot attach
   the billing label that makes per-project spend attributable.
2. **`custom_id` at the top level** of each JSONL row. Batch output order does
   not match input order, so rows must be rejoined by it; it is the documented
   key and the field the output echoes.
3. **`systemInstruction` in camelCase.** The body is raw REST JSON and a
   snake_case key is silently dropped — which here would mean extracting with no
   role vocabulary and no exemplars while still returning well-formed JSON.
4. **Thought parts are skipped when parsing.** Otherwise reasoning text is
   concatenated into the answer.
5. **Results are downloaded from the completed job's own output URI**, never a
   path we guessed, so concurrent jobs cannot contaminate each other.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Iterable

DEFAULT_LOCATION = "global"


# ------------------------------------------------------------ request shape --
def build_request(custom_id: str, user_text: str, *, system: str | None = None,
                  schema: dict | None = None, max_output_tokens: int = 64000,
                  thinking_level: str | None = None,
                  relax_safety: bool = True, seed: int | None = None,
                  safety_threshold: str = "OFF") -> dict:
    """One JSONL row of a batch request."""
    gen: dict[str, Any] = {"maxOutputTokens": max_output_tokens}
    if schema is not None:
        gen["responseMimeType"] = "application/json"
        gen["responseSchema"] = _schema_for_batch(schema)
    if thinking_level:
        gen["thinkingConfig"] = {"thinkingLevel": thinking_level}
    if seed is not None:          # generationConfig.seed (pipeline calls pass prompts.PIPELINE_SEED, 2026-09-24)
        gen["seed"] = seed

    req: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": gen,
    }
    if system:
        req["systemInstruction"] = {"parts": [{"text": system}]}  # camelCase: raw REST
    if relax_safety:
        # 2026-09-24: threshold OFF (was BLOCK_ONLY_HIGH, the training corpus's).
        # OFF is the least restrictive threshold and the default for Gemini 2.5 /
        # 3 when none is sent; sent explicitly so a change of default cannot
        # change our runs. NOTE: this covers the four CONFIGURABLE categories only.
        # blockReason PROHIBITED_CONTENT comes from a separate, non-configurable
        # core-policy filter and is NOT suppressed by these; for that one the
        # only mitigations are a retry (the filter is not fully deterministic) or
        # accepting the loss.
        req["safetySettings"] = [
            {"category": c, "threshold": safety_threshold} for c in (
                "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT")]
    return {"custom_id": str(custom_id), "request": req}


def _schema_for_batch(schema: dict) -> dict:
    """Two batch-only incompatibilities in Vertex's responseSchema parser.

    Batch validates the schema through an older, stricter proto parser than
    online prediction does. It rejects `$ref` as a field name and does not know
    the `const` keyword, both of which online Vertex accepts. Inlining refs and
    rewriting `const` as a one-element `enum` are equivalence-preserving.
    """
    defs = schema.get("$defs", {})

    def resolve(node):
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                return resolve(json.loads(json.dumps(defs[ref[len("#/$defs/"):]])))
            out = {}
            for k, v in node.items():
                if k == "$ref":
                    continue
                if k == "const":
                    out["enum"] = [resolve(v)]
                else:
                    out[k] = resolve(v)
            return out
        if isinstance(node, list):
            return [resolve(v) for v in node]
        return node

    out = resolve(json.loads(json.dumps(schema)))
    out.pop("$defs", None)
    return out


# ------------------------------------------------------------------- upload --
def _storage_client():
    from google.cloud import storage
    return storage.Client()


def _split_gcs(uri: str) -> tuple[str, str]:
    """'gs://bucket/path' -> ('bucket', 'path'), and REFUSE anything else.

    This used to be a bare `uri[len("gs://"):]`, which on a URI missing the
    scheme silently chopped five characters off the bucket name instead of
    failing: `outline-rst-pilot-...` became `ne-rst-pilot-...` and the upload
    died with a 404 naming a bucket nobody had configured.
    """
    if not uri.startswith("gs://"):
        raise ValueError(
            f"GCS URI must start with 'gs://', got {uri!r}. Set IDEADET_GCS_BUCKET "
            f"to 'gs://<bucket>' (or pass bucket= with the scheme).")
    bucket_name, _, rest = uri[len("gs://"):].partition("/")
    if not bucket_name:
        raise ValueError(f"no bucket in GCS URI {uri!r}")
    return bucket_name, rest


def _upload_jsonl(rows: Iterable[dict], gcs_uri: str) -> None:
    bucket_name, blob_name = _split_gcs(gcs_uri)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        tmp = fh.name
    try:
        _storage_client().bucket(bucket_name).blob(blob_name).upload_from_filename(tmp)
    finally:
        os.unlink(tmp)


def _download_output(gcs_prefix: str) -> list[str]:
    bucket_name, prefix = _split_gcs(gcs_prefix)
    client = _storage_client()
    out = []
    for blob in client.list_blobs(bucket_name, prefix=prefix):
        if blob.name.endswith(".jsonl"):
            out.append(blob.download_as_text())
    return out


# -------------------------------------------------------------- submit/poll --
def _auth():
    from google.auth import default as google_auth_default
    from google.auth.transport.requests import Request as AuthRequest
    creds, _ = google_auth_default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(AuthRequest())
    return creds


def _host(location: str) -> str:
    return ("aiplatform.googleapis.com" if location == "global"
            else f"{location}-aiplatform.googleapis.com")


def submit(model: str, gcs_in: str, gcs_out: str, display_name: str, *,
           project: str | None = None, location: str | None = None,
           labels: dict | None = None) -> tuple[dict, Any, str]:
    import requests
    project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set; see ideadet.llm.keys")
    location = location or os.environ.get("GOOGLE_CLOUD_LOCATION") or DEFAULT_LOCATION
    host = _host(location)
    body = {
        "displayName": display_name,
        "model": model if "/" in model else f"publishers/google/models/{model}",
        "inputConfig": {"instancesFormat": "jsonl", "gcsSource": {"uris": [gcs_in]}},
        "outputConfig": {"predictionsFormat": "jsonl",
                         "gcsDestination": {"outputUriPrefix": gcs_out.rstrip("/")}},
        "labels": labels or {},
    }
    creds = _auth()
    r = requests.post(
        f"https://{host}/v1beta1/projects/{project}/locations/{location}/batchPredictionJobs",
        json=body, timeout=120,
        headers={"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"})
    if r.status_code >= 400:
        raise RuntimeError(f"batch create failed [{r.status_code}]: {r.text[:1200]}")
    return r.json(), creds, host


def poll(resource: dict, creds, host: str, interval: int = 60,
         log: Callable[[str], None] = print) -> dict:
    import requests
    from google.auth.transport.requests import Request as AuthRequest
    name, t0 = resource["name"], time.time()
    while True:
        if not creds.valid:
            creds.refresh(AuthRequest())
        try:
            rr = requests.get(f"https://{host}/v1beta1/{name}", timeout=60,
                              headers={"Authorization": f"Bearer {creds.token}"})
            rr.raise_for_status()
            resource = rr.json()
        except Exception as e:                       # transient: keep polling
            log(f"    [poll] {e!r}; retry in {interval}s")
            time.sleep(interval)
            continue
        state = resource.get("state", "")
        stats = resource.get("completionStats") or {}
        log(f"    [{(time.time() - t0) / 60:.1f}m] {state}" +
            (f"  ok={stats.get('successfulCount', 0)} fail={stats.get('failedCount', 0)}"
             if stats else ""))
        if "SUCCEEDED" in state:
            return resource
        if any(k in state for k in ("FAILED", "CANCELLED", "EXPIRED")):
            raise RuntimeError(f"batch {name} ended {state}: {resource.get('error')}")
        time.sleep(interval)


# -------------------------------------------------------------------- parse --
def repair_json(txt: str) -> dict | None:
    """Best-effort salvage of a payload that exists but will not parse.

    Two failure shapes occur in practice, both on very long outputs: a malformed
    \\uXXXX escape, and an object truncated mid-item. `responseSchema` prevents
    neither — it constrains the shape of a candidate that IS returned, not
    whether the returned text is well formed after truncation. Returns None
    rather than raising, so one bad row never takes a 25,000-row job down.
    """
    if not txt:
        return None
    try:
        return json.loads(txt)
    except Exception:
        pass
    fixed = re.sub(r"\\u(?![0-9a-fA-F]{4})", "", txt)
    try:
        return json.loads(fixed)
    except Exception:
        pass
    m = re.search(r'"items"\s*:\s*\[', fixed)
    if not m:
        return None
    depth, last = 0, None
    for i in range(m.end(), len(fixed)):
        if fixed[i] == "{":
            depth += 1
        elif fixed[i] == "}":
            depth -= 1
            if depth == 0:
                last = i
    if last is None:
        return None
    for tail in ("]}", '],"document_description":"","global_themes":[]}'):
        try:
            d = json.loads(fixed[:last + 1] + tail)
            if d.get("items"):
                return d
        except Exception:
            continue
    return None


def _iter_json_values(blob: str):
    """Yield every top-level JSON value in `blob`, newline-delimited or not."""
    dec = json.JSONDecoder()
    i, n = 0, len(blob)
    while i < n:
        while i < n and blob[i] in " \r\n\t":
            i += 1
        if i >= n:
            return
        try:
            val, i = dec.raw_decode(blob, i)
        except ValueError:
            # Unparseable tail: skip to the next plausible object start so one
            # bad record cannot swallow the rest of the file.
            nxt = blob.find("\n{", i)
            if nxt < 0:
                return
            i = nxt + 1
            continue
        yield val


def parse_outputs(texts: Iterable[str], want_json: bool = True) -> tuple[dict, dict, dict]:
    """Return (results, diagnostics, usage), all keyed by custom_id.

    A row can fail three ways and they need different responses, so they are
    counted separately rather than silently dropped:

      blocked   a safety filter withheld the candidate. **The batch job still
                reports these as successes**, so a blocked row looks fine at the
                job level and only shows up here.
      empty     candidate present but carrying no non-thought text.
      malformed payload present but unparseable; `repair_json` is tried first.
    """
    results, usage = {}, {}
    diag = {"blocked": [], "empty": [], "malformed": [], "repaired": []}
    for blob in texts:
        # Vertex output is NOT reliably newline-delimited: a response whose text
        # carries a literal newline spans several lines, so a line-based
        # json.loads throws and the row vanishes into `except: continue`. That
        # silently lost 4 of 48 rows on test36 -- every one of them a row where
        # the model volunteered a justification after its answer, which is
        # content-correlated loss, not a random transient. Stream whole JSON
        # values instead, which reads both shapes.
        for rec in _iter_json_values(blob):
            if not isinstance(rec, dict):
                continue
            cid = rec.get("custom_id")
            if not cid:
                continue
            resp = rec.get("response") or {}
            # Usage is the only record of what was actually billed.
            # thoughtsTokenCount is reasoning: it bills at the OUTPUT rate and is
            # reported SEPARATELY from candidatesTokenCount. Captured even for
            # blocked rows, which still burned their prompt.
            um = resp.get("usageMetadata") or {}
            if um:
                usage[cid] = {k: um.get(k) for k in (
                    "promptTokenCount", "candidatesTokenCount", "thoughtsTokenCount",
                    "totalTokenCount", "cachedContentTokenCount")}
            cands = resp.get("candidates") or []
            if not cands:
                reason = ((resp.get("promptFeedback") or {}).get("blockReason")
                          or (rec.get("error") or {}).get("message", "")[:80])
                diag["blocked"].append((cid, reason or "no candidates"))
                continue
            txt = "".join(p["text"] for p in cands[0].get("content", {}).get("parts", [])
                          if "text" in p and not p.get("thought", False))
            if not txt:
                diag["empty"].append((cid, cands[0].get("finishReason")))
                continue
            if not want_json:
                results[cid] = txt
                continue
            try:
                results[cid] = json.loads(txt)
            except Exception:
                repaired = repair_json(txt)
                if repaired is None:
                    diag["malformed"].append((cid, len(txt)))
                else:
                    results[cid] = repaired
                    diag["repaired"].append(cid)
    return results, diag, usage


# ---------------------------------------------------------------- one call ---
def run_batch(rows: list[dict], model: str, *, bucket: str, prefix: str,
              tag: str, want_json: bool = True, poll_interval: int = 60,
              user_label: str = "", log: Callable[[str], None] = print,
              usage_path: str | Path | None = None) -> dict:
    """Submit one batch job, wait for it, and return {custom_id: parsed result}.

    `rows` come from `build_request`. Order them so identical system prefixes sit
    on consecutive rows: cached input bills at a fraction of the normal rate, and
    a job whose prefix stays warm can cost several times less than one whose
    prefix keeps changing.
    """
    # Accept a bucket with or without the scheme; normalise once, here, so no
    # caller can construct a scheme-less URI further down.
    root = bucket.rstrip("/")
    if not root.startswith("gs://"):
        root = "gs://" + root
    base = f"{root}/{prefix}/{tag}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    gcs_in, gcs_out = f"{base}/input/requests.jsonl", f"{base}/output/"
    log(f"  [{tag}] {len(rows):,} requests -> {model}\n    in  {gcs_in}")
    _upload_jsonl(rows, gcs_in)

    display = f"{user_label}_{tag}" if user_label else tag
    resource, creds, host = submit(model, gcs_in, gcs_out, display,
                                   labels={"user": user_label} if user_label else None)
    log(f"    job {resource.get('name')}")
    done = poll(resource, creds, host, poll_interval, log)

    dest = (done.get("outputInfo") or {}).get("gcsOutputDirectory") or gcs_out
    results, diag, usage = parse_outputs(_download_output(dest), want_json)
    log(f"    parsed {len(results):,}/{len(rows):,}")

    if usage_path and usage:
        with open(usage_path, "a") as fh:
            for cid, u in usage.items():
                fh.write(json.dumps({"id": cid, "stage": tag, "model": model,
                                     "usage": u}) + "\n")
        n = len(usage)
        avg = lambda k: sum((u.get(k) or 0) for u in usage.values()) / max(n, 1)
        log(f"    billed/doc: prompt {avg('promptTokenCount'):,.0f}  "
            f"cached {avg('cachedContentTokenCount'):,.0f}  "
            f"completion {avg('candidatesTokenCount'):,.0f}  "
            f"reasoning {avg('thoughtsTokenCount'):,.0f}")

    for k in ("blocked", "empty", "malformed"):
        if diag[k]:
            log(f"    {k}: {len(diag[k])}  e.g. {diag[k][:2]}")
    if diag["repaired"]:
        log(f"    repaired {len(diag['repaired'])} malformed payload(s)")

    ours = {r["custom_id"] for r in rows}
    stray = set(results) - ours
    if stray:
        log(f"    [WARN] {len(stray)} custom_ids are not ours; ignoring")
        for k in stray:
            results.pop(k, None)
    return results
