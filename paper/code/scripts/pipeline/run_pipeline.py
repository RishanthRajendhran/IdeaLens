#!/usr/bin/env python3
"""Stages 1 and 2: extract role-labelled outlines, then de-leak them.

    python scripts/pipeline/run_pipeline.py --eval test5_peer_review
    python scripts/pipeline/run_pipeline.py --eval my_set --stage 1 --only-format "Academic Writing"
    python scripts/pipeline/run_pipeline.py --eval my_set --dry-run   # cost estimate only

RESUMABLE. Both stages write one JSON file per document, and a rerun processes
only the documents with no file yet. A job that dies at 90% is resumed by running
the same command again.

ONE FORMAT PER JOB. Every row in a job then carries a byte-identical system
prefix, which is what earns the cached-input discount; extraction is roughly 93%
of pipeline spend and the exemplar block is most of the extraction prompt.
Formats are also processed one at a time rather than interleaved so that
concurrent jobs share a prefix instead of evicting each other's.

THE STAGES FAIL FOR DIFFERENT REASONS, which is why `--stage` exists. Stage 1 is
dominated by the long prefix and by safety blocks; stage 2 by long-output
transients (measured around 1-2% against roughly 0.1%). Rerunning a stage-2
failure should not re-walk stage 1's already-extracted documents.
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from ideadet import config as C
from ideadet import formats as F
from ideadet import prompts as P
from ideadet import registry
from ideadet.io import load_jsonl, iter_outline_files, write_json
from ideadet.llm import vertex_batch as VB
from ideadet.pipeline import outline_pipeline as OP


def chunks(seq, size):
    if not size:
        return [seq]
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def run_stage1(ev, rows, cfg, args) -> int:
    out_dir = ev.stage_dir("extract")
    done = 0
    for fmt, group in sorted(OP.group_by_format(rows).items()):
        todo = [r for r in group if r["id"] in set(OP.pending([g["id"] for g in group], out_dir))]
        print(f"\n[stage 1] {fmt}: {len(todo):,} of {len(group):,} pending")
        if not todo or args.dry_run:
            continue
        for n, chunk in enumerate(chunks(todo, cfg.get("chunk", 0))):
            reqs = OP.extraction_requests(
                chunk, fmt, n_shots=cfg["n_shots"],
                thinking_level=cfg.get("thinking_level", "HIGH"),
                template=cfg.get("template", P.EXTRACTION_TEMPLATE),
                max_output_tokens=cfg.get("max_output_tokens", 64000))
            got = VB.run_batch(reqs, cfg["model"], bucket=cfg["gcs"]["bucket"],
                               prefix=cfg["gcs"]["prefix"],
                               tag=f"{ev.id}_extract_{F.slug(fmt)}_{n}",
                               poll_interval=cfg.get("poll_interval", 60),
                               user_label=cfg.get("billing_label", ""),
                               usage_path=ev.path / "usage_extract.jsonl")
            by_id = {r["id"]: r for r in chunk}
            for doc_id, payload in got.items():
                OP.write_outline(out_dir, doc_id, payload, by_id[doc_id],
                                 stage="extract", extractor=cfg["model"],
                                 prompt_version=f"{cfg.get('template', '')}|{P.PROMPT_VERSION}",
                                 n_shots=cfg["n_shots"])
                done += 1
    return done


def run_stage2(ev, rows, cfg, args) -> int:
    src_dir, out_dir = ev.stage_dir("extract"), ev.stage_dir("deleak")
    by_id = {r["id"]: r for r in rows}
    outlines = {d: rec for d, rec in iter_outline_files(src_dir) if d in by_id}
    done = 0
    groups: dict[str, dict] = {}
    for doc_id, rec in outlines.items():
        fmt = F.canonical(rec.get("format") or by_id[doc_id].get("format"))
        groups.setdefault(fmt, {})[doc_id] = rec

    for fmt, group in sorted(groups.items()):
        todo = {d: r for d, r in group.items()
                if not (out_dir / f"{d}.json").exists()}
        print(f"\n[stage 2] {fmt}: {len(todo):,} of {len(group):,} pending")
        if not todo or args.dry_run:
            continue
        items = list(todo.items())
        for n, chunk in enumerate(chunks(items, cfg.get("chunk", 0))):
            reqs = OP.deleak_requests(dict(chunk), fmt,
                                      version=cfg["prompt_version"],
                                      thinking_level=cfg.get("thinking_level", "HIGH"),
                                      max_output_tokens=cfg.get("max_output_tokens", 64000))
            got = VB.run_batch(reqs, cfg["model"], bucket=cfg["gcs"]["bucket"],
                               prefix=cfg["gcs"]["prefix"],
                               tag=f"{ev.id}_deleak_{F.slug(fmt)}_{n}",
                               poll_interval=cfg.get("poll_interval", 60),
                               user_label=cfg.get("billing_label", ""),
                               usage_path=ev.path / "usage_deleak.jsonl")
            for doc_id, payload in got.items():
                src = outlines[doc_id]
                OP.write_outline(out_dir, doc_id, payload, by_id[doc_id],
                                 stage="deleak", extractor=src.get("extractor", ""),
                                 paraphraser=cfg["model"],
                                 prompt_version=cfg["prompt_version"],
                                 n_shots=src.get("n_shots"))
                done += 1
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--extraction-config", default="", help="default: from the eval config")
    ap.add_argument("--deleak-config", default="")
    ap.add_argument("--stage", default="both", choices=["1", "2", "both"])
    ap.add_argument("--only-format", default="", help="comma-separated format names")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true",
                    help="report what is pending and what it would cost, spend nothing")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args()

    ev = registry.get_eval(a.eval)
    over = C.parse_overrides(a.set)
    ex_cfg = C.load(a.extraction_config or ev.raw["pipeline"]["extraction"],
                    kind="pipeline", overrides=over)
    # `deleak: null` in an eval config means the set HAS no stage 2. Since the
    # 2026-09-06 decision that de-leak is in-domain only, that is the normal case
    # for a new OOD set, so loading it eagerly turned `--stage 1` into a crash.
    dl_ref = a.deleak_config or ev.raw["pipeline"].get("deleak")
    dl_cfg = C.load(dl_ref, kind="pipeline", overrides=over) if dl_ref else None

    rows = load_jsonl(ev.corpus, a.limit or None)
    if a.only_format:
        want = {F.canonical(x.strip()) for x in a.only_format.split(",") if x.strip()}
        rows = [r for r in rows
                if F.canonical(r.get("format") or r.get("role_format")) in want]
    print(f"{ev}\n  {len(rows):,} documents"
          f"\n  stage 1: {ex_cfg['model']} {ex_cfg['n_shots']}-shot, thinking "
          f"{ex_cfg.get('thinking_level')}"
          + (f"\n  stage 2: {dl_cfg['model']} prompt {dl_cfg['prompt_version']}"
             if dl_cfg else "\n  stage 2: none (deleak: null)"))

    if a.dry_run:
        from ideadet.llm import pricing
        # Per-document token figures measured on this pipeline. Extraction is
        # dominated by the exemplar block, which is why the shot count is the
        # main lever.
        per_doc = {"extract": (39891, 1284), "deleak": (2779, 1385)}
        stages = [("extract", (ex_cfg["model"], "extract"))]
        if dl_cfg:
            stages.append(("deleak", (dl_cfg["model"], "deleak")))
        for stage, (model, key) in stages:
            i, o = per_doc[key]
            try:
                est = pricing.estimate(model, input_tokens=i * len(rows),
                                       output_tokens=o * len(rows), mode="batch")
                print(f"  [dry run] {stage}: ~${est['usd']:,.2f} at batch rates "
                      f"({model}); run a 1-2 job trial and extrapolate before a sweep")
            except KeyError as e:
                print(f"  [dry run] {stage}: no price recorded — {e}")

    n1 = run_stage1(ev, rows, ex_cfg, a) if a.stage in ("1", "both") else 0
    if a.stage in ("2", "both") and dl_cfg is None:
        if a.stage == "2":
            raise SystemExit(
                f"{a.eval} sets `pipeline.deleak: null` — it has no stage 2. "
                f"Pass --deleak-config explicitly to override that.")
        n2 = 0          # --stage both on a set with no stage 2 runs stage 1 only
    else:
        n2 = run_stage2(ev, rows, dl_cfg, a) if a.stage in ("2", "both") else 0

    for stage in (["extract"] if a.stage in ("1", "both") else []) + \
                 (["deleak"] if a.stage in ("2", "both") and dl_cfg else []):
        OP.audit(ev.stage_dir(stage), len(rows))

    write_json(ev.path / "pipeline_run.json",
               C.stamp({"extraction": ex_cfg, "deleak": dl_cfg},
                       {"eval": a.eval, "n_documents": len(rows),
                        "written_stage1": n1, "written_stage2": n2}))
    print(f"\nwrote {n1:,} extractions and {n2:,} de-leaks")


if __name__ == "__main__":
    sys.exit(main())
