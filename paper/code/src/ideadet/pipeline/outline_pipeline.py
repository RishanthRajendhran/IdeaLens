"""Stages 1 and 2: role-labelled outline extraction, then the de-leak paraphrase.

    stage 1  extraction  document -> role-labelled outline   (format-conditioned, few-shot)
    stage 2  de-leak     outline  -> outline, re-expressed    (source-blind paraphrase)

WHY STAGE 2 EXISTS
------------------
Extraction alone leaks the source document's authorship into the outline, and the
mechanism is copied wording, not structure or topic. The measured picture:

* Outlines of human documents and of AI documents separate at AUC 0.92-0.93 on a
  surface detector, and the ordering across extractors tracks how much each one
  lifts. The highest-fidelity extractor is the leakiest, because it keeps the
  most source wording. Fidelity and blindness sit on the same axis.
* Masking every entity moves it by only 0.037 AUC. Shuffling item order and
  dropping 40% of items are both null. The leak is not in which items, their
  order, or their names.
* The abstractive layer — the description and global themes, the one part written
  in the model's own voice with no source text to paraphrase — discriminates at
  0.592, near chance. **Where the model is not paraphrasing the source, there is
  almost no leak.**
* A source-blind rewrite of every item drops discrimination from 0.933 to 0.755,
  removing about 60% of the excess above chance, at an alignment cost of 0.026
  against a gold outline, with coverage and granularity flat.

So the de-leak is a mandatory stage, not a refinement, and it is applied to
**both classes** and at **both train and test time** — which is why swapping the
paraphraser at test time (Test 7) is the first thing a sceptical reviewer asks
for and is part of the suite.

The residue is the un-paraphrasable content: names, numbers, fixed technical
terms. Entity-dense formats leak most, narrative formats least. That floor is
structural, not a prompt bug.

RESUMABILITY AND COST
---------------------
Both stages write one JSON file per document, so a rerun continues from what is
on disk. Extraction is roughly 93% of pipeline spend and is dominated by the
few-shot exemplar block, so: keep one format per batch job (every row then shares
a byte-identical multi-thousand-token prefix, which is what earns the cached-input
discount), and treat the shot count as a real cost lever.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable

from .. import formats as F
from .. import prompts as P
from ..llm import vertex_batch as VB


def pending(doc_ids: Iterable[str], out_dir: Path) -> list[str]:
    """Document ids with no output file yet — the unit of resumption."""
    out_dir = Path(out_dir)
    return [d for d in doc_ids if not (out_dir / f"{d}.json").exists()]


def group_by_format(rows: list[dict], default_format: str | None = None) -> dict:
    """Split a corpus by format. Never run one format's prompt over another's rows.

    The stage-1 prompt injects that format's role vocabulary and the response
    schema's role enum is per-format, so a mixed batch silently extracts with the
    wrong vocabulary and produces outlines that look valid.
    """
    groups: dict[str, list[dict]] = {}
    for r in rows:
        fmt = r.get("format") or r.get("role_format") or default_format
        if not fmt:
            raise ValueError(
                f"document {r.get('id')!r} has no format. Run "
                f"scripts/pipeline/classify_format.py first; the extraction "
                f"prompt cannot be built without one.")
        groups.setdefault(F.canonical(fmt), []).append(r)
    return groups


# ------------------------------------------------------------------ stage 1 --
def extraction_requests(rows: list[dict], fmt: str, *, n_shots: int = 6,
                        thinking_level: str = "HIGH",
                        template: str = P.EXTRACTION_TEMPLATE,
                        max_output_tokens: int = 64000) -> list[dict]:
    """Batch rows for one format's extraction job."""
    system = P.extraction_system(fmt, n_shots, template)
    schema = P.extraction_schema(fmt)
    # The story goes in <document> tags, as in the training corpus (2026-09-23; it was sent bare before).
    return [VB.build_request(r["id"], f"<document>\n{r['text']}\n</document>", system=system, schema=schema,
                             thinking_level=thinking_level,
                             max_output_tokens=max_output_tokens, seed=P.PIPELINE_SEED)
            for r in rows]


# ------------------------------------------------------------------ stage 2 --
def deleak_requests(outlines: dict[str, dict], fmt: str, *, version: str = "v5",
                    thinking_level: str = "HIGH",
                    max_output_tokens: int = 64000) -> list[dict]:
    """Batch rows for one format's de-leak job.

    The paraphraser sees ONLY the outline, never the source document. That is
    what makes it a de-leak rather than a second extraction: it cannot copy from
    a document it has not been shown.
    """
    system = P.deleak_system(version)
    schema = P.deleak_schema(fmt)
    reqs = []
    for doc_id, rec in outlines.items():
        payload = rec.get("data", rec)
        reqs.append(VB.build_request(
            doc_id, json.dumps(payload, ensure_ascii=False, indent=2),
            system=system, schema=schema, thinking_level=thinking_level,
            max_output_tokens=max_output_tokens, seed=P.PIPELINE_SEED))
    return reqs


# -------------------------------------------------------------------- write --
def write_outline(out_dir: Path, doc_id: str, payload: dict, row: dict,
                  *, stage: str, extractor: str, paraphraser: str | None = None,
                  prompt_version: str = "", n_shots: int | None = None) -> Path:
    """One document's outline, with the provenance needed to interpret it later.

    `extractor` and `paraphraser` are recorded on every file. Outlines built with
    different extractors are a distribution difference, so they must never be
    silently pooled — Test 4 measures that swap deliberately, and it can only do
    so if every file says which models produced it.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fmt = F.canonical(row.get("format") or row.get("role_format"))
    rec = {
        "id": doc_id,
        "source": row.get("source"),
        "format": fmt,
        "role_format": F.slug(fmt),
        "stage": stage,
        "extractor": extractor,
        "paraphraser": paraphraser,
        "prompt_version": prompt_version,
        "n_shots": n_shots,
        "data": payload,
    }
    for k in ("model", "pair_id", "level", "saha_level", "arm", "lang",
              "domain", "attack", "humanized", "words", "topic"):
        if row.get(k) is not None:
            rec[k] = row[k]
    path = out_dir / f"{doc_id}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2))
    return path


def audit(out_dir: Path, expected: int, log: Callable[[str], None] = print) -> dict:
    """Completeness and shape check over a finished stage directory."""
    from ..io import iter_outline_files
    from ..outlines import summary
    from ..schema import validate_outline

    n, bad, items, words = 0, [], [], []
    for doc_id, rec in iter_outline_files(out_dir):
        n += 1
        problems = validate_outline(rec)
        if problems:
            bad.append((doc_id, problems[0]))
            continue
        s = summary(rec.get("data"))
        items.append(s["n_items"])
        words.append(s["n_words"])

    med = lambda v: sorted(v)[len(v) // 2] if v else 0
    report = {"dir": str(out_dir), "written": n, "expected": expected,
              "missing": max(expected - n, 0), "invalid": len(bad),
              "median_items": med(items), "median_words": med(words),
              "examples_invalid": bad[:5]}
    log(f"  {out_dir.name}: {n:,}/{expected:,} written, {len(bad)} invalid, "
        f"median {report['median_items']} items / {report['median_words']} words")
    return report
