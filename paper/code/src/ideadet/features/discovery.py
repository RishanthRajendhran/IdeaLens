"""LLM-driven feature discovery over contrast sets.

TWO AXES, FOUR COMBINATIONS
---------------------------
**Unit** — what one example is:

  `outline`  a whole de-leaked outline. Structure, role composition, ordering
             and transitions are all available and roughly half the resulting
             feature bank is about them.
  `item`     a single de-leaked item. Structure is GONE: there is no ordering,
             no neighbours, no document-level shape. Features about position,
             sequence or "how many items of some kind a document has" cannot be
             computed here and must not be proposed. What remains, and what the
             prompt directs the model to, is the nature of the idea itself — what
             it commits to, how it is warranted, how specific it is.

**Label source** — where each side's membership comes from:

  `corpus`   the corpus's own ground-truth labels, which are distilled from a
             surface detector's document-level verdicts. This discovers what
             distinguishes the CLASSES. It inherits the label source's
             circularity, and any write-up must say so.
  `model`    the tails of our own detectors' per-example scores, taken WITHIN
             each cell. This discovers what our CURRENT DETECTORS key on, which
             is a different question and answers "why does it fire", not "what
             is true of AI writing".

The two label sources answer different questions and their outputs must never be
merged into one bank.

CONTROLS THAT MAKE A PROPOSAL MEANINGFUL
----------------------------------------
* **Role matching.** Items inherit their label from their parent document, and
  the classes use roles at different rates. An unmatched draw lets the model
  "discover" the role distribution and call it an authorship feature. Every role
  contributes the same number of examples to each side, and the prompt says so —
  otherwise the model proposes it anyway.
* **Format handling is explicit.** Either format is held constant (per-format
  run) or deliberately mixed with the model told that a feature must survive
  across all of them (format-agnostic run). Silent mixing discovers formats.
* **Cuts are taken within a cell, never globally.** Median P(human) among human
  items ranges from about 0.38 to about 0.99 across roles, so a global percentile
  selects roles rather than examples and reproduces exactly the confound role
  matching exists to remove.
* **The surface ban.** The examples are already de-leaked, so lexical tells are
  gone by construction. The prompt bans them; a proposal about word choice or
  punctuation will not compute.
"""
from __future__ import annotations

import collections
import json
import random
from typing import Any, Callable

from .. import prompts as P

UNITS = ("outline", "item")
LABEL_SOURCES = ("corpus", "model")


# ------------------------------------------------------------- contrast set --
def sample_contrast(rows: list[dict], *, unit: str = "item",
                    label_source: str = "corpus", per_side: int = 2500,
                    match_roles: bool = True, format_agnostic: bool = False,
                    fmt: str | None = None, extreme_quantile: float = 0.10,
                    score_keys: tuple = ("nemotron", "modernbert"),
                    seed: int = 0) -> dict:
    """Build one balanced contrast set.

    `rows` need `label` ("human"/"ai"), `format`, `content`, and for
    `label_source="model"` a `scores` mapping of detector name -> p_human.
    """
    if unit not in UNITS:
        raise ValueError(f"unit must be one of {UNITS}")
    if label_source not in LABEL_SOURCES:
        raise ValueError(f"label_source must be one of {LABEL_SOURCES}")
    rng = random.Random(seed)

    pool = rows if (format_agnostic or fmt is None) else [
        r for r in rows if r.get("format") == fmt]
    if not pool:
        raise ValueError(f"no rows for format {fmt!r}")

    # Cells are (format, role) when matching roles, (format,) otherwise. Both
    # sampling rules operate strictly inside a cell.
    cells: dict[Any, dict[str, list]] = collections.defaultdict(
        lambda: {"human": [], "ai": []})
    for r in pool:
        key = ((r.get("format"), r.get("role_name")) if match_roles
               else (r.get("format"),))
        side = r.get("label")
        if side in ("human", "ai"):
            cells[key][side].append(r)

    human, ai = [], []
    for key, sides in cells.items():
        take = min(len(sides["human"]), len(sides["ai"]))
        if take == 0:
            continue
        for side, bucket in (("human", human), ("ai", ai)):
            candidates = sides[side]
            if label_source == "model":
                # Confidently-and-correctly called examples, cut within this cell.
                scored = [c for c in candidates
                          if all(c.get("scores", {}).get(k) is not None for k in score_keys)]
                if not scored:
                    continue
                k = max(1, int(len(scored) * extreme_quantile))
                # Human side: the highest P(human). AI side: the lowest.
                scored.sort(key=lambda c: min(c["scores"][s] for s in score_keys),
                            reverse=(side == "human"))
                candidates = scored[:max(k, take)]
            bucket.extend(rng.sample(candidates, min(take, len(candidates))))

    rng.shuffle(human)
    rng.shuffle(ai)
    n = min(per_side, len(human), len(ai))
    return {
        "unit": unit, "label_source": label_source, "format": fmt,
        "format_agnostic": format_agnostic, "role_matched": match_roles,
        "per_side": n, "seed": seed,
        "extreme_quantile": extreme_quantile if label_source == "model" else None,
        "human": human[:n], "ai": ai[:n],
        "n_cells": len(cells),
    }


