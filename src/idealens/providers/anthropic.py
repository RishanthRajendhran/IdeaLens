"""Anthropic Claude through the official SDK (pip install anthropic); credentials from ANTHROPIC_API_KEY (or an
`ant auth login` profile).

- Default model claude-opus-5-5. Extraction runs with adaptive thinking at effort "high" (Claude Opus 5.5 defaults to
  "medium"); classification at effort "low". Claude Haiku 4.5 takes a thinking budget instead.
- The long, identical system prompt carries a cache_control marker, so repeated requests of one format read it from
  the prompt cache.
- Online requests stream (the 64,000-token output budget is too large for a single non-streaming response) and, on
  models that support it, use the server-side refusal fallback: a declined request is re-run on another model inside
  the same call. The model that actually served each request is recorded (Reply.host). Pass fallbacks=False to turn
  this off. Message Batches reject fallbacks, so batch requests run without them.
- Batch: Message Batches (50% of standard prices), split to stay under 256 MB per batch (each extraction request
  carries a ~150-240 KB system prompt).
"""
from __future__ import annotations

import json
import time

from . import Provider, Reply

DEFAULT_MODEL = "claude-opus-5-5"
FALLBACK_MODELS = ("claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5")
BUDGET_MODELS = ("claude-haiku-4-5",)          # thinking via budget_tokens; no effort parameter
MAX_OUTPUT = {"claude-haiku-4-5": 64_000}      # others: 128,000


def _messages(p) -> list:
    msgs = [{"role": "user", "content": p.user}]
    for i, turn in enumerate(p.extra_user):
        msgs.append({"role": "assistant" if i % 2 == 0 else "user", "content": turn})
    return msgs


def _usage(u) -> dict:
    if u is None:
        return {}
    read, write = getattr(u, "cache_read_input_tokens", 0) or 0, getattr(u, "cache_creation_input_tokens", 0) or 0
    return {"input": (u.input_tokens or 0) + read + write, "cached_input": read, "cache_write": write,
            "output": u.output_tokens or 0}


class Claude(Provider):
    name = "anthropic"
    supports_batch = True

    def __init__(self, model=None, api_key=None, fallbacks=True, cache_ttl="5m", max_output_tokens=None,
                 batch_poll=60, max_retries=4):
        import anthropic
        self.model = model or DEFAULT_MODEL
        self.client = anthropic.Anthropic(api_key=api_key, max_retries=max_retries) if api_key else \
            anthropic.Anthropic(max_retries=max_retries)
        self.fallbacks = fallbacks and self.model in FALLBACK_MODELS
        self.cache = {"type": "ephemeral"} | ({"ttl": "1h"} if cache_ttl == "1h" else {})
        self.max_output_tokens, self.batch_poll = max_output_tokens, batch_poll

    def params(self, p) -> dict:
        cap = self.max_output_tokens or MAX_OUTPUT.get(self.model, 128_000)
        budget_model = self.model.startswith(BUDGET_MODELS)
        # thinking tokens count against max_tokens, so short classification replies still get room to think
        mt = min(max(p.max_output_tokens, 4096 if not budget_model else p.max_output_tokens), cap)
        kw = {"model": self.model, "max_tokens": mt, "messages": _messages(p),
              "system": [{"type": "text", "text": p.system, "cache_control": self.cache}]}
        if budget_model:
            if p.reasoning:
                kw["thinking"] = {"type": "enabled", "budget_tokens": max(1024, min(16_000, mt - 2048))}
        else:
            kw["thinking"] = {"type": "adaptive"}
            kw["output_config"] = {"effort": "high" if p.reasoning else "low"}
        return kw

    @staticmethod
    def _reply(msg, requested) -> Reply:
        text = "".join(b.text for b in msg.content if b.type == "text") or None
        err = None
        if msg.stop_reason == "refusal":
            cat = getattr(getattr(msg, "stop_details", None), "category", None)
            err, text = f"refused ({cat or 'no category'})", None
        elif text is None:
            err = "empty reply"
        return Reply(text, _usage(msg.usage), err, msg.stop_reason,
                     host=None if msg.model == requested else f"served by {msg.model}")

    def generate(self, prompt) -> Reply:
        import anthropic
        kw = self.params(prompt)
        try:
            if self.fallbacks:
                with self.client.beta.messages.stream(**kw, betas=["server-side-fallback-2026-07-01"],
                                                      fallbacks="default") as s:
                    msg = s.get_final_message()
            else:
                with self.client.messages.stream(**kw) as s:
                    msg = s.get_final_message()
            return self._reply(msg, self.model)
        except anthropic.APIStatusError as e:
            return Reply(None, error=f"HTTP {e.status_code}: {str(e.message)[:500]}")
        except anthropic.APIConnectionError as e:
            return Reply(None, error=f"connection error: {e}")

    def count_tokens(self, prompt) -> int:
        kw = self.params(prompt)
        return self.client.messages.count_tokens(model=kw["model"], system=kw["system"],
                                                 messages=kw["messages"]).input_tokens

    def run_batch(self, prompts: dict, log=print, description="idealens", max_bytes=200_000_000,
                  max_requests=100_000) -> dict:
        reqs, size, chunks = [], 0, []
        for pid, p in prompts.items():
            r = {"custom_id": str(pid), "params": self.params(p)}
            n = len(json.dumps(r, ensure_ascii=False).encode())
            if reqs and (size + n > max_bytes or len(reqs) >= max_requests):
                chunks.append(reqs); reqs, size = [], 0
            reqs.append(r); size += n
        if reqs:
            chunks.append(reqs)
        results = {}
        for k, chunk in enumerate(chunks):
            b = self.client.messages.batches.create(requests=chunk)
            log(f"Anthropic batch {b.id} ({k + 1}/{len(chunks)}): {len(chunk)} requests")
            t0 = time.time()
            while b.processing_status != "ended":
                time.sleep(self.batch_poll)
                b = self.client.messages.batches.retrieve(b.id)
                rc = b.request_counts
                log(f"  [{(time.time() - t0) / 60:.1f} min] {b.processing_status} ok={rc.succeeded} "
                    f"errored={rc.errored} processing={rc.processing}")
            for res in self.client.messages.batches.results(b.id):   # any order: key by custom_id
                r = res.result
                if r.type == "succeeded":
                    results[res.custom_id] = self._reply(r.message, self.model)
                elif r.type == "errored":
                    results[res.custom_id] = Reply(None, error=f"errored: {getattr(r.error, 'type', r.error)}")
                else:
                    results[res.custom_id] = Reply(None, error=r.type)   # canceled / expired
        for pid in prompts:
            results.setdefault(str(pid), Reply(None, error="missing from batch output"))
        return results
