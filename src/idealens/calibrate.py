"""Fit thresholds on your own human documents, save them as a named profile, and use them later.

    cuts = il.calibrate(records, model="IdeaLens", save_as="essays")     # records: scored JSONL rows or dicts
    il.Detector("IdeaLens", thresholds="essays")

The rules are the project's (ideadet.calibration.derive):
  global     the target-FPR quantile of P(human) over the human documents
  per group  the group's own quantile, shrunk toward the global cut with weight n / (n + 2500), for groups with at
             least 200 human documents (formats, topics, and any --group-by field)
  estimable  a cut at FPR q is fitted only when q * n >= 25 documents fall below it; otherwise it is listed under
             not_estimable with the number of documents it would need
Only human documents set the cuts. If AI documents are included (label field), the report gives the detection rate
at each cut with a bootstrap interval (humans resampled and the cut refitted each time).
"""
from __future__ import annotations

import datetime
import hashlib
import json

import numpy as np

FPR_TARGETS = (0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20)
MIN_BELOW = 25
MIN_GROUP = 200
SHRINK_N = 2500


def estimable(q: float, n: int) -> bool:
    return q * n >= MIN_BELOW


def _key(q: float) -> str:
    return str(float(q))


def derive(p_human, groups: dict | None = None, targets=FPR_TARGETS, min_group=MIN_GROUP) -> dict:
    """Cuts from human scores. groups: {scheme: [label per document]}; scheme "format"/"topic" -> per_format /
    per_topic, anything else -> per_group[scheme]."""
    p = np.asarray(p_human, dtype=float)
    keep = ~np.isnan(p)
    p = p[keep]
    n = int(p.size)
    if n == 0:
        raise ValueError("no human scores to calibrate on")
    out = {"global": {}, "not_estimable": {}, "n_humans": n}
    for q in targets:
        if estimable(q, n):
            out["global"][_key(q)] = float(np.quantile(p, q))
        else:
            out["not_estimable"][_key(q)] = f"needs {int(np.ceil(MIN_BELOW / q)):,} human documents"
    for scheme, labels in (groups or {}).items():
        lab = np.asarray([str(x) if x is not None else None for x in labels], dtype=object)[keep]
        table, counts = {}, {}
        for q in targets:
            if _key(q) not in out["global"]:
                continue
            cell = {}
            for g in sorted({x for x in lab if x is not None}):
                m = lab == g
                ng = int(m.sum())
                counts[g] = ng
                if ng < min_group or not estimable(q, ng):
                    continue
                w = ng / (ng + SHRINK_N)
                cell[g] = float(out["global"][_key(q)] + w * (np.quantile(p[m], q) - out["global"][_key(q)]))
            table[_key(q)] = cell
        name = {"format": "per_format", "topic": "per_topic"}.get(scheme)
        if name:
            out[name], out[f"n_per_{scheme}"] = table, counts
        else:
            out.setdefault("per_group", {})[scheme] = table
            out.setdefault("n_per_group", {})[scheme] = counts
    return out


def _bootstrap_tpr(p_h, p_ai, q, n_boot=200, seed=0):
    rng = np.random.default_rng(seed)
    t = []
    for _ in range(n_boot):
        cut = np.quantile(rng.choice(p_h, p_h.size), q)
        t.append(float((rng.choice(p_ai, p_ai.size) < cut).mean()))
    return [float(np.percentile(t, 2.5)), float(np.percentile(t, 97.5))]


def calibrate(records, model: str, save_as: str | None = None, out: str | None = None, group_by=(),
              label_field: str | None = None, human_value="human", targets=FPR_TARGETS, overwrite=False,
              n_boot: int = 200):
    """records: dicts with p_human (the output of Detector/idealens score/run), optionally format, topic, the
    group_by fields, and a label. Returns a Thresholds object (and saves it when save_as/out is given)."""
    from importlib.metadata import PackageNotFoundError, version
    from .thresholds import Thresholds
    recs = [r for r in records if r.get("p_human") is not None]
    if not recs:
        raise ValueError("no scored records (p_human) to calibrate on")
    models = {r.get("model") for r in recs if r.get("model")}
    if models and models != {model}:
        raise ValueError(f"records were scored by {sorted(models)}, not {model}")
    if label_field:
        is_h = [str(r.get(label_field)).lower() == str(human_value).lower() for r in recs]
    else:
        is_h = [True] * len(recs)
    hum = [r for r, h in zip(recs, is_h) if h]
    groups = {"format": [r.get("format") for r in hum]}
    if any(r.get("topic") for r in hum):
        groups["topic"] = [r.get("topic") for r in hum]
    for g in group_by:
        groups[g] = [r.get(g) for r in hum]
    d = derive([r["p_human"] for r in hum], groups, targets)

    # provenance: how the scores were produced (compared with every later run that uses these cuts)
    def one(key, get):
        vals = {get(r) for r in hum} - {None}
        if len(vals) > 1:
            raise ValueError(f"records mix several {key} values {sorted(map(str, vals))}; calibrate each separately")
        return next(iter(vals), None)
    om = lambda r: r.get("outline_meta") or (r.get("outline") or {}).get("meta") or {}
    try:
        pkg = version("idealens")
    except PackageNotFoundError:
        pkg = "unknown"
    prov = {"backend": one("backend", lambda r: r.get("backend")),
            "format_method": one("format_method", lambda r: r.get("format_method")),
            "extractor_provider": one("extractor_provider", lambda r: om(r).get("provider")),
            "extractor_model": one("extractor_model", lambda r: om(r).get("model")),
            "few_shot": one("few_shot", lambda r: om(r).get("few_shot")),
            "idealens_version": pkg, "date": datetime.date.today().isoformat(),
            "data_sha256": hashlib.sha256(json.dumps(sorted(str(r.get("id")) + f"{r['p_human']:.9g}" for r in hum))
                                          .encode()).hexdigest()}
    data = {"model": f"rishanthrajendhran/{model}", "flag_rule": "flag the document as AI when P(human) < cut",
            "calibration": {"data": "user calibration set (human documents only)", "n_humans": d["n_humans"],
                            **{k: d[k] for k in d if k.startswith("n_per")}},
            "method": {"global": "the target-FPR quantile of P(human) over the human documents",
                       "per_group": f"the group's own quantile, shrunk toward the global cut with weight n / (n + {SHRINK_N})",
                       "min_group_humans": MIN_GROUP, "estimability": f"a cut at FPR q only when q * n >= {MIN_BELOW}",
                       "missing_cut": "no cut for a group means none could be estimated; do not substitute the global cut"},
            "fpr_targets": [float(q) for q in targets], "global": d["global"], "not_estimable": d["not_estimable"],
            "provenance": {k: v for k, v in prov.items() if v is not None}}
    for k in ("per_format", "per_topic", "per_group"):
        if d.get(k):
            data[k] = d[k]
    if label_field and not all(is_h):
        p_h = np.array([r["p_human"] for r in hum])
        p_ai = np.array([r["p_human"] for r, h in zip(recs, is_h) if not h])
        data["report"] = {"n_ai": int(p_ai.size), "detection_rate_at_global_cut": {
            k: {"tpr": float((p_ai < c).mean()), "ci95": _bootstrap_tpr(p_h, p_ai, float(k), n_boot)}
            for k, c in d["global"].items()}}
    th = Thresholds(data, source="calibrate")
    if save_as:
        th.source = f"profile:{save_as}"
        th.save_profile(save_as, overwrite=overwrite)
    if out:
        th.save(out)
    return th
