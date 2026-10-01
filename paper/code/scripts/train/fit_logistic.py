#!/usr/bin/env python3
"""Fit the logistic baseline over cached text embeddings.

    python scripts/train/fit_logistic.py --config logistic_full --run v1m-lr-ep1

Cheap to refit, transparent to read, and multilingual for free because the
embedding is — which makes it the only arm that can attempt fully source-language
classification with no English step, and therefore the right thing to pilot a
multilingual variant with before anything expensive is built.

**The embedding cache is the expensive artifact, not the fit.** Embed once with
`scripts/eval/embed.py`, keep the cache, and refit as often as you like.
"""
from __future__ import annotations

import argparse
import pickle
import sys

import _bootstrap  # noqa: F401

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ideadet import config as C
from ideadet import paths
from ideadet import training as T
from ideadet.io import load_npz, save_npz, write_json


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_args(ap, "training")
    ap.add_argument("--run", required=True)
    ap.add_argument("--embeddings", required=True,
                    help="npz with `ids` and `X`, from scripts/eval/embed.py")
    ap.add_argument("--splits", default="data/calibration/splits.npz")
    a = ap.parse_args()

    cfg = C.from_args(a, "training")
    emb = load_npz(a.embeddings)
    z = load_npz(paths.REPO / a.splits)
    pos = {str(i): k for k, i in enumerate(emb["ids"])}

    data = {}
    for name in ("train", "val", "test"):
        idx = [i for i in np.flatnonzero(z["split"] == name)
               if str(z["ids"][i]) in pos]
        data[name] = {
            "X": emb["X"][[pos[str(z["ids"][i])] for i in idx]],
            "y": np.array([int(z["y"][i]) for i in idx]),
            "ids": [str(z["ids"][i]) for i in idx],
        }
    print("corpus: " + "  ".join(f"{k}={len(v['y']):,}" for k, v in data.items()))

    pipe = make_pipeline(StandardScaler(with_mean=False),
                         LogisticRegression(max_iter=3000, C=1.0))
    pipe.fit(data["train"]["X"], data["train"]["y"])

    ckpt = paths.scratch("checkpoints", f"logistic_{cfg['setting']}_{a.run}.pkl")
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    with open(ckpt, "wb") as fh:
        pickle.dump(pipe, fh)

    out = paths.outputs("training", f"logistic_{cfg['setting']}_{a.run}")
    out.mkdir(parents=True, exist_ok=True)
    for split in ("val", "test"):
        p = pipe.predict_proba(data[split]["X"])[:, cfg.get("human_index", 1)]
        save_npz(out / f"preds_{split}.npz", p_human=p, y=data[split]["y"],
                 doc_ids=np.array(data[split]["ids"], dtype=object))
        print(T.probe_report(0, p, data[split]["y"]).replace("step      0", f"{split:>10}"))
    write_json(out / "run.json", C.stamp(cfg, {"run": a.run, "checkpoint": str(ckpt)}))
    print(f"\nwrote {out}\nAdd `checkpoint: {ckpt}` to configs/models.yaml.")


if __name__ == "__main__":
    sys.exit(main())
