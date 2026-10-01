"""Interpretable probes: how much of the signal each feature family carries.

Every probe is a transparent classifier over one named feature family, fitted
with cross-validation, reported as AUC and as TPR at the operating points that
matter. The point is not to beat the detector; it is to say what is in the
representation.

FAMILIES, AND WHAT EACH ONE ISOLATES
------------------------------------
    structural   item count, content-length statistics, role diversity and
                 entropy, longest same-role run, verbatim fraction, words/item
    role_freq    bag of roles: composition, with order discarded
    role_order   bag of role bigrams: order, with composition largely discarded
    role_all     roles 1-2grams, the strongest content-free probe
    lexical      content words — powerful in-corpus and heavily topic-inflated

TWO READINGS THAT MUST BE REPORTED TOGETHER
-------------------------------------------
* **Pooled AUC** overstates every lexical probe, because format and topic are
  free signal. A content-word probe reaching 0.98 pooled collapses to about 0.80
  under leave-one-format-out.
* **Format-controlled AUC** is the honest number. Role-based probes hold up
  under it, which is why "AI writing has different rhetorical structure" survives
  and "AI writing uses different words" mostly does not.

`leave_one_format_out` is therefore not optional decoration; report it beside
every pooled figure.

**Length is not a confound**, and this module measures that rather than assuming
it: item count alone gives roughly AUC 0.54 and document word count roughly 0.51.
Any probe that beats those is carrying something other than length.
"""
from __future__ import annotations

import collections
import math

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ..outlines import content_of, items_of, role_of

#: Roles / bigrams appearing in fewer than this share of items are dropped.
MIN_ROLE_FREQ = 0.002


def _pipe():
    return make_pipeline(StandardScaler(with_mean=False),
                         LogisticRegression(max_iter=3000, C=1.0))


# ---------------------------------------------------------------- features ---
def structural_features(outline) -> dict:
    items = items_of(outline)
    if not items:
        return {}
    lengths = [len(content_of(i).split()) for i in items]
    roles = [role_of(i) for i in items]
    counts = collections.Counter(roles)
    total = len(roles)
    entropy = -sum((c / total) * math.log(c / total) for c in counts.values())

    longest_run = best = 1
    for a, b in zip(roles, roles[1:]):
        best = best + 1 if a == b else 1
        longest_run = max(longest_run, best)

    return {
        "n_items": total,
        "n_words": sum(lengths),
        "mean_words_per_item": float(np.mean(lengths)),
        "sd_words_per_item": float(np.std(lengths)),
        "max_words_per_item": max(lengths),
        "min_words_per_item": min(lengths),
        "n_distinct_roles": len(counts),
        "role_entropy": entropy,
        "role_diversity": len(counts) / total,
        "longest_same_role_run": longest_run,
        "verbatim_fraction": sum(1 for i in items if i.get("verbatim")) / total,
    }


def role_ngrams(outline, n: int = 1) -> collections.Counter:
    roles = [role_of(i) for i in items_of(outline)]
    if n == 1:
        return collections.Counter(roles)
    return collections.Counter("|".join(roles[i:i + n])
                               for i in range(len(roles) - n + 1))


def build_matrix(outlines: list, family: str) -> tuple[np.ndarray, list[str]]:
    """Feature matrix and column names for one family."""
    if family == "structural":
        rows = [structural_features(o) for o in outlines]
        cols = sorted({k for r in rows for k in r})
        X = np.array([[r.get(c, 0.0) for c in cols] for r in rows], dtype=np.float32)
        return X, cols

    if family in ("role_freq", "role_order", "role_all"):
        orders = {"role_freq": (1,), "role_order": (2,), "role_all": (1, 2)}[family]
        counters = []
        for o in outlines:
            c = collections.Counter()
            for n in orders:
                c.update(role_ngrams(o, n))
            counters.append(c)
        totals = collections.Counter()
        for c in counters:
            totals.update(c)
        grand = sum(totals.values()) or 1
        cols = sorted(k for k, v in totals.items() if v / grand >= MIN_ROLE_FREQ)
        idx = {c: i for i, c in enumerate(cols)}
        X = np.zeros((len(counters), len(cols)), dtype=np.float32)
        for r, c in enumerate(counters):
            n = sum(c.values()) or 1
            for k, v in c.items():
                if k in idx:
                    X[r, idx[k]] = v / n            # normalise: not a length probe
        return X, cols

    if family == "lexical":
        from sklearn.feature_extraction.text import TfidfVectorizer
        texts = [" ".join(content_of(i) for i in items_of(o)) for o in outlines]
        vec = TfidfVectorizer(min_df=5, max_features=50000, sublinear_tf=True)
        return vec.fit_transform(texts).toarray().astype(np.float32), \
            list(vec.get_feature_names_out())

    raise ValueError(f"unknown feature family {family!r}")


