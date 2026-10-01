"""Thresholds: where cuts come from, and how a P(human) becomes verdicts.

A document is flagged as AI when P(human) < cut (strictly below, the rule every reported number in the paper uses).
Cuts are low quantiles of P(human) over human documents, so a cut at FPR q flags about q of human documents.

Sources: a model repo's thresholds.json (the default), a JSON file, or a named profile saved by `idealens calibrate`.
Schemes: "global", "per_format", "per_topic", and "group:<field>" for cuts a user fitted per value of their own field.

No fallback: when a document's format, topic or group has no cut (not calibrated, not estimable, or a forced
format), that verdict is None with a reason. It is never replaced by the global cut, which would silently mix two
operating points.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

DEFAULT_FPR = 0.01
DEFAULT_SCHEME = "global"
_TABLES = {"per_format": "format", "per_topic": "topic"}

#: What the published cuts assume about how outlines were made. Departures are warned about, not refused.
REPO_PROVENANCE = {"extractor_model": "gemini-3.7-flash", "few_shot": True}


def profiles_dir() -> Path:
    base = os.environ.get("IDEALENS_HOME") or os.path.join(
        os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"), "idealens")
    return Path(base) / "thresholds"


def _fpr_key(table: dict, fpr: float) -> str | None:
    for k in table:
        if abs(float(k) - float(fpr)) < 1e-12:
            return k
    return None


class Thresholds:
    def __init__(self, data: dict, source: str):
        self.data = data
        self.source = source
        raw = json.dumps(data, sort_keys=True).encode()
        self.sha256 = hashlib.sha256(raw).hexdigest()

    # ------------------------------------------------------------------ loading
    @classmethod
    def for_model(cls, spec, revision: str | None = None) -> "Thresholds":
        """The published cuts in the model's repo."""
        from huggingface_hub import hf_hub_download
        path = hf_hub_download(spec.repo, "thresholds.json", revision=revision)
        return cls(json.loads(Path(path).read_text()), source=f"repo:{spec.repo}")

    @classmethod
    def load(cls, ref: str | os.PathLike) -> "Thresholds":
        """A thresholds JSON file, or the name of a saved profile."""
        p = Path(ref)
        if p.suffix == ".json" or p.exists():
            return cls(json.loads(p.read_text()), source=f"file:{p}")
        prof = profiles_dir() / f"{ref}.json"
        if prof.exists():
            return cls(json.loads(prof.read_text()), source=f"profile:{ref}")
        raise FileNotFoundError(f"no thresholds file or saved profile named {ref!r} (profiles live in {profiles_dir()})")

    def save(self, path: str | os.PathLike) -> Path:
        p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.data, indent=1) + "\n")
        return p

    def save_profile(self, name: str, overwrite: bool = False) -> Path:
        p = profiles_dir() / f"{name}.json"
        if p.exists() and not overwrite:
            raise FileExistsError(f"profile {name!r} exists at {p}; pass overwrite=True to replace it")
        return self.save(p)

    # ------------------------------------------------------------------ access
    @property
    def model(self) -> str | None:
        m = self.data.get("model")
        return m.split("/")[-1] if m else None

    def table(self, scheme: str) -> dict | None:
        if scheme == "global":
            return self.data.get("global")
        if scheme in _TABLES:
            return self.data.get(scheme)
        if scheme.startswith("group:"):
            return (self.data.get("per_group") or {}).get(scheme[len("group:"):])
        raise ValueError(f"unknown scheme {scheme!r}; use global, per_format, per_topic or group:<field>")

    def schemes(self) -> list[str]:
        out = ["global"] + [s for s in _TABLES if self.data.get(s)]
        return out + [f"group:{f}" for f in (self.data.get("per_group") or {})]

    def cut(self, scheme: str, fpr: float, key: str | None = None) -> float | None:
        t = self.table(scheme)
        if not t:
            return None
        k = _fpr_key(t, fpr)
        if k is None:
            return None
        return t[k] if scheme == "global" else t[k].get(key)

    # ------------------------------------------------------------------ verdicts
    def verdicts(self, p_human: float, format: str | None = None, topic: str | None = None,
                 groups: dict | None = None, forced_format: bool = False) -> dict:
        """Every calibrated FPR under every scheme this file has. Entries that cannot be judged are None with a
        reason under "unavailable"."""
        groups = groups or {}
        out = {}
        for scheme in self.schemes():
            t = self.table(scheme)
            if scheme == "global":
                out[scheme] = {k: {"cut": c, "ai": bool(p_human < c)} for k, c in t.items()}
                continue
            if scheme == "per_format":
                key, why = format, ("forced_format" if forced_format else None if format else "no format")
            elif scheme == "per_topic":
                key, why = topic, (None if topic else "no topic")
            else:
                field = scheme[len("group:"):]
                key = groups.get(field)
                why = None if key is not None else f"no value for {field!r}"
            if why:
                out[scheme] = {"unavailable": why}
                continue
            entry = {}
            for k, cells in t.items():
                c = cells.get(key)
                entry[k] = {"cut": c, "ai": bool(p_human < c)} if c is not None else None
            if all(v is None for v in entry.values()):
                out[scheme] = {"unavailable": f"no cut for {key!r}"}
            else:
                out[scheme] = entry
        return out

    def verdict(self, p_human: float, fpr: float = DEFAULT_FPR, scheme: str = DEFAULT_SCHEME,
                format: str | None = None, topic: str | None = None, groups: dict | None = None,
                forced_format: bool = False) -> dict:
        """The headline verdict: one scheme, one FPR. ai is None (with a reason) when there is no cut."""
        v = {"fpr": fpr, "scheme": scheme, "thresholds": self.source}
        if scheme == "per_format" and forced_format:
            return v | {"ai": None, "cut": None, "reason": "forced_format"}
        key = {"per_format": format, "per_topic": topic}.get(scheme)
        if scheme.startswith("group:"):
            key = (groups or {}).get(scheme[len("group:"):])
        if scheme != "global" and key is None:
            return v | {"ai": None, "cut": None, "reason": f"no value for {scheme}"}
        c = self.cut(scheme, fpr, key)
        if c is None:
            return v | {"ai": None, "cut": None, "reason": f"no cut at FPR {fpr} for {key or scheme}"}
        return v | {"ai": bool(p_human < c), "cut": c}

    # ------------------------------------------------------------------ compatibility
    def check(self, model: str, run: dict) -> list[str]:
        """Compare how these cuts were fitted with how this run scores. Raises on a different model; returns
        warnings for differences that shift scores (extractor, examples, classifier)."""
        if self.model and self.model != model:
            raise ValueError(f"thresholds from {self.source} were fitted for {self.model}, not {model}")
        prov = self.data.get("provenance") or REPO_PROVENANCE
        warn = []
        for k in ("extractor_provider", "extractor_model", "few_shot", "format_method"):
            if k in prov and k in run and run[k] is not None and prov[k] != run[k]:
                warn.append(f"{k} is {run[k]!r} but the cuts in {self.source} were fitted with {prov[k]!r}")
        if "backend" in prov and run.get("backend") and prov["backend"] != run["backend"]:
            warn.append(f"note: cuts fitted with backend {prov['backend']!r}, scoring with {run['backend']!r} "
                        f"(these agree to about 0.004 in P(human))")
        return warn
