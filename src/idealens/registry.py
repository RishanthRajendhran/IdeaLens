"""The released detectors and the exact input contract each was trained with.

Scoring reproduces training only if the prompt text, suffix, label tokens and outline rendering match exactly, so
they live here, in one place, and nothing else builds a prompt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

NEMOTRON_BASE = "nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16"
NEMOTRON_SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
NEMOTRON_LABEL_TOKENS = {"human": 50755, "ai": 2464}
SYSTEM_OUTLINE = ("Given a role-labelled outline of a document, answer with one word: human if the source document was "
                  "human-written, ai if it was AI-generated.")
SYSTEM_DOCUMENT = ("Given a document, answer with one word: human if the document was human-written, ai if it was "
                   "AI-generated.")

#: Longest inputs seen in training, in tokens (WildOutlines train split: documents up to 17,471 words, about 23,000
#: tokens; outlines under about 3,800 tokens). Longer inputs run but their scores are unvalidated.
MAX_TRAIN_TOKENS_DOCUMENT = 23_300
MAX_TRAIN_TOKENS_OUTLINE = 3_800


@dataclass(frozen=True)
class ModelSpec:
    name: str
    repo: str
    family: str                  # "nemotron" | "qwen" | "modernbert" | "logistic"
    input: str                   # "outline" | "document" | "roles" | "items"
    backends: tuple = ()
    system: str | None = None    # nemotron chat contract
    max_train_tokens: int | None = None
    implemented: bool = False
    notes: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def needs_outline(self) -> bool:
        return self.input in ("outline", "roles", "items")

    @property
    def base_model(self) -> str | None:
        return NEMOTRON_BASE if self.family == "nemotron" else None


SYSTEM_ITEM = ("Given a single role-labelled item from a document's outline, answer with one word: human if the source "
               "document was human-written, ai if it was AI-generated.")
_NEMO = ("vllm", "hf", "tinker")
#: Checkpoints published on Tinker (public since 2026-10-02): any Tinker account can score with them, billed to that
#: account. IdeaLens-NoParaphrase is not published; its Tinker backend needs weights="tinker://...".
TINKER_PUBLIC = {"IdeaLens": "tinker://9f500a21-df39-5716-89e5-e65f9390fb14:train:0/sampler_weights/nemo_full_v1m_r64_ep1_final",
                 "ProseLens": "tinker://f21bf499-021e-5735-85f5-f5e1183aad78:train:0/sampler_weights/nemo_docs_v1m_docs_r64_ep1_final"}
_U = "rishanthrajendhran/"


def _m(name, family, input, backends, system=None, max_train=None, canon=None, **extra):
    return ModelSpec(name, _U + name, family, input, backends, system, max_train, implemented=True,
                     extra={"canonical_thresholds": canon, **extra})


# canonical_thresholds: the entry in the project's calibration file (outputs/calibration/thresholds.json) that each repo's
# thresholds.json is built from (None: never calibrated on the 80,000-human calibration split).
MODELS: dict[str, ModelSpec] = {m.name: m for m in (
    _m("IdeaLens", "nemotron", "outline", _NEMO, SYSTEM_OUTLINE, MAX_TRAIN_TOKENS_OUTLINE, "nemotron_1m_full",
       tinker_path=TINKER_PUBLIC["IdeaLens"]),
    _m("ProseLens", "nemotron", "document", _NEMO, SYSTEM_DOCUMENT, MAX_TRAIN_TOKENS_DOCUMENT,
       "nemotron_1m_docs_on_document", tinker_path=TINKER_PUBLIC["ProseLens"]),
    _m("IdeaLens-NoParaphrase", "nemotron", "outline", _NEMO, SYSTEM_OUTLINE, MAX_TRAIN_TOKENS_OUTLINE,
       "nemotron_1m_rawout"),
    _m("IdeaLens-Qwen3.5-9B", "qwen", "outline", ("hf",), SYSTEM_OUTLINE, None, "qwen_1m_full"),
    _m("IdeaLens-Qwen3.5-9B-PerItem", "qwen", "items", ("hf",), SYSTEM_ITEM, None, "qwen_1m_items"),
    _m("IdeaLens-ModernBERT-L", "modernbert", "outline", ("hf",), None, None, "modernbert_1m_full"),
    _m("IdeaLens-ModernBERT-L-NoParaphrase", "modernbert", "outline", ("hf",), None, None, "modernbert_1m_rawout"),
    _m("IdeaLens-ModernBERT-L-RolesOnly", "modernbert", "roles", ("hf",), None, None, "modernbert_1m_roles"),
    _m("IdeaLens-ModernBERT-L-PerItem", "modernbert", "items", ("hf",), None, None, "modernbert_1m_items"),
    _m("ProseLens-ModernBERT-L", "modernbert", "document", ("hf",), None, None, "modernbert_1m_docs_on_document"),
    _m("IdeaLens-LogisticClassifier", "logistic", "outline", ("logistic",), None, None, "logistic_1m_full"),
    _m("IdeaLens-LogisticClassifier-PerItem", "logistic", "items", ("logistic",), None, None, "logistic_1m_items"),
)}

DEFAULT_MODEL = "IdeaLens"


class ModelNotAvailable(NotImplementedError):
    pass


def get(name: str) -> ModelSpec:
    try:
        spec = MODELS[name]
    except KeyError:
        raise KeyError(f"unknown model {name!r}. Available: {', '.join(MODELS)}") from None
    if not spec.implemented:
        raise ModelNotAvailable(f"{name} is not supported in this version of idealens yet "
                                f"(its weights are released at {spec.repo} when public).")
    return spec
