"""Logistic regression over text embeddings: the cheap, transparent baseline.

Kept for three reasons: it costs cents to refit, it is the arm whose feature
weights can be read directly, and it is multilingual for free because the
embedding is — so it is the one arm that can attempt fully source-language
classification without an English step.

The fitted object on disk is an sklearn Pipeline (scaler + LR). Embeddings are
computed by `scripts/eval/embed.py` and cached, because embedding a corpus twice
is pure waste and the cache is the expensive artifact, not the fit.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

from .base import Detector, ScoreBatch


class LogisticDetector(Detector):
    exposes_logits = True          # decision_function is the logit

    def __init__(self, model_id: str, setting: str = "full", *, checkpoint: str = "",
                 embedding_model: str = "text-embedding-3-large",
                 embedding_cache: str = "", human_index: int = 1,
                 batch_size: int = 256, **kw):
        super().__init__(model_id, setting, **kw)
        if not checkpoint:
            raise ValueError(f"{model_id}: no `checkpoint:` (path to the .pkl) "
                             f"in configs/models.yaml")
        self.checkpoint = Path(checkpoint)
        self.embedding_model = embedding_model
        self.embedding_cache = Path(embedding_cache) if embedding_cache else None
        self.human_index = human_index
        self.batch_size = batch_size
        self._pipe = None

    def _load(self):
        if self._pipe is None:
            with open(self.checkpoint, "rb") as fh:
                self._pipe = pickle.load(fh)

    def _embed(self, texts: list[str]) -> np.ndarray:
        """Embed, reusing the on-disk cache for any text already seen."""
        from ..llm.openai_batch import _client
        import hashlib

        cache: dict[str, list[float]] = {}
        if self.embedding_cache and self.embedding_cache.exists():
            cache = dict(np.load(self.embedding_cache, allow_pickle=True)["cache"].item())

        key = lambda t: hashlib.sha256(t.encode()).hexdigest()
        todo = [t for t in texts if key(t) not in cache]
        if todo:
            client = _client()
            for i in range(0, len(todo), self.batch_size):
                chunk = todo[i:i + self.batch_size]
                resp = client.embeddings.create(model=self.embedding_model, input=chunk)
                for t, d in zip(chunk, resp.data):
                    cache[key(t)] = d.embedding
            if self.embedding_cache:
                self.embedding_cache.parent.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(self.embedding_cache, cache=np.array(cache, dtype=object))
        return np.asarray([cache[key(t)] for t in texts], dtype=np.float32)

    def score_texts(self, ids: list[str], texts: list[str]) -> ScoreBatch:
        self._load()
        X = self._embed(texts)
        probs = self._pipe.predict_proba(X)
        margin = self._pipe.decision_function(X)
        return ScoreBatch(ids, probs[:, self.human_index],
                          np.asarray(margin, dtype=np.float32).reshape(len(ids), -1),
                          meta={"model_id": self.model_id, "setting": self.setting,
                                "checkpoint": str(self.checkpoint),
                                "embedding_model": self.embedding_model})

    def score_embeddings(self, ids: list[str], X: np.ndarray) -> ScoreBatch:
        """Score pre-computed embeddings, skipping the API entirely."""
        self._load()
        probs = self._pipe.predict_proba(X)
        return ScoreBatch(ids, probs[:, self.human_index],
                          meta={"model_id": self.model_id, "setting": self.setting})
