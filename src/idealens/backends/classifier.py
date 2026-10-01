"""Sequence-classification checkpoints: the ModernBERT-large and Qwen3.5-9B detectors.

ModernBERT  plain text (the rendered outline, role sequence, item, or document), the tokenizer's [CLS] ... [SEP];
            inputs longer than 8,192 tokens are cut to the first 8,192 (tokenizer truncation, [SEP] kept), as in
            training and in ideadet.detectors.hf_encoder. Float32, right-padded.
Qwen        the rendered input inside the chat template with the model's system prompt and thinking off
            (apply_chat_template(..., add_generation_prompt=True, enable_thinking=False)), token ids cut to the first
            8,192, left-padded; the head reads the last position, as in the scoring runs
            behind the paper. Bfloat16.
Both heads' config label the human class; its logit is returned first, so P(human) = softmax(row)[0].
"""
from __future__ import annotations

import numpy as np


class ClassifierBackend:
    name = "hf"

    def __init__(self, spec, weights: str | None = None, device: str | None = None, max_length: int = 8192,
                 token_budget: int | None = None, max_batch: int = 64, cache_dir: str | None = None):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch, self.spec = torch, spec
        self.qwen = spec.family == "qwen"
        src = weights or spec.repo
        self.tok = AutoTokenizer.from_pretrained(src, cache_dir=cache_dir)
        dtype = torch.bfloat16 if self.qwen else torch.float32
        self.model = AutoModelForSequenceClassification.from_pretrained(
            src, num_labels=2, dtype=dtype, attn_implementation="sdpa", cache_dir=cache_dir)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu" and device is None:
            import warnings
            warnings.warn(f"{spec.name}: no usable GPU (torch.cuda.is_available() is False), running on CPU; this is "
                          f"slow for {'Qwen' if self.qwen else 'large inputs'}. Pass device='cpu' to silence this.")
        self.model.to(self.device).eval()
        labels = {int(k): str(v).lower() for k, v in self.model.config.id2label.items()}
        if sorted(labels.values()) != ["ai", "human"]:
            raise ValueError(f"{src}: expected labels human/ai, found {labels}")
        self.human = next(k for k, v in labels.items() if v == "human")
        self.max_input_tokens = max_length
        self.token_budget = token_budget or (32_768 if self.qwen else 65_536)
        self.max_batch = max_batch
        self.pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id

    def encode(self, text: str) -> list[int]:
        """Full token ids (untruncated, so the caller can see how long the input was)."""
        if self.qwen:
            s = self.tok.apply_chat_template([{"role": "system", "content": self.spec.system},
                                              {"role": "user", "content": str(text)}],
                                             tokenize=False, add_generation_prompt=True, enable_thinking=False)
            return self.tok.encode(s, add_special_tokens=False)
        return self.tok(str(text), add_special_tokens=True, truncation=False)["input_ids"]

    def _cut(self, ids):
        if len(ids) <= self.max_input_tokens:
            return ids
        if self.qwen:
            return ids[:self.max_input_tokens]
        # tokenizer truncation keeps the closing special token
        return ids[:self.max_input_tokens - 1] + [ids[-1]]

    def _forward(self, seqs):
        torch = self.torch
        L = max(map(len, seqs))
        ids = torch.full((len(seqs), L), self.pad, dtype=torch.long)
        am = torch.zeros((len(seqs), L), dtype=torch.long)
        for r, s in enumerate(seqs):
            if self.qwen:      # left pad: the head reads the last position
                ids[r, L - len(s):] = torch.tensor(s); am[r, L - len(s):] = 1
            else:
                ids[r, :len(s)] = torch.tensor(s); am[r, :len(s)] = 1
        with torch.no_grad():
            lg = self.model(input_ids=ids.to(self.device), attention_mask=am.to(self.device)).logits.float().cpu().numpy()
        return np.stack([lg[:, self.human], lg[:, 1 - self.human]], 1)

    def _safe(self, seqs):
        try:
            return self._forward(seqs)
        except self.torch.OutOfMemoryError:
            self.torch.cuda.empty_cache()
        if len(seqs) == 1:
            return np.full((1, 2), np.nan)
        h = len(seqs) // 2
        return np.concatenate([self._safe(seqs[:h]), self._safe(seqs[h:])])

    def score_ids(self, id_lists) -> np.ndarray:
        seqs = [self._cut(x) for x in id_lists]
        out = np.full((len(seqs), 2), np.nan)
        order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
        batch = []
        for i in order:
            if batch and ((len(batch) + 1) * len(seqs[i]) > self.token_budget or len(batch) == self.max_batch):
                out[batch] = self._safe([seqs[j] for j in batch]); batch = []
            batch.append(i)
        if batch:
            out[batch] = self._safe([seqs[j] for j in batch])
        return out
