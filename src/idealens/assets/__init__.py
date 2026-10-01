"""The frozen prompts shipped with the package (built by tools/build_assets.py from the project's canonical builders).
Never edited by hand: every outline and label records the prompt version and hash it was made with."""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=None)
def extraction() -> dict:
    return json.loads(files("idealens.assets").joinpath("extraction.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def classifier() -> dict:
    return json.loads(files("idealens.assets").joinpath("classifier.json").read_text(encoding="utf-8"))
