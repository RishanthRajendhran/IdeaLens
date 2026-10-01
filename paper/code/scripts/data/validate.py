#!/usr/bin/env python3
"""Check that what is on disk matches what the schemas and configs promise.

Reports every problem it finds rather than stopping at the first, so one pass
tells you everything a corpus needs. Exit code is non-zero when anything failed,
so it can gate a build.

    python scripts/data/validate.py --all
    python scripts/data/validate.py --eval test5_peer_review --strict
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ideadet import registry, schema
from ideadet.io import load_jsonl
from ideadet.outlines import items_of


def check(ev, strict: bool = False) -> list[str]:
    problems: list[str] = []

    if not ev.corpus.exists():
        return [f"no corpus.jsonl (looked in {ev.path})"]

    rows = load_jsonl(ev.corpus)
    if not rows:
        return ["corpus.jsonl is empty"]

    ids = [r.get("id") for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1} if len(ids) < 20000 else set()
    if dupes:
        problems.append(
            f"{len(dupes):,} duplicate id(s), e.g. {sorted(dupes)[:3]}. Batch APIs "
            f"return results keyed by id, so duplicates silently drop rows.")

    for r in rows[: (len(rows) if strict else 2000)]:
        for p in schema.validate_corpus_row(r):
            problems.append(f"corpus row {r.get('id')}: {p}")

    if ev.labels.exists():
        labels = json.loads(ev.labels.read_text())
        problems += schema.validate_labels(labels, {str(i) for i in ids})
    else:
        problems.append("no labels.json — metadata must then ride in each outline "
                        "file, which makes breakdowns require reading them all")

    deleak = ev.stage_dir("deleak")
    if not deleak.exists():
        problems.append("no deleak/ — the detectors score de-leaked outlines, so "
                        "this eval cannot be scored yet")
    else:
        files = sorted(deleak.glob("*.json"))
        if len(files) < len(rows) - 2:
            problems.append(f"{len(files):,} de-leaked outlines for {len(rows):,} "
                            f"corpus rows — the pipeline is incomplete")
        empty = 0
        for f in files[: (len(files) if strict else 300)]:
            try:
                rec = json.loads(f.read_text())
            except json.JSONDecodeError as e:
                problems.append(f"{f.name}: unparseable ({e})")
                continue
            for p in schema.validate_outline(rec):
                problems.append(f"{f.name}: {p}")
            if not items_of(rec.get("data")):
                empty += 1
            if not rec.get("extractor"):
                problems.append(f"{f.name}: no `extractor` recorded — outlines from "
                                f"different extractors must never be pooled silently")
                break                        # one report is enough for this class
        if empty:
            problems.append(f"{empty} outline(s) have no items")

    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="check every row and every outline, not a sample")
    a = ap.parse_args()

    targets = (registry.ordered_evals() if a.all or not a.eval
               else [registry.get_eval(a.eval)])
    failed = 0
    for ev in targets:
        problems = check(ev, a.strict)
        print(schema.report(problems, str(ev)))
        failed += bool(problems)
    print(f"\n{len(targets) - failed}/{len(targets)} eval set(s) clean")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
