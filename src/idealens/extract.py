"""Outline extraction: document -> role-labelled outline, with the prompt the training corpus was built with.

Every reply is parsed and checked (valid JSON, the schema's fields, every role in the format's vocabulary). A reply
that fails is sent back to the model with the problem stated, up to `max_repairs` times; each repair is recorded, and a
document that never yields a valid outline comes back with `meta["error"]` set and no items.

few_shot=False drops the six worked examples (the prompt shrinks from roughly 35,000-60,000 tokens to roughly
15,000-24,000, by a four-characters-per-token estimate; the role definitions stay).
The published thresholds assume the default: few-shot extraction by gemini-3.7-flash.
"""
from __future__ import annotations

from . import formats as F
from . import parse, prompts, runner
from .outline import Outline
from .providers import make as make_provider

REPAIR_INSTRUCTION = ("Your reply above could not be used: {problem}. Reply again with only the JSON object described "
                      "in OUTPUT FORMAT, using only the allowed role names, with no Markdown and no other text.")


def _format_of(f) -> str:
    if isinstance(f, F.FormatAssignment):
        if f.format is None:
            raise F.FormatError(f"document has no usable format ({f.error or 'out of scope'})")
        return f.format
    if f is None:
        raise F.FormatError("extraction needs a format: pass one, or classify the document first")
    return F.resolve(f)


def extract(texts, formats, provider=None, few_shot: bool = True, mode: str = "online", workers: int = 8,
            max_repairs: int = 2, seed: int | None = prompts.SEED, log=print) -> list[Outline]:
    """texts: documents; formats: one per document (format names or FormatAssignments) or a single one for all."""
    texts = list(texts)
    formats = list(formats) if isinstance(formats, (list, tuple)) else [formats] * len(texts)
    if len(formats) != len(texts):
        raise ValueError("formats must match texts")
    prov = provider if provider is not None and not isinstance(provider, str) else make_provider(provider or "gemini")
    out: list[Outline | None] = [None] * len(texts)
    todo = {}
    for i, (t, f) in enumerate(zip(texts, formats)):
        try:
            fmt = _format_of(f)
        except F.FormatError as e:
            out[i] = Outline([], None, meta={"error": str(e)}); continue
        todo[i] = prompts.extraction_prompt(t, fmt, few_shot, seed)
    # same-format prompts together: identical system prefixes in a row are what earn cached-input pricing
    order = sorted(todo, key=lambda i: todo[i].format)
    replies = runner.run(prov, {i: todo[i] for i in order}, mode, workers, log, "idealens_extract")
    usage = {i: [] for i in todo}
    pending = {}
    for i in order:
        r = replies[i] if i in replies else replies.get(str(i))
        pending[i] = r
    for attempt in range(max_repairs + 1):
        retry = {}
        for i, r in pending.items():
            usage[i].append(dict(r.usage or {}) | ({"cost_usd": r.cost_usd} if r.cost_usd else {}))
            p = todo[i]
            meta = {"provider": prov.name, "model": prov.model, "mode": mode if attempt == 0 else "online",
                    **p.meta(), "repairs": attempt, "finish": r.finish, "host": r.host}
            if r.text is None:
                out[i] = Outline([], p.format, meta=meta | {"error": r.error or "no reply"}); continue
            try:
                obj = parse.outline(r.text, p.format)
                out[i] = Outline(obj["items"], p.format, obj["document_description"], obj["global_themes"], meta)
            except parse.InvalidReply as e:
                if attempt == max_repairs:
                    out[i] = Outline([], p.format, meta=meta | {"error": f"invalid reply: {e}"})
                else:
                    p.extra_user += [r.text, REPAIR_INSTRUCTION.format(problem=e)]
                    retry[i] = p
        if not retry:
            break
        log(f"repairing {len(retry)} invalid repl{'y' if len(retry) == 1 else 'ies'} (attempt {attempt + 1})")
        pending = runner.run(prov, retry, "online", workers, log)
    for i in todo:
        tot = {}
        for u in usage[i]:
            for k, v in (u or {}).items():
                tot[k] = tot.get(k, 0) + (v or 0)
        out[i].meta["usage"] = tot
    return out
