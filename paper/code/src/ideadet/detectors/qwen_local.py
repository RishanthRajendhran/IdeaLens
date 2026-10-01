"""Local decoder arm (Qwen), fine-tuned with the same generative scoring contract.

Same readout as the Tinker arm — a two-way softmax over the two label tokens at
the final position — but run locally, so the label token ids come from the
model's own tokenizer instead of the contract file. Encoding `human` and `ai`
here rather than trusting hardcoded ids is the difference between a correct
score and a confident one taken off the wrong vocabulary row.

This is the only arm whose memory is genuinely bounded by input length, so it is
also the only one where a `max_length` is a real trade-off rather than pure loss.
"""
from __future__ import annotations

import numpy as np

from .. import prompts as P
from .base import Detector, ScoreBatch


class QwenDetector(Detector):
    exposes_logits = True

    def __init__(self, model_id: str, setting: str = "full", *, checkpoint: str = "",
                 tokenizer: str = "", device: str = "cuda", batch_size: int = 8,
                 max_length: int = 8192, dtype: str = "bfloat16", **kw):
        super().__init__(model_id, setting, **kw)
        if not checkpoint:
            raise ValueError(f"{model_id}: no `checkpoint:` in configs/models.yaml")
        self.checkpoint = checkpoint
        self.tokenizer_id = tokenizer or checkpoint
        self.device, self.batch_size = device, batch_size
        self.max_length, self.dtype = max_length, dtype
        self.system = P.training_system(setting)
        # `suffix`, not `assistant_suffix`: the contract has only ever defined
        # `suffix`, and nemotron_tinker.py reads that key. This arm had never been
        # run from this repo, so the typo raised KeyError on every construction.
        self.suffix = P.scoring_contract()["suffix"]
        self._model = self._tok = None

    def _load(self):
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self._tok = AutoTokenizer.from_pretrained(self.tokenizer_id)
        # Left padding so the final position is a real token in every row; with
        # right padding the readout would land on pad for all but the longest row.
        self._tok.padding_side = "left"
        if self._tok.pad_token is None:
            self._tok.pad_token = self._tok.eos_token
        self._model = AutoModelForCausalLM.from_pretrained(
            self.checkpoint, torch_dtype=getattr(torch, self.dtype)).to(self.device).eval()
        self._torch = torch
        self.tok_human = self._single_token("human")
        self.tok_ai = self._single_token("ai")

    def _single_token(self, word: str) -> int:
        ids = self._tok.encode(word, add_special_tokens=False)
        if len(ids) != 1:
            raise ValueError(
                f"{word!r} is not a single token for {self.tokenizer_id}: {ids}. "
                f"The scoring contract needs both labels to be one token each.")
        return ids[0]

    def _prompt(self, text: str) -> str:
        return (f"<|im_start|>system\n{self.system}<|im_end|>\n"
                f"<|im_start|>user\n{text}<|im_end|>\n{self.suffix}")

    def score_texts(self, ids: list[str], texts: list[str]) -> ScoreBatch:
        self._load()
        torch = self._torch
        order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
        pairs = np.zeros((len(texts), 2), dtype=np.float32)

        with torch.no_grad():
            for start in range(0, len(order), self.batch_size):
                idx = order[start:start + self.batch_size]
                enc = self._tok([self._prompt(texts[i]) for i in idx],
                                return_tensors="pt", padding=True, truncation=True,
                                max_length=self.max_length).to(self.device)
                last = self._model(**enc).logits[:, -1, :].float().cpu().numpy()
                for row, i in zip(last, idx):
                    pairs[i] = [row[self.tok_human], row[self.tok_ai]]

        e = np.exp(pairs - pairs.max(axis=1, keepdims=True))
        probs = e / e.sum(axis=1, keepdims=True)
        return ScoreBatch(ids, probs[:, 0], pairs,
                          meta={"model_id": self.model_id, "setting": self.setting,
                                "checkpoint": self.checkpoint,
                                "readout": "two_way_softmax"})

    def close(self):
        if self._model is not None:
            del self._model
            self._model = None
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:
                pass
