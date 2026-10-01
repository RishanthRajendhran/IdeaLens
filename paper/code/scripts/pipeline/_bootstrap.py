"""Put `src/` on the import path.

Imported as `import _bootstrap` at the top of every script, so the repository
runs from a fresh clone with no install step and no PYTHONPATH to remember.
`pip install -e .` also works and makes this import a harmless no-op.

Walks up from this file until it finds `src/ideadet`, so a copy of this file
works at any depth under `scripts/`.
"""
import sys
from pathlib import Path

for _parent in Path(__file__).resolve().parents:
    _src = _parent / "src"
    if (_src / "ideadet").is_dir():
        if str(_src) not in sys.path:
            sys.path.insert(0, str(_src))
        break
else:  # pragma: no cover
    raise ImportError(
        "cannot find src/ideadet above this script. Run scripts from inside the "
        "repository, or `pip install -e .`.")
