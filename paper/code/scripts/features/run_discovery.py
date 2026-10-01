#!/usr/bin/env python3
"""Ask a frontier model to propose discriminating features from a contrast set.

    python scripts/features/run_discovery.py --config item_corpus_labels \
        --contrast outputs/feature_discovery/contrast/item_corpus_agnostic.json

Produces hypotheses, not measurements. Everything it proposes must then be
computed and tested by `scripts/features/run_probes.py`; a feature that sounds
compelling and does not compute is a failed hypothesis.

The prompt bans surface-level tells because the examples have already been
de-leaked: lexical cues are gone by construction and a proposal about word choice
or punctuation will not compute. It also bans structural features on item-level
runs, and `check_bank` flags any that slip through anyway.
"""
from __future__ import annotations

import argparse
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
    ap.add_argument("--contrast", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    cfg = C.from_args(a, "features")
    contrast = load_json(a.contrast)
    system, user = D.render_prompt(contrast)
    print(f"contrast: {contrast['per_side']}+{contrast['per_side']} "
          f"{contrast['unit']}(s), label_source={contrast['label_source']}\n"
          f"prompt: system {len(system):,} chars, user {len(user):,} chars "
          f"(~{len(user) // 4:,} tokens)")

    text, usage = OB.call_once(
        cfg["model"],
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        reasoning_effort=cfg.get("effort"),
        response_format={"type": "json_schema", "json_schema": {
            "name": "features", "strict": True, "schema": D.feature_schema()}})

    payload = json.loads(text)
    features = payload.get("features", [])
    print(f"\n{D.bank_summary(features)}")

    problems = D.check_bank(features, contrast["unit"])
    if problems:
        print(f"\n{len(problems)} proposal(s) cannot be computed on this unit:")
        for p in problems:
            print(f"  - {p}")

    name = __import__("pathlib").Path(a.contrast).stem
    dest = a.out or paths.outputs("feature_discovery", "proposals", f"{name}.json")
    write_json(dest, {"features": features, "uncomputable": problems,
                      "contrast": {k: v for k, v in contrast.items()
                                   if k not in ("human", "ai")},
                      "usage": usage, "stamp": C.stamp(cfg)})
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    sys.exit(main())
