#!/usr/bin/env python3
"""Everything we hold for one model arm: which evals, how many rows, what level.

    python scripts/report/model_inventory.py --model nemotron_1m_fullitem
    python scripts/report/model_inventory.py --all
    python scripts/report/model_inventory.py --model nemotron_1m_fullitem --items

Answers "what data do we actually have for this arm?" from disk rather than from
memory. Reports document-level rows, item-level rows where the arm produced them,
whether the eval is calibrated for that arm, and whether its outlines were
de-leaked — because an impressive-looking row on an untreated set is an upper
bound, not a result.
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import calibration as CAL
from ideadet import paths, registry
from ideadet.io import load_npz


def rows_for(eval_id: str, run_id: str) -> dict | None:
    d = paths.run_dir(eval_id, run_id)
    f = d / "scores.jsonl"
    if not f.exists():
        return None
    n_docs = sum(1 for _ in open(f))
    out = {"run": run_id, "n_docs": n_docs, "n_items": 0, "labelled": 0}
    npz = d / "scores.npz"
    if npz.exists():
        z = load_npz(npz)
        if "y" in z:
            out["labelled"] = int((np.asarray(z["y"]) >= 0).sum())
    item = d / "item_scores.npz"
    if item.exists():
        out["n_items"] = int(len(load_npz(item)["p_human"]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--items", action="store_true",
                    help="only arms that produced item-level scores")
    a = ap.parse_args()

    tpath = paths.outputs("calibration", "thresholds.json")
    thresholds = CAL.Thresholds.load(tpath) if tpath.exists() else None

    if a.all or not a.model:
        wanted = sorted(registry.models())
    else:
        wanted = [a.model]
    if a.items:
        wanted = [m for m in wanted if registry.get_model(m).setting == "items"]

    for model in wanted:
        run = registry.get_model(model)
        # a run id may qualify the arm by what it was fed
        variants = [model] + [f"{model}{s}" for s in ("_on_extract", "_on_document")]
        found = []
        for ev in registry.ordered_evals():
            for v in variants:
                r = rows_for(ev.id, v)
                if r:
                    found.append((ev, r))
        if not found:
            continue

        cal = "yes" if thresholds and model in thresholds.models else "NO"
        cut = (thresholds.cut(model, 0.01) if cal == "yes" else None)
        print(f"\n{'=' * 96}\n{model}  —  {run.name}")
        print(f"  backend={run.backend}  setting={run.setting}  "
              f"input={run.input_kind}  calibrated={cal}"
              + (f"  cut@1%={cut:.5f}" if cut else ""))
        print(f"{'=' * 96}")
        print(f"  {'eval':<32}{'run':<26}{'docs':>9}{'items':>12}{'labelled':>10}  flags")
        td = ti = 0
        for ev, r in found:
            flags = []
            if not ev.comparable:
                flags.append("UNTREATED")
            if ev.metric == "fire":
                flags.append("fire-rate")
            print(f"  {ev.id:<32}{r['run']:<26}{r['n_docs']:>9,}"
                  f"{(r['n_items'] or ''):>12}{r['labelled']:>10,}  {' '.join(flags)}")
            td += r["n_docs"]
            ti += r["n_items"]
        print(f"  {'-' * 94}\n  {'TOTAL':<58}{td:>9,}{(ti or ''):>12}")


if __name__ == "__main__":
    sys.exit(main())
