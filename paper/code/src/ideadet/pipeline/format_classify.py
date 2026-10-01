"""Stage 0: assign each document a WebOrganizer format.

The extraction prompt is format-conditioned, so this is not optional and its
label must never be asserted from what a corpus "obviously" contains. Nine of
WebOrganizer's 24 categories map onto a role vocabulary we possess; documents in
the other fifteen are out of scope and are **filtered, not remapped**.

TWO BACKENDS, AND WHEN EACH IS RIGHT
------------------------------------
`encoder` — WebOrganizer's released FormatClassifier. Free, fast, and the label
source the taxonomy was defined by. Use it on English web text.

`llm` — `gemini-3.7-flash` zero-shot over WebOrganizer's *own* annotation
config: the same system message and 24 category definitions that were given to
the large model whose labels their encoder was distilled from. Use it when the
encoder is not trustworthy on the corpus at hand. That is not hypothetical: on
one corpus the released encoder called 8,030 novel excerpts "News Article" and
1,829 news articles "Structured Data" at median confidence around 0.2. That is a
classifier failing, not a bias to correct for. It is also the only option
off-English, where the encoder is unusable.

Zero-shot is deliberate for the LLM backend: a pilot showed the five
demonstrations do not change the labels, and they restate the 1,297-token
taxonomy five more times.

A NOTE ON URLS
--------------
WebOrganizer's prompt takes a URL as well as the text. Corpora without one need
the NoURL variant of the encoder; passing an empty URL to the URL-conditioned
model degrades it.
"""
from __future__ import annotations

from typing import Callable, Iterable

from .. import formats as F
from .. import prompts as P

ENCODER_MODEL = "WebOrganizer/FormatClassifier"
ENCODER_MODEL_NOURL = "WebOrganizer/FormatClassifier-NoURL"


def _taxonomy() -> dict:
    """WebOrganizer's annotation config: system template and 24 definitions."""
    import yaml
    return yaml.safe_load(P.read("format_classification", "weborganizer_formats.yaml"))


def llm_prompt(text: str, url: str = "", max_chars: int = 0) -> tuple[str, str]:
    """(system, user) for the LLM backend, built from the released config."""
    y = _taxonomy()
    choices = "\n".join(f"{chr(65 + i)}. {c}" for i, c in enumerate(y["choices"]))
    system = y["system_template"].replace("{choices}", choices)
    doc_only = y["template"].split("Your task is to classify", 1)[0]
    user = doc_only.replace("{url}", url).replace("{text}", text[:max_chars] if max_chars else text)
    return system, user


def parse_llm_label(raw: str) -> str | None:
    """Turn the model's answer into a WebOrganizer label, or None if unusable."""
    y = _taxonomy()
    names = [c.split("\n")[0].strip() for c in y["choices"]]
    text = (raw or "").strip()
    for name in sorted(names, key=len, reverse=True):
        if name.lower() in text.lower():
            return name
    letter = text[:1].upper()
    if letter.isalpha() and 0 <= ord(letter) - 65 < len(names):
        return names[ord(letter) - 65]
    return None


def to_our_format(weborganizer_label: str) -> str | None:
    """Map a WebOrganizer label to our format, or None when out of scope."""
    return F.WEBORGANIZER_TO_FORMAT.get(weborganizer_label)


def classify_encoder(texts: list[str], urls: list[str] | None = None, *,
                     device: str = "cuda", batch_size: int = 16,
                     max_length: int = 8192, use_url: bool = True,
                     log: Callable[[str], None] = print) -> list[dict]:
    """Run the released encoder. Returns the FULL distribution, not just argmax.

    Keeping the distribution is what lets a downstream step judge whether the
    classifier was confident enough to trust on a new corpus, which matters most
    exactly where the encoder is least reliable.
    """
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    model_id = ENCODER_MODEL if use_url else ENCODER_MODEL_NOURL
    log(f"  format encoder: {model_id} on {len(texts):,} documents")
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForSequenceClassification.from_pretrained(
        model_id, trust_remote_code=True,
        # The memory-efficient attention path in this checkpoint is built against
        # a different torch than we run; the plain path works on both devices and
        # the model is small enough that the difference does not matter.
        use_memory_efficient_attention=False, unpad_inputs=False)
    # The released checkpoint registers `position_ids` with persistent=False, so
    # it is absent from the weights and loads as UNINITIALISED memory: garbage
    # indices into the rotary table and an IndexError on the first forward.
    emb = mdl.new.embeddings
    emb.position_ids.copy_(torch.arange(emb.position_ids.size(0)))
    assert bool((emb.position_ids.diff() == 1).all()), "position_ids still not monotonic"
    mdl.to(device).eval()

    labels = [mdl.config.id2label[i] for i in range(len(mdl.config.id2label))]
    inputs = ([f"{u}\n\n{t}" for u, t in zip(urls, texts)]
              if (use_url and urls) else list(texts))

    out = []
    with torch.no_grad():
        for i in range(0, len(inputs), batch_size):
            enc = tok(inputs[i:i + batch_size], return_tensors="pt", padding=True,
                      truncation=True, max_length=max_length).to(device)
            probs = mdl(**enc).logits.softmax(-1).float().cpu().numpy()
            for row in probs:
                j = int(row.argmax())
                out.append({"weborganizer_label": labels[j],
                            "confidence": float(row[j]),
                            "distribution": {labels[k]: round(float(v), 5)
                                             for k, v in enumerate(row)},
                            "format": to_our_format(labels[j]),
                            "backend": model_id})
    return out


def build_llm_requests(rows: Iterable[dict], *, model: str, max_chars: int = 0,
                       max_output_tokens: int = 1024) -> list[dict]:
    """Vertex batch rows for the LLM backend.

    Callers should sort `rows` by any slice field they have first: the system
    prefix is identical across rows and only earns the cached-input discount when
    identical prefixes sit consecutively. On one corpus that ordering took the
    job from about $51 to about $11.
    """
    from ..llm import vertex_batch as VB
    reqs = []
    for r in rows:
        system, user = llm_prompt(r["text"], r.get("url", ""), max_chars)
        reqs.append(VB.build_request(r["id"], user, system=system,
                                     max_output_tokens=max_output_tokens,
                                     schema=None, seed=P.PIPELINE_SEED))
    return reqs


def summarize(results: list[dict]) -> str:
    """Keep rate and confidence per label — read this before spending on extraction."""
    import collections
    counts = collections.Counter(r.get("weborganizer_label") for r in results)
    kept = sum(1 for r in results if r.get("format"))
    lines = [f"{len(results):,} classified, {kept:,} in scope "
             f"({kept / max(len(results), 1) * 100:.1f}%)",
             f"  {'label':<28}{'n':>7}{'kept as':<24}{'median conf':>12}"]
    for label, n in counts.most_common():
        conf = sorted(r["confidence"] for r in results
                      if r.get("weborganizer_label") == label and "confidence" in r)
        med = f"{conf[len(conf) // 2]:.3f}" if conf else "n/a"
        lines.append(f"  {str(label):<28}{n:>7}{str(to_our_format(label) or '— dropped'):<24}{med:>12}")
    return "\n".join(lines)
