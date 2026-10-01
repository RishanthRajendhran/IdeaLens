"""Format classification: which of the eight trained formats a document is.

method="llm" (default): WebOrganizer's own annotation prompt (24 labels) on an LLM, gemini-3.7-flash by default.
method="weborganizer": WebOrganizer's FormatClassifier encoder (FormatClassifier-NoURL when no URL is given). Runs
locally, CPU is fine; needs transformers and torch.

Force-fitting (force_fit=True, the default): a document whose label is outside the eight is assigned the closest of
them, and marked forced=True with its original label. With the LLM that is a second call listing only the eight;
with WebOrganizer it is the most probable of the eight labels, with no extra call. Forced documents get the global
cut only; their per-format verdicts are left empty. With force_fit=False they come back with format=None.
"""
from __future__ import annotations

from . import formats as F
from . import parse, prompts, runner
from .providers import make as make_provider

WEBORGANIZER = "WebOrganizer/FormatClassifier"
WEBORGANIZER_NOURL = "WebOrganizer/FormatClassifier-NoURL"


def classify(texts, urls=None, method: str = "llm", force_fit: bool = True, provider=None, mode: str = "online",
             workers: int = 8, device: str = "cpu", batch_size: int = 16, log=print) -> list[F.FormatAssignment]:
    texts = list(texts)
    urls = list(urls) if urls is not None else [""] * len(texts)
    if len(urls) != len(texts):
        raise ValueError("urls must match texts")
    if method == "llm":
        return _llm(texts, urls, force_fit, provider, mode, workers, log)
    if method == "weborganizer":
        return _encoder(texts, urls, force_fit, device, batch_size, log)
    raise ValueError("method must be 'llm' or 'weborganizer'")


def _llm(texts, urls, force_fit, provider, mode, workers, log):
    prov = provider if provider is not None and not isinstance(provider, str) else make_provider(provider or "gemini")
    first = runner.run(prov, {i: prompts.classification_prompt(t, u) for i, (t, u) in enumerate(zip(texts, urls))},
                       mode, workers, log, "idealens_classify")
    out, need_force = [None] * len(texts), {}
    for i in range(len(texts)):
        r = first[i] if i in first else first.get(str(i))
        meta = {"provider": prov.name, "model": prov.model, "usage": r.usage, "raw": (r.text or "")[:200]}
        if r.text is None:
            out[i] = F.FormatAssignment(None, "llm", error=r.error or "no reply", meta=meta); continue
        lab = parse.label(r.text)
        if lab is None:
            out[i] = F.FormatAssignment(None, "llm", error="unreadable classifier reply", meta=meta); continue
        fmt = F.WEBORGANIZER_TO_FORMAT.get(lab)
        if fmt:
            out[i] = F.FormatAssignment(fmt, "llm", original=None if lab == fmt else lab, meta=meta)
        elif force_fit:
            need_force[i] = (lab, meta)
        else:
            out[i] = F.FormatAssignment(None, "llm", original=lab, error="out_of_scope", meta=meta)
    if need_force:
        second = runner.run(prov, {i: prompts.force_fit_prompt(texts[i], urls[i]) for i in need_force}, mode, workers,
                            log, "idealens_force_fit")
        for i, (lab, meta) in need_force.items():
            r = second[i] if i in second else second.get(str(i))
            meta = meta | {"force_fit_usage": r.usage, "force_fit_raw": (r.text or "")[:200]}
            fmt = parse.force_fit_label(r.text) if r.text else None
            out[i] = (F.FormatAssignment(fmt, "llm", forced=True, original=lab, meta=meta) if fmt else
                      F.FormatAssignment(None, "llm", original=lab, error=r.error or "unreadable force-fit reply",
                                         meta=meta))
    return out


def _repair_buffers(mdl):
    """Recompute the encoder's non-persistent buffers. They are not in the checkpoint, and transformers 5 builds the
    model on the meta device before loading weights, so they come back uninitialised: position_ids, and the rotary
    embedding's inv_freq and cos/sin caches. Without this the classifier runs but returns near-constant labels (8% and
    15% agreement with WebOrganizer's own labels on WildOutlines test documents, against 99% and 74% under
    transformers 4.57). Recomputed exactly as the model's __init__ does, including the NTK-scaled cache."""
    import torch
    emb = mdl.new.embeddings
    emb.position_ids = torch.arange(emb.position_ids.size(0), device=emb.position_ids.device)
    for m in mdl.modules():
        if hasattr(m, "_set_cos_sin_cache") and hasattr(m, "inv_freq"):
            m.inv_freq = 1.0 / (m.base ** (torch.arange(0, m.dim, 2).float() / m.dim))
            seq = m.max_position_embeddings * getattr(m, "scaling_factor", 1) if hasattr(m, "scaling_factor") \
                else m.max_position_embeddings
            m._set_cos_sin_cache(seq, m.inv_freq.device, torch.float32)


