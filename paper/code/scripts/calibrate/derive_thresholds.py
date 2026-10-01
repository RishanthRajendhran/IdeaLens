#!/usr/bin/env python3
"""Fit deployed thresholds and write `outputs/calibration/thresholds.json`.

    python scripts/calibrate/derive_thresholds.py --config outline_1m
    python scripts/calibrate/derive_thresholds.py --config rawdoc_1m --suffix _doc

This is the ONLY producer of deployed cuts. Every reported number reads them
back from that one file, so no script derives a threshold at report time and no
two tables can silently use different operating points.

Running it for a second config MERGES into the existing file rather than
replacing it, so outline and document calibrations coexist. Use `--suffix` to
keep a model's document cuts distinct from its outline cuts.
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import calibration as CAL
from ideadet import config as C
from ideadet import metrics as M
from ideadet import paths
from ideadet.io import load_json, load_npz, write_json


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_args(ap, "calibration")
    ap.add_argument("--models", default="", help="comma-separated; default from the config")
    ap.add_argument("--suffix", default="",
                    help="appended to each model id in the output, e.g. _doc")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    cfg = C.from_args(a, "calibration")
    # `--out` arrives as a str; paths.outputs() returns a Path. Without the
    # wrap, any --out run dies on dest.exists().
    dest = Path(a.out) if a.out else paths.outputs("calibration", "thresholds.json")
    payload = load_json(dest) if dest.exists() else {"models": {}}
    payload["generated"] = datetime.datetime.now().isoformat(timespec="seconds")
    payload["git_revision"] = C.git_revision()

    models = [x.strip() for x in a.models.split(",") if x.strip()] or cfg["models"]
    for model in models:
        f = paths.outputs("calibration", f"{model}__{a.config}.npz")
        if not f.exists():
            print(f"  {model:<26} no scores yet — run score_calibration.py first")
            continue
        z = load_npz(f)
        groups = {}
        if "fmt" in z:
            groups["format"] = z["fmt"]
        if "topic" in z:
            groups["topic"] = z["topic"]
        groups = {k: v for k, v in groups.items()
                  if k in cfg["schemes"] and len(set(map(str, v))) > 1}

        entry = CAL.derive(z["p_human"], groups=groups, targets=cfg["targets"],
                           min_group_humans=cfg["min_group_humans"],
                           apply_shrinkage=cfg["shrinkage"],
                           model_id=model, split=cfg["split"])
        entry["input"] = cfg["input"]
        entry["config"] = a.config
        payload["models"][model + a.suffix] = entry

        primary = str(cfg["primary"])
        cut = entry["global"].get(primary)
        cells = len(entry.get("format", {}).get(primary, {}))
        print(f"  {model + a.suffix:<26} n={entry['n_calibration_humans']:>7,}  "
              f"cut@{float(primary):.0%}={cut if cut is None else round(cut, 5)}  "
              f"per-format cells={cells}  "
              f"floor={entry['estimable_floor']:.4%}")
        if entry["not_estimable"]:
            print(f"    not estimable at this n: {', '.join(entry['not_estimable'])} "
                  f"(needs {M.MIN_CALIBRATION_DOCS} humans below the cut)")

    write_json(dest, payload)
    print(f"\nwrote {dest} with {len(payload['models'])} model(s)")
    print("Every reported number now takes its cut from this file. Nothing should "
          "derive a threshold at report time.")


if __name__ == "__main__":
    sys.exit(main())
