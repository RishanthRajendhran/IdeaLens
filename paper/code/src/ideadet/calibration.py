"""Thresholds: how they are derived, where they live, and which one to use.

A detector score is meaningless without an operating point, and a threshold
picked on the set you are reporting is not an operating point — it is a fitted
parameter. This module implements the project's threshold policy so that no
script has to reimplement it, and so that every reported number can name the
convention it used.

THE TWO CONVENTIONS, ALWAYS LABELLED, NEVER MIXED SILENTLY
----------------------------------------------------------
**deployed** (primary). One threshold per model, fitted once on a held-out,
human-only calibration split, then carried unchanged onto every eval set. This
is what a deployment can actually do, and it is the convention every headline
number uses.

**in-set** (secondary, out-of-domain only). The threshold re-derived from the
eval set's own humans. Reported beside the deployed number on OOD sets because
the two diverge by roughly 4x there, and that divergence is itself a finding
about detector deployment rather than a nuisance. Never report in-set alone,
and never report in-set in-domain.

THREE CALIBRATION-DERIVED SCHEMES
---------------------------------
    global      one cut per model
    format      a cut per document format, routed by the format classifier
    topic       a cut per topic

All three are fitted on the calibration split only. A document whose format has
no calibrated cut is **filtered out and reported as such — never given the
global cut as a fallback**, because a fallback silently mixes two operating
points in one column.

ESTIMABILITY
------------
A target FPR of q needs `q * n_calibration_humans >= 25` (`metrics.MIN_CALIBRATION_DOCS`).
At 10,000 calibration humans, 0.25% is the floor and 0.1% is not reportable.
`derive` refuses to emit a cut it cannot estimate rather than emitting a noisy one.
"""
from __future__ import annotations

import numpy as np

from . import metrics as M
from .io import load_json, write_json

#: Minimum humans in a group before that group gets its own cut. Per-format cuts
#: at 1% FPR are well determined only around 2,500 humans per format; below that
#: they overshoot the nominal FPR, which is why `shrink` exists.
MIN_GROUP_HUMANS = 200


def threshold_at_fpr(p_human_calibration, target_fpr: float) -> float | None:
    """The P(human) cut that puts `target_fpr` of calibration humans below it.

    Returns None when the split has no humans. The detector fires BELOW the cut,
    so this is a LOW quantile of the human score distribution.
    """
    p = np.asarray(p_human_calibration, dtype=float)
    p = p[~np.isnan(p)]
    if p.size == 0:
        return None
    return float(np.quantile(p, target_fpr))


def shrink(group_cut: float, pooled_cut: float, n_group: int,
           n_target: int = 2500) -> float:
    """Pull a thinly-estimated per-group cut toward the pooled cut.

    Per-format thresholds are a real gain (fit-on-half / score-on-half costs
    under a point of TPR), but with roughly a dozen humans per format cell a raw
    per-format cut overshoots the nominal FPR — nominal 1% lands at 1.13-1.18%
    realised. Shrinkage with weight n/(n + n_target) is mandatory, not a
    refinement: below `n_target` humans the group cut is mostly noise and the
    weight reflects that.
    """
    w = n_group / (n_group + n_target)
    return float(pooled_cut + w * (group_cut - pooled_cut))


