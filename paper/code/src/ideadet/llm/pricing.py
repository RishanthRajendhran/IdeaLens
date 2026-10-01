"""Cost estimation. Rates are read from a dated table, never hard-coded inline.

Provider prices and discounts have moved more than once during this project, and
a rate baked into a script goes silently wrong rather than loudly. Two rules:

* **Poll before you spend.** For providers that expose a live price endpoint
  (Tinker), fetch it at run time; `refresh_tinker()` does this.
* **Three meters, not one.** Training, prefill and sampling bill separately.
  Scoring a corpus bills the PREFILL meter — computing log-probabilities
  generates nothing — so costing it at the sample rate is wrong by a large
  factor. Reasoning tokens bill at the OUTPUT rate and are reported separately
  from completion tokens.

The table lives in `configs/pricing.yaml` with an `as_of` date. Anything older
than `STALE_DAYS` prints a warning rather than being trusted silently.
"""
from __future__ import annotations

import datetime
import warnings

from .. import config as C

STALE_DAYS = 60


def table() -> dict:
    cfg = C.load("pricing.yaml")
    as_of = cfg.get("as_of")
    if as_of:
        age = (datetime.date.today() - datetime.date.fromisoformat(str(as_of))).days
        if age > STALE_DAYS:
            warnings.warn(
                f"configs/pricing.yaml is {age} days old (as_of {as_of}). "
                f"Re-check provider pricing before quoting a cost.", stacklevel=2)
    return cfg


def rate(model: str, meter: str = "input", mode: str = "batch") -> float:
    """USD per million tokens for one model, meter and transport mode."""
    t = table()
    entry = (t.get("models") or {}).get(model)
    if entry is None:
        raise KeyError(f"no price recorded for {model!r}. Add it to "
                       f"configs/pricing.yaml with its source and date.")
    block = entry.get(mode) or entry.get("standard") or {}
    if meter not in block:
        raise KeyError(f"{model!r} has no {meter!r} rate under mode {mode!r}; "
                       f"available: {sorted(block)}")
    return float(block[meter])


def estimate(model: str, *, input_tokens: int = 0, output_tokens: int = 0,
             reasoning_tokens: int = 0, cached_input_tokens: int = 0,
             mode: str = "batch") -> dict:
    """Cost of one job. Reasoning bills at the output rate; cache at its own."""
    r_in = rate(model, "input", mode)
    r_out = rate(model, "output", mode)
    try:
        r_cache = rate(model, "cached_input", mode)
    except KeyError:
        r_cache = r_in * 0.1                # the usual cached-prefix discount
    billed_out = output_tokens + reasoning_tokens
    cost = ((input_tokens * r_in) + (cached_input_tokens * r_cache)
            + (billed_out * r_out)) / 1e6
    return {"model": model, "mode": mode, "usd": round(cost, 4),
            "input_tokens": input_tokens, "cached_input_tokens": cached_input_tokens,
            "output_tokens": output_tokens, "reasoning_tokens": reasoning_tokens,
            "rates_per_mtok": {"input": r_in, "cached_input": r_cache, "output": r_out}}


def extrapolate(trial: dict, n_total: int, n_trial: int) -> dict:
    """Scale a measured trial run up to a full corpus.

    Always run one or two trial jobs and extrapolate before launching a sweep.
    `trial` is an `estimate` dict from real, billed usage, not from a guess.
    """
    if n_trial <= 0:
        raise ValueError("n_trial must be positive")
    factor = n_total / n_trial
    return {**trial, "usd": round(trial["usd"] * factor, 2),
            "n_trial": n_trial, "n_total": n_total, "scale_factor": round(factor, 2),
            "basis": "measured trial usage, extrapolated linearly"}


def refresh_tinker() -> dict:
    """Fetch live Tinker rates. Prices there are promotional and undated."""
    import json
    import subprocess
    out = subprocess.run(["tinker", "models", "list", "--json"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)
