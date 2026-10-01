"""The consolidated feature bank, and the interpretable classifier built on it.

Feature discovery produces named, operationalised features; this module makes
them usable. It is the bridge between "a frontier model proposed 201 features"
and "here is a transparent classifier and what it weights".

THE BANK
--------
`prompts/feature_discovery/feature_bank.json` holds the canonical features after
consolidation, each with a direction, a tier and a full scoring spec. Two tiers,
and the difference is operational, not cosmetic:

    programmatic  computable from the outline by deterministic rule. Free, exact,
                  reproducible. Implemented in scripts/features/assign/feature_programmatic.py.
    judgment      needs a model to read the idea and rate it. Costs real money at
                  corpus scale -- roughly $0.015 per document, so about $766 for
                  50,000 and about $2,600 for 170,000, and that is WITH an 81%
                  prompt-cache hit rate.

So the tier split is a budget decision as much as a methodological one. Probe the
programmatic tier first; it costs nothing and tells you whether the judgment tier
is worth buying.

THE SHORTCUT FEATURE
--------------------
One feature, `explicit_machine_authorship_disclosure`, fires when the document
says outright that a model wrote it. It is real, it is predictive, and it is a
shortcut: it measures disclosure practice, not authorship, and a detector leaning
on it would collapse the moment disclosure conventions changed. `DROP_BY_DEFAULT`
holds it and `load_matrix` removes it unless asked otherwise. Report any number
that includes it separately and say so.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from .. import paths

#: Features excluded from the interpretable model by default, and why.
DROP_BY_DEFAULT = {
    "explicit_machine_authorship_disclosure":
        "a self-disclosure shortcut: it measures whether the document ADMITS to "
        "being model-written, not whether it is. Predictive, but it would vanish "
        "with a change in disclosure convention.",
}


@lru_cache(maxsize=1)
def load_bank(path: str | None = None) -> list[dict]:
    """The canonical features. Each has name, direction, tier, output_type, spec."""
    f = Path(path) if path else paths.prompts("feature_discovery", "feature_bank.json")
    payload = json.loads(f.read_text())
    return payload.get("canonical_features") or payload.get("features") or []


def by_tier(tier: str) -> list[dict]:
    return [f for f in load_bank() if f.get("tier") == tier]


def summary() -> str:
    bank = load_bank()
    import collections
    tiers = collections.Counter(f.get("tier") for f in bank)
    dirs = collections.Counter(f.get("direction") for f in bank)
    return (f"{len(bank)} canonical features  "
            f"tier={dict(tiers)}  direction={dict(dirs)}\n"
            f"  programmatic features cost nothing to compute; judgment features "
            f"need a model pass (~$0.015/document)")


def load_matrix(npz_path, drop_shortcuts: bool = True) -> dict:
    """Load an assignment matrix: ids, X, y, feature names.

    `y` is 1 for AI in these files, which is the OPPOSITE of how labels are
    stored everywhere else in this project, so it is flipped here to the standard
    `1 = HUMAN` on the way out. Getting this wrong inverts every reported number.
    """
    with np.load(npz_path, allow_pickle=True) as z:
        ids = [str(x) for x in z["ids"]]
        X = np.asarray(z["X"], dtype=np.float32)
        y_ai = np.asarray(z["y"]).astype(int)
        feats = [str(f) for f in z["feats"]]

    dropped = []
    if drop_shortcuts:
        keep = [i for i, f in enumerate(feats) if f not in DROP_BY_DEFAULT]
        dropped = [f for f in feats if f in DROP_BY_DEFAULT]
        X = X[:, keep]
        feats = [feats[i] for i in keep]

    return {"ids": ids, "X": X, "y_human": 1 - y_ai, "features": feats,
            "dropped": dropped, "n_ai": int(y_ai.sum()),
            "n_human": int((1 - y_ai).sum())}


def fit_interpretable(X, y_human, features, folds: int = 5, seed: int = 0) -> dict:
    """Cross-validated logistic regression over the named features.

    Returns out-of-fold P(human) plus signed weights, so the result is both a
    score that can go through the shared metrics and a readable statement of what
    the features say. This is the arm whose coefficients mean something.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    from .. import metrics as M

    y_ai = 1 - np.asarray(y_human, dtype=int)
    pipe = lambda: make_pipeline(StandardScaler(),
                                 LogisticRegression(max_iter=3000, C=1.0))
    p_ai = cross_val_predict(
        pipe(), X, y_ai,
        cv=StratifiedKFold(folds, shuffle=True, random_state=seed),
        method="predict_proba")[:, 1]
    p_human = 1.0 - p_ai

    w = pipe().fit(X, y_ai)[-1].coef_[0]
    order = np.argsort(w)
    return {
        "n": int(len(y_ai)), "n_features": len(features),
        "p_human": p_human,
        "metrics": M.point_metrics(p_human, y_human),
        "weights": dict(zip(features, w.round(4).tolist())),
        "toward_ai": [(features[i], round(float(w[i]), 4)) for i in order[::-1][:20]],
        "toward_human": [(features[i], round(float(w[i]), 4)) for i in order[:20]],
    }


def spec_of(name: str) -> str:
    """The full scoring instruction for one feature, as handed to a judge."""
    for f in load_bank():
        if f.get("name") == name:
            return f.get("operationalization") or f.get("spec") or ""
    raise KeyError(f"no feature named {name!r} in the bank")