def derive(p_human, *, groups: dict | None = None, targets=M.FPR_TARGETS,
           min_group_humans: int = MIN_GROUP_HUMANS, apply_shrinkage: bool = True,
           model_id: str = "", split: str = "calibration") -> dict:
    """Fit every calibration-derived cut for one model from a human-only split.

    `p_human` are the scores of calibration HUMANS only. `groups` maps a scheme
    name to a parallel array of labels, e.g. {"format": [...], "topic": [...]}.

    The returned dict is the unit stored in `outputs/calibration/thresholds.json`.
    """
    p = np.asarray(p_human, dtype=float)
    p = p[~np.isnan(p)]
    n = int(p.size)
    if n == 0:
        raise ValueError("calibration split contains no scored humans")

    out = {
        "model_id": model_id,
        "split": split,
        "n_calibration_humans": n,
        "min_group_humans": min_group_humans,
        "shrinkage": apply_shrinkage,
        "estimable_floor": round(M.MIN_CALIBRATION_DOCS / n, 6),
        "global": {},
        "not_estimable": [],
        # Saturation matters: when most human scores sit above 0.999 the cut is
        # determined by a handful of near-identical values and small score shifts
        # move the realised FPR a long way.
        "saturation": {
            "gt_0.99": round(float((p > 0.99).mean()), 5),
            "gt_0.999": round(float((p > 0.999).mean()), 5),
            "mid_0.05_0.95": round(float(((p > 0.05) & (p < 0.95)).mean()), 5),
        },
    }

    for q in targets:
        if not M.estimable(q, n):
            out["not_estimable"].append(str(q))
            continue
        out["global"][str(q)] = threshold_at_fpr(p, q)

    for scheme, labels in (groups or {}).items():
        lab = np.asarray([str(x) for x in labels])
        if len(lab) != len(np.asarray(p_human, dtype=float)):
            raise ValueError(f"group array {scheme!r} is not aligned with p_human")
        lab = lab[~np.isnan(np.asarray(p_human, dtype=float))]
        out[scheme] = {}
        for q in targets:
            if str(q) not in out["global"]:
                continue
            cell = {}
            for name in sorted(set(lab.tolist())):
                m = lab == name
                n_g = int(m.sum())
                if n_g < min_group_humans or not M.estimable(q, n_g):
                    continue
                cut = threshold_at_fpr(p[m], q)
                if apply_shrinkage:
                    cut = shrink(cut, out["global"][str(q)], n_g)
                cell[name] = cut
            out[scheme][str(q)] = cell
        out[f"{scheme}_n"] = {name: int((lab == name).sum())
                              for name in sorted(set(lab.tolist()))}
    return out


class MissingGroups(KeyError):
    """A per-group scheme was asked for on scores that carry no such column."""


class Thresholds:
    """Read-side view of `outputs/calibration/thresholds.json`.

    Every scoring and reporting script goes through this class, so a threshold
    can never be produced ad hoc at report time.
    """

    def __init__(self, payload: dict):
        self.payload = payload
        self.models = payload.get("models", {})

    @classmethod
    def load(cls, path) -> "Thresholds":
        return cls(load_json(path))

    def save(self, path):
        return write_json(path, self.payload)

    def model(self, model_id: str) -> dict:
        if model_id not in self.models:
            raise KeyError(
                f"no calibration for model {model_id!r}. Available: "
                f"{sorted(self.models)}. Run scripts/calibrate/derive_thresholds.py "
                f"for this model before reporting any number from it.")
        return self.models[model_id]

    def cut(self, model_id: str, target_fpr: float, scheme: str = "global",
            group: str | None = None) -> float | None:
        """The deployed cut for one model at one target FPR.

        Returns None when the scheme has no cut for that group — the caller must
        FILTER those documents, never substitute the global cut.
        """
        m = self.model(model_id)
        q = str(target_fpr)
        if scheme == "global":
            return m.get("global", {}).get(q)
        if group is None:
            raise ValueError(f"scheme {scheme!r} needs a group label")
        return m.get(scheme, {}).get(q, {}).get(group)

    def apply(self, model_id: str, p_human, target_fpr: float,
              scheme: str = "global", groups=None) -> dict:
        """Fire/no-fire decisions under one scheme, with the filtered rows named.

        Returns `fires` and `covered` boolean arrays. Rows where `covered` is
        False had no calibrated cut and must be excluded from every rate this
        column reports; `n_filtered` is the number to print beside it.
        """
        p = np.asarray(p_human, dtype=float)
        fires = np.zeros(len(p), dtype=bool)
        covered = np.zeros(len(p), dtype=bool)

        if scheme == "global":
            cut = self.cut(model_id, target_fpr)
            if cut is None:
                raise KeyError(
                    f"{model_id} has no estimable cut at {target_fpr}; it needs "
                    f"at least {M.MIN_CALIBRATION_DOCS / target_fpr:,.0f} calibration humans")
            fires = p < cut
            covered[:] = ~np.isnan(p)
            return {"fires": fires, "covered": covered, "cut": cut,
                    "n_filtered": int((~covered).sum()), "scheme": scheme,
                    "target_fpr": target_fpr, "model_id": model_id}

        if groups is None:
            raise MissingGroups(
                f"the {scheme!r} scheme needs a per-row {scheme} label and this "
                f"eval's scores carry none. Either add {scheme} to the score rows "
                f"(scripts/eval/score.py copies it from the corpus when present) "
                f"or drop {scheme!r} from this eval's report.schemes. It must NOT "
                f"fall back to the global cut: that would mix two operating points "
                f"in one column.")
        g = np.asarray([str(x) for x in groups])
        cuts = {}
        for name in sorted(set(g.tolist())):
            cut = self.cut(model_id, target_fpr, scheme, name)
            if cut is None:
                continue
            m = (g == name) & ~np.isnan(p)
            fires[m] = p[m] < cut
            covered[m] = True
            cuts[name] = cut
        return {"fires": fires, "covered": covered, "cuts": cuts,
                "n_filtered": int((~covered).sum()), "scheme": scheme,
                "target_fpr": target_fpr, "model_id": model_id,
                "uncalibrated_groups": sorted(set(g[~covered].tolist()))}


