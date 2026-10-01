#!/usr/bin/env python3
"""Embed outlines (or documents) once and cache them for the logistic arm.

    python scripts/eval/embed.py --eval indomain --out .scratch/cache/emb_indomain.npz

The cache is the expensive artifact; the fit costs cents. Re-embedding a corpus
that has already been embedded is pure waste, so this script skips ids already
present in `--out` and only sends the remainder.

Uses the batch API, which is half price. For a handful of texts the synchronous
path is fine, but never loop it over a corpus.
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import paths, registry
from ideadet.io import iter_outline_files, load_jsonl, load_npz, save_npz
from ideadet.llm import openai_batch as OB
from ideadet.outlines import render


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="text-embedding-3-large")
    ap.add_argument("--stage", default="deleak", choices=["deleak", "extract", "document"])
    ap.add_argument("--setting", default="full")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    ev = registry.get_eval(a.eval)
    if a.stage == "document":
        rows = load_jsonl(ev.corpus, a.limit or None)
        pairs = [(r["id"], r["text"]) for r in rows]
    else:
        pairs = [(d, render(r.get("data"), a.setting))
                 for d, r in iter_outline_files(ev.stage_dir(a.stage))]
        if a.limit:
            pairs = pairs[:a.limit]

    out = paths.REPO / a.out if not str(a.out).startswith("/") else a.out
    have = {}
    if out.exists():
        z = load_npz(out)
        have = {str(i): x for i, x in zip(z["ids"], z["X"])}
        print(f"  {len(have):,} already cached in {out}")

    todo = [(i, t) for i, t in pairs if i not in have]
    print(f"{ev}: {len(pairs):,} texts, {len(todo):,} to embed with {a.model}")
    if todo:
        reqs = [OB.build_embedding_request(i, a.model, t) for i, t in todo]
        got = OB.run_batch(reqs, description=f"{ev.id}_embed")
        for i, _ in todo:
            v = OB.embedding_of(got.get(i, {}))
            if v is not None:
                have[i] = np.asarray(v, dtype=np.float32)

    ids = [i for i, _ in pairs if i in have]
    save_npz(out, ids=np.array(ids, dtype=object),
             X=np.stack([have[i] for i in ids]))
    print(f"wrote {out} with {len(ids):,} vectors of dim {len(have[ids[0]])}")


if __name__ == "__main__":
    sys.exit(main())
