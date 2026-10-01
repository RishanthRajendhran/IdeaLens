#!/usr/bin/env python3
"""Check the repository is internally consistent. Run it after any change.

    python scripts/selfcheck.py

Verifies the things that break silently rather than loudly:

  * every config parses and resolves its `extends:` chain
  * every eval and model in the registry loads
  * every format's extraction prompt and response schema build, at every shot count
  * no prompt template contains an unfilled or double-escaped placeholder
  * the training contract and its system prompts are present
  * every prompt an eval config names exists on disk
  * the metric conventions still hold (orientation guard, estimability floor)

Exits non-zero on any failure, so it can gate a commit.
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np
import yaml

from ideadet import calibration as CAL
from ideadet import config as C
from ideadet import formats as F
from ideadet import metrics as M
from ideadet import prompts as P
from ideadet import paths
from ideadet import registry
from ideadet.features import discovery as D

#: A real slot is {{UPPER_SNAKE}}. Anything else inside doubled braces is an
#: escaped literal left over from a Python .format() string -- it would reach the
#: model as two braces, corrupting the very place a prompt defines its own input
#: format. That is the bug this pattern exists to catch.
ESCAPED_BRACE = re.compile(r"\{\{(?![A-Z][A-Z0-9_]*\}\})[^{}]{0,60}\}?\}")


def main() -> int:
    fails: list[str] = []

    def check(label, fn):
        try:
            fn()
            print(f"  ok    {label}")
        except Exception as e:
            print(f"  FAIL  {label}: {type(e).__name__}: {e}")
            fails.append(label)

    print("configs")
    for f in sorted(glob.glob(str(paths.configs("**", "*.yaml")), recursive=True)):
        p = Path(f)
        if p.stem.startswith("_") or p.parent.name == "configs":
            check(str(p.relative_to(paths.REPO)), lambda p=p: yaml.safe_load(p.read_text()))
        else:
            check(str(p.relative_to(paths.REPO)), lambda p=p: C.load(p.stem, kind=p.parent.name))

    print("registry")
    check("evals load", lambda: registry.ordered_evals())
    check("models load", lambda: registry.models())

    print("prompts")
    for fmt in F.ALL_FORMATS:
        def build(fmt=fmt):
            s = P.extraction_system(fmt, 6)
            enum = (P.extraction_schema(fmt)["properties"]["items"]["items"]
                    ["properties"]["role_name"]["enum"])
            assert len(s) > 5000 and len(enum) > 10, "prompt or role enum too small"
        check(f"extraction/{F.slug(fmt)}", build)
    for n in (6,):
        check(f"exemplar bank n={n}",
              lambda n=n: P.extraction_system("Academic Writing", n))
    check("deleak v1", lambda: (_ for _ in ()).throw(AssertionError("unfilled slot"))
          if "{{" in P.deleak_system("v1") else None)
    check("training contract", lambda: [P.scoring_contract()["label_tokens"]]
          + [P.training_system(s) for s in ("full", "docs")])

    # A template must contain only slots the code knows how to fill, and no
    # doubled braces left over from a Python .format() string -- those reach the
    # model as literal braces and corrupt the one place the prompt defines its
    # own input format.
    def no_escaped_braces():
        bad = []
        for f in sorted(paths.root("prompts").rglob("*.txt")):
            for m in set(ESCAPED_BRACE.findall(f.read_text())):
                bad.append(f"{f}: {{{{{m}")
        assert not bad, "; ".join(bad[:6])
    check("no .format() brace escapes left in any prompt", no_escaped_braces)

    for unit in ("item",):
        for agnostic in (False, True):
            def render(unit=unit, agnostic=agnostic):
                ex = {"id": "x", "role_name": "Claim", "content": "c",
                      "format": "Academic Writing", "outline": {"items": []}}
                _, u = D.render_prompt({
                    "unit": unit, "label_source": "corpus", "per_side": 1,
                    "format": None if agnostic else "Academic Writing",
                    "format_agnostic": agnostic, "human": [ex], "ai": [ex]})
                assert "{{" not in u, "unfilled or escaped placeholder survived"
            check(f"feature prompt {unit}/{'agnostic' if agnostic else 'per_format'}",
                  render)

    def eval_prompts():
        missing = []
        for ev in registry.ordered_evals():
            for k in ("prompt", "brief_prompt", "generate_prompt", "abstract_prompt"):
                ref = (ev.raw.get("generation") or {}).get(k)
                if ref and not list(paths.root("prompts").glob(f"{ref}*")):
                    missing.append(f"{ev.id}.{k} -> {ref}")
        assert not missing, "; ".join(missing)
    check("eval-generation prompts exist", eval_prompts)

    print("conventions")

    def orientation():
        rng = np.random.default_rng(0)
        y = np.r_[np.ones(200, int), np.zeros(200, int)]
        p = np.r_[rng.beta(6, 2, 200), rng.beta(2, 6, 200)]
        M.check_orientation(p, y)
        try:
            M.check_orientation(1 - p, y)
        except ValueError:
            return
        raise AssertionError("orientation guard did not fire on flipped scores")
    check("AI is the positive class; guard fires when flipped", orientation)

    def estimability():
        assert not M.estimable(0.001, 10_000), "0.1% must not be estimable at n=10k"
        assert M.estimable(0.01, 10_000)
        d = CAL.derive(np.random.default_rng(0).beta(8, 2, 5000), model_id="t")
        assert "0.001" in d["not_estimable"], "unestimable target was emitted anyway"
    check("estimability floor enforced", estimability)

    def no_fallback():
        d = CAL.derive(np.random.default_rng(0).beta(8, 2, 5000),
                       groups={"format": ["A"] * 2500 + ["B"] * 2500}, model_id="t")
        t = CAL.Thresholds({"models": {"t": d}})
        r = t.apply("t", np.array([0.5, 0.5]), 0.01, "format", ["A", "ZZZ"])
        assert r["covered"][0] and not r["covered"][1], \
            "an uncalibrated group must be filtered, never given the global cut"
    check("uncalibrated groups filtered, not defaulted", no_fallback)

    print(f"\n{'ALL CLEAN' if not fails else str(len(fails)) + ' FAILURE(S)'}")
    for f in fails:
        print(f"  - {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