def _encoder(texts, urls, force_fit, device, batch_size, log, max_length: int = 8192):
    """WebOrganizer's encoder (ideadet.pipeline.format_classify.classify_encoder), returning the full distribution."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    use_url = any(u for u in urls)
    model_id = WEBORGANIZER if use_url else WEBORGANIZER_NOURL
    log(f"format classifier: {model_id} on {len(texts):,} documents ({device})")
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForSequenceClassification.from_pretrained(
        model_id, trust_remote_code=True, use_memory_efficient_attention=False, unpad_inputs=False)
    _repair_buffers(mdl)
    mdl.to(device).eval()
    labels = [mdl.config.id2label[i] for i in range(len(mdl.config.id2label))]
    inputs = [f"{u}\n\n{t}" for u, t in zip(urls, texts)] if use_url else list(texts)
    in_scope = [j for j, l in enumerate(labels) if l in F.WEBORGANIZER_TO_FORMAT]
    out = []
    with torch.no_grad():
        for s in range(0, len(inputs), batch_size):
            enc = tok(inputs[s:s + batch_size], return_tensors="pt", padding=True, truncation=True,
                      max_length=max_length).to(device)
            for row in mdl(**enc).logits.softmax(-1).float().cpu().numpy():
                dist = {labels[k]: round(float(v), 5) for k, v in enumerate(row)}
                top = labels[int(row.argmax())]
                meta = {"model": model_id, "confidence": float(row.max())}
                fmt = F.WEBORGANIZER_TO_FORMAT.get(top)
                if fmt:
                    out.append(F.FormatAssignment(fmt, "weborganizer", original=None if top == fmt else top,
                                                  probabilities=dist, meta=meta))
                elif force_fit:
                    best = labels[max(in_scope, key=lambda k: row[k])]
                    out.append(F.FormatAssignment(F.WEBORGANIZER_TO_FORMAT[best], "weborganizer", forced=True,
                                                  original=top, probabilities=dist, meta=meta))
                else:
                    out.append(F.FormatAssignment(None, "weborganizer", original=top, probabilities=dist,
                                                  error="out_of_scope", meta=meta))
    return out


def force_fit(texts, urls=None, labels=None, method: str = "llm", provider=None, mode: str = "online",
              workers: int = 8, device: str = "cpu", batch_size: int = 16, log=print) -> list[F.FormatAssignment]:
    """Assign the closest of the eight formats to documents already known to be outside them (e.g. a user-given
    'Product Page' with force_fit requested). labels: the out-of-scope label of each document, recorded as original."""
    texts = list(texts)
    urls = list(urls) if urls is not None else [""] * len(texts)
    labels = list(labels) if labels is not None else [None] * len(texts)
    if method == "weborganizer":
        res = _encoder(texts, urls, True, device, batch_size, log)  # always one of the eight when force-fitting
        return [F.FormatAssignment(r.format, "weborganizer", forced=True, original=lab, probabilities=r.probabilities,
                                   meta=r.meta) for r, lab in zip(res, labels)]
    prov = provider if provider is not None and not isinstance(provider, str) else make_provider(provider or "gemini")
    rep = runner.run(prov, {i: prompts.force_fit_prompt(t, u) for i, (t, u) in enumerate(zip(texts, urls))},
                     mode, workers, log, "idealens_force_fit")
    out = []
    for i, lab in enumerate(labels):
        r = rep[i] if i in rep else rep.get(str(i))
        meta = {"provider": prov.name, "model": prov.model, "force_fit_usage": r.usage,
                "force_fit_raw": (r.text or "")[:200]}
        fmt = parse.force_fit_label(r.text) if r.text else None
        out.append(F.FormatAssignment(fmt, "llm", forced=True, original=lab, meta=meta) if fmt else
                   F.FormatAssignment(None, "llm", original=lab, error=r.error or "unreadable force-fit reply",
                                      meta=meta))
    return out
