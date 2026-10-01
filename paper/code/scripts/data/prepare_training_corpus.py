#!/usr/bin/env python3
"""Turn de-leaked outlines into a frozen, split, ready-to-train corpus.

    python scripts/data/prepare_training_corpus.py --source data/indomain \
        --out data/calibration --name deleaked_outlines_1m

Does four things, in this order, and the order matters:

1. **Deduplicate at the source-document level.** Large web pools carry exact
   duplicate texts. A duplicate spanning the calibration and test slices leaks
   the threshold into the test humans, and no later step can detect it.
2. **Drop the excluded formats**, with the reason recorded in the output.
3. **Split**, stratified by format x label, seeded, into four disjoint slices:
   train / val-select / calibration (HUMAN ONLY) / test.
4. **Freeze**, writing the split assignment before anything is scored, so no
   later choice can be made with knowledge of the results.

Writes `splits.npz` (ids, y, format, topic, split) plus a `calibration.jsonl`
that `scripts/calibrate/score_calibration.py` consumes directly.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import config as C
from ideadet import training as T
from ideadet.io import iter_outline_files, load_jsonl, save_npz, write_json, write_jsonl


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True,
                    help="directory holding corpus.jsonl and deleak/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="training_corpus")
    ap.add_argument("--n-val", type=int, default=6000)
    ap.add_argument("--n-calibration", type=int, default=10000)
    ap.add_argument("--n-test", type=int, default=14000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing frozen split (think first)")
    a = ap.parse_args()

    src, out = Path(a.source), Path(a.out)
    dest = out / "splits.npz"
    if dest.exists() and not a.force:
        raise SystemExit(
            f"{dest} exists. A frozen split should not be redrawn once anything "
            f"has been scored against it; pass --force only if nothing has.")

    corpus = {r["id"]: r for r in load_jsonl(src / "corpus.jsonl")}
    rows = []
    for doc_id, rec in iter_outline_files(src / "deleak"):
        base = corpus.get(doc_id, {})
        rows.append({"id": doc_id, "source": rec.get("source") or base.get("source"),
                     "format": rec.get("format") or base.get("format"),
                     "topic": base.get("topic") or rec.get("topic") or "",
                     "text": base.get("text", ""), "outline": rec.get("data")})
    print(f"{len(rows):,} de-leaked outlines from {src}")

    rows = [r for r in rows if r["source"] in ("human", "ai")]
    rows, n_dupes = T.deduplicate(rows)
    print(f"  dropped {n_dupes:,} exact-duplicate source documents "
          f"(a duplicate across calibration and test would leak the threshold)")

    fmt = np.array([str(r["format"]) for r in rows])
    y = np.array([1 if r["source"] == "human" else 0 for r in rows])
    dropped = int(np.isin(fmt, list(T.DROP_FORMATS)).sum())
    if dropped:
        print(f"  excluding {dropped:,} rows in {T.DROP_FORMATS} — see "
              f"src/ideadet/training.py for why")

    splits = T.make_splits(fmt, y, n_val=a.n_val, n_calibration=a.n_calibration,
                           n_test=a.n_test, seed=a.seed)
    print(T.describe(splits, fmt, y))

    assign = np.array([""] * len(rows), dtype=object)
    for name, idx in splits.items():
        assign[idx] = name

    out.mkdir(parents=True, exist_ok=True)
    save_npz(dest,
             ids=np.array([r["id"] for r in rows], dtype=object),
             y=y, fmt=fmt.astype(object),
             topic=np.array([r["topic"] for r in rows], dtype=object),
             split=assign,
             text_hash=np.array([r["text_hash"] for r in rows], dtype=object))

    # The calibration slice is written out in full, with its outlines, because it
    # is scored separately by every arm and is the input to every deployed cut.
    cal = [rows[i] for i in splits["calibration"]]
    write_jsonl(out / "calibration.jsonl",
                [{"id": r["id"], "source": r["source"], "format": r["format"],
                  "topic": r["topic"], "outline": r["outline"]} for r in cal])
    write_jsonl(out / "document.jsonl",
                [{"id": r["id"], "source": r["source"], "format": r["format"],
                  "topic": r["topic"], "text": r["text"]} for r in cal if r["text"]])

    write_json(out / "splits_run.json", C.stamp(
        {"source": str(src), "name": a.name, "seed": a.seed,
         "n_val": a.n_val, "n_calibration": a.n_calibration, "n_test": a.n_test},
        {"n_rows": len(rows), "n_duplicates_dropped": n_dupes,
         "n_excluded_formats": dropped,
         "sizes": {k: int(len(v)) for k, v in splits.items()},
         "estimable_floor": 25 / max(len(splits["calibration"]), 1)}))

    print(f"\nfroze the split in {dest}\n"
          f"  calibration slice: {out/'calibration.jsonl'} "
          f"({len(cal):,} humans, estimable floor "
          f"{25 / max(len(cal), 1):.4%})")


if __name__ == "__main__":
    sys.exit(main())
