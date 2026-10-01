"""The whole pipeline for a set of documents: format -> outline -> score.

Formats: a document's own format (given by the caller) is used as is. Documents without one are classified. A
given format outside the eight is an error unless force_fit=True, which assigns the closest of the eight and marks the
document forced. check_format=True also classifies documents that came with a format and reports disagreements
(record["format_check"]) without changing the format used.

ProseLens reads the text itself: no extraction, and classification only when per-format verdicts are wanted
(want_format=True) and no format was given.
"""
from __future__ import annotations

from .classify import classify as _classify, force_fit as _force_fit
from . import formats as F
from .extract import extract


def resolve_formats(texts, given, urls=None, classify_method="llm", force_fit=False, check_format=False,
                    provider=None, mode="online", workers=8, log=print, need=True):
    """One FormatAssignment (or None when not needed) per document, plus format_check results."""
    n = len(texts)
    urls = list(urls) if urls is not None else [""] * n
    out, to_classify, to_force, checks = [None] * n, [], [], {}
    for i, g in enumerate(given):
        if g in (None, ""):
            if need:
                to_classify.append(i)
            continue
        try:
            out[i] = F.user_format(g)
        except F.OutOfScopeFormat as e:
            if not force_fit:
                out[i] = F.FormatAssignment(None, "user", original=e.label, error="out_of_scope (use force_fit)")
            else:
                to_force.append((i, e.label))
        # FormatError (unknown value) propagates: a typo should stop the run, not be skipped silently
    kw = dict(provider=provider, mode=mode, workers=workers, log=log)
    if to_classify:
        res = _classify([texts[i] for i in to_classify], [urls[i] for i in to_classify], classify_method,
                         force_fit=True, **kw)
        for i, r in zip(to_classify, res):
            out[i] = r
    if to_force:
        res = _force_fit([texts[i] for i, _ in to_force], [urls[i] for i, _ in to_force],
                          [lab for _, lab in to_force], classify_method, **kw)
        for (i, _), r in zip(to_force, res):
            out[i] = r
    if check_format:
        idx = [i for i in range(n) if out[i] is not None and out[i].method == "user" and out[i].format]
        if idx:
            res = _classify([texts[i] for i in idx], [urls[i] for i in idx], classify_method, force_fit=False, **kw)
            for i, r in zip(idx, res):
                checks[i] = {"classifier_format": r.format, "classifier_label": r.original or r.format,
                             "agrees": r.format == out[i].format}
    return out, checks


def run(texts, detector, formats=None, urls=None, ids=None, topics=None, groups=None, classify_method="llm",
        force_fit=False, check_format=False, provider=None, mode="online", few_shot=True, workers=8, log=print):
    """Score documents end to end. Returns one record per document (the Detector's record, plus the outline)."""
    texts = list(texts)
    n = len(texts)
    given = list(formats) if isinstance(formats, (list, tuple)) else [formats] * n
    doc_model = detector.spec.input == "document"
    fmts, checks = resolve_formats(texts, given, urls, classify_method, force_fit, check_format, provider, mode,
                                   workers, log, need=not doc_model)
    if doc_model:
        recs = detector.score_documents(texts, format=fmts, topic=topics, groups=groups, ids=ids)
    else:
        outlines = extract(texts, [f if f is not None else None for f in fmts], provider=provider,
                           few_shot=few_shot, mode=mode, workers=workers, log=log)
        recs = detector.score_outlines(outlines, format=fmts, topic=topics, groups=groups, ids=ids,
                                       forced_format=[bool(f and f.forced) for f in fmts])
        for r, o in zip(recs, outlines):
            r["outline"] = o.to_dict()
    for i, c in checks.items():
        recs[i]["format_check"] = c
    return recs
