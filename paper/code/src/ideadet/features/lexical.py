"""Lexical overlap between an outline and its source: the leakage measurement.

The de-leak stage exists because outlines leak source authorship through copied
wording. This module computes the proxy that tracks that leak, so a new
extraction prompt can be judged on evidence rather than on how it reads.

THE MEASURE
-----------
`lifting` is the token-weighted share of outline text sitting inside verbatim
runs of at least `min_run` tokens from the source document. It moves with
detectability across extractors, and it is the quantity a revised prompt should
drive down.

CONTENT WORDS ARE THE SIGNAL; FUNCTION WORDS ARE INERT
------------------------------------------------------
Function words are around 35% of outline tokens and their overlap with the
source is saturated near 0.9-0.97 regardless of anything. Restricting overlap to
content words strengthens the correlation with a surface detector's verdict.
Report `content` and `all` separately; a change that only moves the function-word
figure has changed nothing.

ACCEPTANCE CRITERIA FOR A NEW EXTRACTION PROMPT
-----------------------------------------------
1. lifting (>=5-token runs, content-weighted) falls
2. surface-detector AUC between human-source and AI-source outlines falls
3. alignment against a reference outline holds within about 0.03

If 1 and 2 improve while 3 holds, the prompt is better. If 3 falls materially,
it has overshot into unfaithful summarisation.
"""
from __future__ import annotations

import re
from typing import Iterable

#: A small closed-class list. Not a linguistic claim, just the standard split
#: used consistently across every measurement here.
FUNCTION_WORDS = frozenset("""
a about above after again against all am an and any are as at be because been
before being below between both but by can cannot could did do does doing down
during each few for from further had has have having he her here hers herself
him himself his how i if in into is it its itself me more most my myself no nor
not of off on once only or other ought our ours ourselves out over own same she
should so some such than that the their theirs them themselves then there these
they this those through to too under until up very was we were what when where
which while who whom why with would you your yours yourself yourselves
""".split())

_TOKEN = re.compile(r"[a-z0-9']+")


def tokens(text: str) -> list[str]:
    return _TOKEN.findall((text or "").lower())


def content_tokens(text: str) -> list[str]:
    return [t for t in tokens(text) if t not in FUNCTION_WORDS]


def _runs(source: list[str], target: list[str], min_run: int) -> list[tuple[int, int]]:
    """Maximal spans of `target` of length >= min_run that occur in `source`.

    Greedy left-to-right extension: at each position, grow the match as far as
    the source allows, then continue past it. That measures copied material once
    rather than counting every overlapping substring.
    """
    ngrams = set()
    for n in (min_run,):
        for i in range(len(source) - n + 1):
            ngrams.add(tuple(source[i:i + n]))
    src_text = " " + " ".join(source) + " "

    spans, i = [], 0
    while i <= len(target) - min_run:
        if tuple(target[i:i + min_run]) not in ngrams:
            i += 1
            continue
        j = i + min_run
        while j < len(target) and f" {' '.join(target[i:j + 1])} " in src_text:
            j += 1
        spans.append((i, j))
        i = j
    return spans


def lifting(source_text: str, outline_text: str, min_run: int = 5) -> dict:
    """Share of outline tokens inside verbatim runs of >= min_run from the source."""
    out = {}
    for name, tok in (("all", tokens), ("content", content_tokens)):
        src, tgt = tok(source_text), tok(outline_text)
        if not tgt:
            out[name] = 0.0
            continue
        covered = sum(b - a for a, b in _runs(src, tgt, min_run))
        out[name] = covered / len(tgt)
    out["min_run"] = min_run
    out["n_outline_tokens"] = len(tokens(outline_text))
    return out


def ngram_overlap(a: str, b: str, n: int = 3, content_only: bool = False) -> float:
    """Jaccard overlap of n-gram sets. Used for brief-leakage audits.

    A generated-from-brief arm is only a brief arm if its brief does not carry
    the source's structure. When this rises, that test has quietly become a
    different test.
    """
    tok = content_tokens if content_only else tokens
    ta, tb = tok(a), tok(b)
    if len(ta) < n or len(tb) < n:
        return 0.0
    ga = {tuple(ta[i:i + n]) for i in range(len(ta) - n + 1)}
    gb = {tuple(tb[i:i + n]) for i in range(len(tb) - n + 1)}
    return len(ga & gb) / len(ga | gb)


def coverage(source_text: str, outline_text: str, content_only: bool = True) -> float:
    """Share of outline tokens that appear anywhere in the source (unigram)."""
    tok = content_tokens if content_only else tokens
    src, tgt = set(tok(source_text)), tok(outline_text)
    return sum(1 for t in tgt if t in src) / len(tgt) if tgt else 0.0


def report(pairs: Iterable[tuple[str, str]], min_run: int = 5) -> dict:
    """Aggregate lifting over (source, outline) pairs."""
    import numpy as np
    rows = [lifting(s, o, min_run) for s, o in pairs]
    if not rows:
        return {}
    return {
        "n": len(rows), "min_run": min_run,
        "lifting_all_mean": float(np.mean([r["all"] for r in rows])),
        "lifting_content_mean": float(np.mean([r["content"] for r in rows])),
        "lifting_content_median": float(np.median([r["content"] for r in rows])),
        "note": "content-weighted lifting is the figure that tracks detectability; "
                "the all-token figure is dominated by inert function-word overlap",
    }