def in_set_cut(p_human, y_human, target_fpr: float) -> float | None:
    """The secondary convention: threshold from the eval set's OWN humans.

    Only for out-of-domain sets, only reported beside the deployed number, and
    always labelled `in-set` wherever it appears.
    """
    p = np.asarray(p_human, dtype=float)
    y = np.asarray(y_human, dtype=int)
    return threshold_at_fpr(p[y == 1], target_fpr)


def bootstrap_deployed_tpr(p_calibration_human, p_test, y_test,
                           target_fpr: float, n_boot: int = 1000,
                           seed: int = 0) -> dict:
    """TPR with threshold uncertainty folded in.

    Resamples the CALIBRATION humans, refits the cut on each draw, and applies it
    to the test set. The plain test-set bootstrap in `metrics` treats the cut as
    exact; at 5,000 calibration humans the realised FPR at a nominal 1% ran
    0.66-1.35% across draws, so treating it as exact understates the interval.
    """
    cal = np.asarray(p_calibration_human, dtype=float)
    cal = cal[~np.isnan(cal)]
    p = np.asarray(p_test, dtype=float)
    y_ai = 1 - np.asarray(y_test, dtype=int)
    rng = np.random.default_rng(seed)

    tprs, fprs, cuts = [], [], []
    for _ in range(n_boot):
        draw = cal[rng.integers(0, len(cal), len(cal))]
        cut = float(np.quantile(draw, target_fpr))
        fires = p < cut
        cuts.append(cut)
        if y_ai.sum():
            tprs.append(float(fires[y_ai == 1].mean()))
        if (y_ai == 0).sum():
            fprs.append(float(fires[y_ai == 0].mean()))

    q = lambda v: None if not v else [float(np.quantile(v, 0.025)),
                                      float(np.quantile(v, 0.975))]
    return {"target_fpr": target_fpr, "n_boot": n_boot,
            "n_calibration_humans": int(len(cal)),
            "cut_mean": float(np.mean(cuts)), "cut_sd": float(np.std(cuts)),
            "tpr_mean": float(np.mean(tprs)) if tprs else None, "tpr_ci": q(tprs),
            "realised_fpr_mean": float(np.mean(fprs)) if fprs else None,
            "realised_fpr_ci": q(fprs)}
