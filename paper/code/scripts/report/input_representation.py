#!/usr/bin/env python
"""How much does the verdict move when the SAME checkpoint reads a different rendering?

`nemotron_1m_full` was trained on de-leaked outlines, but it has been scored on
three renderings of the same documents. One checkpoint, three inputs:

    document        the raw source prose                (outputs/*/nemotron_1m_full_on_document)
    raw outline     the stage-1 extraction, un-de-leaked (outputs/*/nemotron_1m_full_on_extract)
    de-leaked       the deployed input                   (outputs/*/nemotron_1m_full)

That gives two contrasts the write-up needs, and this script reports both, split
by the four-quadrant lens (configs/evals/_quadrants.yaml):

    outline vs document   -- does reading prose instead of the outline change who
                             gets credited? Run both against the de-leaked outline
                             (the deployed comparison) and against the raw outline
                             (the representation change alone, both sides untreated).
    raw vs de-leaked      -- what the de-leak paraphrase costs and buys.

Rows are joined on document id, so every contrast is PAIRED: the same documents
under both renderings, never two differently-sized samples.

THRESHOLD CAVEAT, and why the in-set column exists. `nemotron_1m_full` and
`nemotron_1m_full_on_document` are calibrated; `nemotron_1m_full_on_extract` is
NOT, and per docs/CONVENTIONS.md an uncalibrated arm is never given another
arm's cut. So the deployed column is blank for the raw-outline stage, and the
comparable numbers for that contrast are the in-set column (a cut refitted on
each eval's own humans, identically for every stage) and AUC, which needs no cut
at all.

    python scripts/report/input_representation.py
    python scripts/report/input_representation.py --target-fpr 0.01 --scheme format
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import _bootstrap  # noqa: F401
import numpy as np
import yaml
from scipy.stats import spearmanr

from ideadet import calibration as C
from ideadet import formats as F
from ideadet import metrics as M
from ideadet.io import load_jsonl, write_json

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
QUADRANT_CONFIG = ROOT / "configs" / "evals" / "_quadrants.yaml"
THRESHOLDS = OUTPUTS / "calibration" / "thresholds.json"

#: The three renderings, in pipeline order: prose -> extracted outline -> de-leaked.
STAGES = {
    "document": "nemotron_1m_full_on_document",
    "raw_outline": "nemotron_1m_full_on_extract",
    "deleaked_outline": "nemotron_1m_full",
}

#: (name, stage_a, stage_b). The reported delta is always b - a.
CONTRASTS = [
    ("deleaked_outline_vs_document", "document", "deleaked_outline"),
    ("raw_outline_vs_document", "document", "raw_outline"),
    ("raw_vs_deleaked_outline", "raw_outline", "deleaked_outline"),
]

QUADRANT_ORDER = ["HH", "HA", "AH", "AA", "mixed"]


# --------------------------------------------------------------------- data --

def load_quadrants() -> dict:
    return yaml.safe_load(QUADRANT_CONFIG.read_text())


def quadrant_of(spec: dict, eval_id: str, arm) -> str | None:
    """The cell for one row, or None when this eval is not on the map."""
    entry = spec["evals"].get(eval_id)
    if entry is None:
        return None
    arms = entry.get("arms", {})
    if arm in arms:
        return arms[arm]
    if "default" in entry:
        return entry["default"]
    raise KeyError(
        f"{eval_id} arm {arm!r} has no quadrant and the eval has no default. "
        f"Add it to configs/evals/_quadrants.yaml against the label-mapping "
        f"table rather than letting the row vanish.")


def read_stage(eval_id: str, stage: str) -> dict[str, dict] | None:
    """Score rows for one eval and one rendering, keyed by document id."""
    path = OUTPUTS / eval_id / STAGES[stage] / "scores.jsonl"
    if not path.exists():
        return None
    rows = {}
    for r in load_jsonl(path):
        if r.get("y") is None:
            continue                      # unlabelled probe rows carry no quadrant
        rows[r["id"]] = r
    return rows or None


def join(eval_id: str, stage_a: str, stage_b: str, spec: dict) -> dict | None:
    """Inner-join two renderings of one eval on document id.

    `role_format` is carried from whichever side has it: the document rows do not
    store a format, but it is a property of the document, not of the rendering,
    so the outline side's label is the same label.
    """
    a, b = read_stage(eval_id, stage_a), read_stage(eval_id, stage_b)
    if a is None or b is None:
        return None
    ids = sorted(set(a) & set(b))
    if not ids:
        return None

    out = {"ids": ids, "y": [], "arm": [], "quadrant": [], "format": [],
           "p_a": [], "p_b": []}
    for i in ids:
        ra, rb = a[i], b[i]
        q = quadrant_of(spec, eval_id, ra.get("arm"))
        if q is None:
            return None
        fmt = ra.get("role_format") or rb.get("role_format")
        try:
            fmt = F.canonical(fmt) if fmt else None
        except ValueError:
            fmt = None
        out["y"].append(int(ra["y"]))
        out["arm"].append(ra.get("arm"))
        out["quadrant"].append(q)
        out["format"].append(fmt)
        out["p_a"].append(float(ra["p_human"]))
        out["p_b"].append(float(rb["p_human"]))
    for k in ("y", "p_a", "p_b"):
        out[k] = np.asarray(out[k], dtype=float if k != "y" else int)
    out["quadrant"] = np.asarray(out["quadrant"])
    out["format"] = np.asarray([f if f else "" for f in out["format"]])
    return out


# ------------------------------------------------------------------ scoring --

def deployed_fires(thresholds, stage: str, p, formats, target_fpr, scheme):
    """Fire/covered arrays under the deployed cut, or None when uncalibrated."""
    model_id = STAGES[stage]
    if model_id not in thresholds.models:
        return None
    groups = formats if scheme == "format" else None
    if scheme == "format" and (formats is None or not formats.any()):
        return None
    try:
        return thresholds.apply(model_id, p, target_fpr, scheme=scheme, groups=groups)
    except (KeyError, C.MissingGroups):
        return None


def cell(p, y, quad_mask, fires, covered, ref_p_human, ref_y):
    """One quadrant, one rendering."""
    m = quad_mask
    n = int(m.sum())
    d = {"n": n,
         "mean_p_human": float(np.mean(p[m])) if n else None,
         "median_p_human": float(np.median(p[m])) if n else None}
    if fires is not None:
        cov = m & covered
        d["n_covered"] = int(cov.sum())
        d["fire_rate"] = float(fires[cov].mean()) if cov.any() else None
    else:
        d["n_covered"], d["fire_rate"] = None, None
    # Threshold-free separation from this eval's human-conceived, human-written
    # rows. Defined only for the AI-idea cells; HH is the reference itself.
    if n and ref_p_human is not None and len(ref_p_human):
        yy = np.concatenate([np.zeros(n), np.ones(len(ref_p_human))])
        pp = np.concatenate([p[m], ref_p_human])
        d["auc_vs_HH"] = M.auc_score(pp, yy)
    else:
        d["auc_vs_HH"] = None
    return d


def analyse_eval(eval_id, joined, thresholds, stage_a, stage_b,
                 target_fpr, scheme, in_set_fpr):
    y = joined["y"]
    quads = joined["quadrant"]
    fmts = joined["format"]
    res = {"eval": eval_id, "n_paired": len(y),
           "n_human": int((y == 1).sum()), "n_ai": int((y == 0).sum()),
           "quadrants": {}}

    hh = quads == "HH"
    per_stage = {}
    for stage, p in ((stage_a, joined["p_a"]), (stage_b, joined["p_b"])):
        dep = deployed_fires(thresholds, stage, p, fmts, target_fpr, scheme)
        # The in-set cut is refitted per stage on THIS eval's own humans, which is
        # the only cut every stage can be given, uncalibrated arms included.
        n_hum = int((y == 1).sum())
        if M.estimable(in_set_fpr, n_hum):
            cut = C.in_set_cut(p, y, in_set_fpr)
            in_set = {"cut": cut, "fires": p < cut}
        else:
            in_set = None
        per_stage[stage] = {"p": p, "deployed": dep, "in_set": in_set,
                            "calibrated": dep is not None,
                            "in_set_estimable": in_set is not None,
                            "n_humans_for_in_set": n_hum}

    for q in QUADRANT_ORDER:
        m = quads == q
        if not m.any():
            continue
        entry = {"n": int(m.sum()),
                 "arms": sorted({a for a, k in zip(joined["arm"], m) if k}),
                 "label": "human" if q in ("HH", "HA") else
                          ("ai" if q in ("AH", "AA") else "mixed"),
                 "stages": {}}
        for stage, s in per_stage.items():
            p = s["p"]
            ref = p[hh] if (q != "HH" and hh.any()) else None
            dep = s["deployed"]
            c = cell(p, y, m, dep["fires"] if dep else None,
                     dep["covered"] if dep else None, ref, None)
            if s["in_set"] is not None:
                c["in_set_cut"] = s["in_set"]["cut"]
                c["in_set_fire_rate"] = float(s["in_set"]["fires"][m].mean())
            else:
                c["in_set_cut"] = c["in_set_fire_rate"] = None
            entry["stages"][stage] = c

        pa, pb = per_stage[stage_a]["p"][m], per_stage[stage_b]["p"][m]
        entry["paired"] = {
            "mean_shift_p_human": float(np.mean(pb - pa)),
            "median_shift_p_human": float(np.median(pb - pa)),
            "spearman": (float(spearmanr(pa, pb).statistic)
                         if m.sum() > 2 and np.ptp(pa) > 0 and np.ptp(pb) > 0 else None),
        }
        da, db = per_stage[stage_a]["deployed"], per_stage[stage_b]["deployed"]
        if da is not None and db is not None:
            cov = m & da["covered"] & db["covered"]
            if cov.any():
                entry["paired"]["verdict_agreement_deployed"] = float(
                    (da["fires"][cov] == db["fires"][cov]).mean())
                entry["paired"]["delta_fire_rate_deployed"] = float(
                    db["fires"][cov].mean() - da["fires"][cov].mean())
        ia, ib = per_stage[stage_a]["in_set"], per_stage[stage_b]["in_set"]
        if ia is not None and ib is not None:
            entry["paired"]["verdict_agreement_in_set"] = float(
                (ia["fires"][m] == ib["fires"][m]).mean())
            entry["paired"]["delta_fire_rate_in_set"] = float(
                ib["fires"][m].mean() - ia["fires"][m].mean())
        res["quadrants"][q] = entry

    res["stage_notes"] = {s: {k: v for k, v in d.items()
                              if k in ("calibrated", "in_set_estimable",
                                       "n_humans_for_in_set")}
                          for s, d in per_stage.items()}
    return res


def aggregate(per_eval, stage_a, stage_b):
    """Macro-average over evals per quadrant, with the pooled n beside it.

    Macro, not pooled: OpAI-Bench alone is 37k rows and would otherwise decide
    every HA number in the suite on its own.
    """
    agg = {}
    for q in QUADRANT_ORDER:
        rows = [r["quadrants"][q] for r in per_eval if q in r["quadrants"]]
        if not rows:
            continue
        entry = {"n_evals": len(rows), "n_docs": sum(r["n"] for r in rows),
                 "evals": [r["eval"] for r in per_eval if q in r["quadrants"]],
                 "stages": {}}
        for stage in (stage_a, stage_b):
            for key, out in (("fire_rate", "macro_fire_rate_deployed"),
                             ("in_set_fire_rate", "macro_fire_rate_in_set"),
                             ("auc_vs_HH", "macro_auc_vs_HH"),
                             ("mean_p_human", "macro_mean_p_human")):
                vals = [r["stages"][stage][key] for r in rows
                        if r["stages"][stage].get(key) is not None]
                entry["stages"].setdefault(stage, {})[out] = (
                    float(np.mean(vals)) if vals else None)
                entry["stages"][stage][out + "_n_evals"] = len(vals)
        for key, out in (("delta_fire_rate_deployed", "macro_delta_fire_deployed"),
                         ("delta_fire_rate_in_set", "macro_delta_fire_in_set"),
                         ("verdict_agreement_deployed", "macro_agreement_deployed"),
                         ("verdict_agreement_in_set", "macro_agreement_in_set"),
                         ("mean_shift_p_human", "macro_mean_shift_p_human"),
                         ("spearman", "macro_spearman")):
            vals = [r["paired"][key] for r in rows if r["paired"].get(key) is not None]
            entry[out] = float(np.mean(vals)) if vals else None
            entry[out + "_n_evals"] = len(vals)
        agg[q] = entry
    return agg


# ------------------------------------------------------------------ display --

def fmt(v, nd=3):
    return "  --  " if v is None else f"{v:.{nd}f}"


def render(report) -> str:
    L = []
    for name, block in report["contrasts"].items():
        a, b = block["stage_a"], block["stage_b"]
        L += ["", "=" * 100,
              f"{name}   ({a}  ->  {b})",
              f"  {block['n_evals']} evals, {block['n_docs']} paired documents",
              "=" * 100]
        cal = block["calibration"]
        for s in (a, b):
            L.append(f"  {s:<18} deployed cut: "
                     + ("available" if cal[s]["calibrated"]
                        else "NONE -- no deployed number is reportable for this stage"))
        L += ["",
              f"  {'quadrant':<8} {'evals':>5} {'docs':>7} |"
              f" {'fire@dep A':>10} {'fire@dep B':>10} {'d':>7} |"
              f" {'fire@set A':>10} {'fire@set B':>10} {'d':>7} |"
              f" {'AUC A':>7} {'AUC B':>7} |"
              f" {'agree':>6} {'dp_hum':>7}",
              "  " + "-" * 116]
        for q in QUADRANT_ORDER:
            e = block["aggregate"].get(q)
            if not e:
                continue
            sa, sb = e["stages"][a], e["stages"][b]
            direction = {"HH": "(fires are errors)", "HA": "(fires are errors)",
                         "AH": "(fires are correct)", "AA": "(fires are correct)",
                         "mixed": "(no label)"}[q]
            L.append(
                f"  {q:<8} {e['n_evals']:>5} {e['n_docs']:>7} |"
                f" {fmt(sa['macro_fire_rate_deployed']):>10}"
                f" {fmt(sb['macro_fire_rate_deployed']):>10}"
                f" {fmt(e['macro_delta_fire_deployed']):>7} |"
                f" {fmt(sa['macro_fire_rate_in_set']):>10}"
                f" {fmt(sb['macro_fire_rate_in_set']):>10}"
                f" {fmt(e['macro_delta_fire_in_set']):>7} |"
                f" {fmt(sa['macro_auc_vs_HH']):>7}"
                f" {fmt(sb['macro_auc_vs_HH']):>7} |"
                f" {fmt(e['macro_agreement_in_set'] if e['macro_agreement_in_set'] is not None else e['macro_agreement_deployed']):>6}"
                f" {fmt(e['macro_mean_shift_p_human']):>7}   {direction}")
        L += ["", "  per eval:"]
        for r in block["per_eval"]:
            L.append(f"    {r['eval']}  (n={r['n_paired']})")
            for q, e in r["quadrants"].items():
                sa, sb = e["stages"][a], e["stages"][b]
                L.append(
                    f"      {q:<6} n={e['n']:>6}  "
                    f"fire@dep {fmt(sa['fire_rate'])} -> {fmt(sb['fire_rate'])}   "
                    f"fire@set {fmt(sa['in_set_fire_rate'])} -> {fmt(sb['in_set_fire_rate'])}   "
                    f"AUCvHH {fmt(sa['auc_vs_HH'])} -> {fmt(sb['auc_vs_HH'])}   "
                    f"arms={','.join(e['arms'])}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target-fpr", type=float, default=0.01,
                    help="deployed operating point (default 0.01)")
    ap.add_argument("--scheme", default="global", choices=["global", "format"],
                    help="which calibration-derived scheme the deployed cut uses")
    ap.add_argument("--in-set-fpr", type=float, default=0.05,
                    help="secondary in-set operating point. 5%% because most of "
                         "these sets hold far too few humans for an estimable 1%%")
    ap.add_argument("--out", default=str(OUTPUTS / "reports" / "input_representation.json"))
    args = ap.parse_args()

    spec = load_quadrants()
    thresholds = C.Thresholds.load(THRESHOLDS)

    report = {"model": "nemotron_1m_full",
              "note": "one checkpoint, three renderings of the same documents",
              "stages": STAGES, "target_fpr": args.target_fpr,
              "scheme": args.scheme, "in_set_fpr": args.in_set_fpr,
              "contrasts": {}}

    for name, stage_a, stage_b in CONTRASTS:
        per_eval = []
        for eval_id in sorted(spec["evals"]):
            j = join(eval_id, stage_a, stage_b, spec)
            if j is None:
                continue
            per_eval.append(analyse_eval(eval_id, j, thresholds, stage_a, stage_b,
                                         args.target_fpr, args.scheme, args.in_set_fpr))
        if not per_eval:
            continue
        report["contrasts"][name] = {
            "stage_a": stage_a, "stage_b": stage_b,
            "n_evals": len(per_eval),
            "n_docs": sum(r["n_paired"] for r in per_eval),
            "calibration": {s: {"model_id": STAGES[s],
                                "calibrated": STAGES[s] in thresholds.models,
                                "n_calibration_humans":
                                    thresholds.models.get(STAGES[s], {}).get("n_calibration_humans")}
                            for s in (stage_a, stage_b)},
            "per_eval": per_eval,
            "aggregate": aggregate(per_eval, stage_a, stage_b),
        }

    text = render(report)
    print(text)
    write_json(args.out, report)
    Path(args.out).with_suffix(".txt").write_text(text)
    print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