# ------------------------------------------------------------------ prompts --
def render_prompt(contrast: dict) -> tuple[str, str]:
    """(system, user) for one discovery call, from prompts/feature_discovery/."""
    unit = contrast["unit"]
    system = P.read("feature_discovery", f"{unit}_system.txt")
    head_file = ("agnostic" if contrast.get("format_agnostic") else "per_format")
    head = P.read("feature_discovery", f"{unit}_user_{head_file}.txt")

    agnostic = bool(contrast.get("format_agnostic"))

    def block(rows) -> str:
        """Render one side. The layout is part of the prompt: the instructions
        refer to items by their ITEM n index, and the format tag is shown only on
        the agnostic runs, where the model is told formats are mixed on purpose."""
        if unit != "item":
            return "\n\n".join(_render_outline_example(r) for r in rows)
        out = []
        for i, r in enumerate(rows, 1):
            tag = f"  <{r['format']}>" if agnostic and r.get("format") else ""
            out.append(f"ITEM {i}{tag}\n  [{r.get('role_name', 'Other')}]   "
                       f"{(r.get('content') or '').strip()}")
        return "\n".join(out)

    return system, P.render(
        head,
        FORMAT=contrast.get("format") or "MIXED",
        N=contrast["per_side"],
        HUMAN=block(contrast["human"]),
        AI=block(contrast["ai"]))


def _render_outline_example(rec: dict) -> str:
    from ..outlines import items_of, content_of, role_of
    lines = [f"--- outline {rec.get('id', '')} ---"]
    for i, item in enumerate(items_of(rec.get("outline") or rec), 1):
        mark = " ·v" if item.get("verbatim") else ""
        lines.append(f"{i}. ({role_of(item)}){mark} {content_of(item)}")
    return "\n".join(lines)


def feature_schema() -> dict:
    """Structured-output schema for a proposal batch."""
    return P.read_json("feature_discovery", "feature.schema.json")


def consolidation_prompt(banks: list[dict]) -> tuple[str, str]:
    """Merge per-format or per-batch banks into one deduplicated feature set.

    The consolidation pass is where per-format proposals become usable: the same
    construct arrives under three names from three formats, and a bank that keeps
    all three cannot be probed without triple-counting it. It returns
    `canonical_features` (not `features`), each carrying `subsumes` so the merge
    is auditable, and a single format-agnostic operationalization synthesised
    across the cluster.
    """
    flat = []
    for bank in banks:
        for f in bank.get("features", []):
            flat.append({"raw_name": f.get("name"),
                         "source": bank.get("source", "AGNOSTIC"),
                         **{k: f.get(k) for k in
                            ("direction", "tier", "output_type",
                             "description", "operationalization")}})
    system = P.read("feature_discovery", "consolidation_system.txt")
    user = P.render(P.read("feature_discovery", "consolidation_user.txt"),
                    N=len(flat),
                    BANKS=json.dumps(flat, ensure_ascii=False, indent=2))
    return system, user


def consolidation_schema() -> dict:
    return P.read_json("feature_discovery", "consolidation.schema.json")


# ------------------------------------------------------------------- verify --
def bank_summary(features: list[dict]) -> str:
    tiers = collections.Counter(f.get("tier") for f in features)
    dirs = collections.Counter(f.get("direction") for f in features)
    lines = [f"{len(features)} features  "
             f"(tier: {dict(tiers)}; direction: {dict(dirs)})"]
    for f in features:
        lines.append(f"  [{f.get('direction', '?'):<5}] {f.get('name')}: "
                     f"{(f.get('description') or '')[:90]}")
    return "\n".join(lines)


def check_bank(features: list[dict], unit: str) -> list[str]:
    """Flag proposals that cannot be computed on this unit.

    Structural features are meaningless at item level and a model asked for them
    anyway will happily produce them, so this is a guard rather than a nicety.
    """
    banned = ("order", "ordering", "sequence", "position", "transition",
              "first item", "last item", "how many items", "number of items",
              "across the outline", "document-level")
    problems = []
    for f in features:
        text = f"{f.get('name', '')} {f.get('description', '')} {f.get('operationalization', '')}".lower()
        if unit == "item" and any(b in text for b in banned):
            problems.append(f"{f.get('name')}: proposes a structural property that "
                            f"cannot be computed from a single item")
        if not f.get("operationalization"):
            problems.append(f"{f.get('name')}: no operationalization, so it cannot be probed")
    return problems
