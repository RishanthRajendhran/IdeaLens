"""Reading model replies: format labels, force-fit letters, and outline JSON (validated against the format's schema).

Structured output is requested wherever a provider offers it but never relied on, so every reply is checked here.
"""
from __future__ import annotations

import json
import re

from . import assets


class InvalidReply(ValueError):
    pass


def label(raw: str | None) -> str | None:
    """First-pass classifier reply -> WebOrganizer label (ideadet.format_classify.parse_llm_label)."""
    names = assets.classifier()["labels"]
    text = (raw or "").strip()
    for name in sorted(names, key=len, reverse=True):
        if name.lower() in text.lower():
            return name
    letter = text[:1].upper()
    if letter.isalpha() and 0 <= ord(letter) - 65 < len(names):
        return names[ord(letter) - 65]
    return None


def force_fit_label(raw: str | None) -> str | None:
    """Force-fit reply (a letter A-H) -> one of the eight formats."""
    names = assets.classifier()["force_fit_labels"]
    txt = (raw or "").strip()
    m = (re.fullmatch(r"\s*\**\s*([A-H])\**\s*\.?\s*", txt) or re.match(r"\s*\**\s*([A-H])[.)\s]", txt)
         or re.search(r"\b([A-H])\.\s", txt))
    if m:
        return names[ord(m.group(1)) - 65]
    for name in names:
        if name.lower() in txt.lower():
            return name
    return None


def _json_object(raw: str) -> dict:
    s = (raw or "").strip()
    s = re.sub(r"<think>.*?</think>", "", s, flags=re.S).strip()        # reasoning text some open models emit
    fence = re.search(r"```(?:json)?\s*(.*?)```", s, flags=re.S)
    if fence:
        s = fence.group(1).strip()
    if not s.startswith("{"):
        i, j = s.find("{"), s.rfind("}")
        if i < 0 or j <= i:
            raise InvalidReply("no JSON object in the reply")
        s = s[i:j + 1]
    try:
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        raise InvalidReply(f"reply is not valid JSON: {e}") from None
    if not isinstance(obj, dict):
        raise InvalidReply("reply is JSON but not an object")
    return obj


def outline(raw: str | None, fmt: str) -> dict:
    """Parse and validate an extraction reply. Returns the outline object; raises InvalidReply with a message that
    can be sent back to the model."""
    obj = _json_object(raw)
    roles = set(assets.extraction()["formats"][fmt]["role_names"])
    problems = []
    if not isinstance(obj.get("document_description"), str):
        problems.append("`document_description` must be a string")
    gt = obj.get("global_themes")
    if not (isinstance(gt, list) and all(isinstance(t, str) for t in gt)):
        problems.append("`global_themes` must be a list of strings")
    items = obj.get("items")
    if not isinstance(items, list) or not items:
        problems.append("`items` must be a non-empty list")
        items = []
    for n, it in enumerate(items, 1):
        if not isinstance(it, dict):
            problems.append(f"item {n} is not an object"); continue
        if it.get("role_name") not in roles:
            problems.append(f"item {n} has role_name {it.get('role_name')!r}, which is not one of the allowed roles")
        if not isinstance(it.get("content"), str) or not it.get("content", "").strip():
            problems.append(f"item {n} has no `content`")
        if not isinstance(it.get("verbatim"), bool):
            problems.append(f"item {n} needs a boolean `verbatim`")
    if problems:
        raise InvalidReply("; ".join(problems[:10]) + (f" (and {len(problems) - 10} more)" if len(problems) > 10 else ""))
    return {"document_description": obj["document_description"], "global_themes": obj["global_themes"],
            "items": [{"role_name": i["role_name"], "content": i["content"], "verbatim": i["verbatim"]} for i in items]}
