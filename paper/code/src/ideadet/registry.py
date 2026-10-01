"""Lookups over the config tree: which evals exist, which model runs exist.

Nothing here holds data of its own. `configs/evals/*.yaml` and
`configs/models.yaml` are the source of truth; this module is the typed reader
so that no script has to open a YAML file directly or hardcode an eval name.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from . import config as C
from . import paths


@dataclass
class Eval:
    """One evaluation set, as declared by `configs/evals/<id>.yaml`."""
    id: str
    name: str
    number: int | None                 # canonical test number; None for in-domain
    group: str                         # In-domain / Pipeline ablations / Idea provenance / Out of domain
    asks: str                          # the question this eval answers, in one sentence
    metric: str                        # "tpr" (both classes present) or "fire" (single class)
    positive: str                      # "ai", "human", or "mixed"
    upstream: str                      # where the raw data came from
    data_dir: str
    raw: dict = field(default_factory=dict)

    @property
    def path(self):
        return paths.data(self.data_dir)

    @property
    def corpus(self):
        return self.path / "corpus.jsonl"

    @property
    def labels(self):
        return self.path / "labels.json"

    def stage_dir(self, stage: str):
        """`extract` (stage-1 outlines) or `deleak` (stage-2, what models score).

        Returns the directory path even when the eval stores that stage as a
        single `<stage>.jsonl` instead; `io.iter_outline_files` accepts either.
        """
        if stage not in ("extract", "deleak"):
            raise ValueError(f"stage must be 'extract' or 'deleak', got {stage!r}")
        return self.path / stage

    def has_stage(self, stage: str) -> bool:
        from .io import has_outlines
        return has_outlines(self.stage_dir(stage))

    def n_outlines(self, stage: str) -> int:
        from .io import count_outlines
        return count_outlines(self.stage_dir(stage))

    @property
    def deleak_status(self) -> str:
        """`done` or `not_run`. Anything but `done` means this eval's numbers come
        from UNTREATED outlines and are not comparable with the de-leaked sets."""
        return str(self.raw.get("deleak_status", "done"))

    @property
    def comparable(self) -> bool:
        return self.deleak_status == "done"

    @property
    def groups(self) -> list[str]:
        """Metadata columns this eval is broken down by in reports."""
        return list(self.raw.get("report", {}).get("group_by", ["format"]))

    def __str__(self):
        num = f"Test {self.number}" if self.number is not None else "In-domain"
        return f"{self.id} ({num}: {self.name})"


@lru_cache(maxsize=1)
def evals() -> dict[str, Eval]:
    out = {}
    for name in C.list_configs("evals"):
        cfg = C.load(name, kind="evals")
        out[name] = Eval(
            id=name,
            name=cfg.get("name", name),
            number=cfg.get("number"),
            group=cfg.get("group", "Out of domain"),
            asks=cfg.get("asks", ""),
            metric=cfg.get("metric", "tpr"),
            positive=cfg.get("positive", "ai"),
            upstream=cfg.get("upstream", "UNKNOWN — record before release"),
            data_dir=cfg.get("data_dir", name),
            raw=cfg,
        )
    return out


def get_eval(eval_id: str) -> Eval:
    e = evals()
    if eval_id not in e:
        raise KeyError(f"unknown eval {eval_id!r}. Available: {sorted(e)}")
    return e[eval_id]


def evals_in_group(group: str) -> list[Eval]:
    return [e for e in evals().values() if e.group == group]


def ordered_evals() -> list[Eval]:
    """Every eval, in canonical reporting order: in-domain first, then by number.

    THE MAIN RESULTS ARTIFACT IS BUILT FROM THIS LIST, so an eval that has a
    config appears in the report whether or not it has been scored yet — an
    unscored set shows up as a named gap rather than silently vanishing.
    """
    return sorted(evals().values(),
                  key=lambda e: (-1 if e.number is None else e.number, e.id))


@dataclass
class ModelRun:
    """One trained detector arm, as declared by `configs/models.yaml`."""
    id: str
    name: str
    backend: str                       # nemotron_tinker | hf_encoder | qwen_local | logistic | pangram
    setting: str                       # full | items | roles | docs | rawout
    corpus: str                        # which training corpus produced it
    checkpoint: str | None
    tokenizer: str | None
    detail: str
    raw: dict = field(default_factory=dict)

    @property
    def input_kind(self) -> str:
        return {"docs": "Raw document", "rawout": "Outline before de-leak"}.get(
            self.setting, "De-leaked outline")


@lru_cache(maxsize=1)
def models() -> dict[str, ModelRun]:
    cfg = C.load("models.yaml")
    out = {}
    for mid, m in (cfg.get("models") or {}).items():
        out[mid] = ModelRun(
            id=mid,
            name=m.get("name", mid),
            backend=m["backend"],
            setting=m.get("setting", "full"),
            corpus=m.get("corpus", ""),
            checkpoint=m.get("checkpoint"),
            tokenizer=m.get("tokenizer"),
            detail=m.get("detail", ""),
            raw=m,
        )
    return out


def get_model(model_id: str) -> ModelRun:
    m = models()
    if model_id not in m:
        raise KeyError(f"unknown model run {model_id!r}. Available: {sorted(m)}")
    return m[model_id]


def summary_table() -> str:
    lines = ["EVALS", f"  {'id':<28}{'test':>6}  {'metric':<7}{'group':<20}name"]
    for e in ordered_evals():
        num = "" if e.number is None else str(e.number)
        lines.append(f"  {e.id:<28}{num:>6}  {e.metric:<7}{e.group:<20}{e.name}")
    lines += ["", "MODEL RUNS", f"  {'id':<22}{'backend':<18}{'setting':<9}input"]
    for m in models().values():
        lines.append(f"  {m.id:<22}{m.backend:<18}{m.setting:<9}{m.input_kind}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary_table())
