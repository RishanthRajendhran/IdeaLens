#!/usr/bin/env python3
"""Replace the symlinks under `data/` with real copies.

Run this before moving the tree to a machine that cannot see the originals, or
before archiving a frozen snapshot for a submission. It is deliberately separate
from `link_sources.py`: linking is the normal working state, copying is a
deliberate act that duplicates a lot of bytes.

    python scripts/data/materialize.py --dry-run     # what it would copy, and how big
    python scripts/data/materialize.py --eval test5_peer_review
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ideadet import paths, registry


def size_of(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval", default="", help="one eval id; default is all")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    targets = ([registry.get_eval(a.eval)] if a.eval else registry.ordered_evals())
    total = 0
    for ev in targets:
        if not ev.path.exists():
            continue
        for member in sorted(ev.path.iterdir()):
            if not member.is_symlink():
                continue
            src = member.resolve()
            if not src.exists():
                print(f"  {ev.id}/{member.name}: dangling link -> {src}")
                continue
            n = size_of(src)
            total += n
            print(f"  {ev.id}/{member.name:<14}{n / 1e6:>10.1f} MB")
            if a.dry_run:
                continue
            member.unlink()
            if src.is_dir():
                shutil.copytree(src, member)
            else:
                shutil.copy2(src, member)
    print(f"\n{'would copy' if a.dry_run else 'copied'} {total / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
