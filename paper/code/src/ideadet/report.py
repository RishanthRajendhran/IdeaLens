"""Turning score files into the tables and payloads that go into a write-up.

Every reported number passes through here, so the conventions in `metrics` and
`calibration` are applied once and identically. Two habits this module enforces:

* **Every TPR is printed beside its realised FPR.** A TPR at a nominal 1% cut
  that actually lands at 2.4% is not a 1% number, and out of domain the two come
  apart routinely.
* **Filtered rows are counted, never hidden.** When a per-format scheme has no
  cut for some format, those documents leave the column and the count is printed.
"""
from __future__ import annotations

import numpy as np

from . import calibration as CAL
from . import metrics as M


def evaluate(p_human, y_human, *, thresholds: CAL.Thresholds | None = None,
             model_id: str = "", calibration_id: str = "", target_fpr: float = 0.01,
             scheme: str = "global", groups=None, group_name: str = "format",
             in_set: bool = False, n_boot: int = 1000) -> dict:
    """One (eval set, model arm) result under one calibration scheme.

    Set `in_set=True` only for out-of-domain sets, and only alongside the
    deployed number. It is always labelled in the output.
    """
    p = np.asarray(p_human, dtype=float)
    y = np.asarray(y_human, dtype=int)
    single_class = not (0 < (1 - y).sum() < len(y))

    out: dict = {"model_id": model_id, "n": int(len(p)),
                 "n_human": int(y.sum()), "n_ai": int((1 - y).sum()),
                 "convention": "in-set" if in_set else "deployed",
                 "scheme": scheme, "target_fpr": target_fpr}

    if in_set:
        cut = CAL.in_set_cut(p, y, target_fpr)
        if cut is None:
            out["error"] = ("in-set calibration needs humans in the eval set; "
                            "this set has none. Use the deployed convention.")
            return out
        fires = p < cut
        covered = np.ones(len(p), dtype=bool)
        out["cut"] = cut
        out["estimable"] = M.estimable(target_fpr, int(y.sum()))
        if not out["estimable"]:
            out["warning"] = (f"{int(y.sum())} humans cannot estimate a {target_fpr:.1%} "
                              f"quantile; needs {M.MIN_CALIBRATION_DOCS / target_fpr:,.0f}")
    else:
        if thresholds is None:
            raise ValueError("the deployed convention needs a Thresholds object; "
                             "run scripts/calibrate/derive_thresholds.py first")
        # A run id records the arm AND what it was fed (`..._on_document`), but a
        # cut is fitted per arm-and-input pair, so the calibration entry may be
        # named differently from the run. `calibration_id` names it explicitly.
        applied = thresholds.apply(calibration_id or model_id, p, target_fpr,
                                   scheme, groups)
        fires, covered = applied["fires"], applied["covered"]
        out["cut"] = applied.get("cut")
        out["cuts"] = applied.get("cuts")
        out["n_filtered"] = applied["n_filtered"]
        if applied.get("uncalibrated_groups"):
            out["uncalibrated_groups"] = applied["uncalibrated_groups"]

    f, yc = fires[covered], y[covered]
    out["n_scored"] = int(covered.sum())
    out["fire_rate"] = float(f.mean()) if f.size else float("nan")
    if yc.sum():
        out["realised_fpr"] = float(f[yc == 1].mean())
    if (1 - yc).sum():
        out["tpr"] = float(f[yc == 0].mean())

    if not single_class:
        out["auc"] = M.auc_score(p, y)
        out["tpr_at_fpr"] = M.point_metrics(p, y)["tpr_at_fpr"]
        if n_boot:
            out["ci"] = M.bootstrap_ci(p, y, n_boot=n_boot)
        if groups is not None:
            out[f"by_{group_name}"] = M.by_group(p, y, groups,
                                                 threshold=out.get("cut") or 0.5)
    else:
        out["note"] = ("single-class set: fire rate is the reading; there is no "
                       "TPR or FPR to report")
    return out


def table(results: list[tuple[str, dict]]) -> str:
    """Comparison table across arms, with realised FPR beside every TPR."""
    head = (f"{'arm':<28}{'n':>7}{'conv':>10}{'scheme':>9}{'cut':>10}"
            f"{'TPR':>9}{'realised FPR':>14}{'fire rate':>11}{'AUC':>9}{'filtered':>10}")
    lines = [head, "-" * len(head)]
    for name, r in results:
        fmt = lambda k, w, d=4: (f"{r[k]:>{w}.{d}f}" if isinstance(r.get(k), float)
                                 and not np.isnan(r[k]) else f"{'—':>{w}}")
        lines.append(
            f"{name:<28}{r.get('n', 0):>7}{r.get('convention', ''):>10}"
            f"{r.get('scheme', ''):>9}{fmt('cut', 10, 5)}{fmt('tpr', 9)}"
            f"{fmt('realised_fpr', 14)}{fmt('fire_rate', 11)}{fmt('auc', 9)}"
            f"{r.get('n_filtered', 0):>10}")
    return "\n".join(lines)


def ladder_table(results: dict[str, dict], order: list[str] | None = None) -> str:
    """Fire rate by rung, for sets where every row carries the same true label.

    Ladders are read as a shape, not as a score: the question is whether the fire
    rate tracks how much of the idea was the human's.
    """
    rungs = order or sorted(results)
    lines = [f"{'rung':<26}{'n':>7}{'fire rate':>12}{'mean P(human)':>16}"]
    for rung in rungs:
        r = results.get(rung, {})
        mp = r.get("mean_p_human")
        lines.append(f"{rung:<26}{r.get('n', 0):>7}"
                     f"{r.get('fire_rate', float('nan')):>12.4f}"
                     + (f"{mp:>16.4f}" if isinstance(mp, float) else f"{'—':>16}"))
    return "\n".join(lines)


def quadrant_table(cells: dict[tuple[str, str], dict]) -> str:
    """Fire rates on the ideas x prose grid.

    Rows are who conceived the ideas, columns who wrote the prose. The claim
    under test is that an idea-level detector varies down the rows and a surface
    detector varies across the columns.
    """
    ideas = sorted({k[0] for k in cells})
    prose = sorted({k[1] for k in cells})
    corner = "ideas \\ prose"
    lines = [f"{corner:<18}" + "".join(f"{p:>16}" for p in prose)]
    for i in ideas:
        row = f"{i:<18}"
        for p in prose:
            c = cells.get((i, p))
            row += (f"{c['fire_rate']:>15.3f} " if c and c.get("fire_rate") is not None
                    else f"{'—':>16}")
        lines.append(row)
    return "\n".join(lines)


def markdown_table(rows: list[dict], columns: list[str],
                   headers: list[str] | None = None) -> str:
    """Plain markdown, for pasting into a document."""
    headers = headers or columns
    fmt = lambda v: (f"{v:.4f}" if isinstance(v, float) else
                     ("" if v is None else str(v)))
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(fmt(r.get(c)) for c in columns) + " |")
    return "\n".join(out)
