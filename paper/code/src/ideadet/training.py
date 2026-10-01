"""Training corpus: splits, rendering, and checkpoint selection.

SPLIT DESIGN
------------
Three DISJOINT slices carved from one held-out budget, each with exactly one job:

    val-select   checkpoint selection only
    calib        threshold derivation only -- HUMAN ONLY
    test         headline reporting only

Using one slice for two jobs is a leak, and the most common version of it is
letting the test set supply both the threshold and the number.

Calibration is human-only because the operating point is a low quantile of the
human score distribution; AI documents contribute nothing to it, so spending the
budget on humans is what lowers the reportable FPR floor.

**Disjointness must hold at the SOURCE-DOCUMENT level, not the outline level.**
Large web pools carry exact-duplicate texts; a duplicate spanning calibration and
test silently leaks the threshold into the test humans. Deduplicate first.

Stratify by format x label, seed it, and freeze it BEFORE anything is scored.

CHECKPOINT SELECTION
--------------------
`sel_metric` is the mean TPR at {0.5%, 1%, 2%} on the val-select slice. A single
operating point is too noisy to rank correlated checkpoints from one epoch. The
test slice is never used for selection, and the calibration slice never for
either.
"""
from __future__ import annotations

import hashlib

import numpy as np

from . import metrics as M
from .outlines import render, render_items

#: Formats excluded from training and why. Transcript / Interview had heavily
#: skewed labels and no test rows, so a model could learn "reads like a
#: transcript -> human" with no eval able to catch or penalise it, and the source
#: pool was exhausted so it could not be rebalanced.
DROP_FORMATS = ("Transcript / Interview",)

SPLIT_NAMES = ("train", "val", "calibration", "test")


def text_hash(text: str) -> str:
    """Stable id for deduplication at the source-document level."""
    return hashlib.sha256(" ".join(str(text).split()).encode()).hexdigest()[:32]


def deduplicate(rows: list[dict], key: str = "text") -> tuple[list[dict], int]:
    """Drop exact duplicate source texts, keeping the first occurrence."""
    seen, out = set(), []
    for r in rows:
        h = r.get("text_hash") or text_hash(r.get(key, ""))
        if h in seen:
            continue
        seen.add(h)
        r["text_hash"] = h
        out.append(r)
    return out, len(rows) - len(out)


def make_splits(fmt, y, *, n_val: int = 6000, n_calibration: int = 10000,
                n_test: int = 14000, drop_formats=DROP_FORMATS,
                seed: int = 0) -> dict:
    """Stratified, seeded, disjoint slices. Returns {name: index array}.

    `fmt` and `y` are parallel arrays over the deduplicated pool; `y` is 1 for
    HUMAN. Calibration draws HUMANS ONLY.
    """
    fmt = np.asarray([str(f) for f in fmt])
    y = np.asarray(y, dtype=int)
    keep = np.flatnonzero(~np.isin(fmt, list(drop_formats)))
    rng = np.random.default_rng(seed)

    strata = np.array([f"{fmt[i]}||{y[i]}" for i in keep])
    taken = np.zeros(len(keep), dtype=bool)

    def draw(n: int, humans_only: bool) -> np.ndarray:
        """Proportional stratified draw from what is still untaken."""
        pool = np.flatnonzero(~taken & ((y[keep] == 1) if humans_only else True))
        if not len(pool):
            return np.array([], dtype=int)
        picked = []
        for s in sorted(set(strata[pool].tolist())):
            where = pool[strata[pool] == s]
            take = min(len(where), int(round(n * len(where) / len(pool))))
            if take:
                picked.extend(rng.choice(where, size=take, replace=False).tolist())
        taken[picked] = True
        return keep[np.array(sorted(picked), dtype=int)]

    # Order matters: the scarcest constraint (human-only calibration) draws first.
    calibration = draw(n_calibration, humans_only=True)
    test = draw(n_test, humans_only=False)
    val = draw(n_val, humans_only=False)
    train = keep[~taken]

    splits = {"train": train, "val": val, "calibration": calibration, "test": test}
    _assert_disjoint(splits)
    return splits


def _assert_disjoint(splits: dict) -> None:
    seen = set()
    for name, idx in splits.items():
        overlap = seen & set(idx.tolist())
        if overlap:
            raise ValueError(
                f"split {name} overlaps an earlier split on {len(overlap):,} rows. "
                f"Splits must be disjoint or the threshold leaks into the test set.")
        seen |= set(idx.tolist())


def describe(splits: dict, fmt, y) -> str:
    fmt = np.asarray([str(f) for f in fmt])
    y = np.asarray(y, dtype=int)
    lines = [f"  {'split':<13}{'n':>9}{'human':>9}{'ai':>9}{'human frac':>12}{'formats':>9}"]
    for name in SPLIT_NAMES:
        idx = splits.get(name, np.array([], dtype=int))
        if not len(idx):
            continue
        h = int((y[idx] == 1).sum())
        lines.append(f"  {name:<13}{len(idx):>9,}{h:>9,}{len(idx) - h:>9,}"
                     f"{h / len(idx):>12.4f}{len(set(fmt[idx].tolist())):>9}")
    return "\n".join(lines)


def render_examples(records, setting: str) -> tuple[list[str], list[int], list[str]]:
    """(texts, labels, owner ids) for one training setting.

    `records` yields (doc_id, outline_or_text, y_human). The item setting emits
    one example per outline item, all inheriting the parent document's label,
    which is why item-level results are pooled back to documents for reporting.
    """
    texts, labels, owners = [], [], []
    for doc_id, payload, y in records:
        if setting == "docs":
            texts.append(str(payload))
            labels.append(int(y))
            owners.append(str(doc_id))
        elif setting == "items":
            for t in render_items(payload):
                texts.append(t)
                labels.append(int(y))
                owners.append(str(doc_id))
        else:
            texts.append(render(payload, setting))
            labels.append(int(y))
            owners.append(str(doc_id))
    return texts, labels, owners


def sel_metric(p_human, y_human, targets=(0.005, 0.01, 0.02)) -> float:
    """Mean TPR at several low FPRs — the checkpoint-selection score."""
    pt = M.point_metrics(p_human, y_human)
    if "tpr_at_fpr" not in pt:
        return float("nan")
    return float(np.mean([pt["tpr_at_fpr"][str(t)] for t in targets]))


def probe_report(step: int, p_human, y_human) -> str:
    pt = M.point_metrics(p_human, y_human)
    auc = pt["auc"]
    return (f"  step {step:>6}  sel={sel_metric(p_human, y_human):.4f}  "
            f"AUC={auc:.4f}  " if auc is not None else f"  step {step:>6}  ") + \
        " ".join(f"@{t:.1%}={pt['tpr_at_fpr'][str(t)]:.4f}"
                 for t in (0.005, 0.01, 0.02) if "tpr_at_fpr" in pt)
