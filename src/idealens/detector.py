"""Detector: a released model, a backend, and a set of thresholds. Turns outlines (or documents, for the ProseLens
models) into P(human) and verdicts.

    det = Detector("IdeaLens")                          # vLLM, the model repo's published cuts
    r = det.score_outline(outline, format="News Article")
    r["p_human"], r["verdict"]["ai"], r["verdicts"]

What a model reads is fixed by how it was trained (registry.ModelSpec.input):
  outline   the whole outline, one "[Role] content" line per item
  roles     the role labels only, one "[Role]" per line
  items     each item on its own ("[Role] content"), pooled to the document by the mean of the item log-odds
  document  the document text
"""
from __future__ import annotations

import math

import numpy as np

from . import formats as F
from . import registry
from .backends import make as make_backend
from .outline import Outline, as_items, render_items, render_roles
from .thresholds import DEFAULT_FPR, DEFAULT_SCHEME, Thresholds


def _p_human(lh: float, la: float) -> float:
    m = max(lh, la)
    return math.exp(lh - m) / (math.exp(lh - m) + math.exp(la - m))


def pool_logit_mean(ps) -> float:
    """ideadet.outlines.pool_item_scores(method="logit_mean"): the mean of the clipped item log-odds."""
    p = np.clip(np.asarray(ps, dtype=float), 1e-6, 1 - 1e-6)
    return float(1.0 / (1.0 + np.exp(-np.log(p / (1 - p)).mean())))


