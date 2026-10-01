"""Record shapes for every file the pipeline reads or writes, and their checks.

Four record types travel between stages. Each is documented here and validated
by `validate_*`, which returns a list of human-readable problems rather than
raising, so a build script can report every bad row at once instead of dying on
the first.

The corresponding JSON Schema files under `data/schemas/` are generated from
these definitions by `scripts/data/write_schemas.py`, so the two cannot drift.

    corpus row   one source document                 data/<eval>/corpus.jsonl
    label entry  its ground truth and slice metadata data/<eval>/labels.json
    outline      the extracted or de-leaked outline  data/<eval>/{extract,deleak}/<id>.json
    score row    one model's verdict on one document outputs/<eval>/<run>/scores.jsonl
"""
from __future__ import annotations

from typing import Any

from . import formats as F

# --------------------------------------------------------------- corpus row --
#: Required on every corpus row.
CORPUS_REQUIRED = ("id", "text", "source")
#: Recognised optional fields. Anything else is kept but not interpreted.
CORPUS_OPTIONAL = (
    "format",        # display name, e.g. "Academic Writing"
    "role_format",   # its slug, e.g. "academic_writing"
    "model",         # generator model id; null for human documents
    "words",         # word count of `text`
    "pair_id",       # joins matched human/AI documents built from one prompt
    "level",         # rung on a collaboration ladder, or a Saha level
    "saha_level",    # one of H, H-AI, AI-HI, AI-EP, AI-BP
    "arm",           # treatment arm within a multi-condition eval
    "lang",          # ISO code; "en" for the main suite
    "domain", "subset", "attack", "humanized", "draw", "topic",
    "src_wc", "gen_wc", "ext_id", "url",
)

#: `source` is the ground-truth authorship of the IDEAS, not of the prose.
#: Under the project's labelling rule, a document whose ideas are human is
#: `human` however much of its surface an AI wrote.
SOURCE_VALUES = ("human", "ai")

#: Saha et al.'s levels of AI assistance, increasing human intervention downward.
SAHA_LEVELS = ("AI-BP", "AI-EP", "AI-HI", "H-AI", "H")


def validate_corpus_row(row: dict, require_format: bool = True) -> list[str]:
    problems = []
    for k in CORPUS_REQUIRED:
        if not row.get(k):
            problems.append(f"missing required field {k!r}")
    if row.get("source") not in SOURCE_VALUES:
        problems.append(f"source must be one of {SOURCE_VALUES}, got {row.get('source')!r}")
    if row.get("saha_level") and row["saha_level"] not in SAHA_LEVELS:
        problems.append(f"saha_level must be one of {SAHA_LEVELS}")
    if require_format:
        fmt = row.get("format") or row.get("role_format")
        if not fmt:
            problems.append("no format: the extraction prompt is format-conditioned, "
                            "so classify_format.py must run before extraction")
        else:
            try:
                F.canonical(fmt)
            except KeyError as e:
                problems.append(str(e).splitlines()[0])
    if isinstance(row.get("text"), str) and len(row["text"].split()) < 50:
        problems.append(f"text is {len(row['text'].split())} words; outline "
                        f"extraction has a practical floor around 500")
    return problems


def normalise_corpus_row(row: dict) -> dict:
    """Fill the derivable fields so downstream stages never have to guess."""
    out = dict(row)
    fmt = out.get("format") or out.get("role_format")
    if fmt:
        out["format"] = F.canonical(fmt)
        out["role_format"] = F.slug(out["format"])
    if "words" not in out and isinstance(out.get("text"), str):
        out["words"] = len(out["text"].split())
    return out


# -------------------------------------------------------------- label entry --
#: labels.json maps document id -> this. `source` is required; everything else
#: is slice metadata carried through to reporting so results can be broken down
#: without re-reading the corpus.
LABEL_REQUIRED = ("source",)


def validate_labels(labels: dict, corpus_ids: set[str] | None = None) -> list[str]:
    problems = []
    for doc_id, entry in labels.items():
        if not isinstance(entry, dict):
            problems.append(f"{doc_id}: label entry must be an object")
            continue
        if entry.get("source") not in SOURCE_VALUES:
            problems.append(f"{doc_id}: source must be one of {SOURCE_VALUES}")
    if corpus_ids is not None:
        missing = corpus_ids - set(labels)
        extra = set(labels) - corpus_ids
        if missing:
            problems.append(f"{len(missing):,} corpus rows have no label "
                            f"(e.g. {sorted(missing)[:3]})")
        if extra:
            problems.append(f"{len(extra):,} labels have no corpus row "
                            f"(e.g. {sorted(extra)[:3]})")
    return problems


def y_human(source: str) -> int:
    """Ground truth in the stored convention: 1 = HUMAN, 0 = AI."""
    if source not in SOURCE_VALUES:
        raise ValueError(f"source must be one of {SOURCE_VALUES}, got {source!r}")
    return 1 if source == "human" else 0


# ------------------------------------------------------------------ outline --
OUTLINE_REQUIRED = ("id", "data")
OUTLINE_DATA_REQUIRED = ("items",)
ITEM_REQUIRED = ("role_name", "content")


def validate_outline(rec: dict) -> list[str]:
    problems = []
    for k in OUTLINE_REQUIRED:
        if k not in rec:
            problems.append(f"missing {k!r}")
    data = rec.get("data") or {}
    items = data.get("items")
    if not isinstance(items, list) or not items:
        problems.append("data.items must be a non-empty list")
        return problems
    for i, item in enumerate(items):
        for k in ITEM_REQUIRED:
            if not item.get(k):
                problems.append(f"item {i}: missing {k!r}")
    return problems


# ----------------------------------------------------------------- score row --
#: One row per scored document. `p_human` is P(human); the detector fires below
#: the threshold. `logits` is kept whenever the backend exposes it.
SCORE_REQUIRED = ("id", "p_human")


def validate_score_row(row: dict) -> list[str]:
    problems = []
    for k in SCORE_REQUIRED:
        if k not in row:
            problems.append(f"missing {k!r}")
    p = row.get("p_human")
    if p is not None and not (0.0 <= float(p) <= 1.0):
        problems.append(f"p_human out of range: {p}")
    if "y" in row and row["y"] not in (0, 1):
        problems.append(f"y must be 0 (ai) or 1 (human), got {row['y']!r}")
    return problems


def report(problems: list[str], context: str, limit: int = 20) -> str:
    if not problems:
        return f"{context}: ok"
    head = "\n".join(f"  - {p}" for p in problems[:limit])
    more = f"\n  ... and {len(problems) - limit} more" if len(problems) > limit else ""
    return f"{context}: {len(problems)} problem(s)\n{head}{more}"


#: Metadata every generated record must carry, so that a result can be broken
#: down by construction without re-deriving anything. Enforced by the eval
#: builders in scripts/data/.
GENERATED_RECORD_FIELDS: dict[str, str] = {
    "id": "source document id, STABLE across every condition built from it",
    "condition": "which arm this row is, e.g. 'C1_rewrite_medium'",
    "source": "'human' or 'ai' under the idea-level labelling rule",
    "saha_level": "one of H, H-AI, AI-HI, AI-EP, AI-BP",
    "format": "WebOrganizer format, from the classifier and never asserted",
    "model": "model that produced the document; null for human",
    "extractor": "model that produced the outline",
    "paraphraser": "model that produced the de-leak",
    "lang": "ISO code",
    "src_wc": "word count of the source human document",
    "gen_wc": "word count of the generated document",
    "align_score": "outline alignment of the generated document to the source outline",
    "brief_leak": "n-gram overlap of the brief with the source document (brief-conditioned arms)",
}
