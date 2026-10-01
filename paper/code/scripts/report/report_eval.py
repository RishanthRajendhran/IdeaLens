#!/usr/bin/env python3
"""Report one eval set: every scored arm, under every convention it calls for.

    python scripts/report/report_eval.py --eval test5_peer_review
    python scripts/report/report_eval.py --eval test3_collaboration_ladder --markdown
    python scripts/report/report_eval.py --eval test8_storyscope --fpr 0.001

Writes `outputs/<eval>/<model>/metrics.json` for each arm and prints the
comparison table. Two rules the printer enforces:

* every TPR appears beside its **realised** FPR, because a nominal 1% cut that
  lands at 2.4% is not a 1% number;
* documents filtered for want of a calibrated cut are **counted in the table**,
  never quietly dropped.
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import calibration as CAL
from ideadet import config as C
from ideadet import paths, registry, report
from ideadet.io import load_jsonl, write_json


def arms(ev):
    """Every model run with scores on disk for this eval."""
    base = paths.outputs(ev.id)
    if not base.exists():
        return []
    return sorted(d.name for d in base.iterdir()
                  if (d / "scores.jsonl").exists())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--models", default="", help="comma-separated; default all scored")
    ap.add_argument("--fpr", type=float, default=0.0, help="override the primary target")
    ap.add_argument("--thresholds", default="")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--n-boot", type=int, default=-1)
    a = ap.parse_args()

    ev = registry.get_eval(a.eval)
    rep = ev.raw.get("report", {})
    target = a.fpr or rep.get("primary_fpr", 0.01)
    n_boot = rep.get("n_boot", 1000) if a.n_boot < 0 else a.n_boot

    tpath = a.thresholds or paths.outputs("calibration", "thresholds.json")
    thresholds = CAL.Thresholds.load(tpath) if tpath.exists() else None
    if thresholds is None:
        print(f"note: no {tpath}. Only the in-set convention is available; run "
              f"scripts/calibrate/derive_thresholds.py for deployed numbers.")

    models = [x.strip() for x in a.models.split(",") if x.strip()] or arms(ev)
    if not models:
        raise SystemExit(f"{ev.id}: nothing scored yet. Run scripts/eval/score.py.")

    uncalibrated: list[str] = []
    rows, payload = [], {"eval": ev.id, "name": ev.name, "number": ev.number,
                         "group": ev.group, "asks": ev.asks,
                         "deleak_status": ev.deleak_status,
                         "target_fpr": target, "arms": {}}
    if not ev.comparable:
        print(f"\n*** {ev.id}: the de-leak paraphrase has NOT been run on this set. "
              f"Everything below is from untreated outlines: an upper bound, not "
              f"comparable with the de-leaked sets. ***")
    for model in models:
        d = paths.run_dir(ev.id, model)
        scored = load_jsonl(d / "scores.jsonl")
        p = np.array([r["p_human"] for r in scored], dtype=float)
        y = np.array([r.get("y", 1) for r in scored], dtype=int)
        has_labels = any("y" in r for r in scored)
        groups_by = {g: [str(r.get(g, "")) for r in scored] for g in ev.groups}
        results = {}

        # Formats are needed by the per-format scheme whether or not this eval
        # reports a format breakdown, so read them off the rows directly.
        fmt_col = [str(r.get("format") or r.get("role_format") or "") for r in scored]
        have_formats = any(fmt_col)
        # Which calibration entry applies: the same weights scoring a document and
        # scoring an outline have different cuts, so the input is part of the key.
        cal_id = ""
        if thresholds is not None:
            for cand in (model, model.replace("_on_extract", "")):
                if cand in thresholds.models:
                    cal_id = cand
                    break
        if thresholds is not None and not cal_id:
            # An arm with no calibration cannot be reported at a deployed cut.
            # Say so and move on: substituting another arm's cut would be worse
            # than reporting nothing.
            uncalibrated.append(model)
            payload["arms"][model] = {"error": (
                f"no calibration for {model}. Run scripts/calibrate/"
                f"score_calibration.py and derive_thresholds.py for this arm "
                f"before reporting a deployed number from it.")}
            continue

        for scheme in rep.get("schemes", ["global"]):
            if thresholds is None:
                continue
            if scheme == "format" and not have_formats:
                results[scheme] = {"skipped": "no format column on these scores",
                                   "scheme": scheme, "model_id": model}
                continue
            try:
                res = report.evaluate(
                    p, y, thresholds=thresholds, model_id=model,
                    calibration_id=cal_id, target_fpr=target, scheme=scheme,
                    groups=fmt_col if scheme == "format" else None,
                    group_name=ev.groups[0] if ev.groups else "format",
                    n_boot=n_boot)
            except (KeyError, CAL.MissingGroups) as e:
                res = {"error": str(e), "scheme": scheme, "model_id": model}
            results[scheme] = res
            if "error" not in res:
                rows.append((f"{model} [{scheme}]", res))

        if rep.get("in_set") and has_labels:
            res = report.evaluate(p, y, model_id=model, target_fpr=target,
                                  in_set=True, n_boot=n_boot,
                                  groups=groups_by.get("format"))
            results["in_set"] = res
            rows.append((f"{model} [in-set]", res))

        # Per-group breakdowns, and the fire-rate-by-rung reading for ladders.
        if ev.metric == "fire" and thresholds is not None:
            cut = thresholds.cut(cal_id, target)
            # `arm` is the rung on most sets; `level` on the ones built earlier.
            key = "level" if any(r.get("level") for r in scored) else "arm"
            by_level = {}
            for r in scored:
                by_level.setdefault(str(r.get(key, "")), []).append(r["p_human"])
            results["by_rung"] = {
                k: {"n": len(v), "fire_rate": float((np.array(v) < cut).mean()),
                    "mean_p_human": float(np.mean(v))}
                for k, v in sorted(by_level.items())}

        payload["arms"][model] = results
        write_json(d / "metrics.json",
                   C.stamp({"eval": ev.id, "model": model, "target_fpr": target},
                           {"results": results}))

    print(f"\n{ev}\n{ev.asks.strip()}\n")
    print(report.table(rows))
    if uncalibrated:
        print(f"\n{len(uncalibrated)} arm(s) have scores but no calibration, so no "
              f"deployed number can be reported for them:\n  "
              + ", ".join(uncalibrated))
    payload["uncalibrated_arms"] = uncalibrated
    if any(r.get("n_filtered") for _, r in rows):
        print("\n`filtered` counts documents whose group had no calibrated cut. "
              "They are excluded from that column's rates, never given the global "
              "cut as a fallback.")

    for model, res in payload["arms"].items():
        if "by_rung" in res:
            caption = ev.raw.get("report", {}).get("rung_caption", "")
            print(f"\n{model} — fire rate by arm"
                  + (f" ({caption})" if caption else "") + ":")
            print(report.ladder_table(res["by_rung"]))

    out = paths.outputs("reports", f"{ev.id}.json")
    write_json(out, payload)
    print(f"\nwrote {out}")

    if a.markdown:
        md = [{"arm": n, "n": r.get("n"), "tpr": r.get("tpr"),
               "realised_fpr": r.get("realised_fpr"), "auc": r.get("auc")}
              for n, r in rows]
        print("\n" + report.markdown_table(
            md, ["arm", "n", "tpr", "realised_fpr", "auc"],
            ["arm", "n", f"TPR@{target:.0%}", "realised FPR", "AUC"]))


if __name__ == "__main__":
    sys.exit(main())
