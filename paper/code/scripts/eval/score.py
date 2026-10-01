#!/usr/bin/env python3
"""Score one eval set with one detector arm.

    python scripts/eval/score.py --eval test5_peer_review --model nemotron_1m_full
    python scripts/eval/score.py --eval test0_deleak_invariance --model modernbert_1m_full \
        --stage extract                       # the untreated-outline side of the pair
    python scripts/eval/score.py --eval test8_storyscope --model modernbert_1m_docs \
        --stage document                      # the counterfactual arm reads prose

Writes `outputs/<eval>/<model>/`:

    scores.jsonl   one row per document, joinable and human-readable
    scores.npz     the same plus raw logits, which only exist at scoring time
    run.json       config, git revision, checkpoint — the provenance stamp

This script does not threshold anything. Thresholds come from the calibration
split and are applied at report time, so a score file can be re-read under a new
operating point without re-scoring.
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import config as C
from ideadet import paths, registry
from ideadet.detectors import load as load_detector
from ideadet.io import iter_outline_files, load_jsonl, save_npz, write_json, write_jsonl
from ideadet.outlines import summary as outline_summary
from ideadet.schema import y_human


def load_records(ev, stage: str, where: dict | None = None):
    """(ids, inputs, labels, metadata). `inputs` are outline records or documents."""
    labels = json.loads(ev.labels.read_text()) if ev.labels.exists() else {}
    corpus = {r["id"]: r for r in load_jsonl(ev.corpus)} if ev.corpus.exists() else {}
    keep = None
    if where:
        # Filter on corpus fields, so an arm can be scored without standing up a
        # separate eval dir for it (e.g. just the human arm of a matched set).
        keep = {i for i, r in corpus.items()
                if all(str(r.get(k)) == v for k, v in where.items())}
        if not keep:
            raise SystemExit(f"--where {where} matched no corpus rows")
        corpus = {i: r for i, r in corpus.items() if i in keep}
        print(f"  --where {where}: kept {len(corpus):,} rows")

    if stage == "document":
        if not corpus:
            raise SystemExit(f"{ev.id}: --stage document needs corpus.jsonl")
        rows = list(corpus.values())
        ids = [r["id"] for r in rows]
        return ids, [r["text"] for r in rows], rows, labels

    d = ev.stage_dir(stage)
    if not d.exists():
        raise SystemExit(
            f"{ev.id}: no {stage}/ directory. Run "
            f"scripts/pipeline/run_pipeline.py --eval {ev.id} first.")
    ids, inputs, meta = [], [], []
    for doc_id, rec in iter_outline_files(d):
        if keep is not None and doc_id not in keep:
            continue
        ids.append(doc_id)
        inputs.append(rec.get("data", rec))
        # Metadata may ride in labels.json, in the corpus row, or in the outline
        # file itself; several externally-built sets carry only the last.
        meta.append({**rec, **corpus.get(doc_id, {}), **labels.get(doc_id, {})})
    return ids, inputs, meta, labels


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--stage", default="", choices=["", "deleak", "extract", "document"],
                    help="default: the eval config's scoring.stage")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--where", action="append", default=[], metavar="KEY=VALUE",
                    help="keep only corpus rows whose KEY equals VALUE; repeatable")
    ap.add_argument("--run-id", default="", help="output directory name; default is --model")
    ap.add_argument("--force", action="store_true", help="rescore even if scores exist")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args()

    ev = registry.get_eval(a.eval)
    run = registry.get_model(a.model)
    stage = a.stage or ev.raw.get("scoring", {}).get("stage", "deleak")
    if run.setting == "docs" and stage != "document":
        stage = "document"                    # this arm reads prose by construction

    run_id = a.run_id or a.model
    out_dir = paths.run_dir(ev.id, run_id, create=True)
    if (out_dir / "scores.jsonl").exists() and not a.force:
        raise SystemExit(f"{out_dir/'scores.jsonl'} exists — pass --force to rescore")

    where = dict(w.split('=', 1) for w in a.where) if a.where else None
    ids, inputs, meta, _ = load_records(ev, stage, where)
    if a.limit:
        ids, inputs, meta = ids[:a.limit], inputs[:a.limit], meta[:a.limit]
    print(f"{ev}\n  arm {run.id} ({run.backend}, setting={run.setting}) "
          f"over {len(ids):,} {stage} records")

    det = load_detector(a.model, **C.parse_overrides(a.set))
    try:
        if run.setting == "items" and stage != "document":
            batch, items = det.score_items(zip(ids, inputs),
                                           pooling=run.raw.get("pooling", "logit_mean"))
            save_npz(out_dir / "item_scores.npz", doc_ids=np.asarray(items.ids, object),
                     p_human=items.p_human,
                     owner=np.asarray(items.meta.get("owner", []), object))
            print(f"  pooled {len(items.ids):,} items -> {len(batch.ids):,} documents "
                  f"by {run.raw.get('pooling', 'logit_mean')}")
        elif stage == "document":
            batch = det.score_texts(ids, inputs)
        else:
            batch = det.score_outlines(zip(ids, inputs))
    finally:
        det.close()

    by_id = {m.get("id", i): m for i, m in zip(ids, meta)}
    rows = []
    for doc_id, p in zip(batch.ids, batch.p_human):
        m = by_id.get(doc_id, {})
        row = {"id": doc_id, "p_human": float(p), "model_id": run.id,
               "setting": run.setting, "stage": stage}
        if m.get("source"):
            row["y"] = y_human(m["source"])
        for k in ("format", "model", "level", "saha_level", "lang", "domain",
                  "attack", "arm", "humanized", "pair_id", "topic", "extractor",
                  "paraphraser"):
            if m.get(k) is not None:
                row[k] = m[k]
        if stage != "document" and isinstance(m.get("data"), dict):
            row["n_items"] = outline_summary(m["data"])["n_items"]
        rows.append(row)

    write_jsonl(out_dir / "scores.jsonl", rows)
    save_npz(out_dir / "scores.npz",
             doc_ids=np.asarray(batch.ids, dtype=object),
             p_human=batch.p_human,
             **({"logits": batch.logits} if batch.logits is not None else {}),
             y=np.asarray([r.get("y", -1) for r in rows]),
             fmt=np.asarray([str(r.get("format", "")) for r in rows], dtype=object),
             level=np.asarray([str(r.get("level", "")) for r in rows], dtype=object))
    write_json(out_dir / "run.json", C.stamp(
        {"eval": ev.id, "model": run.id, "backend": run.backend,
         "setting": run.setting, "stage": stage, "checkpoint": run.checkpoint},
        {"n_scored": len(rows), "detector_meta": {
            k: v for k, v in batch.meta.items() if not isinstance(v, (list, np.ndarray))}}))

    n_lab = sum(1 for r in rows if "y" in r)
    print(f"  wrote {len(rows):,} scores to {out_dir}"
          f"\n  {n_lab:,} labelled; mean P(human) {batch.p_human.mean():.4f}")
    if not batch.exposes_logits if hasattr(batch, "exposes_logits") else False:
        print("  note: this backend exposes no logits; only p_human was stored")


if __name__ == "__main__":
    sys.exit(main())
