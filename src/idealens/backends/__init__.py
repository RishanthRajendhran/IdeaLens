"""Scoring backends for the Nemotron detectors. Each returns, per input, the log-probabilities of the `human` and
`ai` label tokens at the answer position; idealens.detector turns those into P(human) and verdicts."""
from __future__ import annotations


def build_prompt_ids(tokenizer, system: str, text: str) -> list[int]:
    """The training prompt, as token ids. Built as a string, not through the chat template, exactly as in training
    and in the load_adapter.py shipped with each model."""
    from ..registry import NEMOTRON_SUFFIX
    return tokenizer.encode(f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{text}{NEMOTRON_SUFFIX}",
                            add_special_tokens=False)


def make(name: str, spec, **kwargs):
    if name == "vllm":
        from .vllm import VLLMBackend
        return VLLMBackend(spec, **kwargs)
    if name == "hf" and spec.family in ("modernbert", "qwen"):
        from .classifier import ClassifierBackend
        return ClassifierBackend(spec, **kwargs)
    if name == "hf":
        from .hf import HFBackend
        return HFBackend(spec, **kwargs)
    if name == "tinker":
        from .tinker import TinkerBackend
        return TinkerBackend(spec, **kwargs)
    if name == "logistic":
        from .logistic import LogisticBackend
        return LogisticBackend(spec, **kwargs)
    raise ValueError(f"unknown backend {name!r}; {spec.name} supports {', '.join(spec.backends)}")
