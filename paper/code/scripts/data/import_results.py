#!/usr/bin/env python3
"""Import predictions produced before this repository existed into `outputs/`.

    python scripts/data/import_results.py --dry-run
    python scripts/data/import_results.py
    python scripts/data/import_results.py --only test26_research_ideas_ideation

Earlier runs wrote their scores into a working directory with per-run filename
conventions rather than into `outputs/<eval>/<model>/`. This reads those files,
maps each one onto the model arm that produced it, and writes them out in the
canonical layout so `report_eval.py` can read them like anything else.

It is a ONE-WAY IMPORT, not a sync. Everything it writes carries a `run.json`
recording the source file, so an imported number can always be traced back, and
`imported: true` so it is never mistaken for a run made by this codebase.

WHAT THE FILENAME SUFFIXES MEAN — this mapping is the whole point of the script,
and getting it wrong silently mislabels which model produced a number:

    _scores_nemo / _scores_mb        the outline arms, on STAGE-1 outlines
    _scores_*_dl                     the same arms on DE-LEAKED outlines
    _rawdoc_nemo / _rawdoc_mb        the outline-trained arms given raw DOCUMENTS
    _rawdoc_*_docsmodel              the DOCUMENT-TRAINED counterfactual arm
    _scores_*_rawoutmodel            the arm trained on untreated outlines

A set that has both a `_dl` file and a plain one is scored twice, and only the
`_dl` version is comparable with the de-leaked benchmarks. Both are imported,
under different run ids, so the comparison stays available and neither is lost.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np
import yaml

from ideadet import config as C
from ideadet import paths, registry
from ideadet.io import load_jsonl, load_npz, save_npz, write_json, write_jsonl

#: filename suffix -> (model id in configs/models.yaml, p_human column, what it is)
SUFFIXES = {
    "scores_nemo_dl":            ("nemotron_1m_full",   "p_human_nemo1m", "de-leaked outline"),
    "scores_mb_dl":              ("modernbert_1m_full", "p_human_mb1m",   "de-leaked outline"),
    "scores_nemo":               ("nemotron_1m_full",   "p_human_nemo1m", "outline"),
    "scores_mb":                 ("modernbert_1m_full", "p_human_mb1m",   "outline"),
    "scores_nemo_rawoutmodel_dl": ("nemotron_1m_rawout", "p_human_nemo1m", "de-leaked outline"),
    "scores_nemo_rawoutmodel":   ("nemotron_1m_rawout", "p_human_nemo1m", "outline"),
    "rawdoc_nemo_docsmodel":     ("nemotron_1m_docs",   "p_human_doc",    "raw document"),
    "rawdoc_mb_docsmodel":       ("modernbert_1m_docs", "p_human_doc",    "raw document"),
    "rawdoc_nemo":               ("nemotron_1m_full",   "p_human_doc",    "raw document"),
    "rawdoc_mb":                 ("modernbert_1m_full", "p_human_doc",    "raw document"),
    # The joint full+item checkpoint, read at document level.
    "scores_mb_joint1m_dl":      ("modernbert_1m_joint_full", "p_human_mb1m", "de-leaked outline"),
    "scores_mb_joint1m":         ("modernbert_1m_joint_full", "p_human_mb1m", "outline"),
}

#: Sharded per-ITEM predictions: <preds>/<stem_prefix>_<eval>/shard*.npz.
#: These store `doc` (the owning document, repeated per item) and a two-way
#: `logits` pair; P(human) is the softmax over that pair, exactly as at scoring
#: time. There is no `p_human` column to read -- deriving it here rather than
#: trusting a stored scalar keeps the readout identical to the trained contract.
ITEM_SHARD_PREFIXES = {
    "nemo_fullitem": "nemotron_1m_fullitem",
}
#: A run id says which arm AND what it was fed, because the same weights scoring
#: a document and scoring an outline are two different results.
RUN_SUFFIX = {"outline": "_on_extract", "de-leaked outline": "",
              "raw document": "_on_document"}


def eval_metadata(ev) -> dict:
    """document id -> its label and slice metadata, from wherever the eval keeps it.

    Three places, checked in order of increasing specificity: the corpus row, the
    outline record, then labels.json. Externally-built sets carry it in only one
    of the three, so all three are consulted rather than assuming a layout.
    """
    import json
    from ideadet.io import iter_outline_files, load_jsonl
    meta: dict = {}
    if ev.corpus.exists():
        for r in load_jsonl(ev.corpus):
            meta[str(r["id"])] = dict(r)
            meta[str(r["id"])].pop("text", None)
    for stage in ("extract", "deleak"):
        if ev.has_stage(stage):
            for doc_id, rec in iter_outline_files(ev.stage_dir(stage)):
                m = meta.setdefault(str(doc_id), {})
                for k, v in rec.items():
                    if k != "data" and v is not None:
                        m.setdefault(k, v)
    if ev.labels.exists():
        for doc_id, entry in json.loads(ev.labels.read_text()).items():
            if isinstance(entry, dict):
                meta.setdefault(str(doc_id), {}).update(entry)
    return meta


def sources(map_file: Path) -> dict:
    spec = yaml.safe_load(map_file.read_text()) or {}
    out = {}
    for eval_id, entry in (spec.get("flat_sources") or {}).items():
        stem = None
        for m in entry.get("members", []):
            if isinstance(m, dict) and m.get("as", "").startswith("extract"):
                stem = m["from"].replace("_outlines.jsonl", "")
        if stem:
            out[eval_id] = (Path(entry["path"]), stem)
    return out


def import_jsonl(ev, work: Path, stem: str, dry: bool) -> list[str]:
    """Import every score file this working directory holds for one eval."""
    done = []
    for suffix, (model_id, col, fed) in SUFFIXES.items():
        f = work / f"{stem}_{suffix}.jsonl"
        if not f.exists():
            continue
        run_id = model_id + RUN_SUFFIX[fed]
        # A de-leaked score and a stage-1 score of the same arm are different
        # results; only skip when this exact pair has already landed.
        rows_in = load_jsonl(f)
        rows = []
        for r in rows_in:
            p = r.get(col)
            if p is None:
                continue
            row = {"id": str(r["id"]), "p_human": float(p), "model_id": model_id,
                   "setting": registry.get_model(model_id).setting,
                   "stage": {"raw document": "document",
                             "outline": "extract",
                             "de-leaked outline": "deleak"}[fed],
                   "imported": True}
            if r.get("y") in (0, 1):
                row["y"] = int(r["y"])
            elif r.get("source") in ("human", "ai"):
                row["y"] = 1 if r["source"] == "human" else 0
            for k in ("arm", "level", "format", "role_format", "lang", "domain",
                      "attack", "model", "generator", "pair_id", "words",
                      "n_items", "topic", "stage", "reviewed_condition",
                      "idea_origin", "text_origin", "condition"):
                if r.get(k) is not None and k not in row:
                    row[k] = r[k]
            # Keep the raw log-probabilities when the file carried them: a
            # probability is a lossy summary and re-scoring is expensive.
            if r.get("logp_human") is not None:
                row["logits"] = [r["logp_human"], r.get("logp_ai")]
            rows.append(row)
        if not rows:
            continue
        done.append(f"{run_id:<32}{len(rows):>8,}  <- {f.name}")
        if dry:
            continue

        out_dir = paths.run_dir(ev.id, run_id, create=True)
        write_jsonl(out_dir / "scores.jsonl", rows)
        logits = [r["logits"] for r in rows if "logits" in r]
        save_npz(out_dir / "scores.npz",
                 doc_ids=np.array([r["id"] for r in rows], dtype=object),
                 p_human=np.array([r["p_human"] for r in rows], dtype=float),
                 y=np.array([r.get("y", -1) for r in rows]),
                 arm=np.array([str(r.get("arm", "")) for r in rows], dtype=object),
                 **({"logits": np.array(logits, dtype=np.float32)}
                    if len(logits) == len(rows) else {}))
        write_json(out_dir / "run.json", C.stamp(
            {"eval": ev.id, "model": model_id, "input": fed},
            {"imported": True, "source_file": str(f), "n": len(rows),
             "n_labelled": sum(1 for r in rows if "y" in r),
             "deleak_status": ev.deleak_status,
             "note": "Imported from a pre-existing run, not produced by this "
                     "codebase. The source file above is the authority."}))
    return done


def import_item_shards(ev, pred_dirs: list[Path], dry: bool) -> list[str]:
    """Import sharded per-item predictions and pool them to document scores.

    Both levels are kept: the item file is what the per-item attribution and
    mixture analyses are built from, and throwing it away to store only the
    pooled score would make those unrecoverable without re-scoring.
    """
    stem = ev.raw.get("legacy_item_stem") or ev.raw.get("legacy_npz_stem")
    if not stem:
        return []
    from ideadet.outlines import pool_item_scores
    done = []
    for d in pred_dirs:
        for prefix, model_id in ITEM_SHARD_PREFIXES.items():
            src = d / f"{prefix}_{stem}"
            if not src.is_dir():
                continue
            shards = sorted(src.glob("shard*.npz"))
            if not shards:
                continue
            owners, p_items, logits = [], [], []
            for sh in shards:
                z = load_npz(sh)
                lg = np.asarray(z["logits"], dtype=np.float64)
                e = np.exp(lg - lg.max(axis=1, keepdims=True))
                p_items.extend((e / e.sum(axis=1, keepdims=True))[:, 0].tolist())
                owners.extend(str(x) for x in z["doc"])
                logits.append(lg.astype(np.float32))
            done.append(f"{model_id:<32}{len(p_items):>8,} items / "
                        f"{len(set(owners)):>7,} docs  <- {src.name}/ ({len(shards)} shards)")
            if dry:
                continue

            by_doc: dict[str, list[float]] = {}
            for o, p in zip(owners, p_items):
                by_doc.setdefault(o, []).append(p)
            doc_ids = list(by_doc)
            pooled = [pool_item_scores(by_doc[i], "logit_mean") for i in doc_ids]

            # The shards carry no label -- they were written by a scorer that
            # only needed scores. Without `y` these rows can produce a fire rate
            # and nothing else, so the labels are joined back from the eval
            # itself, which is where the ground truth lives.
            meta = eval_metadata(ev)
            out_dir = paths.run_dir(ev.id, model_id, create=True)
            rows = []
            for i, p in zip(doc_ids, pooled):
                row = {"id": i, "p_human": float(p), "model_id": model_id,
                       "setting": "items", "stage": "deleak",
                       "pooling": "logit_mean", "n_items": len(by_doc[i]),
                       "imported": True}
                m = meta.get(i, {})
                # Two label spellings in circulation: `source` ("human"/"ai") and
                # a raw `y` (1 = human). Externally-built sets use one or the
                # other, so accept both rather than assuming a layout.
                if m.get("source") in ("human", "ai"):
                    row["y"] = 1 if m["source"] == "human" else 0
                elif m.get("y") in (0, 1):
                    row["y"] = int(m["y"])
                for k in ("format", "level", "arm", "lang", "model", "domain",
                          "attack", "pair_id"):
                    if m.get(k) is not None:
                        row[k] = m[k]
                rows.append(row)
            n_lab = sum(1 for r in rows if "y" in r)
            if n_lab < len(rows):
                done[-1] += f"  [{len(rows) - n_lab:,} unlabelled]"
            write_jsonl(out_dir / "scores.jsonl", rows)
            save_npz(out_dir / "scores.npz",
                     doc_ids=np.array(doc_ids, dtype=object),
                     p_human=np.array(pooled, dtype=float),
                     y=np.array([r.get("y", -1) for r in rows]),
                     fmt=np.array([str(r.get("format", "")) for r in rows], dtype=object))
            save_npz(out_dir / "item_scores.npz",
                     owner=np.array(owners, dtype=object),
                     p_human=np.array(p_items, dtype=float),
                     logits=np.concatenate(logits, axis=0))
            write_json(out_dir / "run.json", C.stamp(
                {"eval": ev.id, "model": model_id, "input": "de-leaked outline, per item"},
                {"imported": True, "source_dir": str(src), "n_shards": len(shards),
                 "n_items": len(p_items), "n_documents": len(doc_ids),
                 "pooling": "logit_mean",
                 "note": "P(human) is the two-way softmax over the stored logit "
                         "pair, matching the trained scoring contract. Item-level "
                         "scores are kept in item_scores.npz."}))
    return done


def import_npz(ev, pred_dirs: list[Path], dry: bool) -> list[str]:
    """Import the `ood_<arm>_<stem>.npz` files the older scorer wrote."""
    stem = ev.raw.get("legacy_npz_stem")
    if not stem:
        return []
    ARMS = {"nemotron_full_v1m-r64-ep1": "nemotron_1m_full",
            "modernbert_full_v1m-LAST": "modernbert_1m_full",
            "modernbert_full_v1m-lr2e5-ep1": "modernbert_1m_full",
            "logistic_full_v1m-lr-ep1": "logistic_1m_full",
            "docs_v1m": "modernbert_1m_docs"}
    done = []
    for d in pred_dirs:
        if not d.exists():
            continue
        for arm_stem, model_id in ARMS.items():
            f = d / f"ood_{arm_stem}_{stem}.npz"
            if not f.exists():
                continue
            z = load_npz(f)
            n = len(z["p_human"])
            done.append(f"{model_id:<32}{n:>8,}  <- {f.name}")
            if dry:
                continue
            out_dir = paths.run_dir(ev.id, model_id, create=True)
            rows = []
            for i in range(n):
                row = {"id": str(z["doc_ids"][i]) if "doc_ids" in z else str(i),
                       "p_human": float(z["p_human"][i]),
                       "model_id": model_id, "stage": "deleak", "imported": True}
                if "y" in z:
                    row["y"] = int(z["y"][i])
                for src, dst in (("fmt", "format"), ("level", "level"),
                                 ("lang", "lang"), ("model", "model"),
                                 ("domain", "domain"), ("attack", "attack")):
                    if src in z:
                        row[dst] = str(z[src][i])
                rows.append(row)
            write_jsonl(out_dir / "scores.jsonl", rows)
            save_npz(out_dir / "scores.npz", **z)
            write_json(out_dir / "run.json", C.stamp(
                {"eval": ev.id, "model": model_id, "input": "de-leaked outline"},
                {"imported": True, "source_file": str(f), "n": n,
                 "note": "Imported from a pre-existing run."}))
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", default="configs/data_sources.yaml")
    ap.add_argument("--preds", action="append", default=[],
                    help="directory of ood_*.npz files, repeatable")
    ap.add_argument("--only", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    flat = sources(paths.REPO / a.map)
    pred_dirs = [Path(p) for p in a.preds]
    only = {x.strip() for x in a.only.split(",") if x.strip()}

    total = 0
    for ev in registry.ordered_evals():
        if only and ev.id not in only:
            continue
        lines = []
        if ev.id in flat:
            work, stem = flat[ev.id]
            lines += import_jsonl(ev, work, stem, a.dry_run)
        lines += import_npz(ev, pred_dirs, a.dry_run)
        lines += import_item_shards(ev, pred_dirs, a.dry_run)
        if lines:
            flag = "" if ev.comparable else "   [UNTREATED OUTLINES]"
            print(f"\n{ev.id}{flag}")
            for ln in lines:
                print(f"  {ln}")
            total += len(lines)

    print(f"\n{'would import' if a.dry_run else 'imported'} {total} score file(s)")
    if not a.dry_run:
        print("Run scripts/report/build_manifest.py to refresh the inventory.")


if __name__ == "__main__":
    sys.exit(main())
