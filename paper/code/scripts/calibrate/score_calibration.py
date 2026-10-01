#!/usr/bin/env python3
"""Score the human-only calibration split, so cuts can be fitted from it.

    python scripts/calibrate/score_calibration.py --config outline_1m --model nemotron_1m_full
    python scripts/calibrate/score_calibration.py --config rawdoc_1m  --model modernbert_1m_docs

Writes `outputs/calibration/<model_id>__<config>.npz` with the score, format and
topic of every calibration human. `derive_thresholds.py` turns those into cuts.

THE SPLIT IS HUMAN-ONLY AND DISJOINT FROM TEST at the source-document level. AI
documents contribute nothing to a low quantile of the human score distribution,
and a duplicate document spanning calibration and test would leak the threshold
into the test humans.

OUTLINE AND DOCUMENT CALIBRATIONS ARE NOT INTERCHANGEABLE. A column reporting
document-level scores needs a cut fitted on documents scored by the same model;
applying an outline cut to a document score is the distribution mismatch this
project keeps getting bitten by.
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import config as C
from ideadet import metrics as M
from ideadet import paths, registry
from ideadet.detectors import load as load_detector
from ideadet.io import load_jsonl, save_npz, write_json


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_args(ap, "calibration")
    ap.add_argument("--model", required=True)
    ap.add_argument("--input", default="",
                    help="calibration jsonl; default data/calibration/<input>.jsonl")
    ap.add_argument("--n", type=int, default=0, help="override the config's n_humans")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    cfg = C.from_args(a, "calibration")
    run = registry.get_model(a.model)
    tag = f"{a.model}__{a.config}"
    out = paths.outputs("calibration", f"{tag}.npz")
    if out.exists() and not a.force:
        raise SystemExit(f"{out} exists — pass --force to rescore")

    src = a.input or paths.data("calibration", f"{cfg['input']}.jsonl")
    rows = load_jsonl(src)
    rows = [r for r in rows if (r.get("source") or "human") == "human"]
    n = a.n or cfg.get("n_humans") or len(rows)
    rows = rows[:n]
    if not rows:
        raise SystemExit(f"no calibration humans in {src}")

    floor = M.MIN_CALIBRATION_DOCS / len(rows)
    print(f"calibration: {len(rows):,} humans from {src}\n"
          f"  estimable floor {floor:.4%} "
          f"(a target below it rests on fewer than {M.MIN_CALIBRATION_DOCS} documents)")
    for q in cfg["targets"]:
        mark = "ok " if M.estimable(q, len(rows)) else "NOT estimable"
        print(f"    {q:>8.3%}  k = {q * len(rows):>8,.0f}   {mark}")

    det = load_detector(a.model)
    try:
        if cfg["input"] == "document":
            batch = det.score_texts([r["id"] for r in rows], [r["text"] for r in rows])
        else:
            batch = det.score_outlines((r["id"], r["outline"]) for r in rows)
    finally:
        det.close()

    save_npz(out, doc_ids=np.asarray(batch.ids, dtype=object),
             p_human=batch.p_human,
             fmt=np.asarray([str(r.get("format", "")) for r in rows], dtype=object),
             topic=np.asarray([str(r.get("topic", "")) for r in rows], dtype=object),
             **({"logits": batch.logits} if batch.logits is not None else {}))
    write_json(paths.outputs("calibration", f"{tag}.run.json"),
               C.stamp(cfg, {"model": a.model, "n_humans": len(rows),
                             "estimable_floor": floor, "source": str(src)}))

    p = batch.p_human
    print(f"\n  wrote {out}\n"
          f"  P(human): mean {p.mean():.4f}  "
          f"above 0.99 {float((p > 0.99).mean()):.1%}  "
          f"above 0.999 {float((p > 0.999).mean()):.1%}")
    if float((p > 0.999).mean()) > 0.5:
        print("  note: the score distribution is saturated at the ceiling, so the "
              "cut rests on near-identical values and small score shifts will move "
              "the realised FPR a long way")


if __name__ == "__main__":
    sys.exit(main())
