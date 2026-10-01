#!/usr/bin/env python3
"""Score many (eval, model) pairs in one command, then report.

    python scripts/eval/run_suite.py --models nemotron_1m_full,modernbert_1m_full
    python scripts/eval/run_suite.py --group "Idea provenance" --dry-run
    python scripts/eval/run_suite.py --evals test1_source_paraphrase,test14_partial_documents

Skips pairs already scored unless --force. Failures are collected and printed at
the end rather than stopping the sweep, so one missing checkpoint does not cost
you the other twenty results.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from ideadet import paths, registry

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default="", help="comma-separated; default from each eval config")
    ap.add_argument("--evals", default="", help="comma-separated; default all")
    ap.add_argument("--group", default="", help="only evals in this reporting group")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    evals = registry.ordered_evals()
    if a.evals:
        want = {x.strip() for x in a.evals.split(",") if x.strip()}
        evals = [e for e in evals if e.id in want]
    if a.group:
        evals = [e for e in evals if e.group == a.group]

    planned, skipped, failed = [], [], []
    for ev in evals:
        models = ([x.strip() for x in a.models.split(",") if x.strip()]
                  or ev.raw.get("scoring", {}).get("models", []))
        for model in models:
            done = (paths.run_dir(ev.id, model) / "scores.jsonl").exists()
            if done and not a.force:
                skipped.append((ev.id, model))
                continue
            planned.append((ev.id, model))

    print(f"{len(planned)} to score, {len(skipped)} already done")
    for ev_id, model in planned:
        print(f"  {ev_id:<32} {model}")
    if a.dry_run:
        return 0

    for ev_id, model in planned:
        cmd = [sys.executable, str(HERE / "score.py"), "--eval", ev_id,
               "--model", model] + (["--force"] if a.force else [])
        print(f"\n=== {ev_id} / {model} ===", flush=True)
        if subprocess.run(cmd).returncode:
            failed.append((ev_id, model))

    if failed:
        print(f"\n{len(failed)} pair(s) failed:")
        for ev_id, model in failed:
            print(f"  {ev_id} / {model}")
    print(f"\n{len(planned) - len(failed)}/{len(planned)} scored")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
