#!/usr/bin/env python3
"""Remove SYMLINKS under data/<eval>/ that the source map no longer names.

link_sources.py only ever adds or repoints links. When an eval moves from a pilot directory
(`extract/`, `deleak/`, `labels.json`) to single-file stages (`extract.jsonl`,
`deleak.jsonl`), the old links stay behind, and the loader accepts either layout -- so a
reader could silently pick up the 1,000-document pilot beside the 10,000-document corpus.

Only symlinks are touched, never real files, and every removal is logged with its target
so it can be restored.

    python scripts/data/prune_stale_links.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import yaml
from ideadet import paths

MEMBERS = ("corpus.jsonl", "labels.json", "extract", "deleak", "extract.jsonl", "deleak.jsonl")


def expected(spec) -> dict[str, set[str]]:
    want: dict[str, set[str]] = {}
    for section in ("sources", "flat_sources", "corpus_sources", "raw_sources"):
        for ev, entry in (spec.get(section) or {}).items():
            names = want.setdefault(ev, set())
            for m in entry.get("members", ("corpus.jsonl", "labels.json", "extract", "deleak")):
                name = m if isinstance(m, str) else m["as"]
                rel = m if isinstance(m, str) else m["from"]
                root = Path(str(entry["path"]).rstrip("/"))
                if (root if rel == "." else root / rel).exists():
                    names.add(name)
    return want


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default="configs/data_sources.yaml")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    want = expected(yaml.safe_load((paths.REPO / a.map).read_text()))
    log = []
    for ev, names in sorted(want.items()):
        d = paths.data(ev)
        for m in MEMBERS:
            f = d / m
            if f.is_symlink() and m not in names:
                log.append(f"{ev}\t{m}\t{f.resolve()}")
                if not a.dry_run:
                    f.unlink()
    for line in log:
        print(("would remove  " if a.dry_run else "removed  ") + line)
    if log and not a.dry_run:
        out = paths.data(f"_pruned_links_{time.strftime('%Y%m%d-%H%M%S')}.tsv")
        out.write_text("eval\tmember\ttarget\n" + "\n".join(log) + "\n")
        print(f"logged to {out}")
    print(f"{len(log)} stale link(s)")


if __name__ == "__main__":
    main()
