"""Dry-run cost estimates, and the cost of a finished run.

Tokens: the request prompts are built exactly as a real run would build them, then measured. Input tokens use fits
from the WildOutlines build (gemini-3.7-flash: prompt tokens = a + b * characters, within ~0.5% for 90% of documents),
scaled to the prompt actually sent (few-shot or zero-shot). Output tokens are the measured means (visible output +
reasoning, which bills at the output rate); p90 gives a high estimate. For other providers these Gemini counts are a
rough proxy: tokenizers and reasoning lengths differ.

Prices: USD per million tokens, from the dated table below (edit or pass price_in/price_out/price_cached for anything
not listed); OpenRouter prices come live from its catalog. Every estimate is a range: "no cache" bills the full prompt
on every request; "cached" bills the shared system prompt at the cached rate after the first request of each format.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from importlib.resources import files

from . import prompts

PRICES_AS_OF = "2026-09-30"
# in, cached_in, out per 1M tokens (standard / online); batch = half of each where the provider has a batch API.
# cache_write: Anthropic 5-minute cache writes (1.25x input). Gemini 3.7 Flash rates hold to 2026-12-31 and double
# from 2027-01-01 (Google's published schedule).
PRICES = {
    ("gemini", "gemini-3.7-flash"): {"in": 0.75, "cached_in": 0.075, "out": 3.75, "batch": True},
    ("vertex", "gemini-3.7-flash"): {"in": 0.75, "cached_in": 0.075, "out": 3.75, "batch": True},
    ("openai", "gpt-6-astra"): {"in": 10.0, "cached_in": 1.0, "out": 50.0, "batch": True},
    ("openai", "gpt-6.1-sol"): {"in": 2.0, "cached_in": 0.1, "out": 10.0, "batch": False},  # Batch API rejects it (2026-09-30)
    ("openai", "gpt-6-sol"): {"in": 2.0, "cached_in": 0.2, "out": 10.0, "batch": True},
    ("openai", "gpt-6-luna"): {"in": 0.1, "cached_in": 0.01, "out": 0.5, "batch": True},
    ("openai", "gpt-5.6-sol"): {"in": 4.0, "cached_in": 0.4, "out": 20.0, "batch": True},
    ("openai", "gpt-5.6-terra"): {"in": 2.0, "cached_in": 0.2, "out": 12.0, "batch": True},
    ("openai", "gpt-5.6-luna"): {"in": 0.2, "cached_in": 0.02, "out": 1.2, "batch": True},
    ("openai", "gpt-5.5"): {"in": 5.0, "cached_in": 0.5, "out": 30.0, "batch": True},
    ("openai", "gpt-5.4"): {"in": 2.5, "cached_in": 0.25, "out": 15.0, "batch": True},
    ("openai", "gpt-5.4-mini"): {"in": 0.75, "cached_in": 0.075, "out": 4.5, "batch": True},
    ("openai", "gpt-5.4-nano"): {"in": 0.2, "cached_in": 0.02, "out": 1.25, "batch": True},
    ("anthropic", "claude-fable-5-1"): {"in": 10.0, "cached_in": 0.25, "cache_write": 12.5, "out": 50.0, "batch": True},
    ("anthropic", "claude-opus-5-5"): {"in": 4.0, "cached_in": 0.20, "cache_write": 5.0, "out": 20.0, "batch": True},
    ("anthropic", "claude-sonnet-5-5"): {"in": 2.0, "cached_in": 0.20, "cache_write": 2.5, "out": 10.0, "batch": True},
    ("anthropic", "claude-haiku-4-5"): {"in": 1.0, "cached_in": 0.10, "cache_write": 1.25, "out": 5.0, "batch": True},
}
# measured scoring throughput (one A100 80GB, IdeaLens-NoParaphrase calibration outlines)
SCORING_TOKENS_PER_S = {"vllm": 26_585, "hf": 2.79 * 640}


@lru_cache(maxsize=None)
def usage_stats() -> dict:
    return json.loads(files("idealens.assets").joinpath("usage_stats.json").read_text())


def price(provider: str, model: str, price_in=None, price_out=None, price_cached=None) -> dict | None:
    if price_in is not None and price_out is not None:
        return {"in": price_in, "out": price_out, "cached_in": price_cached if price_cached is not None else price_in,
                "batch": False, "source": "user"}
    if provider == "openrouter":
        from .providers.openai_compat import catalog_entry
        m = catalog_entry(model) or {}
        pr = m.get("pricing") or {}
        if pr.get("prompt") is not None:
            f = lambda k: float(pr[k]) * 1e6 if pr.get(k) not in (None, "") else None
            return {"in": f("prompt"), "out": f("completion"), "cached_in": f("input_cache_read") or f("prompt"),
                    "batch": False, "source": "openrouter catalog (live)"}
        return None
    p = PRICES.get((provider, model))
    return (p | {"source": f"idealens price table ({PRICES_AS_OF})"}) if p else None


@dataclass
class StageEstimate:
    stage: str
    requests: int
    input_tokens: float
    shared_prefix_tokens: float          # the part a prompt cache could serve after the first request per group
    output_tokens: float                 # visible + reasoning, mean
    output_tokens_p90: float
    groups: int = 1                      # distinct cached prefixes (formats)
    cost: dict = field(default_factory=dict)


def _cost(e: StageEstimate, p: dict | None, batch: bool) -> dict:
    """no_cache: every token at the input rate. cached: the shared prefix is written once per group (Anthropic bills
    that write at the cache-write rate) and read at the cached rate on every later request."""
    if not p:
        return {}
    k = 0.5 if (batch and p.get("batch")) else 1.0
    first = e.shared_prefix_tokens / max(e.requests, 1) * e.groups     # prefix tokens of each group's first request
    cached = max(0.0, e.shared_prefix_tokens - first)
    write = first if "cache_write" in p else 0.0
    plain_in = e.input_tokens - cached - write
    per_m = lambda x: x / 1e6 * k
    return {"no_cache": per_m(e.input_tokens * p["in"] + e.output_tokens * p["out"]),
            "cached": per_m(plain_in * p["in"] + write * p.get("cache_write", p["in"]) + cached * p["cached_in"]
                            + e.output_tokens * p["out"]),
            "no_cache_p90_output": per_m(e.input_tokens * p["in"] + e.output_tokens_p90 * p["out"])}


def estimate(texts, formats=None, need_classify=None, provider="gemini", model="gemini-3.7-flash", few_shot=True,
             mode="batch", force_fit_share=0.15, extract=True, price_in=None, price_out=None, price_cached=None,
             scoring_backend="vllm") -> dict:
    """Estimate tokens and cost. formats: one per document (None where it must be classified)."""
    st = usage_stats()
    texts = list(texts)
    n = len(texts)
    formats = list(formats) if isinstance(formats, (list, tuple)) else [formats] * n
    need = [f is None for f in formats] if need_classify is None else list(need_classify)
    stages = []
    # classification (+ an assumed share force-fitted)
    cl = [i for i in range(n) if need[i]]
    if cl:
        c, words = st["classify"], [len(texts[i].split()) for i in cl]
        sys_tok = c["prompt_vs_words"]["a"]
        stages.append(StageEstimate("classify", len(cl), sum(c["prompt_vs_words"]["a"] + c["prompt_vs_words"]["b"] * w
                                                              for w in words), sys_tok * len(cl),
                                    len(cl) * (c["output"]["mean"] + c["reasoning"]["mean"]),
                                    len(cl) * (c["output"]["p90"] + c["reasoning"]["p90"])))
        k = round(len(cl) * force_fit_share)
        if k:
            ff = st["force_fit"]
            mean_w = sum(words) / len(words)
            stages.append(StageEstimate(f"force_fit (assumed {force_fit_share:.0%} out of scope)", k,
                                        k * (ff["prompt_vs_words"]["a"] + ff["prompt_vs_words"]["b"] * mean_w),
                                        k * ff["prompt_vs_words"]["a"],
                                        k * (ff["output"]["mean"] + ff["reasoning"]["mean"]),
                                        k * (ff["output"]["p90"] + ff["reasoning"]["p90"])))
    # extraction, per format; documents still needing classification are spread like the classified mix (unknown
    # until classified) -- here: the pooled average of the formats.
    if extract:
        ex = st["extraction"]
        known = [f for f in formats if f is not None]
        pooled = known or list(ex)
        tot_in = shared = out = out90 = 0.0
        max_prompt = 0.0
        groups = set()
        sys_len = {f: len(prompts.extraction_prompt("", f, few_shot).system) for f in ex}
        for i in range(n):
            fmts = [formats[i]] if formats[i] is not None else pooled
            for f in fmts:
                s = ex[f]
                sys_tok = s["prompt_vs_chars"]["a"] * sys_len[f] / s["training_system_chars"]
                w = 1 / len(fmts)
                tot_in += w * (sys_tok + s["prompt_vs_chars"]["b"] * len(texts[i]))
                max_prompt = max(max_prompt, sys_tok + s["prompt_vs_chars"]["b"] * len(texts[i]))
                shared += w * sys_tok
                out += w * (s["output"]["mean"] + s["reasoning"]["mean"])
                out90 += w * (s["output"]["p90"] + s["reasoning"]["p90"])
                groups.add(f)
        stages.append(StageEstimate("extract" + ("" if few_shot else " (zero-shot)"), n, tot_in, shared, out, out90,
                                    groups=len(groups)))
    if not extract:
        max_prompt = None
    p = price(provider, model, price_in, price_out, price_cached)
    batch = mode == "batch"
    for e in stages:
        e.cost = _cost(e, p, batch)
    total = {k: sum(e.cost.get(k, 0) for e in stages) for k in ("no_cache", "cached", "no_cache_p90_output")} if p else {}
    avg_outline_tokens = 640  # WildOutlines calibration outlines with the prompt
    score_tok = n * avg_outline_tokens
    return {"documents": n, "provider": provider, "model": model, "mode": mode, "few_shot": few_shot,
            "prices": p, "stages": [asdict(e) for e in stages], "total_usd": total,
            "scoring": {"backend": scoring_backend, "gpu_minutes_one_a100":
                        score_tok / SCORING_TOKENS_PER_S[scoring_backend] / 60},
            "notes": _notes(provider, model, p, batch, max_prompt)}


def _notes(provider, model, p, batch, max_prompt_tokens=None):
    notes = []
    if provider == "openrouter":
        from .providers.openai_compat import MIN_REPLY_TOKENS, catalog_entry
        ctx = (catalog_entry(model) or {}).get("context_length")
        if ctx and max_prompt_tokens and ctx - max_prompt_tokens < MIN_REPLY_TOKENS:
            notes.append(f"{model} has a {ctx:,}-token context; the longest prompt here is about "
                         f"{max_prompt_tokens:,.0f} tokens, which leaves too little room for the reply. Those "
                         f"documents would fail: use --no-few-shot or a longer-context model")
        elif not ctx:
            notes.append(f"{model} was not found in OpenRouter's catalog")
        cap = ((catalog_entry(model) or {}).get("top_provider") or {}).get("max_completion_tokens")
        if cap and max_prompt_tokens:
            need = max(v["output"]["p90"] + v["reasoning"]["p90"] for v in usage_stats()["extraction"].values())
            if cap < need:
                notes.append(f"{model} caps replies at {int(cap):,} tokens; extraction replies (visible + reasoning) "
                             f"reached about {need:,.0f} at the 90th percentile in the corpus build, so some replies "
                             f"may be cut off (they are retried, then marked failed)")
    if not (provider in ("gemini", "vertex") and model == "gemini-3.7-flash"):
        notes.append("token counts are gemini-3.7-flash measurements used as a proxy for this model")
    if not p:
        notes.append(f"no price for {provider}/{model}: pass price_in/price_out (USD per 1M tokens) for a dollar figure")
    if batch and p and not p.get("batch"):
        notes.append("this provider has no batch API in idealens; costs are online rates")
    return notes


def format_report(r: dict) -> str:
    lines = [f"Dry run: {r['documents']:,} documents, {r['provider']}/{r['model']}, mode={r['mode']}, "
             f"few_shot={r['few_shot']} (nothing sent)", ""]
    lines.append(f"{'stage':44s} {'requests':>9s} {'input tok':>12s} {'output tok':>12s} "
                 f"{'$ no cache':>11s} {'$ cached':>10s}")
    for s in r["stages"]:
        c = s["cost"]
        money = lambda k: f"{c[k]:>10.2f}" if k in c else f"{'-':>10s}"
        lines.append(f"{s['stage']:44s} {s['requests']:>9,} {s['input_tokens']:>12,.0f} {s['output_tokens']:>12,.0f} "
                     f"{money('no_cache'):>11s} {money('cached')}")
    t = r["total_usd"]
    if t:
        lines += ["", f"total: ${t['cached']:,.2f} (prompt cache working) to ${t['no_cache']:,.2f} (no cache); "
                      f"${t['no_cache_p90_output']:,.2f} if every reply is as long as the 90th percentile"]
    if r.get("prices"):
        pr = r["prices"]
        lines.append(f"prices per 1M tokens: in ${pr['in']}, cached ${pr['cached_in']}, out ${pr['out']} "
                     f"({pr['source']}){'; batch = half' if r['mode'] == 'batch' and pr.get('batch') else ''}")
    lines.append(f"scoring: about {r['scoring']['gpu_minutes_one_a100']:.1f} GPU-minutes on one A100 "
                 f"({r['scoring']['backend']}), plus ~2 minutes to load the model")
    lines += [f"note: {x}" for x in r["notes"]]
    return "\n".join(lines)


def actual(records, provider=None, model=None) -> dict:
    """Tokens and cost of a finished run, from the usage recorded in outline and format metadata."""
    agg = {"input": 0, "cached_input": 0, "cache_write": 0, "output": 0, "reasoning": 0, "reported_cost_usd": 0.0}
    prov_model = None
    for r in records:
        for u in ((r.get("outline") or {}).get("meta", {}).get("usage"), (r.get("format_meta") or {}).get("usage"),
                  (r.get("format_meta") or {}).get("force_fit_usage")):
            for k, v in (u or {}).items():
                if k == "cost_usd":
                    agg["reported_cost_usd"] += v or 0
                elif k in agg:
                    agg[k] += v or 0
        m = (r.get("outline") or {}).get("meta") or {}
        prov_model = prov_model or ((m.get("provider"), m.get("model")) if m.get("provider") else None)
    provider, model = provider or (prov_model or (None, None))[0], model or (prov_model or (None, None))[1]
    p = price(provider, model) if provider else None
    out = agg | {"provider": provider, "model": model}
    if p:
        # Gemini reports reasoning separately from visible output; OpenAI and Anthropic include it in output
        billed_out = agg["output"] + (agg["reasoning"] if provider in ("gemini", "vertex") else 0)
        out["cost_usd_online"] = ((agg["input"] - agg["cached_input"] - agg["cache_write"]) * p["in"]
                                  + agg["cached_input"] * p["cached_in"] + agg["cache_write"] * p.get("cache_write", p["in"])
                                  + billed_out * p["out"]) / 1e6
        if p.get("batch"):
            out["cost_usd_batch"] = out["cost_usd_online"] / 2
    return out
