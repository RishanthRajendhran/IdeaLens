"""Run many prompts through a provider: concurrently online, or as one batch job."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .providers import Reply


def run(provider, prompts: dict, mode: str = "online", workers: int = 8, log=print, description="idealens") -> dict:
    """prompts: {id: Prompt} -> {id: Reply}."""
    if not prompts:
        return {}
    if mode == "batch":
        return provider.run_batch(prompts, log=log, description=description)
    if mode != "online":
        raise ValueError("mode must be 'online' or 'batch'")

    def one(item):
        pid, p = item
        try:
            return pid, provider.generate(p)
        except Exception as e:  # a provider bug must not lose the other documents
            return pid, Reply(None, error=f"{type(e).__name__}: {e}")

    with ThreadPoolExecutor(max(1, workers)) as ex:
        return dict(ex.map(one, prompts.items()))
