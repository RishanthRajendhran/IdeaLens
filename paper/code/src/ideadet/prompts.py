"""Prompt loading and assembly.

Prompts live as plain text under `prompts/`, never as string literals in Python,
for three reasons: they are the experimental variable in several results, they
are large (the six-shot extraction block is 31k-51k tokens), and they must be
citable in the paper exactly as run.

Templates use `{{PLACEHOLDER}}`. `render` fills them and refuses to return a
string that still contains an unfilled placeholder, because a silently unfilled
`{{ROLES_BLOCK}}` produces a well-formed outline extracted with no role
vocabulary at all.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from . import formats as F
from . import paths

_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def read(*parts) -> str:
    p = paths.prompts(*parts)
    if not p.exists():
        raise FileNotFoundError(
            f"no prompt at {p}. `ls {p.parent}` for what is available; "
            f"prompts/README.md explains the naming.")
    return p.read_text()


def read_json(*parts) -> dict:
    return json.loads(read(*parts))


def render(template: str, **values) -> str:
    """Fill {{PLACEHOLDER}}s and verify none survive."""
    out = template
    for k, v in values.items():
        out = out.replace("{{" + k.upper() + "}}", str(v))
    left = sorted(set(_PLACEHOLDER.findall(out)))
    if left:
        raise ValueError(
            f"unfilled placeholder(s) {left} — an unfilled prompt slot produces "
            f"output that looks valid and is not. Supply them or edit the template.")
    return out


# ------------------------------------------------------------ role vocabulary --
@lru_cache(maxsize=32)
def role_vocabulary(fmt: str) -> list[dict]:
    """The consolidated role set for one format, as produced by role discovery.

    Each entry has at least `name` and `description`. This is the vocabulary the
    extractor is allowed to label items with, and the enum of the response schema.
    """
    slug = F.slug(F.canonical(fmt))
    f = paths.prompts("role_vocabularies", f"{slug}.json")
    if not f.exists():
        raise FileNotFoundError(
            f"no role vocabulary for {fmt!r} at {f}. Formats without one are out "
            f"of scope; see prompts/role_vocabularies/README.md.")
    payload = json.loads(f.read_text())
    roles = payload.get("final_roles") or payload.get("roles") or payload
    if isinstance(roles, dict):
        roles = roles.get("final_roles", [])
    return list(roles)


def role_names(fmt: str) -> list[str]:
    """Sorted role names plus the 'Other' escape hatch, for the response enum."""
    return sorted({r["name"] for r in role_vocabulary(fmt)}) + ["Other"]


def roles_block(fmt: str, excerpts_only: bool = True) -> str:
    """The role vocabulary rendered for injection as {{ROLES_BLOCK}}, in the layout of the TRAINING corpus
    (${AUX_DIR} detector/train/v391/score_one_doc.build_roles_block): per role its definition, assignment test,
    what it is distinguished from, and its examples.
    Examples are rendered as their excerpt text only; excerpts_only=False
    reproduces the training block byte for byte, raw example objects included.
    """
    out = []
    for r in role_vocabulary(fmt):
        block = (f"### {r['name']}\n"
                 f"- **Definition:** {r['definition']}\n"
                 f"- **Assignment test:** {r['assignment_test']}\n"
                 f"- **Distinguished from:** {r.get('distinguished_from', '')}")
        ex = r.get("examples", "")
        if not excerpts_only:
            block += f"\n- **Examples:** {ex if ex is not None else ''}"
        else:
            xs = [str(e.get("excerpt", "")).strip() if isinstance(e, dict) else str(e).strip() for e in (ex or [])]
            xs = [x for x in xs if x]
            if xs:
                block += "\n- **Examples:**" + "".join(f"\n  - {x}" for x in xs)
        out.append(block)
    return "\n\n".join(out)


# ------------------------------------------------------------------ few-shot --
def fewshot(fmt: str, n_shots: int) -> list[dict]:
    """The n-shot exemplars for one format: [{document, outline}, ...].

    Exemplar count is an experimental axis (Test 4 folds in 6 -> 3 -> 2 -> 0),
    and it dominates cost: extraction is roughly 93% of pipeline spend and the
    exemplar block is most of the extraction prompt.
    """
    if n_shots == 0:
        return []
    f = paths.prompts("extraction", "fewshot", f"n{n_shots}_exemplars.json")
    if not f.exists():
        raise FileNotFoundError(
            f"no {n_shots}-shot exemplar bank at {f}; available: "
            f"{sorted(p.name for p in f.parent.glob('n*_exemplars.json'))}")
    bank = json.loads(f.read_text())
    fmt = F.canonical(fmt)
    if fmt not in bank:
        raise KeyError(f"{n_shots}-shot bank has no exemplars for {fmt!r}")
    return bank[fmt]


# The few-shot preface of the TRAINING corpus (score_one_doc.FEWSHOT_PREFACE), 2026-09-23. The previous one read
# "# EXAMPLES / The following are complete worked examples ... in the analyst's own words ...".
FEWSHOT_PREFACE = (
    "\n\n\n# WORKED EXAMPLES\n\n"
    "Complete, correct outputs for other documents of this format. Study how finely each document "
    "is decomposed: every distinct substantive, rhetorical, or structural commitment becomes its "
    "own item, even where one broader item could technically cover several. Match that level of "
    "granularity. Do not carry over these examples' content, themes, or role distribution.\n")

# The format descriptions the TRAINING corpus was extracted with (score_one_doc.FORMAT_DESCRIPTIONS), used for the
# extraction prompt only; formats.FORMAT_DESCRIPTIONS keeps its own wording for everything else.
EXTRACTION_FORMAT_DESCRIPTIONS = {
    "Personal Blog": "A personal weblog entry written in a first-person voice, relating the author's own experience, opinion, or reflection to a general readership.",
    "Nonfiction Writing": "Long-form nonfiction prose that develops an argument, reflection, or analysis in an authorial voice, as opposed to reporting news or explaining a topic encyclopaedically.",
    "Academic Writing": "Scholarly prose presenting research, argument or review for an academic readership.",
    "News Article": "Journalistic reporting of events for a general readership.",
    "Knowledge Article": "Encyclopaedic or instructional prose explaining a topic.",
    "Creative Writing": "Imaginative prose such as fiction or narrative storytelling.",
    "Personal About Page": "A self-descriptive page introducing a person or their work.",
    "User Reviews": "First-person evaluative reviews of a product, service or place.",
    "Transcript / Interview": "A transcribed spoken exchange between two or more participants.",
}
PROMPT_VERSION = "train_v391+excerpts+en"   # recorded on every outline extracted with this prompt
# 2026-09-24: extraction template is labeled_outline_extraction_en.txt, the training template plus the OUTPUT LANGUAGE
# block (every output field in English); outlines from 2026-09-23 until then carry "train_v391+excerpts".
EXTRACTION_TEMPLATE = "labeled_outline_extraction_en.txt"
# Gemini generationConfig.seed for every pipeline call (format gate, extraction, de-leak), from 2026-09-24; the same value
# as ${AUX_DIR} modules/training_extraction.SEED (drawn at random, not chosen). Makes repeat runs return the same output.
PIPELINE_SEED = 1865679507


def extraction_system(fmt: str, n_shots: int = 6,
                      template: str = EXTRACTION_TEMPLATE) -> str:
    """Assemble the full stage-1 system prompt for one format.

    The exemplar block is appended after the instruction body and before the
    input-format section, mirroring the prompt as actually run. Exemplars teach
    by imitation, so an exemplar that lifts phrasing from its source teaches the
    model to lift: the banks under prompts/extraction/fewshot/ are paraphrased.
    """
    fmt = F.canonical(fmt)
    body = render(read("extraction", template),
                  FORMAT=fmt,
                  FORMAT_DESCRIPTION=EXTRACTION_FORMAT_DESCRIPTIONS[fmt],
                  ROLES_BLOCK=roles_block(fmt))
    shots = fewshot(fmt, n_shots)
    if not shots:
        return body
    head = body[:body.index("# INPUT FORMAT")].rstrip()
    blocks = [
        f"## Example {i + 1}\n\n<document>\n{s['document']}\n</document>\n\n"
        f"Expected output:\n{json.dumps(s['outline'], ensure_ascii=False, indent=2)}"
        for i, s in enumerate(shots)
    ]
    return head + FEWSHOT_PREFACE + "\n\n".join(blocks)


def extraction_schema(fmt: str) -> dict:
    """Structured-output schema for stage 1, with the per-format role enum."""
    return {
        "type": "object",
        "required": ["document_description", "global_themes", "items"],
        "properties": {
            "document_description": {"type": "string"},
            "global_themes": {"type": "array", "items": {"type": "string"}},
            "items": {"type": "array", "items": {
                "type": "object",
                "required": ["role_name", "content", "verbatim"],
                "properties": {
                    "role_name": {"type": "string", "enum": role_names(fmt)},
                    "content": {"type": "string"},
                    "verbatim": {"type": "boolean"},
                }}},
        },
    }


def deleak_system(version: str = "v1") -> str:
    """Assemble the stage-2 (de-leak paraphrase) system prompt.

    The outline placeholder sits near the top of the template, with every
    invariant — structural, semantic, canonical re-expression, protected
    material, verbatim, final check — AFTER it. Taking only the text before the
    placeholder would ship a short preamble with none of the constraints that
    make stage 2 a de-leaking step, so both halves are rejoined as the system
    prompt and the outline itself goes in the user message.
    """
    raw = read("deleak", f"canonical_paraphrasing_{version}.txt")
    if "{{LABELED_OUTLINE_JSON}}" not in raw:
        return raw.strip()
    before, after = raw.split("{{LABELED_OUTLINE_JSON}}")
    before = re.sub(r"\n+#\s*INPUT OUTLINE\s*$", "\n", before)
    return (before.rstrip() + "\n\n" + after.lstrip()).strip()


def deleak_schema(fmt: str) -> dict:
    return extraction_schema(fmt)


def training_system(setting: str) -> str:
    """The classifier's system prompt for one input setting.

    This is part of the scoring contract: training and scoring must use the byte-
    identical string, or a threshold fitted under one lands somewhere else under
    the other.
    """
    return read("training", f"system_{setting}.txt").strip()


def scoring_contract() -> dict:
    """The full generative-scoring contract: template, label tokens, readout."""
    return read_json("training", "contract.json")
