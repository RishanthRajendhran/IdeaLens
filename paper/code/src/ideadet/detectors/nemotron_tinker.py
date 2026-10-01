"""Nemotron LoRA served through Tinker: the headline arm.

THE SCORING CONTRACT (must match training byte for byte)
--------------------------------------------------------
    <|im_start|>system
    {SYSTEM}<|im_end|>
    <|im_start|>user
    {rendered input}<|im_end|>
    <|im_start|>assistant
    <think>

    </think>

    score = softmax over ONLY the two label tokens at the final position -> P(human)

Three things about that readout matter:

* It is a **two-way** softmax over the `human` and `ai` token ids, not
  `exp(logprob)` of `human` alone. The two are monotone-related per prompt but
  not globally, so a threshold fitted under one lands somewhere else under the
  other. An earlier scorer used the one-way form and its thresholds did not carry.
* Around 99% of probability mass sits on those two tokens after fine-tuning, and
  the two-way readout agrees with the single-token readout at Spearman 0.9997.
  **P(human) is therefore conditional on the answer being one of the two words,
  not a calibrated posterior** — say so in any write-up.
* Batches are **left-padded** so the final position is a real token in every row.

Scoring bills the PREFILL meter: `compute_logprobs` generates nothing. Costing a
scoring run at the sampling rate overstates it by a large factor.
"""
from __future__ import annotations

import numpy as np

from .. import prompts as P
from ..llm.keys import require_key
from .base import Detector, ScoreBatch


class TinkerDetector(Detector):
    exposes_logits = True

    def __init__(self, model_id: str, setting: str = "full", *, weights: str = "",
                 base_model: str = "", batch_size: int = 128,
                 max_len: int = 65536, **kw):
        super().__init__(model_id, setting, **kw)
        require_key("tinker")
        contract = P.scoring_contract()
        self.base_model = base_model or kw.get("checkpoint") or contract["base_model_tinker"]
        self.weights = weights or kw.get("weights") or kw.get("checkpoint")
        if not self.weights:
            raise ValueError(
                f"{model_id}: no LoRA weights path. Set `weights:` (a tinker://<checkpoint> "
                f"sampler path) in configs/models.yaml.")
        self.system = P.training_system(setting)
        self.suffix = contract["suffix"]
        self.tok_human = int(contract["label_tokens"]["human"])
        self.tok_ai = int(contract["label_tokens"]["ai"])
        self.batch_size = batch_size
        # The deployed scorer and training both used 65536.
        # contract.json still says max_len_tokens.tinker = 4096.
        self.max_len = max_len
        self._client = None

    def _sampling_client(self):
        if self._client is None:
            import tinker
            sc = tinker.ServiceClient()
            self._client = sc.create_sampling_client(model_path=self.weights)
        return self._client

    def _prompt(self, text: str) -> str:
        # `suffix` ALREADY opens with <|im_end|>\n. Adding another here emitted it
        # twice and put the model on a prompt it never saw in training.
        return (f"<|im_start|>system\n{self.system}<|im_end|>\n"
                f"<|im_start|>user\n{text}{self.suffix}")

    def score_texts(self, ids: list[str], texts: list[str]) -> ScoreBatch:
        """Two-way normalised P(human), matching the deployed scorer exactly.

        TWO forward passes per text, one per label token. `compute_logprobs`
        returns the logprob of each token IN THE PROMPT, not a distribution over
        the vocabulary, so the label token is appended and its logprob read off
        the final position. Indexing a vocab distribution instead (as an earlier
        version here did) cannot work against this API.
        """
        import tinker

        client = self._sampling_client()
        tokenizer = client.get_tokenizer()
        # The label ids are baked into the contract; assert rather than trust.
        for tid, want in ((self.tok_human, "human"), (self.tok_ai, "ai")):
            got = tokenizer.decode([tid]).strip()
            if got != want:
                raise ValueError(
                    f"label token {tid} decodes to {got!r}, expected {want!r}: "
                    "tokenizer does not match the one training used")
        keep = tokenizer.encode(self.suffix, add_special_tokens=False)

        def one(label_tok: int) -> np.ndarray:
            out = np.zeros(len(texts))
            for start in range(0, len(texts), self.batch_size):
                chunk = texts[start:start + self.batch_size]
                futures = []
                for text in chunk:
                    toks = tokenizer.encode(self._prompt(text),
                                            add_special_tokens=False)
                    # TWO tokens of the window are not ours to spend: the
                    # label token appended below counts inside the prompt, and
                    # Tinker adds max_tokens on top of it. The constraint it
                    # enforces is
                    #     len(toks) + 1 (label) + 1 (max_tokens) <= max_len
                    # so the body budget is max_len - 2. Truncating to max_len
                    # sent 65,537 against a 65,536 window; max_len - 1 sent
                    # 65,536 and was still refused. Nothing hit this before:
                    # the longest document previously scored was ~55k tokens,
                    # and only a 77,560-word input reaches the cap at all.
                    budget = self.max_len - 2
                    if len(toks) > budget:
                        # truncate the BODY, never the suffix: the readout
                        # position has to stay the last token.
                        toks = toks[: budget - len(keep)] + keep
                    futures.append(client.compute_logprobs(
                        tinker.ModelInput.from_ints(toks + [label_tok])))
                for j, fut in enumerate(futures):
                    lp = fut.result()
                    lp = lp.tolist() if hasattr(lp, "tolist") else list(lp)
                    out[start + j] = float(lp[-1])
            return out

        lh, la = one(self.tok_human), one(self.tok_ai)
        mx = np.maximum(lh, la)
        p_human = np.exp(lh - mx) / (np.exp(lh - mx) + np.exp(la - mx))
        # Keep the RAW label logprobs: they cost two forward passes per row, the
        # whole price of the run, and the normalised p discards the margin every
        # calibration diagnostic needs.
        return ScoreBatch(ids, p_human, np.stack([lh, la], 1),
                          meta={"model_id": self.model_id, "setting": self.setting,
                                "weights": self.weights, "readout": "two_way_softmax"})
