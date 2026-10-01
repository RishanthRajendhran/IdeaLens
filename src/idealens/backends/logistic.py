"""Logistic regression over OpenAI text-embedding-3-large vectors (IdeaLens-LogisticClassifier and -PerItem).

The repo holds `coef` (1 x 3072) and `intercept`; AI is the positive class, so P(human) = predict_proba(x)[:, 0] =
1 - sigmoid(coef . x + intercept). Returned as the logit pair [0, coef . x + intercept], whose two-way softmax gives
that P(human). Embeddings need OPENAI_API_KEY (pip install openai); pass `embed=` (a function from a list of strings
to an (n, 3072) array) to use your own cache or precomputed vectors.
"""
from __future__ import annotations

import numpy as np


class LogisticBackend:
    name = "logistic"
    max_input_tokens = None

    def __init__(self, spec, weights: str | None = None, embed=None, batch_size: int = 256, cache_dir: str | None = None,
                 api_key: str | None = None):
        from huggingface_hub import hf_hub_download
        fname = {"outline": "lr_full_v1m.npz", "items": "lr_items_v1m.npz"}[spec.input]
        path = weights or hf_hub_download(spec.repo, fname, cache_dir=cache_dir)
        z = np.load(path, allow_pickle=True)
        self.coef = z["coef"].astype(np.float64).ravel()
        self.intercept = float(np.ravel(z["intercept"])[0])
        self.embedder = str(z["embedder"])
        if str(z["positive_class"]) != "ai":
            raise ValueError(f"{path}: expected AI as the positive class")
        self.batch_size, self._embed, self._client, self._key = batch_size, embed, None, api_key

    def encode(self, text: str) -> str:
        return str(text)

    def embed(self, texts) -> np.ndarray:
        if self._embed is not None:
            return np.asarray(self._embed(list(texts)), dtype=np.float64)
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._key) if self._key else OpenAI()
        out = []
        for s in range(0, len(texts), self.batch_size):
            resp = self._client.embeddings.create(model=self.embedder, input=list(texts[s:s + self.batch_size]))
            out += [d.embedding for d in resp.data]
        return np.asarray(out, dtype=np.float64)

    def score_ids(self, texts) -> np.ndarray:
        if not texts:
            return np.zeros((0, 2))
        z = self.embed(texts) @ self.coef + self.intercept
        return np.stack([np.zeros_like(z), z], 1)
