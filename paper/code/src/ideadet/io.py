"""File I/O helpers shared by every stage.

Two rules this module exists to enforce:

  * **Writes are atomic.** A job killed by the Slurm time limit halfway through
    a 900 MB JSONL must not leave a file that parses for the first 800 MB and
    then stops. Everything is written to a temporary sibling and renamed, which
    is atomic on POSIX filesystems.
  * **Raw model outputs are never discarded.** `save_scores` keeps logits and
    every metadata column alongside the probability, because re-scoring is
    expensive and a summary written today cannot answer tomorrow's question.
"""
from __future__ import annotations

import gzip
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Iterator

import numpy as np


def _open(path: Path, mode: str):
    return gzip.open(path, mode + "t") if str(path).endswith(".gz") else open(path, mode)


def read_jsonl(path: str | Path, limit: int | None = None) -> Iterator[dict]:
    """Stream a JSONL file. Blank lines are skipped; a bad line raises with its number."""
    path = Path(path)
    with _open(path, "r") as fh:
        for i, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{i}: {e}") from None
            if limit and i >= limit:
                return


def load_jsonl(path: str | Path, limit: int | None = None) -> list[dict]:
    return list(read_jsonl(path, limit))


def write_jsonl(path: str | Path, rows: Iterable[dict], append: bool = False) -> int:
    """Write rows as JSONL. Returns the row count. Atomic unless `append`."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if append:
        n = 0
        with _open(path, "a") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
        return n
    n = 0
    with _atomic(path) as tmp:
        with _open(tmp, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    return n


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())


def write_json(path: str | Path, obj: Any, indent: int = 2) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _atomic(path) as tmp:
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=indent, default=_default))
    return path


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")


class _atomic:
    """Context manager yielding a temp path in the same directory, renamed on exit."""

    def __init__(self, target: Path):
        self.target = Path(target)

    def __enter__(self) -> Path:
        fd, tmp = tempfile.mkstemp(dir=self.target.parent,
                                   prefix=f".{self.target.name}.", suffix=".tmp")
        os.close(fd)
        self.tmp = Path(tmp)
        return self.tmp

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            os.replace(self.tmp, self.target)
        else:
            self.tmp.unlink(missing_ok=True)
        return False


def save_npz(path: str | Path, **arrays) -> Path:
    """Compressed .npz, atomically. Object arrays (strings) are allowed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _atomic(path) as tmp:
        # np.savez_compressed appends .npz unless the handle is already open
        with open(tmp, "wb") as fh:
            np.savez_compressed(fh, **arrays)
    return path


def load_npz(path: str | Path) -> dict:
    """Load an .npz into a plain dict, so callers cannot accidentally re-read.

    NpzFile decompresses a member on EVERY attribute access. Looping over rows
    while indexing `z["p_human"]` inside the loop re-reads the whole array each
    iteration; hoisting the members here removes that failure mode entirely.
    """
    with np.load(path, allow_pickle=True) as z:
        return {k: z[k] for k in z.files}


def save_scores(path: str | Path, *, doc_ids, p_human, y=None, logits=None,
                meta: dict | None = None, **extra) -> Path:
    """Canonical per-document score file.

    Always stores the raw logits when the backend produces them: a probability
    is a lossy summary, and margins, temperature studies and re-pooling all need
    the pre-softmax values that only exist at scoring time.
    """
    arrays = {"doc_ids": np.asarray([str(x) for x in doc_ids], dtype=object),
              "p_human": np.asarray(p_human, dtype=np.float64)}
    if y is not None:
        arrays["y"] = np.asarray(y, dtype=np.int64)
    if logits is not None:
        arrays["logits"] = np.asarray(logits, dtype=np.float32)
    for k, v in {**(meta or {}), **extra}.items():
        arrays[k] = np.asarray(v, dtype=object if not np.isscalar(v) and
                               not np.issubdtype(np.asarray(v).dtype, np.number) else None)
    return save_npz(path, **arrays)


def scores_to_jsonl(npz_path: str | Path) -> list[dict]:
    """Row-wise view of a score file, for joins and human inspection."""
    z = load_npz(npz_path)
    n = len(z["doc_ids"])
    keys = [k for k in z if k != "logits" and len(np.atleast_1d(z[k])) == n]
    return [{k: (z[k][i].item() if hasattr(z[k][i], "item") else z[k][i]) for k in keys}
            for i in range(n)]


def iter_outline_files(directory: str | Path) -> Iterator[tuple[str, dict]]:
    """Yield (document id, outline record) for one stage of one eval.

    TWO ON-DISK LAYOUTS, both supported, because they suit different sizes:

      `deleak/<id>.json`  one file per document. What the pipeline writes, so a
                          run that dies part-way resumes from what already landed
                          rather than restarting a 25,000-document batch.
      `deleak.jsonl`      one row per document in a single file. How the larger
                          externally-built sets arrive; at 20,000+ documents the
                          per-file layout costs more in inodes and directory
                          walks than it returns.

    The sibling `.jsonl` wins when both exist, since that is the compact form.
    """
    directory = Path(directory)
    flat = directory.with_suffix(".jsonl")
    if flat.exists():
        for rec in read_jsonl(flat):
            doc_id = rec.get("id")
            if doc_id is not None:
                yield str(doc_id), rec
        return
    for f in sorted(directory.glob("*.json")):
        try:
            yield f.stem, json.loads(f.read_text())
        except json.JSONDecodeError:
            continue


def count_outlines(directory: str | Path) -> int:
    """Number of outlines in a stage, under either layout."""
    directory = Path(directory)
    flat = directory.with_suffix(".jsonl")
    if flat.exists():
        return sum(1 for _ in _open(flat, "r"))
    return len(list(directory.glob("*.json"))) if directory.exists() else 0


def has_outlines(directory: str | Path) -> bool:
    directory = Path(directory)
    return directory.with_suffix(".jsonl").exists() or directory.is_dir()
