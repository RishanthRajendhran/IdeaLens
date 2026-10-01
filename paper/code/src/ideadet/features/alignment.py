"""Outline-to-outline alignment: the faithfulness audit.

Several evals generate a document from a human outline or from a brief, then ask
whether the detector still credits the human. That question is only answerable if
the generated document actually realises the outline it was given. Without this
audit, "the model strayed from the outline" and "the detector fired" are
indistinguishable.

THE PROTOCOL
------------
Re-extract an outline from the generated document, then align it item by item to
the source outline using embedding similarity, and report:

    alignment_score        mean similarity of matched pairs
    gold_coverage          share of source items with a match above threshold
    granularity_agreement  ratio of item counts, capped at 1

WHAT TO EXPECT, AND WHAT IT MEANS IF YOU DO NOT GET IT
-------------------------------------------------------
* Outline-conditioned arms should align **high**. That is the evidence the ideas
  are the human's.
* Brief-conditioned arms should sit at the **random-pair baseline**, which must
  be computed explicitly by aligning unrelated document pairs. If they sit
  meaningfully above it, the brief is leaking structure and that arm has quietly
  become the outline-conditioned arm. This is the single largest validity threat
  in the suite, so `random_baseline` is a required output, not an optional one.
"""
from __future__ import annotations

import numpy as np

from ..outlines import content_of, items_of


def cosine_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return a @ b.T


def align(sim: np.ndarray, threshold: float = 0.5) -> dict:
    """Greedy one-to-one matching on a similarity matrix (source x candidate).

    Greedy on descending similarity rather than optimal assignment: the outlines
    are short, the two agree closely in practice, and greedy is order-independent
    given the same matrix, which keeps the number reproducible.
    """
    if sim.size == 0:
        return {"alignment_score": 0.0, "gold_coverage": 0.0,
                "granularity_agreement": 0.0, "n_matched": 0}
    n_src, n_cand = sim.shape
    pairs = sorted(((float(sim[i, j]), i, j)
                    for i in range(n_src) for j in range(n_cand)), reverse=True)
    used_src, used_cand, matched = set(), set(), []
    for s, i, j in pairs:
        if i in used_src or j in used_cand:
            continue
        used_src.add(i)
        used_cand.add(j)
        matched.append(s)

    above = [s for s in matched if s >= threshold]
    return {
        "alignment_score": float(np.mean(matched)) if matched else 0.0,
        "gold_coverage": len(above) / n_src,
        "granularity_agreement": min(n_cand, n_src) / max(n_cand, n_src),
        "n_matched": len(matched), "n_source_items": n_src,
        "n_candidate_items": n_cand, "threshold": threshold,
    }


def align_outlines(source, candidate, embed_fn, threshold: float = 0.5) -> dict:
    """Align two outline records. `embed_fn` maps a list of strings to a matrix."""
    src = [content_of(i) for i in items_of(source)]
    cand = [content_of(i) for i in items_of(candidate)]
    if not src or not cand:
        return {"alignment_score": 0.0, "gold_coverage": 0.0,
                "granularity_agreement": 0.0, "n_matched": 0}
    return align(cosine_matrix(np.asarray(embed_fn(src)),
                               np.asarray(embed_fn(cand))), threshold)


def random_baseline(outlines: list, embed_fn, n_pairs: int = 200,
                    threshold: float = 0.5, seed: int = 0) -> dict:
    """Alignment of unrelated outline pairs — the floor every arm is read against.

    A brief-conditioned arm at this level is behaving as designed. One well above
    it is not testing what it claims to test.
    """
    import random
    rng = random.Random(seed)
    scores = []
    for _ in range(n_pairs):
        a, b = rng.sample(range(len(outlines)), 2)
        scores.append(align_outlines(outlines[a], outlines[b], embed_fn,
                                     threshold)["alignment_score"])
    return {"n_pairs": len(scores), "mean": float(np.mean(scores)),
            "sd": float(np.std(scores)),
            "p95": float(np.quantile(scores, 0.95)),
            "note": "brief-conditioned arms should sit here; materially above "
                    "means the brief is leaking structure"}