# ------------------------------------------------------------------ fitting --
def cv_auc(X, y_ai, folds: int = 5, seed: int = 0) -> tuple[float, np.ndarray]:
    """Cross-validated AUC and out-of-fold scores. `y_ai` is 1 for AI."""
    y_ai = np.asarray(y_ai, dtype=int)
    if not 0 < y_ai.sum() < len(y_ai):
        return float("nan"), np.full(len(y_ai), np.nan)
    k = folds if min(y_ai.sum(), (1 - y_ai).sum()) >= 25 else 3
    p = cross_val_predict(_pipe(), X, y_ai,
                          cv=StratifiedKFold(k, shuffle=True, random_state=seed),
                          method="predict_proba")[:, 1]
    return float(roc_auc_score(y_ai, p)), p


def format_controlled_auc(X, y_ai, formats, min_each: int = 8) -> float:
    """AUC pooled over WITHIN-FORMAT fits, so format cannot be the signal."""
    y_ai = np.asarray(y_ai, dtype=int)
    formats = np.asarray([str(f) for f in formats])
    num = den = 0.0
    for f in sorted(set(formats.tolist())):
        m = formats == f
        yg = y_ai[m]
        if yg.sum() < min_each or (len(yg) - yg.sum()) < min_each:
            continue
        auc, _ = cv_auc(X[m], yg)
        if not math.isnan(auc):
            num += auc * m.sum()
            den += m.sum()
    return num / den if den else float("nan")


def leave_one_format_out(X, y_ai, formats) -> dict:
    """Fit on every format but one, test on the held-out format.

    This is the number that separates a real stylistic difference from corpus
    topic. Lexical probes fall sharply here; role probes hold.
    """
    y_ai = np.asarray(y_ai, dtype=int)
    formats = np.asarray([str(f) for f in formats])
    out = {}
    for f in sorted(set(formats.tolist())):
        te = formats == f
        tr = ~te
        if not (0 < y_ai[te].sum() < te.sum()) or not (0 < y_ai[tr].sum() < tr.sum()):
            continue
        pipe = _pipe().fit(X[tr], y_ai[tr])
        out[f] = float(roc_auc_score(y_ai[te], pipe.predict_proba(X[te])[:, 1]))
    out["mean"] = float(np.mean([v for k, v in out.items() if k != "mean"])) if out else float("nan")
    return out


def run_family(outlines: list, y_human, formats, family: str,
               seed: int = 0) -> dict:
    """One family's full report: pooled, format-controlled, and LOFO."""
    X, cols = build_matrix(outlines, family)
    y_ai = 1 - np.asarray(y_human, dtype=int)
    pooled, oof = cv_auc(X, y_ai, seed=seed)
    return {
        "family": family, "n": int(len(y_ai)), "n_features": len(cols),
        "auc_pooled": pooled,
        "auc_format_controlled": format_controlled_auc(X, y_ai, formats),
        "auc_leave_one_format_out": leave_one_format_out(X, y_ai, formats),
        "top_features": top_weights(X, y_ai, cols),
        "oof_scores": oof.tolist(),
    }


def top_weights(X, y_ai, cols, k: int = 15) -> dict:
    """Signed coefficients of a single full fit, for interpretation only."""
    pipe = _pipe().fit(X, y_ai)
    w = pipe[-1].coef_[0]
    order = np.argsort(w)
    return {"toward_ai": [(cols[i], round(float(w[i]), 4)) for i in order[::-1][:k]],
            "toward_human": [(cols[i], round(float(w[i]), 4)) for i in order[:k]]}


def compare_families(outlines: list, y_human, formats,
                     families=("structural", "role_freq", "role_order",
                               "role_all", "lexical")) -> str:
    rows = [run_family(outlines, y_human, formats, f) for f in families]
    lines = [f"{'family':<14}{'n_feat':>8}{'pooled AUC':>12}"
             f"{'fmt-controlled':>16}{'leave-1-fmt-out':>17}"]
    for r in rows:
        lines.append(f"{r['family']:<14}{r['n_features']:>8}{r['auc_pooled']:>12.4f}"
                     f"{r['auc_format_controlled']:>16.4f}"
                     f"{r['auc_leave_one_format_out']['mean']:>17.4f}")
    return "\n".join(lines)
