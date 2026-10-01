#!/usr/bin/env python3
"""Point `data/<eval>/` at corpora that already exist elsewhere on this machine.

Datasets are large and several are redistributable only under their upstream
licence, so this repository does not carry copies. Instead each eval directory
holds its documentation (`README.md`, `dataset.yaml`) as real tracked files, and
`corpus.jsonl`, `labels.json`, `extract/` and `deleak/` as **symlinks** into
wherever the data actually lives.

Code therefore reads `data/test5_peer_review/corpus.jsonl` and does not care
which it is, and `scripts/data/materialize.py` turns the links into real copies
when the tree is moved to a machine that cannot see the originals.

    python scripts/data/link_sources.py --map configs/data_sources.yaml
    python scripts/data/link_sources.py --map ... --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import yaml

from ideadet import paths

MEMBERS = ("corpus.jsonl", "labels.json", "extract", "deleak")


def link(target: Path, dest: Path, dry: bool, log=print) -> str:
    if not target.exists():
        return "source missing"
    if dest.is_symlink():
        if dest.resolve() == target.resolve():
            return "already linked"
        if not dry:
            dest.unlink()
    elif dest.exists():
        return "SKIPPED: a real file is already here"
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(target)
    return "linked"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", default="configs/data_sources.yaml",
                    help="YAML mapping eval id -> source directory")
    ap.add_argument("--only", default="", help="comma-separated eval ids")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    spec = yaml.safe_load((paths.REPO / a.map).read_text()) or {}
    # `sources` use the per-document directory layout; `flat_sources` store a
    # whole stage as one JSONL. Both end up under data/<eval>/ and both are read
    # by io.iter_outline_files, so nothing downstream cares which a set uses.
    # Four sections, merged in order of increasing specificity so a later one can
    # add members to an eval an earlier one already touched:
    #   sources        per-document directory layout (corpus + both stages)
    #   flat_sources   a whole stage as one JSONL
    #   corpus_sources the raw documents as fed to the pipeline
    #   raw_sources    the untouched upstream archive
    sources: dict = {}
    for section in ("sources", "flat_sources", "corpus_sources", "raw_sources"):
        for eval_id, entry in (spec.get(section) or {}).items():
            if eval_id in sources:
                sources[eval_id] = {**sources[eval_id],
                                    "extra": sources[eval_id].get("extra", []) + [entry]}
            else:
                sources[eval_id] = dict(entry)
    only = {x.strip() for x in a.only.split(",") if x.strip()}

    for eval_id, entry in sorted(sources.items()):
        if only and eval_id not in only:
            continue
        src = Path(str(entry["path"]).rstrip("/"))
        dest = paths.data(eval_id)
        dest.mkdir(parents=True, exist_ok=True)
        for block in [entry] + entry.get("extra", []):
            root = Path(str(block["path"]).rstrip("/"))
            print(f"{eval_id}\n  <- {root}")
            for member in block.get("members", MEMBERS):
                name = member if isinstance(member, str) else member["as"]
                rel = member if isinstance(member, str) else member["from"]
                target = root if rel == "." else root / rel
                print(f"     {name:<16}{link(target, dest / name, a.dry_run)}")
    if a.dry_run:
        print("\n(dry run: nothing was written)")


if __name__ == "__main__":
    main()
