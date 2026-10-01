"""transformers backend. Two ways to get the weights:

  mode="merged"  (default) AutoModelForCausalLM on the merged weights at the repo root.
  mode="adapter" the base model plus the repo's adapter/ folder, merged in memory (bit-identical to "merged").

Both were verified against Tinker on 200 in-domain documents per model. Scoring is batched: inputs are sorted by
length and right-padded, and each row is read at its own last real token. The model is causal throughout (attention,
Mamba scan, per-token MoE), so padding after a row's end cannot change that position; batched and unbatched scores
agreed to bf16 noise (max |dP| 0.018) in the calibration runs. A batch that runs out of GPU memory is split in half.

Memory: the weights take 59 GiB, and transformers' PyTorch Mamba scan adds about 4.2 MiB per token in a batch, so
one 80 GB GPU handles about 4,000 tokens at a time. Use the vLLM backend for long documents.
"""
from __future__ import annotations

import numpy as np

from . import build_prompt_ids
from ..registry import NEMOTRON_LABEL_TOKENS


class HFBackend:
    name = "hf"

    def __init__(self, spec, weights: str | None = None, mode: str = "merged", device_map="auto",
                 token_budget: int = 2560, max_batch: int = 32, cache_dir: str | None = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.spec, self.mode = spec, mode
        self.token_budget, self.max_batch = token_budget, max_batch
        if mode == "merged":
            src = weights or spec.repo
            self.tokenizer = AutoTokenizer.from_pretrained(src, cache_dir=cache_dir)
            self.model = AutoModelForCausalLM.from_pretrained(src, dtype=torch.bfloat16, device_map=device_map,
                                                              cache_dir=cache_dir).eval()
        elif mode == "adapter":
            from huggingface_hub import snapshot_download
            from .tinker_merge import apply_tinker_lora
            self.tokenizer = AutoTokenizer.from_pretrained(spec.base_model, cache_dir=cache_dir)
            self.model = AutoModelForCausalLM.from_pretrained(spec.base_model, dtype=torch.bfloat16,
                                                              device_map=device_map, cache_dir=cache_dir).eval()
            adir = weights or (snapshot_download(spec.repo, allow_patterns=["adapter/*"], cache_dir=cache_dir)
                               + "/adapter")
            apply_tinker_lora(self.model, adir)
        else:
            raise ValueError("mode must be 'merged' or 'adapter'")
        self.device = self.model.get_input_embeddings().weight.device
        self.pad = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id
        self.h, self.a = NEMOTRON_LABEL_TOKENS["human"], NEMOTRON_LABEL_TOKENS["ai"]

    def encode(self, text: str) -> list[int]:
        return build_prompt_ids(self.tokenizer, self.spec.system, text)

    def _forward(self, seqs: list[list[int]]) -> np.ndarray:
        torch = self.torch
        L = max(map(len, seqs))
        ids = torch.full((len(seqs), L), self.pad, dtype=torch.long)
        am = torch.zeros((len(seqs), L), dtype=torch.long)
        for r, s in enumerate(seqs):
            ids[r, :len(s)] = torch.tensor(s); am[r, :len(s)] = 1
        with torch.no_grad():
            hid = self.model.model(input_ids=ids.to(self.device), attention_mask=am.to(self.device)).last_hidden_state
            last = hid[torch.arange(len(seqs), device=hid.device),
                       torch.tensor([len(s) - 1 for s in seqs], device=hid.device)]
            lp = torch.log_softmax(self.model.lm_head(last).float(), -1)
        return torch.stack([lp[:, self.h], lp[:, self.a]], 1).cpu().numpy()

    def _safe(self, seqs):
        """_forward, halving the batch on out-of-memory; a single input that still does not fit gets a NaN row."""
        try:
            return self._forward(seqs)
        except self.torch.OutOfMemoryError:
            self.torch.cuda.empty_cache()
        if len(seqs) == 1:
            return np.full((1, 2), np.nan)
        h = len(seqs) // 2
        return np.concatenate([self._safe(seqs[:h]), self._safe(seqs[h:])])

    def score_ids(self, id_lists: list[list[int]]) -> np.ndarray:
        """(n, 2) array of [logprob(human), logprob(ai)]; NaN rows for inputs that do not fit in GPU memory."""
        out = np.full((len(id_lists), 2), np.nan)
        order = sorted(range(len(id_lists)), key=lambda i: len(id_lists[i]))
        batch = []
        for i in order:  # length-sorted, so each new input is the batch's longest and padding waste is small
            if batch and ((len(batch) + 1) * len(id_lists[i]) > self.token_budget or len(batch) == self.max_batch):
                out[batch] = self._safe([id_lists[j] for j in batch]); batch = []
            batch.append(i)
        if batch:
            out[batch] = self._safe([id_lists[j] for j in batch])
        return out
