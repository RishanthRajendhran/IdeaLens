"""Local encoder classifiers: ModernBERT-large (primary) and mmBERT (multilingual).

A plain sequence-classification head over the rendered outline. Two conventions:

* The stored label convention is **1 = HUMAN, 0 = AI**, so `p_human` is
  `softmax(logits)[:, 1]` when the head was trained with human as class 1.
  `human_index` in `configs/models.yaml` records which it is per checkpoint, so a
  head trained the other way round cannot be read silently backwards.
* **Do not cap input length below the model context.** The head emits one
  decision, so truncation only throws information away; long inputs (fiction,
  full reviews) are exactly the cases where the tail matters.

Rows are sorted by length before batching and restored afterwards, which cuts
padding waste substantially on corpora with a long length tail.
"""
from __future__ import annotations

import numpy as np

from .base import Detector, ScoreBatch


class EncoderDetector(Detector):
    exposes_logits = True

    def __init__(self, model_id: str, setting: str = "full", *, checkpoint: str = "",
                 tokenizer: str = "", device: str = "cuda", batch_size: int = 32,
                 max_length: int = 8192, human_index: int = 1, **kw):
        super().__init__(model_id, setting, **kw)
        if not checkpoint:
            raise ValueError(f"{model_id}: no `checkpoint:` in configs/models.yaml")
        self.checkpoint = checkpoint
        self.tokenizer_id = tokenizer or checkpoint
        self.device = device
        self.batch_size = batch_size
        self.max_length = max_length
        self.human_index = human_index
        self._model = self._tok = None

    def _load(self):
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        self._tok = AutoTokenizer.from_pretrained(self.tokenizer_id)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            self.checkpoint, num_labels=2, attn_implementation="sdpa")
        self._model.to(self.device).eval()
        self._torch = torch

    def score_texts(self, ids: list[str], texts: list[str]) -> ScoreBatch:
        self._load()
        torch = self._torch
        order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
        logits = np.zeros((len(texts), 2), dtype=np.float32)

        with torch.no_grad():
            for start in range(0, len(order), self.batch_size):
                idx = order[start:start + self.batch_size]
                enc = self._tok([texts[i] for i in idx], return_tensors="pt",
                                padding=True, truncation=True,
                                max_length=self.max_length).to(self.device)
                out = self._model(**enc).logits.float().cpu().numpy()
                for row, i in zip(out, idx):
                    logits[i] = row

        e = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = e / e.sum(axis=1, keepdims=True)
        return ScoreBatch(ids, probs[:, self.human_index], logits,
                          meta={"model_id": self.model_id, "setting": self.setting,
                                "checkpoint": self.checkpoint,
                                "human_index": self.human_index})

    def close(self):
        if self._model is not None:
            del self._model
            self._model = None
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:
                pass
