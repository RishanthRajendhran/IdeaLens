"""OpenAI, OpenRouter and any OpenAI-compatible endpoint (local vLLM, Ollama, Together, Fireworks, Groq, DeepSeek, ...),
through the official `openai` SDK (pip install openai).

Structured output is requested where the endpoint is known to support it (OpenAI; OpenRouter) but not required:
every reply is validated by idealens.parse and repaired if needed. --strict-json (strict_json=True) makes OpenRouter
route only to hosts that honour the JSON schema.

Credentials: OPENAI_API_KEY; OPENROUTER_API_KEY; for other endpoints api_key=... (or none, for local servers).
"""
from __future__ import annotations

import json
import os
import tempfile
import time
import urllib.request

from . import Provider, Reply

REASONING_FAMILIES = ("gpt-5", "gpt-6", "o1", "o3", "o4")
OPENROUTER_URL = "https://openrouter.ai/api/v1"


def _messages(p) -> list:
    msgs = [{"role": "system", "content": p.system}, {"role": "user", "content": p.user}]
    for i, turn in enumerate(p.extra_user):  # repair retries: the bad reply, then the correction
        msgs.append({"role": "assistant" if i % 2 == 0 else "user", "content": turn})
    return msgs


def _usage(u) -> dict:
    if u is None:
        return {}
    d = u.model_dump() if hasattr(u, "model_dump") else dict(u)
    return {"input": d.get("prompt_tokens") or 0,
            "cached_input": ((d.get("prompt_tokens_details") or {}).get("cached_tokens") or 0),
            "output": d.get("completion_tokens") or 0,
            "reasoning": ((d.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0)}


class OpenAIChat(Provider):
    """Chat Completions. kind: "openai" (api.openai.com, with Batch), or "compatible" (any base_url)."""
    name = "openai"
    supports_batch = True

    def __init__(self, model=None, api_key=None, base_url=None, kind="openai", reasoning_effort="auto",
                 structured="auto", send_seed=True, max_output_tokens=None, extra_body=None, timeout=900,
                 max_retries=4, batch_poll=60):
        from openai import OpenAI
        if not model:
            raise ValueError(f"{kind}: pass a model name (--llm-model)")
        self.model, self.kind = model, kind
        self.name = kind if kind != "openai" else "openai"
        self.supports_batch = kind == "openai"
        key = api_key or (os.environ.get("OPENAI_API_KEY") if kind == "openai" else None) or "none"
        self.client = OpenAI(api_key=key, base_url=base_url, timeout=timeout, max_retries=max_retries)
        self.reasoning_effort, self.structured, self.send_seed = reasoning_effort, structured, send_seed
        self.max_output_tokens, self.extra_body, self.batch_poll = max_output_tokens, dict(extra_body or {}), batch_poll

    # ------------------------------------------------------------------ request
    def _reasoning(self, p):
        if not p.reasoning:
            return None
        if self.reasoning_effort == "auto":
            return p.reasoning if (self.kind == "openai" and self.model.startswith(REASONING_FAMILIES)) else None
        return self.reasoning_effort or None

    def params(self, p) -> dict:
        mt = min(p.max_output_tokens, self.max_output_tokens) if self.max_output_tokens else p.max_output_tokens
        kw = {"model": self.model, "messages": _messages(p)}
        kw["max_completion_tokens" if self.kind == "openai" else "max_tokens"] = mt
        eff = self._reasoning(p)
        if eff:
            kw["reasoning_effort"] = eff
        use_schema = self.structured is True or (self.structured == "auto" and self.kind in ("openai", "openrouter"))
        if p.schema is not None and use_schema:
            kw["response_format"] = {"type": "json_schema",
                                     "json_schema": {"name": "outline", "schema": p.schema, "strict": False}}
        if self.send_seed and p.seed is not None:
            kw["seed"] = p.seed
        if self.extra_body:
            kw["extra_body"] = dict(self.extra_body)
        return kw

    def _reply(self, resp) -> Reply:
        ch = resp.choices[0] if resp.choices else None
        text = (ch.message.content if ch and ch.message else None) or None
        extra = getattr(resp, "model_extra", None) or {}
        cost = None
        if resp.usage is not None:
            ue = getattr(resp.usage, "model_extra", None) or {}
            cost = ue.get("cost")
        return Reply(text, _usage(resp.usage), None if text else "empty reply",
                     ch.finish_reason if ch else None, host=extra.get("provider"), cost_usd=cost)

    def generate(self, prompt) -> Reply:
        import openai
        try:
            return self._reply(self.client.chat.completions.create(**self.params(prompt)))
        except openai.APIStatusError as e:
            return Reply(None, error=f"HTTP {e.status_code}: {str(e.message)[:500]}")
        except openai.APIConnectionError as e:
            return Reply(None, error=f"connection error: {e}")

    # ------------------------------------------------------------------ batch (OpenAI only)
    def run_batch(self, prompts: dict, log=print, description="idealens", max_bytes=190_000_000,
                  max_requests=50_000) -> dict:
        if self.kind != "openai":
            return super().run_batch(prompts, log)
        lines, size, chunks = [], 0, []
        for pid, p in prompts.items():
            body = self.params(p); body.pop("extra_body", None)
            line = json.dumps({"custom_id": str(pid), "method": "POST", "url": "/v1/chat/completions",
                               "body": body}, ensure_ascii=False) + "\n"
            if lines and (size + len(line.encode()) > max_bytes or len(lines) >= max_requests):
                chunks.append(lines); lines, size = [], 0
            lines.append(line); size += len(line.encode())
        if lines:
            chunks.append(lines)
        results = {}
        for k, chunk in enumerate(chunks):
            with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
                fh.writelines(chunk)
            f = self.client.files.create(file=open(fh.name, "rb"), purpose="batch")
            os.unlink(fh.name)
            b = self.client.batches.create(input_file_id=f.id, endpoint="/v1/chat/completions",
                                           completion_window="24h", metadata={"description": description[:500]})
            log(f"OpenAI batch {b.id} ({k + 1}/{len(chunks)}): {len(chunk)} requests")
            t0 = time.time()
            while b.status not in ("completed", "failed", "expired", "cancelled"):
                time.sleep(self.batch_poll)
                b = self.client.batches.retrieve(b.id)
                rc = b.request_counts
                log(f"  [{(time.time() - t0) / 60:.1f} min] {b.status} done={getattr(rc, 'completed', 0)} "
                    f"failed={getattr(rc, 'failed', 0)}")
            if b.status == "failed":   # rejected as a whole (e.g. a model the Batch API does not serve): no results
                msgs = sorted({f"{e.code}: {e.message}" for e in (b.errors.data if b.errors else [])})
                raise RuntimeError(f"OpenAI batch {b.id} failed: {'; '.join(msgs) or 'no reason given'}")
            for fid in (b.output_file_id, b.error_file_id):
                if not fid:
                    continue
                for line in self.client.files.content(fid).text.splitlines():
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    cid, resp = rec.get("custom_id"), rec.get("response") or {}
                    body = resp.get("body") or {}
                    if resp.get("status_code") == 200 and body.get("choices"):
                        ch = body["choices"][0]
                        text = (ch.get("message") or {}).get("content") or None
                        results[cid] = Reply(text, _usage(body.get("usage")), None if text else "empty reply",
                                             ch.get("finish_reason"))
                    else:
                        results[cid] = Reply(None, error=json.dumps(rec.get("error") or body.get("error") or resp)[:500])
        for pid in prompts:
            results.setdefault(str(pid), Reply(None, error="missing from batch output"))
        return results


class OpenRouter(OpenAIChat):
    """OpenRouter: open and closed models behind one OpenAI-compatible API.

    Checks the model against OpenRouter's catalog (context length, max output, supported parameters, live prices),
    asks for high reasoning effort on extraction, records the host that served each request and the cost OpenRouter
    reports. strict_json=True routes only to hosts that enforce the JSON schema; providers=[...] pins hosts;
    full_precision=True excludes quantised hosts.
    """
    name = "openrouter"

    def __init__(self, model=None, api_key=None, strict_json=False, providers=None, full_precision=False, **kw):
        key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("no OpenRouter key: pass api_key or set OPENROUTER_API_KEY")
        routing = {"require_parameters": bool(strict_json)}
        if providers:
            routing["order"], routing["allow_fallbacks"] = list(providers), False
        if full_precision:
            routing["quantizations"] = ["bf16", "fp16", "fp32"]
        self.catalog = catalog_entry(model) if model else None
        cap = (self.catalog or {}).get("top_provider", {}).get("max_completion_tokens")
        if cap and not kw.get("max_output_tokens"):
            kw["max_output_tokens"] = int(cap)
        super().__init__(model=model, api_key=key, base_url=OPENROUTER_URL, kind="openrouter",
                         extra_body={"usage": {"include": True}, "provider": routing}, **kw)
        self.name = "openrouter"

    def params(self, p) -> dict:
        kw = super().params(p)
        if p.reasoning:
            kw["extra_body"] = kw.get("extra_body", {}) | {"reasoning": {"effort": p.reasoning}}
        ctx = self.context_length
        if ctx:  # prompt + max_tokens must fit the context; trim the output budget to what is left
            key = "max_tokens" if "max_tokens" in kw else "max_completion_tokens"
            kw[key] = min(kw[key], ctx - prompt_tokens_upper(p) - 256)
        return kw

    def generate(self, prompt) -> Reply:
        ctx = self.context_length
        if ctx and ctx - prompt_tokens_upper(prompt) < MIN_REPLY_TOKENS:
            return Reply(None, error=f"prompt (about {prompt_tokens_upper(prompt):,} tokens) leaves under "
                                     f"{MIN_REPLY_TOKENS:,} tokens of {self.model}'s {ctx:,}-token context for the "
                                     f"reply; use few_shot=False or a longer-context model")
        return super().generate(prompt)

    @property
    def context_length(self):
        return (self.catalog or {}).get("context_length")


MIN_REPLY_TOKENS = 8192   # an outline plus some reasoning; the corpus build averaged ~6,000-8,000


def prompt_tokens_upper(p) -> int:
    """A deliberately high token estimate for a prompt (3.5 characters per token; the Gemini tokenizer averages
    ~4.2-5 on these prompts), so the context check errs towards refusing rather than overflowing."""
    return int((len(p.system) + len(p.user) + sum(len(t) for t in p.extra_user)) / 3.5)


_CATALOG: dict | None = None


def catalog_entry(model: str) -> dict | None:
    """The model's entry in OpenRouter's public catalog (no key needed), or None if it cannot be fetched."""
    global _CATALOG
    if _CATALOG is None:
        try:
            req = urllib.request.Request(f"{OPENROUTER_URL}/models", headers={"User-Agent": "idealens"})
            with urllib.request.urlopen(req, timeout=30) as r:
                _CATALOG = {m["id"]: m for m in json.loads(r.read())["data"]}
        except Exception:
            _CATALOG = {}
    return _CATALOG.get(model)
