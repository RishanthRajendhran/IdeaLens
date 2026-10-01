"""The outline record, and how it is rendered into detector input.

An outline is what the detector sees instead of the document. It has three
parts, of which only the third reaches the classifier:

    document_description  one paragraph naming the document's kind and shape
    global_themes         the document's overall claims, in the model's own words
    items                 the ordered list of atomic ideas, each with a role label

`document_description` and `global_themes` are written in the extractor's own
voice with no source text to paraphrase, so they carry almost no authorship
signal (measured AUC 0.592, near chance) while adding tokens. They are kept in
the stored record for inspection and dropped from every training and scoring
input.

CONVENTIONS THAT MUST NOT DRIFT
-------------------------------
* **Items are joined by newline, never by space.** The space-joined variant
  scores about 0.067 lower at 1% FPR. Both variants exist in older files, so
  anything reading an outline must render it through this module rather than
  formatting it inline.
* **Role labels stay in English** in every language variant. They are a small
  closed vocabulary the classifier keys on heavily; translating them discards
  in-distribution structure.
* The four settings below are the only input variants; a new one means a new
  trained arm, not an ad-hoc render at scoring time.
"""
from __future__ import annotations

from typing import Any, Iterable

#: The detector input settings. `full` is the headline arm.
SETTINGS = ("full", "items", "roles", "docs", "rawout")

SETTING_HELP = {
    "full":   "the whole de-leaked outline, one '[Role] content' line per item",
    "items":  "a single outline item, scored independently and pooled per document",
    "roles":  "the sequence of role labels only, every word of content stripped",
    "docs":   "the raw source document — the counterfactual control arm",
    "rawout": "the outline BEFORE the de-leak paraphrase — isolates what de-leaking costs",
}


def items_of(outline: Any) -> list[dict]:
    """Pull the item list out of any of the shapes an outline is stored in.

    Files written by the pipeline nest the payload under `data`; some older and
    some externally-built files store it flat. Accepting both here is cheaper
    than migrating every file on disk, and keeps old results re-scoreable.
    """
    if outline is None:
        return []
    if isinstance(outline, list):
        return [x for x in outline if isinstance(x, dict)]
    if not isinstance(outline, dict):
        return []
    for key in ("items", "data"):
        node = outline.get(key)
        if isinstance(node, list):
            return [x for x in node if isinstance(x, dict)]
        if isinstance(node, dict) and isinstance(node.get("items"), list):
            return [x for x in node["items"] if isinstance(x, dict)]
    return []


def role_of(item: dict) -> str:
    return str(item.get("role_name") or item.get("role") or "Other")


def content_of(item: dict) -> str:
    return str(item.get("content") or "").strip()


def render_item(item: dict) -> str:
    """One item as the classifier sees it: '[Role] content'."""
    return f"[{role_of(item)}] {content_of(item)}"


def render(outline: Any, setting: str = "full") -> str:
    """Render an outline into the exact string a detector arm was trained on."""
    if setting not in SETTINGS:
        raise ValueError(f"unknown setting {setting!r}; expected one of {SETTINGS}")
    if setting == "docs":
        raise ValueError("the 'docs' arm takes the source document, not an outline; "
                         "pass the document text straight to the detector")
    items = items_of(outline)
    if setting == "roles":
        # Content stripped entirely. A classifier given only this reaches AUC
        # 0.877, which is why extractor sensitivity (Test 4) is load-bearing
        # rather than a robustness footnote: role labels come from the extractor.
        return "\n".join(f"[{role_of(i)}]" for i in items)
    return "\n".join(render_item(i) for i in items)


def render_items(outline: Any) -> list[str]:
    """One rendered string per item, for the item-level arm."""
    return [render_item(i) for i in items_of(outline)]


def role_sequence(outline: Any) -> list[str]:
    return [role_of(i) for i in items_of(outline)]


def word_count(outline: Any) -> int:
    return sum(len(content_of(i).split()) for i in items_of(outline))


def verbatim_fraction(outline: Any) -> float:
    """Share of items the extractor flagged as quoted verbatim from the source.

    High values mean the extractor lifted wording rather than paraphrasing, which
    is the mechanism behind source-authorship leakage into the outline.
    """
    items = items_of(outline)
    if not items:
        return 0.0
    return sum(1 for i in items if i.get("verbatim")) / len(items)


def summary(outline: Any) -> dict:
    """Cheap structural description, used in audits and manifests."""
    items = items_of(outline)
    roles = role_sequence(outline)
    return {"n_items": len(items), "n_words": word_count(outline),
            "n_distinct_roles": len(set(roles)),
            "verbatim_fraction": round(verbatim_fraction(outline), 4)}


def as_prose(outline: Any, with_roles: bool = False) -> str:
    """Numbered-prose rendering, for surface detectors and for display.

    `with_roles=False` by default: the `N. (Role)` scaffolding adds a uniform
    machine sheen that raises a surface detector's AI score on both classes
    without improving discrimination, so it should not be present when an
    outline is scored as prose.
    """
    items = items_of(outline)
    if with_roles:
        return "\n".join(f"{n}. ({role_of(i)}) {content_of(i)}"
                         for n, i in enumerate(items, 1))
    return "\n".join(f"{n}. {content_of(i)}" for n, i in enumerate(items, 1))


def pool_item_scores(p_human: Iterable[float], method: str = "logit_mean") -> float:
    """Combine per-item P(human) into one document score.

    `logit_mean` is the project default (adopted 2026-08-24): the mean of the
    per-item log-odds, which is the pooling that makes the collaboration-ladder
    rungs come out monotone. `mean` and `min` are kept for comparison only.
    """
    import numpy as np
    p = np.clip(np.asarray(list(p_human), dtype=float), 1e-6, 1 - 1e-6)
    if p.size == 0:
        return float("nan")
    if method == "mean":
        return float(p.mean())
    if method == "min":
        return float(p.min())
    if method == "logit_mean":
        return float(1.0 / (1.0 + np.exp(-np.log(p / (1 - p)).mean())))
    raise ValueError(f"unknown pooling method {method!r}")
