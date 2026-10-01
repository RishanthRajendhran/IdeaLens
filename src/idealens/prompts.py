"""Provider-neutral prompts for classification, force-fitting and extraction, and the Gemini REST body.

The Gemini body is the request the training corpus was built with (prompt version train_v391+excerpts+en) and the pipeline's format gate: seed 1865679507, safety threshold OFF on the four
configurable categories, thinking HIGH and a 64,000-token output budget for extraction. It was checked byte for byte
against the request builder that made the training corpus.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from . import assets
from .formats import FORMATS

SEED = 1865679507


@dataclass
class Prompt:
    kind: str                      # "extract" | "classify" | "force_fit"
    system: str
    user: str
    max_output_tokens: int
    schema: dict | None = None     # JSON schema of the reply, when the provider can enforce one
    reasoning: str | None = None   # "high" for extraction
    seed: int | None = SEED
    format: str | None = None
    few_shot: bool | None = None
    version: str | None = None
    system_sha256: str | None = None
    extra_user: list[str] = field(default_factory=list)  # follow-up turns on a repair retry

    def meta(self) -> dict:
        return {"prompt_kind": self.kind, "prompt_version": self.version, "system_sha256": self.system_sha256,
                "few_shot": self.few_shot, "seed": self.seed}


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def extraction_prompt(text: str, fmt: str, few_shot: bool = True, seed: int | None = SEED) -> Prompt:
    if fmt not in FORMATS:
        raise ValueError(f"extraction needs one of the eight formats, not {fmt!r}")
    ex = assets.extraction()
    f = ex["formats"][fmt]
    system = f["system_fewshot" if few_shot else "system_zeroshot"]
    return Prompt("extract", system, ex["user_template"].replace("{text}", text), ex["max_output_tokens"],
                  schema=f["schema"], reasoning="high", seed=seed, format=fmt, few_shot=few_shot,
                  version=ex["prompt_version"] + ("" if few_shot else "+zeroshot"), system_sha256=_sha(system))


def classification_prompt(text: str, url: str = "", seed: int | None = SEED) -> Prompt:
    c = assets.classifier()
    return Prompt("classify", c["system"], c["user_template"].replace("{url}", url).replace("{text}", text),
                  c["generation"]["maxOutputTokens"], seed=seed, version="weborganizer_formats",
                  system_sha256=_sha(c["system"]))


def force_fit_prompt(text: str, url: str = "", seed: int | None = SEED) -> Prompt:
    c = assets.classifier()
    return Prompt("force_fit", c["force_fit_system"], c["user_template"].replace("{url}", url).replace("{text}", text),
                  c["generation"]["maxOutputTokens"], seed=seed, version="weborganizer_formats+force_fit",
                  system_sha256=_sha(c["force_fit_system"]))


def safety_settings(threshold: str = "OFF") -> list:
    return [{"category": c, "threshold": threshold} for c in assets.extraction()["safety_categories"]]


def gemini_body(p: Prompt, schema_key: str = "responseSchema") -> dict:
    """The generateContent body. schema_key: "responseSchema" (Vertex, and the training requests) or
    "responseJsonSchema" (the Gemini API's JSON-Schema field)."""
    gen = {"maxOutputTokens": p.max_output_tokens}
    if p.schema is not None:
        gen["responseMimeType"] = "application/json"
        gen[schema_key] = p.schema
    if p.reasoning:
        gen["thinkingConfig"] = {"thinkingLevel": p.reasoning.upper()}
    if p.seed is not None:
        gen["seed"] = p.seed
    contents = [{"role": "user", "parts": [{"text": p.user}]}]
    for i, turn in enumerate(p.extra_user):  # repair retries: the model's bad reply, then the correction request
        contents.append({"role": "model" if i % 2 == 0 else "user", "parts": [{"text": turn}]})
    return {"contents": contents, "systemInstruction": {"parts": [{"text": p.system}]}, "generationConfig": gen,
            "safetySettings": safety_settings()}
