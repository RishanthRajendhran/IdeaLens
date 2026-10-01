#!/usr/bin/env python3
"""Generate `data/<eval>/README.md` from the eval config plus what is on disk.

Written as a generator rather than as hand-maintained files so the documentation
cannot drift from either the configuration or the data. Re-run it after building
or rebuilding any corpus:

    python scripts/data/write_dataset_docs.py
    python scripts/data/write_dataset_docs.py --only test5_peer_review

Each README states what the eval asks, where its data came from, how it is
labelled, how to report it, and the caveats that are NOT visible from the data
and must survive to write-up.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ideadet import paths, registry
from ideadet.io import load_jsonl


def counts(ev) -> dict:
    out = {"corpus_rows": 0, "extract": 0, "deleak": 0, "labels": 0,
           "by_source": {}, "by_format": {}, "columns": []}
    if ev.corpus.exists():
        try:
            rows = load_jsonl(ev.corpus)
        except Exception:
            rows = []
        out["corpus_rows"] = len(rows)
        if rows:
            out["columns"] = sorted({k for r in rows[:2000] for k in r if k != "text"})
            out["by_source"] = dict(collections.Counter(
                r.get("source") for r in rows))
            out["by_format"] = dict(collections.Counter(
                r.get("format") or r.get("role_format") for r in rows).most_common(12))
    for stage in ("extract", "deleak"):
        out[stage] = ev.n_outlines(stage)
    if not out["corpus_rows"] and out["deleak"]:
        # A set delivered as finished outlines has no separate corpus file; its
        # composition is read off the outlines instead.
        out["corpus_rows"] = out["deleak"]
        from ideadet.io import iter_outline_files
        recs = [r for _, r in iter_outline_files(ev.stage_dir("deleak"))]
        out["columns"] = sorted({k for r in recs[:2000] for k in r if k != "data"})
        out["by_source"] = dict(collections.Counter(r.get("source") for r in recs))
        out["by_format"] = dict(collections.Counter(
            (r.get("data") or {}).get("format") or r.get("role_format")
            for r in recs).most_common(12))
    if ev.labels.exists():
        try:
            out["labels"] = len(json.loads(ev.labels.read_text()))
        except Exception:
            pass
    return out


def render(ev, c: dict) -> str:
    cfg = ev.raw
    num = f"Test {ev.number}" if ev.number is not None else "In-domain"
    lines = [f"# {num} — {ev.name}", ""]
    if ev.asks:
        lines += [f"**Asks:** {ev.asks.strip()}", ""]

    lines += ["## Provenance", "", ev.upstream.strip(), ""]

    lines += ["## What is here", "",
              "| file | what | rows |", "|---|---|---|"]
    linked = lambda p: (f" → `{p.resolve()}`" if p.is_symlink() else "")
    lines.append(f"| `corpus.jsonl` | source documents "
                 f"([schema](../schemas/corpus.schema.json)){linked(ev.corpus)} "
                 f"| {c['corpus_rows']:,} |")
    lines.append(f"| `labels.json` | ground truth and slice metadata "
                 f"([schema](../schemas/labels.schema.json)) | {c['labels']:,} |")
    lines.append(f"| `extract/` | stage-1 outlines, one JSON per document "
                 f"([schema](../schemas/outline.schema.json)) | {c['extract']:,} |")
    lines.append(f"| `deleak/` | stage-2 outlines — **this is what the detectors "
                 f"score** | {c['deleak']:,} |")
    lines.append("")

    if ev.deleak_status != "done":
        lines += ["> **The de-leak paraphrase has not been run on this set.** What is "
                  "here is stage-1 output. Scores from it are an UPPER BOUND that "
                  "partly measures wording lifted from the source, and are **not "
                  "comparable** with the de-leaked sets. Run "
                  f"`scripts/pipeline/run_pipeline.py --eval {ev.id} --stage 2` "
                  "before using any number from it in a comparison.", ""]
    if c["corpus_rows"] and c["deleak"] and c["deleak"] < c["corpus_rows"] - 2:
        lines += [f"> **Incomplete.** {c['corpus_rows']:,} corpus rows but "
                  f"{c['deleak']:,} de-leaked outlines. Numbers from this set are "
                  f"partial until the pipeline finishes; rerun "
                  f"`scripts/pipeline/run_pipeline.py --eval {ev.id}` to continue "
                  f"from what is already on disk.", ""]
    if c["corpus_rows"] and not c["labels"]:
        lines += ["> **No `labels.json`.** Per-document metadata rides in each "
                  "outline file instead. Loaders fall back to the outline record, "
                  "but a `labels.json` is preferred: it lets a result be broken "
                  "down without reading every outline.", ""]

    if c["by_source"]:
        lines += ["### Composition", "",
                  "| slice | n |", "|---|---|"]
        for k, v in sorted(c["by_source"].items(), key=lambda x: -x[1]):
            lines.append(f"| source = `{k}` | {v:,} |")
        for k, v in c["by_format"].items():
            if k:
                lines.append(f"| format = {k} | {v:,} |")
        lines.append("")
        n_h = c["by_source"].get("human", 0)
        if 0 < n_h < 0.15 * max(c["corpus_rows"], 1):
            lines += [f"> Only {n_h:,} of {c['corpus_rows']:,} rows are human "
                      f"({n_h / c['corpus_rows']:.1%}). Any FPR from this set rests "
                      f"on that slice, so print n beside every rate.", ""]

    if c["columns"]:
        lines += ["### Metadata columns present", "",
                  ", ".join(f"`{x}`" for x in c["columns"]), ""]

    rep = cfg.get("report", {})
    lines += ["## How to report it", "",
              f"- **Metric:** {'fire rate' if ev.metric == 'fire' else 'TPR at a deployed cut, with the realised FPR beside it'}",
              f"- **Primary operating point:** {rep.get('primary_fpr', 0.01):.1%} FPR",
              f"- **Calibration schemes:** {', '.join(rep.get('schemes', ['global']))}",
              f"- **In-set threshold reported alongside:** "
              f"{'yes (this is out of domain, and the deployed/in-set divergence is itself a finding)' if rep.get('in_set') else 'no'}",
              f"- **Break down by:** {', '.join(rep.get('group_by', ['format']))}"]
    if rep.get("baselines"):
        lines.append(f"- **External baselines required:** {', '.join(rep['baselines'])}")
    lines.append("")

    if ev.metric == "fire":
        lines += ["> Every row in this set carries the same true label, so there "
                  "is no TPR to report. The reading is the **fire rate** as the "
                  "construction varies, against a cut carried in from the "
                  "calibration split.", ""]

    for section, title in (("generation", "How the data was generated"),
                           ("arms", "Arms"),
                           ("variants", "Pipeline variants"),
                           ("audits", "Mandatory validity audits"),
                           ("levels", "Levels")):
        if cfg.get(section):
            lines += [f"## {title}", "", "```yaml",
                      _yaml(cfg[section]).rstrip(), "```", ""]

    if cfg.get("caveats"):
        lines += ["## Caveats", "",
                  "These are not visible from the data and must survive to write-up.", ""]
        for cv in cfg["caveats"]:
            lines.append(f"- {' '.join(str(cv).split())}")
        lines.append("")

    if cfg.get("notes"):
        lines += ["## Notes", "", " ".join(str(cfg["notes"]).split()), ""]

    lines += ["---", "",
              f"Generated by `scripts/data/write_dataset_docs.py` from "
              f"`configs/evals/{ev.id}.yaml`. Edit the config, not this file."]
    return "\n".join(lines) + "\n"


def _yaml(obj) -> str:
    import yaml
    return yaml.safe_dump(obj, sort_keys=False, default_flow_style=False,
                          allow_unicode=True, width=88)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="", help="comma-separated eval ids")
    a = ap.parse_args()
    only = {x.strip() for x in a.only.split(",") if x.strip()}

    for ev in registry.ordered_evals():
        if only and ev.id not in only:
            continue
        ev.path.mkdir(parents=True, exist_ok=True)
        c = counts(ev)
        (ev.path / "README.md").write_text(render(ev, c))
        print(f"{ev.id:<32} corpus {c['corpus_rows']:>7,}  "
              f"extract {c['extract']:>7,}  deleak {c['deleak']:>7,}")


if __name__ == "__main__":
    main()
