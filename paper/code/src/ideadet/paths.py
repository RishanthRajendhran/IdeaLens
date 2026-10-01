"""Every filesystem location the project uses, resolved in one place.

Nothing else in the codebase may contain an absolute path. Scripts ask this
module, this module reads `configs/paths.yaml`, and `configs/paths.yaml` is the
single file a new user edits when they clone the repo onto a different machine.

Resolution order for each root, first hit wins:

  1. an environment variable  (IDEADET_DATA_ROOT, IDEADET_WORK_ROOT, ...)
  2. the matching key in configs/paths.yaml
  3. a default relative to the repository itself

That order lets a Slurm job override a root for one run without editing a
tracked file, and lets the checked-in defaults stay machine-independent.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

#: Repository root: three levels up from src/ideadet/paths.py.
REPO = Path(__file__).resolve().parents[2]

_ENV_PREFIX = "IDEADET_"

#: Roots this module knows about, and where they live when nothing overrides them.
#: `work` holds things that must survive (data, outputs); `scratch` holds large
#: regenerable intermediates (checkpoints, token caches, raw batch payloads).
_DEFAULTS = {
    "repo": ".",
    "configs": "configs",
    "data": "data",
    "outputs": "outputs",
    "prompts": "../prompts",
    "scripts": "scripts",
    "scratch": ".scratch",
    "cache": ".scratch/cache",
}


@lru_cache(maxsize=1)
def _file_roots() -> dict:
    f = REPO / "configs" / "paths.yaml"
    if not f.exists():
        return {}
    return (yaml.safe_load(f.read_text()) or {}).get("roots", {}) or {}


def root(name: str) -> Path:
    """Absolute path of a named root. Relative values resolve against the repo."""
    if name not in _DEFAULTS:
        raise KeyError(f"unknown root {name!r}; known roots: {sorted(_DEFAULTS)}")
    raw = (os.environ.get(f"{_ENV_PREFIX}{name.upper()}_ROOT")
           or _file_roots().get(name)
           or _DEFAULTS[name])
    p = Path(os.path.expandvars(str(raw))).expanduser()
    return p if p.is_absolute() else (REPO / p).resolve()


def data(*parts) -> Path:
    return root("data").joinpath(*map(str, parts))


def outputs(*parts) -> Path:
    return root("outputs").joinpath(*map(str, parts))


def prompts(*parts) -> Path:
    return root("prompts").joinpath(*map(str, parts))


def configs(*parts) -> Path:
    return root("configs").joinpath(*map(str, parts))


def scratch(*parts) -> Path:
    return root("scratch").joinpath(*map(str, parts))


def cache(*parts) -> Path:
    return root("cache").joinpath(*map(str, parts))


def eval_dir(eval_id: str) -> Path:
    """Dataset directory for one eval, e.g. `data/test5_peer_review/`."""
    return data(eval_id)


def run_dir(eval_id: str, run_id: str, create: bool = False) -> Path:
    """Output directory for one (eval, model run) pair.

    One directory per run rather than one file keeps `scores.jsonl`,
    `metrics.json` and the `run.json` provenance stamp together, so a result can
    never be read without the configuration that produced it.
    """
    d = outputs(eval_id, run_id)
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def describe() -> str:
    return "\n".join(f"  {k:<9} {root(k)}" for k in _DEFAULTS)


if __name__ == "__main__":  # `python -m ideadet.paths` prints the resolved roots
    print(f"repository: {REPO}\nresolved roots:\n{describe()}")
