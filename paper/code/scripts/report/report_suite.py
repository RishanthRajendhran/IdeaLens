#!/usr/bin/env python3
"""One payload for the whole suite: every eval, every arm, both conventions.

    python scripts/report/report_suite.py
    python scripts/report/report_suite.py --group "Idea provenance"

Prints a per-group summary and writes `outputs/reports/suite.json`, which is what
figures and tables are built from. Evals with nothing scored are listed as gaps
rather than omitted, so the report always says what is missing.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from ideadet import config as C
from ideadet import paths, registry
from ideadet.io import load_json, write_json

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group", default="")
    ap.add_argument("--refresh", action="store_true",
                    help="re-run report_eval.py for every eval first")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    evals = registry.ordered_evals()
    if a.group:
        evals = [e for e in evals if e.group == a.group]

    suite = {"stamp": C.stamp({}), "evals": {}, "gaps": []}
    for ev in evals:
        if a.refresh:
            subprocess.run([sys.executable, str(HERE / "report_eval.py"),
                            "--eval", ev.id], check=False)
        f = paths.outputs("reports", f"{ev.id}.json")
        if not f.exists():
            suite["gaps"].append({"eval": ev.id, "why": "not scored or not reported"})
            continue
        payload = load_json(f)
        payload["deleak_status"] = ev.deleak_status
        payload["group"] = ev.group
        suite["evals"][ev.id] = payload

    by_group: dict[str, list] = {}
    for ev in evals:
        by_group.setdefault(ev.group, []).append(ev)

    for group, members in by_group.items():
        print(f"\n{'=' * 96}\n{group}\n{'=' * 96}")
        for ev in members:
            payload = suite["evals"].get(ev.id)
            if not payload:
                print(f"  {ev.id:<32} not scored")
                continue
            flag = "" if ev.comparable else "   [UNTREATED OUTLINES]"
            for model, res in sorted(payload["arms"].items()):
                if "error" in res:
                    print(f"  {ev.id:<32}{model:<34}not calibrated{flag}")
                    continue
                g = res.get("global") or res.get("in_set") or {}
                tpr = g.get("tpr")
                fpr = g.get("realised_fpr")
                fire = g.get("fire_rate")
                cell = (f"TPR {tpr:.3f} @ realised FPR {fpr:.3f}"
                        if tpr is not None and fpr is not None
                        else (f"fire rate {fire:.3f}" if fire is not None else "—"))
                print(f"  {ev.id:<32}{model:<34}{cell}{flag}")

    untreated = [k for k, v in suite["evals"].items()
                 if v.get("deleak_status") != "done"]
    if untreated:
        print(f"\n{len(untreated)} eval(s) scored on UNTREATED outlines. Their "
              f"numbers are upper bounds and must not be pooled with the "
              f"de-leaked sets:\n  " + ", ".join(untreated))

    if suite["gaps"]:
        print(f"\n{len(suite['gaps'])} eval(s) with no result yet:")
        for g in suite["gaps"]:
            print(f"  {g['eval']}")

    out = a.out or paths.outputs("reports", "suite.json")
    write_json(out, suite)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    sys.exit(main())
