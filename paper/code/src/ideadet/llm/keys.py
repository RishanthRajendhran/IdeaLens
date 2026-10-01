"""Credentials, read from the environment and never from a tracked file.

No key, token, service-account JSON or `.env` file belongs in this repository.
`preflight()` reports which providers are usable so a long batch job fails in
the first second rather than after the upload.
"""
from __future__ import annotations

import os

#: provider -> (env var, what it is for, where to get it)
PROVIDERS = {
    "vertex": ("GOOGLE_CLOUD_PROJECT",
               "Gemini extraction / de-leak / generation via Vertex batch",
               "gcloud auth application-default login, then export "
               "GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION=global / "
               "GOOGLE_GENAI_USE_VERTEXAI=1"),
    "openai":  ("OPENAI_API_KEY", "feature discovery, embeddings, GPT arms",
                "platform.openai.com API keys"),
    "anthropic": ("ANTHROPIC_API_KEY", "Claude arms in generation and judging",
                  "console.anthropic.com API keys"),
    "tinker":  ("TINKER_API_KEY", "Nemotron LoRA training and scoring",
                "your Tinker account"),
    "pangram": ("PANGRAM_API_KEY", "Pangram surface-detector baseline and labels",
                "Pangram API access"),
    "hf":      ("HF_TOKEN", "dataset and model downloads",
                "huggingface.co/settings/tokens"),
}


class MissingCredential(RuntimeError):
    pass


def require_key(provider: str) -> str:
    if provider not in PROVIDERS:
        raise KeyError(f"unknown provider {provider!r}; known: {sorted(PROVIDERS)}")
    var, purpose, how = PROVIDERS[provider]
    val = os.environ.get(var)
    if not val:
        raise MissingCredential(
            f"{var} is not set. Needed for: {purpose}. How to get it: {how}. "
            f"Export it in your shell; never write it into a file in this repo.")
    return val


def available() -> dict[str, bool]:
    return {p: bool(os.environ.get(v)) for p, (v, _, _) in PROVIDERS.items()}


def preflight(required: list[str] | None = None) -> str:
    """Human-readable credential report; raises if a required provider is absent."""
    have = available()
    lines = ["credentials:"]
    for p, (var, purpose, _) in PROVIDERS.items():
        mark = "ok     " if have[p] else "MISSING"
        lines.append(f"  {mark} {p:<10} {var:<24} {purpose}")
    missing = [p for p in (required or []) if not have[p]]
    out = "\n".join(lines)
    if missing:
        raise MissingCredential(out + "\n\nrequired but missing: " + ", ".join(missing))
    return out


if __name__ == "__main__":
    print(preflight())
