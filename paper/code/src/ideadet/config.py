"""YAML configuration: loading, inheritance, overrides, and provenance.

Every script in this repository is driven by a config file rather than by
constants in its own source, so that a run can be reproduced from the config
alone and so that a new eval or model arm is a new YAML file, not a new script.

Three features beyond plain `yaml.safe_load`:

  * `extends:` — a config may name one or more parents, merged depth-first with
    the child winning. Shared defaults live in one place (`configs/evals/_base.yaml`).
  * `${ENV_VAR}` interpolation in string values, so secrets and machine-specific
    paths never appear in a tracked file.
  * `stamp()` — the exact resolved config, plus git revision and timestamp,
    written next to every result as `run.json`.
"""
from __future__ import annotations

import copy
import datetime
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

from . import paths

_ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


class ConfigError(RuntimeError):
    pass


def _interpolate(node: Any) -> Any:
    """Expand ${VAR} and ${VAR:-default} inside every string in the tree."""
    if isinstance(node, str):
        def sub(m):
            val = os.environ.get(m.group(1))
            if val is None:
                val = m.group(2)
            if val is None:
                raise ConfigError(
                    f"config references ${{{m.group(1)}}} but it is not set in the "
                    f"environment and has no ${{{m.group(1)}:-default}}")
            return val
        return _ENV_RE.sub(sub, node)
    if isinstance(node, dict):
        return {k: _interpolate(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_interpolate(v) for v in node]
    return node


def merge(base: dict, over: dict) -> dict:
    """Recursive dict merge; `over` wins. Lists replace rather than concatenate.

    Lists replace deliberately: an eval that overrides `fpr_targets` means "use
    exactly these", and a concatenating merge would silently keep the defaults
    alongside them.
    """
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def resolve_path(ref: str, kind: str | None = None) -> Path:
    """Turn a config reference into a real file.

    Accepts an absolute path, a path relative to the repo, or a bare name that
    is looked up under `configs/<kind>/<name>.yaml`.
    """
    p = Path(ref)
    if p.suffix in (".yaml", ".yml"):
        if p.is_absolute():
            return p
        # A sibling reference like `extends: _base.yaml` resolves inside the
        # child's own kind directory first, so shared defaults can sit beside the
        # configs that inherit them.
        candidates = []
        if kind:
            candidates.append(paths.configs(kind, p))
        candidates += [paths.configs(p), paths.REPO / p]
        for cand in candidates:
            if cand.exists():
                return cand
        return candidates[0]
    if kind is None:
        raise ConfigError(f"cannot resolve config reference {ref!r} without a kind")
    return paths.configs(kind, f"{ref}.yaml")


def load(ref: str, kind: str | None = None, overrides: dict | None = None,
         _seen: tuple = ()) -> dict:
    """Load a config, resolving `extends:` chains and ${ENV} interpolation.

    `kind` is the subdirectory under configs/ used when `ref` is a bare name,
    e.g. load("test5_peer_review", kind="evals").
    """
    f = resolve_path(ref, kind)
    if not f.exists():
        raise ConfigError(f"no such config: {f}")
    key = str(f.resolve())
    if key in _seen:
        raise ConfigError(f"circular extends: {' -> '.join(_seen + (key,))}")

    raw = yaml.safe_load(f.read_text()) or {}
    parents = raw.pop("extends", [])
    if isinstance(parents, str):
        parents = [parents]

    cfg: dict = {}
    for parent in parents:
        cfg = merge(cfg, load(parent, kind=kind, _seen=_seen + (key,)))
    cfg = merge(cfg, raw)
    cfg = merge(cfg, overrides or {})
    cfg = _interpolate(cfg)
    cfg.setdefault("_source", str(f.relative_to(paths.REPO)) if f.is_relative_to(paths.REPO) else str(f))
    return cfg


def parse_overrides(pairs: list[str]) -> dict:
    """Turn `--set a.b=1 --set c=x` into a nested dict for `load(overrides=...)`.

    Values go through the YAML scalar parser, so `true`, `3`, `0.01` and
    `[a, b]` arrive with the type they look like.
    """
    out: dict = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ConfigError(f"--set expects key=value, got {pair!r}")
        key, _, val = pair.partition("=")
        node = out
        parts = key.strip().split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = yaml.safe_load(val)
    return out


def git_revision() -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(paths.REPO), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, check=True).stdout.strip()
    except Exception:
        return None


def stamp(cfg: dict, extra: dict | None = None) -> dict:
    """Provenance record to store beside a result."""
    return {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_revision": git_revision(),
        "config": {k: v for k, v in cfg.items() if not k.startswith("_")},
        "config_source": cfg.get("_source"),
        **(extra or {}),
    }


def add_config_args(ap, kind: str, required: bool = True, flag: str = "--config"):
    """Attach the standard `--config` / `--set` pair to an ArgumentParser."""
    ap.add_argument(flag, required=required,
                    help=f"config name under configs/{kind}/ or a path to a YAML file")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a config value, repeatable (e.g. --set limit=10)")
    return ap


def from_args(args, kind: str, flag: str = "config") -> dict:
    return load(getattr(args, flag), kind=kind, overrides=parse_overrides(args.set))


def list_configs(kind: str) -> list[str]:
    d = paths.configs(kind)
    return sorted(p.stem for p in d.glob("*.yaml") if not p.stem.startswith("_"))
