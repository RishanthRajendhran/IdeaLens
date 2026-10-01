"""vLLM backend (the default). Verified against Tinker on 200 in-domain documents per model: Pearson >= 0.99998,
mean |dP| about 0.001; about 15x the throughput of the transformers backend, and inputs up to 262,144 tokens on one
80 GB GPU.

Readout: one generated token with the top-20 raw log-probabilities (vLLM's default logprobs_mode is the full-vocabulary
log-softmax, the same quantity the transformers backend computes). If either label token is missing from the top 20,
that input is re-scored exactly with prompt_logprobs on prompt + label, and counted in `n_fallback`.
"""
from __future__ import annotations

import atexit
import os

import numpy as np

from . import build_prompt_ids
from ..registry import NEMOTRON_LABEL_TOKENS

MAX_MODEL_LEN = 262_144  # the base model's max_position_embeddings


def _weight_bytes(weights: str) -> int | None:
    """Size of the safetensors weights at the repo root (the merged model), or None when it cannot be looked up."""
    try:
        if os.path.isdir(weights):
            return sum(os.path.getsize(os.path.join(weights, f)) for f in os.listdir(weights)
                       if f.endswith(".safetensors")) or None
        from huggingface_hub import HfApi
        info = HfApi().model_info(weights, files_metadata=True)
        return sum(s.size or 0 for s in info.siblings
                   if s.rfilename.endswith(".safetensors") and "/" not in s.rfilename) or None
    except Exception:
        return None


def _check_fits(weights: str, util: float, tp: int):
    """Fail before vLLM starts when the weights cannot fit in the GPU memory vLLM may use, instead of an out-of-memory
    traceback from its engine process."""
    import torch
    size = _weight_bytes(weights)
    if not size or not torch.cuda.is_available():
        return
    total = torch.cuda.get_device_properties(0).total_memory
    usable = total * util * tp
    if size * 1.05 > usable:   # weights plus a little room for activations, the Mamba state and the KV cache
        gib = 2 ** 30
        raise RuntimeError(
            f"{weights}: the weights take {size / gib:.0f} GiB, but vLLM may use {usable / gib:.0f} GiB "
            f"({tp} x {total / gib:.0f} GiB GPU x gpu_memory_utilization {util}). Use an 80 GB GPU (A100 80GB, H100), "
            f"or spread the model over more GPUs with tensor_parallel_size.")


class VLLMBackend:
    name = "vllm"

    def __init__(self, spec, weights: str | None = None, max_model_len: int = MAX_MODEL_LEN,
                 gpu_memory_utilization: float = 0.90, tensor_parallel_size: int = 1, max_num_seqs: int = 256,
                 cache_dir: str | None = None, **llm_kwargs):
        # FlashInfer kernels compile CUDA code on first use and fail on machines without nvcc: the top-k sampler (not
        # needed for a one-token readout) and, on H100s, the MoE kernels. Triton MoE kernels are the ones verified
        # against Tinker.
        os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")
        os.environ.setdefault("VLLM_USE_FLASHINFER_MOE_FP16", "0")
        # On Hopper, vLLM's start-up warmup probes DeepGEMM (FP8 kernels) and crashes when it is not installed, even
        # for bf16 weights; FlashInfer autotuning there can also trigger compilation.
        os.environ.setdefault("VLLM_USE_DEEP_GEMM", "0")
        llm_kwargs.setdefault("enable_flashinfer_autotune", False)
        if cache_dir:
            for var, sub in (("VLLM_CACHE_ROOT", "vllm"), ("TRITON_CACHE_DIR", "triton"),
                             ("TORCHINDUCTOR_CACHE_DIR", "inductor")):
                os.environ.setdefault(var, os.path.join(cache_dir, sub))
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams

        self.spec = spec
        self.weights = weights or spec.repo
        self.max_model_len = max_model_len
        self.tokenizer = AutoTokenizer.from_pretrained(self.weights)
        _check_fits(self.weights, gpu_memory_utilization, tensor_parallel_size)
        self.llm = LLM(model=self.weights, dtype="bfloat16", max_model_len=max_model_len,
                       gpu_memory_utilization=gpu_memory_utilization, tensor_parallel_size=tensor_parallel_size,
                       max_num_seqs=max_num_seqs,  # each running sequence holds one Mamba state block; vLLM's H100
                       # default (1,024) exceeds the blocks that fit next to the 59 GiB of weights
                       enable_prefix_caching=False, max_logprobs=20, seed=0, **llm_kwargs)
        self._sp = SamplingParams(max_tokens=1, temperature=0.0, logprobs=20)
        self._SamplingParams = SamplingParams
        self.h, self.a = NEMOTRON_LABEL_TOKENS["human"], NEMOTRON_LABEL_TOKENS["ai"]
        self.n_fallback = 0
        atexit.register(self.close)  # without this the engine process keeps the interpreter alive at exit

    def close(self):
        llm = getattr(self, "llm", None)
        if llm is not None:
            try:
                llm.llm_engine.engine_core.shutdown()
            finally:
                self.llm = None

    def encode(self, text: str) -> list[int]:
        return build_prompt_ids(self.tokenizer, self.spec.system, text)

    def score_ids(self, id_lists: list[list[int]]) -> np.ndarray:
        """(n, 2) array of [logprob(human), logprob(ai)]; NaN rows for inputs longer than max_model_len."""
        if self.llm is None:
            raise RuntimeError("this backend has been closed")
        out = np.full((len(id_lists), 2), np.nan)
        ok = [i for i, x in enumerate(id_lists) if len(x) < self.max_model_len]
        if not ok:
            return out
        res = self.llm.generate([{"prompt_token_ids": id_lists[i]} for i in ok], self._sp, use_tqdm=False)
        for i, r in zip(ok, res):
            lp = r.outputs[0].logprobs[0]
            if self.h in lp and self.a in lp:
                out[i] = lp[self.h].logprob, lp[self.a].logprob
            else:
                self.n_fallback += 1
                sp = self._SamplingParams(max_tokens=1, prompt_logprobs=0)
                two = self.llm.generate([{"prompt_token_ids": id_lists[i] + [self.h]},
                                         {"prompt_token_ids": id_lists[i] + [self.a]}], sp, use_tqdm=False)
                out[i] = two[0].prompt_logprobs[-1][self.h].logprob, two[1].prompt_logprobs[-1][self.a].logprob
        return out
