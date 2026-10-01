"""The detector interface every backend implements.

One interface means `scripts/eval/score.py` is written once and works for the
Tinker-hosted Nemotron LoRA, a local ModernBERT, a local Qwen, the logistic
embedding baseline, and the Pangram surface baseline. Adding an arm is adding a
subclass and a `configs/models.yaml` entry, never a new scoring script.

Every backend returns P(HUMAN) and, wherever the backend exposes them, the raw
logits. Probabilities are lossy summaries; re-scoring is expensive.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np


@dataclass
class ScoreBatch:
    """One backend's output for a list of inputs, aligned row for row."""
    ids: list[str]
    p_human: np.ndarray
    logits: np.ndarray | None = None
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        self.p_human = np.asarray(self.p_human, dtype=np.float64)
        if len(self.ids) != len(self.p_human):
            raise ValueError(f"{len(self.ids)} ids but {len(self.p_human)} scores")
        if self.logits is not None:
            self.logits = np.asarray(self.logits, dtype=np.float32)

    def as_dict(self) -> dict[str, float]:
        return dict(zip(self.ids, self.p_human.tolist()))


class Detector:
    """Base class. Subclasses implement `score_texts`.

    `setting` selects which rendering of a document the arm consumes and MUST
    match what the checkpoint was trained on: a `full` checkpoint fed `items`
    input produces confident nonsense, not an error.
    """

    #: Whether this backend returns pre-softmax logits.
    exposes_logits = False

    def __init__(self, model_id: str, setting: str = "full", **kwargs):
        self.model_id = model_id
        self.setting = setting
        self.kwargs = kwargs

    def score_texts(self, ids: list[str], texts: list[str]) -> ScoreBatch:
        raise NotImplementedError

    # -- convenience wrappers shared by every backend -----------------------
    def score_outlines(self, records: Iterable[tuple[str, dict]]) -> ScoreBatch:
        """Score (id, outline record) pairs, rendering per this arm's setting."""
        from ..outlines import render
        ids, texts = [], []
        for doc_id, outline in records:
            ids.append(str(doc_id))
            texts.append(render(outline, self.setting))
        return self.score_texts(ids, texts)

    def score_items(self, records: Iterable[tuple[str, dict]],
                    pooling: str = "logit_mean") -> tuple[ScoreBatch, ScoreBatch]:
        """Item-level arm: score every item, then pool to one score per document.

        Returns (document-level batch, item-level batch). The item-level batch is
        kept because item scores are what the mixture analyses and the per-item
        attribution figures are built from.
        """
        from ..outlines import pool_item_scores, render_items
        item_ids, item_texts, owner = [], [], []
        for doc_id, outline in records:
            for i, text in enumerate(render_items(outline)):
                item_ids.append(f"{doc_id}#{i}")
                item_texts.append(text)
                owner.append(str(doc_id))
        items = self.score_texts(item_ids, item_texts)

        by_doc: dict[str, list[float]] = {}
        for o, p in zip(owner, items.p_human):
            by_doc.setdefault(o, []).append(float(p))
        doc_ids = list(by_doc)
        pooled = [pool_item_scores(by_doc[d], pooling) for d in doc_ids]
        items.meta["owner"] = owner
        return (ScoreBatch(doc_ids, np.asarray(pooled),
                           meta={"pooling": pooling, "model_id": self.model_id}),
                items)

    def close(self):
        """Release GPU memory or a network session. Safe to call twice."""


def load(model_id: str, **overrides) -> Detector:
    """Build the detector named in `configs/models.yaml`.

    Imports the backend lazily so that scoring a ModernBERT arm does not require
    the Tinker SDK, and vice versa.
    """
    from ..registry import get_model
    run = get_model(model_id)
    cfg = {**run.raw, **overrides}
    # `setting` and `backend` are consumed here, not forwarded: every backend
    # takes `setting` positionally, so leaving it in cfg passes it twice.
    backend = cfg.pop("backend", run.backend)
    setting = cfg.pop("setting", run.setting)

    if backend == "nemotron_tinker":
        from .nemotron_tinker import TinkerDetector
        return TinkerDetector(model_id, setting, **cfg)
    if backend == "hf_encoder":
        from .hf_encoder import EncoderDetector
        return EncoderDetector(model_id, setting, **cfg)
    if backend == "qwen_local":
        from .qwen_local import QwenDetector
        return QwenDetector(model_id, setting, **cfg)
    if backend == "logistic":
        from .logistic import LogisticDetector
        return LogisticDetector(model_id, setting, **cfg)
    if backend == "pangram":
        from .pangram_detector import PangramDetector
        return PangramDetector(model_id, setting, **cfg)
    raise ValueError(
        f"unknown backend {backend!r} for model {model_id!r}. Implement it in "
        f"src/ideadet/detectors/ and register it in detectors/base.py::load.")
