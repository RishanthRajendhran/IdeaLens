"""LLM providers for classification and extraction.

A provider turns a Prompt into a Reply. Online calls go through `generate` (run concurrently by the caller);
providers with a batch API also implement `run_batch`, which submits every prompt as one job and waits for it.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Reply:
    text: str | None
    usage: dict = field(default_factory=dict)   # input, cached_input, output, reasoning tokens (as reported)
    error: str | None = None
    finish: str | None = None
    host: str | None = None                     # who served it, where the provider reports it
    cost_usd: float | None = None               # where the provider reports it


class Provider:
    name = "base"
    model: str = ""
    supports_batch = False

    def generate(self, prompt) -> Reply:
        raise NotImplementedError

    def run_batch(self, prompts: dict, log=print) -> dict:
        raise NotImplementedError(f"{self.name} has no batch mode; use mode='online'")


DEFAULT_PROVIDER = "gemini"


def make(name: str = DEFAULT_PROVIDER, model: str | None = None, **kw) -> Provider:
    if name == "gemini":
        from .gemini import GeminiAPI
        return GeminiAPI(model=model, **kw)
    if name == "vertex":
        from .gemini import Vertex
        return Vertex(model=model, **kw)
    if name == "openai":
        from .openai_compat import OpenAIChat
        return OpenAIChat(model=model, kind="openai", **kw)
    if name == "openrouter":
        from .openai_compat import OpenRouter
        return OpenRouter(model=model, **kw)
    if name == "compatible":
        from .openai_compat import OpenAIChat
        if not kw.get("base_url"):
            raise ValueError("provider 'compatible' needs base_url (e.g. http://localhost:8000/v1)")
        return OpenAIChat(model=model, kind="compatible", **kw)
    if name == "anthropic":
        from .anthropic import Claude
        return Claude(model=model, **kw)
    raise ValueError(f"unknown provider {name!r}; use one of {', '.join(PROVIDERS)}")


PROVIDERS = ("gemini", "vertex", "openai", "anthropic", "openrouter", "compatible")
