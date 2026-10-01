"""Outlines: the extractor's JSON, and the text a detector reads.

The scoring text is one `[Role] content` line per item, in order, joined by newlines -- the training rendering
(the WildOutlines training strings and the research code's ideadet.outlines.render) -- and must not change.
Roles-only models read one `[Role]` per line; per-item models read each `[Role] content` line on its own.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

_LINE = re.compile(r"^\[([^\[\]]*)\]\s?(.*)$")


@dataclass
class Outline:
    items: list[dict]                       # {"role_name": str, "content": str, "verbatim": bool}
    format: str | None = None
    document_description: str | None = None
    global_themes: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)  # extractor provenance, filled by idealens.extract

    @classmethod
    def from_json(cls, obj, format: str | None = None) -> "Outline":
        """From the extractor's JSON object (or its string form)."""
        if isinstance(obj, str):
            obj = json.loads(obj)
        items = obj.get("items") or (obj.get("data") or {}).get("items") or []
        return cls(items=[dict(i) for i in items], format=format or obj.get("format"),
                   document_description=obj.get("document_description"),
                   global_themes=list(obj.get("global_themes") or []), meta=dict(obj.get("meta") or {}))

    def render(self) -> str:
        return "\n".join(render_items(self.items))

    def to_dict(self) -> dict:
        return {"format": self.format, "document_description": self.document_description,
                "global_themes": self.global_themes, "items": self.items, "meta": self.meta}


def render_item(i: dict) -> str:
    return f"[{i.get('role_name', '')}] {(i.get('content') or '').strip()}"


def render_items(items) -> list[str]:
    """One `[Role] content` string per item."""
    return [render_item(i) for i in items]


def render_roles(items) -> str:
    """The role sequence, one `[Role]` per line (ideadet.outlines.render(..., "roles"))."""
    return "\n".join(f"[{i.get('role_name') or 'Other'}]" for i in items)


def parse_rendered(text: str) -> list[dict]:
    """Items from an already-rendered outline (`[Role] content` lines). A line that does not start with a role
    continues the previous item's content."""
    items = []
    for line in text.splitlines():
        m = _LINE.match(line.strip())
        if m:
            items.append({"role_name": m.group(1), "content": m.group(2)})
        elif items and line.strip():
            items[-1]["content"] += " " + line.strip()
    return items


def as_items(outline) -> list[dict]:
    """The item list of an Outline, an extractor JSON object/string, or a rendered outline string."""
    if isinstance(outline, Outline):
        return outline.items
    if isinstance(outline, dict):
        return Outline.from_json(outline).items
    if isinstance(outline, str):
        s = outline.strip()
        if s.startswith("{"):
            try:
                return Outline.from_json(s).items
            except (json.JSONDecodeError, AttributeError):
                pass
        return parse_rendered(outline)
    raise TypeError(f"cannot read an outline from {type(outline).__name__}")


def as_text(outline) -> str:
    """Scoring text (the full rendering) from any outline form. A rendered string is returned unchanged."""
    if isinstance(outline, str) and not outline.strip().startswith("{"):
        return outline
    return "\n".join(render_items(as_items(outline)))
