#!/usr/bin/env python3
"""Merge per-format or per-batch feature banks into one deduplicated set.

    python scripts/features/consolidate.py --glob 'outputs/feature_discovery/proposals/item_corpus_*.json'

Banks from DIFFERENT LABEL SOURCES are never merged — they answer different
questions — and the script refuses to do so rather than producing a bank whose
provenance cannot be recovered.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys

import _bootstrap  # noqa: F401

from ideadet import config as C
from ideadet import paths
from ideadet.features import discovery as D
from ideadet.io import load_json, write_json
from ideadet.llm import openai_batch as OB


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_args(ap, "features")
    ap.add_argument("--glob", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    cfg = C.from_args(a, "features")
    files = sorted(glob.glob(a.glob))
    if not files:
        raise SystemExit(f"no files matched {a.glob!r}")
    banks = [load_json(f) for f in files]

    sources = {b["contrast"]["label_source"] for b in banks}
    units = {b["contrast"]["unit"] for b in banks}
    if len(sources) > 1 or len(units) > 1:
        raise SystemExit(
            f"refusing to merge across label sources {sources} / units {units}. "
            f"They answer different questions and a merged bank cannot be "
            f"attributed. Consolidate each separately.")

    print(f"{len(files)} bank(s), "
          f"{sum(len(b['features']) for b in banks)} features, "
          f"unit={units.pop()} label_source={sources.pop()}")

    system, user = D.consolidation_prompt(
        [{"source": f, "features": b["features"]} for f, b in zip(files, banks)])
    text, usage = OB.call_once(
        cfg["model"],
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        reasoning_effort=cfg.get("effort"),
        response_format={"type": "json_schema", "json_schema": {
            "name": "canonical_features", "strict": True,
            "schema": D.consolidation_schema()}})
    payload = json.loads(text)
    merged = payload.get("canonical_features") or payload.get("features", [])
    print(f"\n{D.bank_summary(merged)}")

    dest = a.out or paths.outputs("feature_discovery", "consolidated.json")
    write_json(dest, {"canonical_features": merged, "sources": files, "usage": usage,
                      "stamp": C.stamp(cfg)})
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    sys.exit(main())
