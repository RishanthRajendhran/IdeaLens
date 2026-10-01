"""Pangram wrapped in the Detector interface, so it can enter the same tables.

Two cautions, both repeated from `ideadet.llm.pangram` because they decide
whether a reported number is meaningful:

* `p_human` here is Pangram's `fraction_human`, which makes it rankable on AUC
  and TPR@FPR. That is the **in-set** convention Pangram's own rank metrics use.
  For the headline baseline claim, report `verdict_deployed` instead — Pangram's
  fixed production rule, applied unchanged.
* This detector takes **documents**, not outlines. Scoring an outline with a
  surface detector answers a different question (whether the outline reads
  machine-written), which is the leakage study, not the baseline.
"""
from __future__ import annotations

import numpy as np

from ..llm import pangram as PG
from .base import Detector, ScoreBatch


class PangramDetector(Detector):
    exposes_logits = False

    def __init__(self, model_id: str, setting: str = "docs", *,
                 pangram_model: str = "pangram-4", timeout: int = 7200, **kw):
        super().__init__(model_id, setting, **kw)
        if setting != "docs":
            raise ValueError(
                "Pangram is a surface detector: it reads documents. Use setting "
                "'docs'.")
        self.pangram_model = pangram_model
        self.timeout = timeout
        self.rows: list[dict] = []

    def score_texts(self, ids: list[str], texts: list[str]) -> ScoreBatch:
        est = PG.estimate_cost(texts, self.pangram_model)
        print(f"  pangram: {est['n_texts']:,} texts, {est['billing_units']:,} units, "
              f"~${est['usd']:.2f}")
        self.rows = PG.score([{"id": i, "text": t} for i, t in zip(ids, texts)],
                             self.pangram_model, timeout=self.timeout)
        p = np.array([r["fraction_human"] if r["fraction_human"] is not None else np.nan
                      for r in self.rows], dtype=float)
        return ScoreBatch(ids, p, meta={
            "model_id": self.model_id, "pangram_model": self.pangram_model,
            "verdict_deployed": [r["verdict_deployed"] for r in self.rows],
            "fraction_ai": [r["fraction_ai"] for r in self.rows],
            "fraction_ai_assisted": [r["fraction_ai_assisted"] for r in self.rows],
            "note": "p_human is fraction_human (in-set convention); the deployed "
                    "convention is verdict_deployed"})
