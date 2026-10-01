"""Pangram, used two ways in this project — keep them distinct.

**As a baseline detector.** Pangram is the strongest published surface detector,
and the headline comparison is that it tracks prose while an idea-level detector
tracks ideas. When reporting it as a baseline, use **its own deployed verdict
rule**, not a threshold we choose:

    Human  iff fraction_human >= 0.90
    AI     iff fraction_ai    >= 0.80
    Mixed  otherwise

"Pangram as deployed flags these" is a much stronger claim than "Pangram flags
these at a threshold we selected", and it removes the rebuttal that we tuned
them into failure. Note the asymmetry in Pangram's own reports: their verdict
metrics use this fixed global rule, but their published AUROC and TPR@X%FPR are
recalibrated per benchmark (in-set). Match whichever convention you are entering.

**As a label source.** The training corpus inherits its ground truth from
Pangram's document-level labels. Anything derived from those labels inherits the
circularity, which is exactly why the framing tests carry labels known by
construction instead.

Cost and batching: bulk is cheaper than per-text, so always submit in bulk.
Pangram 4 bills per 100 words; Pangram 3 ("default") per 1,000. Outline items
average around 25 words, below one billing unit, so submitting per item costs
several times more than per outline and asks the classifier to judge fragments
far shorter than anything it was trained on. Submit whole outlines.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

from .keys import require_key

#: Pangram's own production verdict rule, applied unchanged.
VERDICT_HUMAN_MIN = 0.90
VERDICT_AI_MIN = 0.80

MODELS = {"pangram-3": "default", "pangram-4": "pangram-4"}
#: USD per billing unit, and the unit size in words. Verify against your contract.
BILLING = {"default": (0.05, 1000), "pangram-4": (0.05, 100)}
BULK_DISCOUNT = 0.8
SUBMIT_TIMEOUT = 300      # seconds for the bulk POST; the SDK default of 10 is
                          # far too short for a multi-megabyte payload


def _client():
    from pangram import Pangram
    require_key("pangram")
    return Pangram()


def verdict(result: dict) -> str:
    """Pangram's deployed three-way label from a result payload."""
    if result.get("fraction_human", 0.0) >= VERDICT_HUMAN_MIN:
        return "human"
    if result.get("fraction_ai", 0.0) >= VERDICT_AI_MIN:
        return "ai"
    return "mixed"


def estimate_cost(texts: Iterable[str], model: str = "pangram-4",
                  bulk: bool = True) -> dict:
    price, unit = BILLING[MODELS.get(model, model)]
    words = [len(t.split()) for t in texts]
    units = sum(max(1, math.ceil(w / unit)) for w in words)
    usd = units * price * (BULK_DISCOUNT if bulk else 1.0)
    return {"model": model, "n_texts": len(words), "total_words": sum(words),
            "billing_units": units, "usd": round(usd, 2), "bulk": bulk}


def submit_bulk(items: list[dict], model: str = "pangram-4",
                submit_timeout: int = SUBMIT_TIMEOUT) -> str:
    """items: [{"id": str, "text": str}, ...]. Returns the bulk job id.

    The SDK's HTTP_REQUEST_TIMEOUT_SECONDS defaults to 10, which is fine for a
    one-document `predict` and far too short to upload a multi-megabyte bulk
    payload: 138 StoryScope stories are ~4.5 MB and timed the submit out. The
    constant is read at call time inside the SDK, so raising it around the call
    is enough. It is restored afterwards so nothing else sees a long timeout.

    A read timeout here is the DANGEROUS failure: the server may have accepted
    the job and started billing while we never saw the `bulk_id`. Pangram has no
    endpoint that enumerates bulk jobs (checked against their API reference and
    llms.txt index), so an orphaned job is unrecoverable except through the web
    dashboard, and a blind resubmit pays twice. Hence the callback in `score`.
    """
    import pangram.text_classifier as _tc
    prev = _tc.HTTP_REQUEST_TIMEOUT_SECONDS
    _tc.HTTP_REQUEST_TIMEOUT_SECONDS = max(prev, submit_timeout)
    try:
        return _client().submit_bulk(items=items,
                                     model=MODELS.get(model, model))["bulk_id"]
    finally:
        _tc.HTTP_REQUEST_TIMEOUT_SECONDS = prev


def wait_and_fetch(bulk_id: str, timeout: int = 7200,
                   poll_interval: float = 5.0) -> dict[str, dict]:
    """Block until terminal, then return {id: {"stage", "error", "result"}}.

    `get_bulk_results` returns `{"items": [...]}`, not a flat list; the shape here
    is verified against a real call rather than read off the docs summary.
    """
    client = _client()
    client.wait_for_bulk(bulk_id, timeout=timeout, poll_interval=poll_interval)
    payload = client.get_bulk_results(bulk_id)
    return {item["id"]: {"stage": item.get("stage"), "error": item.get("error"),
                         "result": item.get("result")}
            for item in payload["items"]}


def score(items: list[dict], model: str = "pangram-4",
          timeout: int = 7200, submit_timeout: int = SUBMIT_TIMEOUT,
          on_bulk_id=None, bulk_id: str | None = None) -> list[dict]:
    """Submit, wait, and return one flat row per input item.

    Rows keep the three fractions, which sum to 1. For outlines the
    discriminative axis is **AI vs AI-assisted**, not AI vs human: an LLM
    paraphrase of a human document is correctly "AI-assisted" (human content,
    machine-processed), so a low `fraction_human` is not evidence the source was
    AI.
    """
    if bulk_id is None:
        bulk_id = submit_bulk(items, model, submit_timeout=submit_timeout)
        if on_bulk_id is not None:
            # Persist BEFORE waiting. A crash between submit and fetch otherwise
            # orphans a job that has already been paid for.
            on_bulk_id(bulk_id)
    res = wait_and_fetch(bulk_id, timeout=timeout)
    out = []
    for item in items:
        r = res.get(item["id"]) or {}
        pred = r.get("result") or {}
        out.append({
            "id": item["id"], "bulk_id": bulk_id, "model": model,
            "stage": r.get("stage"), "error": r.get("error"),
            "prediction": pred.get("prediction_short") or pred.get("prediction"),
            "fraction_ai": pred.get("fraction_ai"),
            "fraction_ai_assisted": pred.get("fraction_ai_assisted"),
            "fraction_human": pred.get("fraction_human"),
            "verdict_deployed": verdict(pred) if pred else None,
            "n_words": len(item["text"].split()),
            # Window detail supports the per-span analyses; keep it, it is free.
            "windows": pred.get("windows"),
        })
    return out


def as_detector_scores(rows: list[dict]) -> dict[str, float]:
    """Pangram rows -> {id: p_human}, so it can go through the shared metrics.

    Uses `fraction_human` as P(human). This makes Pangram comparable on AUC and
    TPR@FPR, but it is NOT the deployed convention: for the headline baseline
    table use `verdict_deployed` instead, so Pangram is judged at its own
    operating point rather than one we picked.
    """
    return {r["id"]: float(r["fraction_human"]) for r in rows
            if r.get("fraction_human") is not None}