class Detector:
    def __init__(self, model: str = registry.DEFAULT_MODEL, backend: str | None = None,
                 thresholds: str | Thresholds | None = None, fpr: float = DEFAULT_FPR, scheme: str = DEFAULT_SCHEME,
                 weights: str | None = None, **backend_kwargs):
        self.spec = registry.get(model)
        backend = backend or self.spec.backends[0]
        if isinstance(backend, str) and backend not in self.spec.backends:
            raise ValueError(f"{model} supports backends {self.spec.backends}, not {backend!r}")
        if isinstance(thresholds, Thresholds):
            self.thresholds = thresholds
        elif thresholds:
            self.thresholds = Thresholds.load(thresholds)
        else:
            self.thresholds = Thresholds.for_model(self.spec)
        self.thresholds.check(self.spec.name, {})  # model mismatch raises before any weights load
        self.fpr, self.scheme = fpr, scheme
        # a backend name, or an object with .name, .encode(text) and .score_ids(list of encoded inputs)
        self.backend = (make_backend(backend, self.spec, weights=weights, **backend_kwargs)
                        if isinstance(backend, str) else backend)

    def close(self):
        """Release the backend (shuts vLLM's engine process down)."""
        if hasattr(self.backend, "close"):
            self.backend.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # ------------------------------------------------------------------ scoring
    def score_outline(self, outline, **kw) -> dict:
        return self.score_outlines([outline], **{k: [v] if k in _PER_ITEM else v for k, v in kw.items()})[0]

    def score_document(self, text: str, **kw) -> dict:
        return self.score_documents([text], **{k: [v] if k in _PER_ITEM else v for k, v in kw.items()})[0]

    def score_outlines(self, outlines, format=None, topic=None, groups=None, ids=None, forced_format=None) -> list[dict]:
        """Score outlines (Outline objects, extractor JSON, or rendered `[Role] content` strings).

        format/topic/groups/ids/forced_format: one value per outline (lists), or a single value for all. A format
        given here overrides the outline's own; either is validated against the eight formats.
        """
        if self.spec.input == "document":
            raise ValueError(f"{self.spec.name} reads documents; use score_documents")
        items = [as_items(o) for o in outlines]
        if self.spec.input == "items":
            units = [render_items(it) for it in items]
        elif self.spec.input == "roles":
            units = [[render_roles(it)] if it else [] for it in items]
        else:  # a rendered outline string is scored exactly as given
            units = [([o] if isinstance(o, str) and not o.strip().startswith("{") and o.strip() else
                      ["\n".join(render_items(it))] if it else []) for o, it in zip(outlines, items)]
        own = [o.format if isinstance(o, Outline) else (o.get("format") if isinstance(o, dict) else None)
               for o in outlines]
        metas = [o.meta if isinstance(o, Outline) else (o.get("meta") if isinstance(o, dict) else None) or {}
                 for o in outlines]
        fmts = _broadcast(format, len(units))
        fmts = [f if f is not None else o for f, o in zip(fmts, own)]
        return self._score(units, fmts, topic, groups, ids, forced_format, metas)

    def score_documents(self, texts, format=None, topic=None, groups=None, ids=None) -> list[dict]:
        if self.spec.input != "document":
            raise ValueError(f"{self.spec.name} reads outlines; use score_outlines (or idealens.run for documents)")
        units = [[t] if t and t.strip() else [] for t in texts]
        return self._score(units, _broadcast(format, len(units)), topic, groups, ids, None, None)

    # ------------------------------------------------------------------ internals
    def _score(self, units, fmts, topic, groups, ids, forced, metas) -> list[dict]:
        n = len(units)
        topics, groups_, ids_, forced_ = (_broadcast(topic, n), _broadcast(groups, n), _broadcast(ids, n),
                                          _broadcast(forced, n))
        metas = metas or [{}] * n
        assigned = [_assignment(f, bool(fz)) for f, fz in zip(fmts, forced_)]
        enc = [[self.backend.encode(u) for u in us] for us in units]
        flat = [e for es in enc for e in es]
        lp = np.asarray(self.backend.score_ids(flat), dtype=float) if flat else np.zeros((0, 2))
        max_in = getattr(self.backend, "max_input_tokens", None)
        tokens = lambda e: len(e) if isinstance(e, (list, tuple)) else None
        out, k = [], 0
        for i in range(n):
            a, rows = assigned[i], lp[k:k + len(enc[i])]
            k += len(enc[i])
            toks = [tokens(e) for e in enc[i]]
            rec = {"id": ids_[i], "model": self.spec.name, "backend": self.backend.name,
                   "input_tokens": sum(toks) if toks and None not in toks else None}
            if a is not None:
                rec.update(a.to_dict())
            if metas[i]:
                rec["outline_meta"] = metas[i]
            if not enc[i]:  # failed extraction, or an empty input: nothing to score
                rec |= {"p_human": None, "verdict": None, "verdicts": None,
                        "error": metas[i].get("error") or "empty input", "warnings": []}
                out.append(rec); continue
            warnings = []
            longest = max((t for t in toks if t is not None), default=0)
            if max_in and longest > max_in:
                warnings.append(f"input is {longest:,} tokens; {self.spec.name} reads the first {max_in:,}, as in "
                                f"training")
            elif self.spec.max_train_tokens and longest > self.spec.max_train_tokens:
                warnings.append(f"input is {longest:,} tokens; the longest {self.spec.name} training input was "
                                f"about {self.spec.max_train_tokens:,}, so this score is outside the validated range")
            run = {"backend": self.backend.name, "format_method": a.method if a else None,
                   "extractor_provider": metas[i].get("provider"), "extractor_model": metas[i].get("model"),
                   "few_shot": metas[i].get("few_shot")}
            warnings += self.thresholds.check(self.spec.name, run)
            if np.isnan(rows).any():
                rec |= {"p_human": None, "verdict": None, "verdicts": None, "warnings": warnings,
                        "error": "input too long for this backend's memory or context limit"}
                out.append(rec); continue
            if self.spec.input == "items":
                item_p = [_p_human(*r) for r in rows]
                p = pool_logit_mean(item_p)
                rec |= {"item_p_human": item_p, "pooling": "logit_mean"}
            else:
                p = _p_human(*rows[0])
                rec |= {"logit_human": float(rows[0][0]), "logit_ai": float(rows[0][1])}
            fmt, frc = (a.format, a.forced) if a else (None, False)
            rec |= {"p_human": p,
                    "verdict": self.thresholds.verdict(p, self.fpr, self.scheme, fmt, topics[i], groups_[i], frc),
                    "verdicts": self.thresholds.verdicts(p, fmt, topics[i], groups_[i], frc),
                    "warnings": warnings}
            out.append(rec)
        return out


_PER_ITEM = ("format", "topic", "groups", "ids", "forced_format")


def _broadcast(v, n):
    if isinstance(v, (list, tuple)):
        if len(v) != n:
            raise ValueError(f"expected {n} values, got {len(v)}")
        return list(v)
    return [v] * n


def _assignment(f, forced: bool):
    if f is None:
        return None
    if isinstance(f, F.FormatAssignment):
        return f
    a = F.user_format(f)
    return F.FormatAssignment(a.format, a.method, forced, a.original) if forced else a
