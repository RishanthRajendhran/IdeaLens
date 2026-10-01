#!/usr/bin/env python3
"""Stage 0: assign every document a WebOrganizer format.

Run this on EVERY new corpus, including ones that obviously contain only one
kind of document. The extraction prompt is format-conditioned — it carries that
format's role vocabulary and its exemplars, and the response schema's role enum
is per format — so a wrong label produces an outline that looks valid and is
extracted against the wrong vocabulary.

Nine of WebOrganizer's 24 categories map onto a role vocabulary we possess.
Documents in the other fifteen are out of scope and are filtered out, not
remapped to something nearby.

    python scripts/pipeline/classify_format.py --eval test10_detectionai \
        --config format_llm_flash
    python scripts/pipeline/classify_format.py --eval my_new_set \
        --config format_encoder --set device=cuda
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from ideadet import config as C
from ideadet import registry
from ideadet.io import load_jsonl, write_json, write_jsonl
from ideadet.pipeline import format_classify as FC


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval", required=True)
    C.add_config_args(ap, "pipeline", required=False)
    ap.set_defaults(config="format_llm_flash")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="", help="default: data/<eval>/formats.jsonl")
    ap.add_argument("--apply", action="store_true",
                    help="write the labels back into corpus.jsonl (keeps a .bak)")
    a = ap.parse_args()

    cfg = C.from_args(a, "pipeline")
    ev = registry.get_eval(a.eval)
    rows = load_jsonl(ev.corpus, a.limit or None)
    print(f"{ev}: {len(rows):,} documents, backend={cfg['backend']}")

    # Results come back keyed by id, so a repeated id silently drops rows.
    ids = [r["id"] for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1} if len(ids) < 20000 else set()
    if dupes:
        raise SystemExit(
            f"ABORT: {len(dupes):,} duplicate id(s), e.g. {sorted(dupes)[:3]}. "
            f"Ids must be unique or results cannot be joined back.")

    if cfg["backend"] == "encoder":
        results = FC.classify_encoder(
            [r["text"] for r in rows], [r.get("url", "") for r in rows],
            device=cfg.get("device", "cuda"), batch_size=cfg.get("batch_size", 16),
            max_length=cfg.get("max_length", 8192), use_url=cfg.get("use_url", True))
    else:
        from ideadet.llm import vertex_batch as VB
        # Sort so identical system prefixes sit consecutively: that is what earns
        # the cached-input discount, and it is a several-fold cost difference.
        sort_keys = [k for k in ("domain", "genre", "model", "arm")
                     if rows and k in rows[0]]
        rows.sort(key=lambda r: tuple(str(r.get(k, "")) for k in sort_keys))
        reqs = FC.build_llm_requests(rows, model=cfg["model"],
                                     max_chars=cfg.get("max_chars", 0),
                                     max_output_tokens=cfg.get("max_output_tokens", 1024))
        raw = VB.run_batch(reqs, cfg["model"], bucket=cfg["gcs"]["bucket"],
                           prefix=cfg["gcs"]["prefix"], tag=f"{a.eval}_format",
                           want_json=False, poll_interval=cfg.get("poll_interval", 60),
                           user_label=cfg.get("billing_label", ""))
        results = []
        for r in rows:
            label = FC.parse_llm_label(raw.get(r["id"], ""))
            results.append({"weborganizer_label": label,
                            "format": FC.to_our_format(label) if label else None,
                            "backend": cfg["model"], "raw": raw.get(r["id"])})

    out = [{"id": r["id"], **res} for r, res in zip(rows, results)]
    dest = a.out or (ev.path / "formats.jsonl")
    write_jsonl(dest, out)
    print(FC.summarize(results))
    print(f"\nwrote {dest}")
    write_json(ev.path / "formats_run.json",
               C.stamp(cfg, {"eval": a.eval, "n": len(out),
                             "n_in_scope": sum(1 for r in out if r.get("format"))}))

    if a.apply:
        from ideadet import formats as F
        by_id = {r["id"]: r for r in out}
        kept = []
        for r in load_jsonl(ev.corpus):
            fmt = (by_id.get(r["id"]) or {}).get("format")
            if not fmt:
                continue                     # out of scope: filtered, not remapped
            r["format"] = fmt
            r["role_format"] = F.slug(fmt)
            kept.append(r)
        # Write THROUGH the symlink, and back up by copy rather than rename.
        # data/<eval>/corpus.jsonl is normally a link into the source tree (see
        # scripts/data/link_sources.py); renaming the target and writing to the
        # link path replaces the link with a real file and silently orphans the
        # source, so every later run reads a stale corpus.
        import shutil
        target = ev.corpus.resolve()
        shutil.copy2(target, str(target) + ".bak")
        write_jsonl(target, kept)
        print(f"applied: {len(kept):,} rows kept, previous corpus saved as .bak")


if __name__ == "__main__":
    sys.exit(main())
