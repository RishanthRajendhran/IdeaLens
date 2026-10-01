"""The single source of truth for every reported number.

Every model arm calls this module and nothing else, so the arms stay directly
comparable and a change to a metric changes all of them at once.

CONVENTIONS
-----------
    y_human : 1 = HUMAN, 0 = AI          (this is how labels are stored)
    p_human : P(human), in [0, 1]

    The POSITIVE CLASS for every reported metric is AI:
        y_ai     = 1 - y_human
        score_ai = 1 - p_human
        fires    = p_human < threshold

A detector therefore "fires" BELOW the threshold, and thresholds are LOW
quantiles of the human score distribution. Getting this backwards is the single
most common error in this codebase's history; one earlier run reported AUC 0.276
because of it. `check_orientation` below exists to catch it.

**TPR at a fixed low FPR is the headline metric.** AUC may be reported
alongside, never alone: at the operating points that matter, two arms with the
same AUC can differ by 30 points of TPR.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve

#: Reported FPR operating points. 1% is the field standard and the primary one.
#: The two strictest rest on very few human documents unless the calibration set
#: is large; see `estimable`.
FPR_TARGETS = (0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20)

#: A threshold at quantile q is only reportable when it rests on at least this
#: many human documents. At 10,000 calibration humans the floor is 0.25%.
MIN_CALIBRATION_DOCS = 25


def estimable(q: float, n_human: int) -> bool:
    """Is a target FPR of `q` estimable from `n_human` calibration documents?"""
    return q * n_human >= MIN_CALIBRATION_DOCS


def check_orientation(p_human, y_human, tol: float = 0.05) -> float:
    """Raise if the arrays look flipped. Returns the AUC it computed.

    A detector that has learned anything scores humans HIGHER than AI. An AUC
    materially below 0.5 almost always means `y` or `p` was passed inverted, not
    that the model is anti-predictive.
    """
    auc = auc_score(p_human, y_human)
    if auc is not None and auc < 0.5 - tol:
        raise ValueError(
            f"AUC {auc:.4f} is well below chance. Check the label orientation: "
            f"y_human must be 1 for HUMAN and p_human must be P(human). "
            f"Pass 1-y / 1-p if the source stored AI as the positive class.")
    return auc


def auc_score(p_human, y_human) -> float | None:
    p = np.asarray(p_human, dtype=float)
    y_ai = 1 - np.asarray(y_human, dtype=int)
    if not 0 < y_ai.sum() < len(y_ai):
        return None                      # single-class set: AUC undefined
    return float(roc_auc_score(y_ai, 1 - p))


def point_metrics(p_human, y_human, threshold: float = 0.5,
                  fpr_targets: tuple = FPR_TARGETS) -> dict:
    """Confusion-matrix metrics at one threshold, plus the TPR@FPR sweep."""
    p = np.asarray(p_human, dtype=float)
    y_h = np.asarray(y_human, dtype=int)
    y_ai = 1 - y_h

    fires = p < threshold
    tp = int((fires & (y_ai == 1)).sum())
    fp = int((fires & (y_ai == 0)).sum())
    fn = int((~fires & (y_ai == 1)).sum())
    tn = int((~fires & (y_ai == 0)).sum())

    prec = tp / (tp + fp or 1)
    rec = tp / (tp + fn or 1)
    out = {
        "n": int(len(y_h)), "n_human": int(y_h.sum()), "n_ai": int(y_ai.sum()),
        "threshold": float(threshold),
        "accuracy": (tp + tn) / (len(y_h) or 1),
        "tpr": rec,                       # AI recall: the headline quantity
        "fpr": fp / (fp + tn or 1),       # humans wrongly flagged AI
        "precision": prec,
        "f1": 2 * prec * rec / ((prec + rec) or 1),
        "auc": auc_score(p, y_h),
        "counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
    }
    if out["auc"] is not None:
        fpr_c, tpr_c, _ = roc_curve(y_ai, 1 - p)
        out["tpr_at_fpr"] = {str(t): float(np.interp(t, fpr_c, tpr_c))
                             for t in fpr_targets}
    return out


def fire_rate(p_human, threshold: float) -> float:
    """Share of documents the detector flags AI, with no labels involved.

    The right metric for sets where every document carries the same true label
    (the collaboration ladder, OpAI-Bench): there is no TPR to report, only how
    often the detector fires as the construction varies.
    """
    p = np.asarray(p_human, dtype=float)
    return float((p < threshold).mean()) if p.size else float("nan")


def bootstrap_ci(p_human, y_human, n_boot: int = 1000, seed: int = 0,
                 alpha: float = 0.05, fpr_targets: tuple = FPR_TARGETS) -> dict:
    """Percentile CIs for AUC and TPR@FPR, resampling documents with replacement.

    This propagates sampling noise in the TEST set only. To also propagate
    threshold uncertainty, use `calibration.bootstrap_deployed_tpr`, which
    resamples the calibration humans and refits the cut on each draw.
    """
    p = np.asarray(p_human, dtype=float)
    y_h = np.asarray(y_human, dtype=int)
    n = len(y_h)
    rng = np.random.default_rng(seed)

    aucs, tprs = [], {str(t): [] for t in fpr_targets}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        ys, ps = y_h[idx], p[idx]
        y_ai = 1 - ys
        if not 0 < y_ai.sum() < len(y_ai):
            continue
        aucs.append(roc_auc_score(y_ai, 1 - ps))
        fpr_c, tpr_c, _ = roc_curve(y_ai, 1 - ps)
        for t in fpr_targets:
            tprs[str(t)].append(float(np.interp(t, fpr_c, tpr_c)))

    def ci(v):
        return None if not v else [float(np.quantile(v, alpha / 2)),
                                   float(np.quantile(v, 1 - alpha / 2))]

    return {"n_boot": len(aucs), "auc_ci": ci(aucs),
            "tpr_at_fpr_ci": {k: ci(v) for k, v in tprs.items()}}


def by_group(p_human, y_human, groups, min_n: int = 30,
             threshold: float = 0.5) -> dict:
    """Point metrics per group (format, language, generator, rung, ...).

    Groups below `min_n` are omitted rather than reported with unusable error
    bars. In-domain per-format TPR@1% spans roughly 3x across formats, so a
    pooled number alone hides most of what is going on.
    """
    p = np.asarray(p_human, dtype=float)
    y_h = np.asarray(y_human, dtype=int)
    g = np.asarray([str(x) for x in groups])
    out = {}
    for name in sorted(set(g.tolist())):
        m = g == name
        if m.sum() < min_n:
            continue
        out[name] = point_metrics(p[m], y_h[m], threshold)
    return out


def paired_delta(p_a, p_b, y_human, threshold: float, n_boot: int = 2000,
                 seed: int = 0) -> dict:
    """Paired comparison of two conditions over the SAME documents.

    Pairing roughly halves the CI width on every difference, which is why the
    evaluation core keeps one frozen document set across conditions. `p_a` and
    `p_b` must be aligned row by row.
    """
    p_a = np.asarray(p_a, dtype=float)
    p_b = np.asarray(p_b, dtype=float)
    y_h = np.asarray(y_human, dtype=int)
    if not (len(p_a) == len(p_b) == len(y_h)):
        raise ValueError("paired_delta needs three arrays of equal length, "
                         "aligned by document id")
    ok = ~(np.isnan(p_a) | np.isnan(p_b))
    p_a, p_b, y_h = p_a[ok], p_b[ok], y_h[ok]

    fire_a, fire_b = p_a < threshold, p_b < threshold
    d_score = float(np.mean(p_b - p_a))
    d_fire = float(fire_b.mean() - fire_a.mean())

    rng = np.random.default_rng(seed)
    n = len(p_a)
    ds, df = [], []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        ds.append(float(np.mean(p_b[i] - p_a[i])))
        df.append(float((p_b[i] < threshold).mean() - (p_a[i] < threshold).mean()))

    # McNemar on the discordant pairs: the exact test for a paired change in a
    # binary decision, which a two-sample proportion test would get wrong here.
    b = int((fire_a & ~fire_b).sum())
    c = int((~fire_a & fire_b).sum())
    mcnemar = ((b - c) ** 2 / (b + c)) if (b + c) else 0.0

    q = lambda v: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]
    return {"n_paired": n,
            "mean_score_shift": d_score, "mean_score_shift_ci": q(ds),
            "fire_rate_shift": d_fire, "fire_rate_shift_ci": q(df),
            "discordant": {"a_only": b, "b_only": c},
            "mcnemar_chi2": mcnemar,
            "spearman": float(_spearman(p_a, p_b))}


def _spearman(a, b) -> float:
    from scipy.stats import spearmanr
    if len(a) < 3:
        return float("nan")
    return spearmanr(a, b).statistic


def summarize(p_human, y_human, *, threshold: float = 0.5, groups=None,
              group_name: str = "format", n_boot: int = 1000,
              seed: int = 0, fpr_targets: tuple = FPR_TARGETS) -> dict:
    """Everything reportable about one (eval set, model arm) pair."""
    out = {"point": point_metrics(p_human, y_human, threshold, fpr_targets)}
    if out["point"]["auc"] is not None:
        if n_boot:
            out["ci"] = bootstrap_ci(p_human, y_human, n_boot, seed,
                                     fpr_targets=fpr_targets)
        if groups is not None:
            out[f"by_{group_name}"] = by_group(p_human, y_human, groups,
                                               threshold=threshold)
    else:
        # Single-class set: fire rate is the only meaningful reading.
        out["fire_rate"] = fire_rate(p_human, threshold)
    return out


def format_table(rows: list[tuple[str, dict]],
                 fpr_targets: tuple = FPR_TARGETS) -> str:
    """Aligned TPR@FPR comparison table. `rows` is [(name, summarize(...)), ...]."""
    head = "".join(f"{t * 100:>9g}%" for t in fpr_targets)
    lines = [f"{'arm':<30}{'n':>8}   TPR@FPR:{head}{'AUC':>10}"]
    for name, s in rows:
        pt = s.get("point", {})
        if "tpr_at_fpr" not in pt:
            lines.append(f"{name:<30}{pt.get('n', 0):>8}   "
                         f"fire rate {s.get('fire_rate', float('nan')):.4f} (single class)")
            continue
        cells = "".join(f"{pt['tpr_at_fpr'][str(t)]:>10.4f}" for t in fpr_targets)
        auc = f"{pt['auc']:.4f}" if pt["auc"] is not None else "n/a"
        lines.append(f"{name:<30}{pt['n']:>8}           {cells}{auc:>10}")
    return "\n".join(lines)
