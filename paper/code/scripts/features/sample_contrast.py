#!/usr/bin/env python3
"""Build a balanced contrast set for feature discovery.

    # what distinguishes the CLASSES, one idea at a time
    python scripts/features/sample_contrast.py --config item_corpus_labels

    # what our CURRENT DETECTORS key on, whole outlines
    python scripts/features/sample_contrast.py --config outline_model_labels

Four configurations exist, crossing two axes:

    unit          outline  whole outline: structure, ordering and role composition
                           are all available
                  item     a single idea: structure is GONE, and the prompt
                           forbids proposing it
    label_source  corpus   the corpus's own labels -> what distinguishes the classes
                  model    the tails of our detectors' scores -> what the detectors
                           key on

The two label sources answer different questions and their outputs must never be
merged into one bank.

CONTROLS APPLIED HERE, NOT LEFT TO THE PROMPT:

* **Role matching.** Items inherit their label from the parent document and the
  classes use roles at different rates, so an unmatched draw lets the model
  "discover" the role distribution and call it authorship.
* **Within-cell cuts.** For the model-label source the percentile is taken inside
  each (format, role) cell. Median P(human) among human items ranges from about
  0.38 to about 0.99 across roles, so a global percentile would select roles
  rather than examples.
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from ideadet import config as C
from ideadet import formats as F
from ideadet import paths, registry
from ideadet.features import discovery as D
from ideadet.io import iter_outline_files, load_jsonl, write_json
from ideadet.outlines import content_of, items_of, role_of


def load_rows(eval_id: str, unit: str, scores_by_model: dict) -> list[dict]:
    ev = registry.get_eval(eval_id)
    labels = {}
    if ev.labels.exists():
        import json
        labels = json.loads(ev.labels.read_text())
    rows = []
    for doc_id, rec in iter_outline_files(ev.stage_dir("deleak")):
        label = rec.get("source") or (labels.get(doc_id) or {}).get("source")
        if label not in ("human", "ai"):
            continue
        fmt = rec.get("format")
        if unit == "outline":
            rows.append({"id": doc_id, "label": label, "format": fmt,
                         "role_name": None, "outline": rec.get("data"),
                         "scores": {m: s.get(doc_id) for m, s in scores_by_model.items()}})
        else:
            for i, item in enumerate(items_of(rec.get("data"))):
                key = f"{doc_id}#{i}"
                rows.append({"id": key, "label": label, "format": fmt,
                             "role_name": role_of(item), "content": content_of(item),
                             "scores": {m: s.get(key) for m, s in scores_by_model.items()}})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_args(ap, "features")
    ap.add_argument("--eval", default="indomain",
                    help="which scored set to draw from; the in-domain test slice by default")
    ap.add_argument("--formats", default="", help="comma-separated; default all, or agnostic")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    cfg = C.from_args(a, "features")
    scores = {}
    if cfg["label_source"] == "model":
        for key in cfg.get("score_keys", []):
            f = paths.outputs(a.eval, key, "scores.jsonl")
            alt = paths.outputs(a.eval, key, "item_scores.npz")
            if f.exists():
                scores[key] = {r["id"]: r["p_human"] for r in load_jsonl(f)}
            elif alt.exists():
                from ideadet.io import load_npz
                z = load_npz(alt)
                scores[key] = {str(i): float(p) for i, p in zip(z["doc_ids"], z["p_human"])}
            else:
                raise SystemExit(
                    f"label_source=model needs scores from {key!r} on {a.eval}. "
                    f"Run scripts/eval/score.py --eval {a.eval} --model {key} first.")

    rows = load_rows(a.eval, cfg["unit"], scores)
    print(f"{len(rows):,} {cfg['unit']}(s) from {a.eval}, "
          f"label_source={cfg['label_source']}")

    out_dir = paths.outputs("feature_discovery", "contrast")
    out_dir.mkdir(parents=True, exist_ok=True)

    targets = ([None] if cfg.get("format_agnostic")
               else [x.strip() for x in a.formats.split(",") if x.strip()]
               or list(F.TRAIN_FORMATS))
    for fmt in targets:
        contrast = D.sample_contrast(
            rows, unit=cfg["unit"], label_source=cfg["label_source"],
            per_side=cfg["per_side"], match_roles=cfg["match_roles"],
            format_agnostic=cfg.get("format_agnostic", False),
            fmt=fmt, extreme_quantile=cfg.get("extreme_quantile", 0.10),
            score_keys=tuple(cfg.get("score_keys", ())), seed=cfg["seed"])
        tag = f"{cfg['unit']}_{cfg['label_source']}_" + (F.slug(fmt) if fmt else "agnostic")
        dest = out_dir / f"{tag}.json"
        write_json(dest, {**contrast, "stamp": C.stamp(cfg, {"eval": a.eval})})
        print(f"  {tag:<44}{contrast['per_side']:>6} per side  "
              f"{contrast['n_cells']:>5} cells -> {dest.name}")
        if contrast["per_side"] < cfg["per_side"] * 0.5:
            print(f"    note: only {contrast['per_side']} per side available after "
                  f"role matching; the smaller side of some cells is the binding "
                  f"constraint, not the request")


if __name__ == "__main__":
    sys.exit(main())
