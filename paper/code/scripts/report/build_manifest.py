#!/usr/bin/env python3
"""Inventory every corpus, outline set and score file, by inspecting disk.

Written as a generator rather than a hand-maintained file so it cannot drift from
reality. Rerun it after any pipeline or scoring run:

    python scripts/report/build_manifest.py

It records provenance for every corpus (upstream source, row counts,
completeness) and every score file (which arm, which set, how many rows, whether
raw logits were kept), and it WARNS about anything it cannot vouch for rather
than guessing: an unrecorded upstream, an incomplete pipeline, a score file with
no logits.
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from ideadet import config as C
from ideadet import paths, registry
from ideadet.io import load_json, load_npz, write_json


def corpus_entry(ev) -> dict:
    n_corpus = sum(1 for _ in open(ev.corpus)) if ev.corpus.exists() else 0
    stages = {s: ev.n_outlines(s) for s in ("extract", "deleak")}
    # Sets that arrive as finished outlines carry no separate corpus file; their
    # outline count IS their size, and calling that "incomplete" would be wrong.
    if not n_corpus and stages["deleak"]:
        n_corpus = stages["deleak"]
    size = sum(f.stat().st_size for f in ev.path.rglob("*") if f.is_file())
    return {"test": ev.number, "name": ev.name, "group": ev.group,
            "deleak_status": ev.deleak_status,
            "upstream": ev.upstream.strip(), "dir": str(ev.path.relative_to(paths.REPO)),
            "corpus_rows": n_corpus, **stages,
            "complete": bool(n_corpus) and stages["deleak"] >= n_corpus - 2,
            "has_labels": ev.labels.exists(), "bytes": size}


def score_entry(d) -> dict:
    entry = {"eval": d.parent.name, "model": d.name,
             "dir": str(d.relative_to(paths.REPO))}
    npz = d / "scores.npz"
    if npz.exists():
        try:
            z = load_npz(npz)
            entry.update(rows=len(z["doc_ids"]), fields=sorted(z),
                         has_logits="logits" in z, bytes=npz.stat().st_size)
        except Exception as e:
            entry["error"] = str(e)[:100]
    if (d / "run.json").exists():
        try:
            run = load_json(d / "run.json")
            entry["stamped"] = run.get("generated")
            entry["git_revision"] = run.get("git_revision")
        except Exception:
            pass
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    man = {"stamp": C.stamp({}), "corpora": {}, "scores": [], "warnings": []}

    for ev in registry.ordered_evals():
        e = corpus_entry(ev)
        man["corpora"][ev.id] = e
        if e["upstream"].startswith("UNKNOWN"):
            man["warnings"].append(f"{ev.id}: upstream provenance not recorded — "
                                   f"do this before any release")
        if e["corpus_rows"] and not e["complete"]:
            man["warnings"].append(
                f"{ev.id}: {e['corpus_rows']:,} corpus rows but {e['deleak']:,} "
                f"de-leaked — numbers from it are partial")
        if e["corpus_rows"] and not e["has_labels"]:
            man["warnings"].append(f"{ev.id}: no labels.json")
        if ev.deleak_status != "done":
            man["warnings"].append(
                f"{ev.id}: de-leak NOT RUN — untreated outlines only, not "
                f"comparable with the de-leaked sets")

    root = paths.root("outputs")
    for eval_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if eval_dir.name in ("calibration", "reports", "feature_discovery"):
            continue
        for run_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir()):
            if (run_dir / "scores.jsonl").exists():
                man["scores"].append(score_entry(run_dir))

    no_logits = [s["model"] for s in man["scores"] if s.get("rows") and not s.get("has_logits")]
    if no_logits:
        man["warnings"].append(
            f"{len(no_logits)} score file(s) carry no raw logits. Anything needing "
            f"margins, temperature or re-pooling must be re-scored.")

    thresholds = paths.outputs("calibration", "thresholds.json")
    man["calibration"] = {"exists": thresholds.exists()}
    if thresholds.exists():
        t = load_json(thresholds)
        man["calibration"]["models"] = {
            k: {"n_calibration_humans": v.get("n_calibration_humans"),
                "estimable_floor": v.get("estimable_floor"),
                "not_estimable": v.get("not_estimable")}
            for k, v in t.get("models", {}).items()}
    else:
        man["warnings"].append("no outputs/calibration/thresholds.json — no "
                               "deployed number can be reported without it")

    man["totals"] = {
        "evals": len(man["corpora"]),
        "corpus_documents": sum(v["corpus_rows"] for v in man["corpora"].values()),
        "deleaked_outlines": sum(v["deleak"] for v in man["corpora"].values()),
        "score_files": len(man["scores"]),
        "corpus_gb": round(sum(v["bytes"] for v in man["corpora"].values()) / 1e9, 2),
    }

    out = a.out or paths.outputs("reports", "MANIFEST.json")
    write_json(out, man)
    print(f"{'eval':<32}{'test':>5}{'corpus':>10}{'extract':>10}{'deleak':>10}  complete")
    for k, v in man["corpora"].items():
        print(f"{k:<32}{str(v['test'] or ''):>5}{v['corpus_rows']:>10,}"
              f"{v['extract']:>10,}{v['deleak']:>10,}  {'yes' if v['complete'] else 'NO'}")
    print(f"\ntotals: {man['totals']}")
    if man["warnings"]:
        print(f"\n{len(man['warnings'])} warning(s):")
        for w in man["warnings"]:
            print(f"  - {w}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    sys.exit(main())
