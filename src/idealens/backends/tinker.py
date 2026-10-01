"""Tinker: score with the training checkpoints on Tinker's servers (pip install tinker; TINKER_API_KEY).

Pass the checkpoint as weights="tinker://..."; only accounts that can read it can use it (no checkpoint is published). The readout is the one
that produced the paper's Tinker scores: each label token is appended to the prompt and
its log-probability read from compute_logprobs, one pass per label; the prompt body is cut to fit a 65,536-token
window, never the answer suffix. Billed at Tinker's prefill rate.
"""
from __future__ import annotations

import numpy as np

from . import build_prompt_ids
from ..registry import NEMOTRON_LABEL_TOKENS, NEMOTRON_SUFFIX

MAX_TOKENS = 65_536


class TinkerBackend:
    name = "tinker"
    max_input_tokens = MAX_TOKENS - 2

    def __init__(self, spec, weights: str | None = None, batch: int = 64):
        import tinker
        self.tinker, self.spec = tinker, spec
        path = weights or spec.extra.get("tinker_path")
        if not path:
            raise ValueError(f"{spec.name}: the Tinker backend needs weights='tinker://...', a checkpoint your account can read")
        self.client = tinker.ServiceClient().create_sampling_client(model_path=path)
        self.tokenizer = self.client.get_tokenizer()
        self.h, self.a = NEMOTRON_LABEL_TOKENS["human"], NEMOTRON_LABEL_TOKENS["ai"]
        for tid, want in ((self.h, "human"), (self.a, "ai")):
            if self.tokenizer.decode([tid]).strip() != want:
                raise ValueError(f"tokenizer mismatch: token {tid} is not {want!r}")
        self.keep = self.tokenizer.encode(NEMOTRON_SUFFIX, add_special_tokens=False)
        self.batch = batch

    def encode(self, text: str) -> list[int]:
        return build_prompt_ids(self.tokenizer, self.spec.system, text)

    def _logprobs(self, prompts, label) -> list[float]:
        out = []
        for s in range(0, len(prompts), self.batch):
            futs = [self.client.compute_logprobs(self.tinker.ModelInput.from_ints(ids + [label]))
                    for ids in prompts[s:s + self.batch]]
            for f in futs:
                lp = f.result()
                lp = lp.tolist() if hasattr(lp, "tolist") else list(lp)
                out.append(float(lp[-1]))
        return out

    def score_ids(self, id_lists) -> np.ndarray:
        prompts = [ids if len(ids) <= self.max_input_tokens else ids[:self.max_input_tokens - len(self.keep)] + self.keep
                   for ids in id_lists]
        return np.stack([self._logprobs(prompts, self.h), self._logprobs(prompts, self.a)], 1)
