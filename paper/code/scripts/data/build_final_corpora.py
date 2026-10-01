#!/usr/bin/env python3
"""Build the document corpora whose FINAL instance set is not a single existing file.

Most evals already have one file holding every document we sampled, and `data/<eval>/`
simply links to it. Seven do not, because the final set was assembled after the fact:

    indomain                 the 1M corpus's held-out test split (parquet -> jsonl)
    test3  rungs 0-5         the 2,500-document scale-up plus the 500 rung-0 generations
    test4  sources           the 625 documents the three extractors were run over
    test7  DetectRL-X A/B    plans A and B of the DetectRL-X build
    test14 partial docs      the original 1,486 windows plus the 3,210-window rebuild
    test20 HART              the test split plus the dev split
    test24 DetectRL-X C      plan C, the attack sweep

Every document keeps its original id, so any prediction made on these files joins back
to whichever subset a result is reported over. Rows are copied, never altered, apart from
a `_part` field naming the file each came from. Refuses to overwrite, and aborts on a
duplicate id whose text differs between parts.

    python scripts/data/build_final_corpora.py [--out DIR]
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

W = Path("${WORK_DIR}")
N = W / "newevals"


def rows(path: Path):
    with open(path) as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def union(parts: list[tuple[str, Path]], keep=lambda r: True) -> list[dict]:
    out, seen = [], {}
    for name, p in parts:
        for r in rows(p):
            if not keep(r):
                continue
            i = str(r["id"])
            if i in seen:
                if (seen[i] or "") != (r.get("text") or ""):
                    raise SystemExit(f"id {i} appears in two parts with DIFFERENT text")
                continue                       # same window listed twice: keep the first
            seen[i] = r.get("text")
            out.append({**r, "_part": name})
    return out


def indomain() -> list[dict]:
    import pyarrow.parquet as pq
    out = []
    for f in sorted(glob.glob(str(W / "v391/hf_push_splits/test-*.parquet"))):
        for r in pq.read_table(f, columns=["id", "source", "format", "role_format", "topic",
                                           "url", "word_count", "source_text"]).to_pylist():
            out.append({"id": r["id"], "text": r["source_text"], "source": r["source"],
                        "format": r["format"], "role_format": r["role_format"],
                        "topic": r["topic"], "url": r["url"],
                        "words": int(r["word_count"]) if str(r["word_count"]).isdigit() else None,
                        "_part": "hf_push_splits/test"})
    return out


def outlines(out: Path):
    """Stage-1 / stage-2 OUTLINE files for the evals whose final set spans several files.

    Same rules as the corpora: rows copied unaltered plus `_part`, exact expected counts,
    no duplicate ids, refuse to overwrite. DetectRL-X outlines carry no `plan` field, so
    the split takes it from the document file by id.
    """
    M = W / "multiling"
    plan = {json.loads(l)["id"]: json.loads(l).get("plan") for l in open(N / "drlx2_format_input.jsonl")}
    build = {
        "t3_rungs0to5_outlines.jsonl": ([("t3gen", N / "t3gen_outlines.jsonl"),
                                         ("t3rung0", N / "t3rung0_outlines.jsonl")], None, 3000),
        "t3_rungs0to5_deleaked.jsonl": ([("t3gen", N / "t3gen_deleaked.jsonl"),
                                         ("t3rung0", N / "t3rung0_deleaked.jsonl")], None, 3000),
        "drlx2_planAB_outlines.jsonl": ([("drlx2", N / "drlx2_outlines.jsonl")],
                                        lambda r: plan.get(r["id"]) in ("A", "B"), None),
        "drlx2_planC_outlines.jsonl": ([("drlx2", N / "drlx2_outlines.jsonl")],
                                       lambda r: plan.get(r["id"]) == "C", None),
        "multiling9_outlines.jsonl": ([("human_pages", M / "outlines.jsonl"),
                                       ("ladder_rungs", M / "ladder_outlines_full.jsonl")], None, 12686),
        "t5_partial_consolidated_outlines.jsonl": ([
            ("partial_full", N / "partial_full_outlines.jsonl"),
            ("partial_windows_only", N / "partial_windows_only_outlines.jsonl"),
            ("t5b", N / "t5b_outlines.jsonl"), ("t5c", N / "t5c_outlines.jsonl"),
            ("t5c_fa", N / "t5c_fa_outlines.jsonl")], None, 4696),
        # only the original half was ever de-leaked; the rebuild has stage 1 only
        "t5_partial_original_deleaked.jsonl": ([
            ("partial_full", N / "partial_full_deleaked.jsonl"),
            ("partial_windows_only", N / "partial_windows_only_deleaked.jsonl")], None, 1486),
        "hart_test_dev_outlines.jsonl": ([("hart_test", N / "hart_outlines.jsonl"),
                                          ("hart_dev", N / "hartdev_outlines.jsonl")], None, 30642),
    }
    od = out / "outlines"; od.mkdir(parents=True, exist_ok=True)
    got = {}
    for name, (parts, keep, expect) in build.items():
        rs = union(parts, keep or (lambda r: True))
        if expect is not None and len(rs) != expect:
            raise SystemExit(f"{name}: {len(rs):,} rows, expected {expect:,}")
        got[name] = len(rs)
        p = od / name
        if p.exists():
            print(f"  outlines/{name}: exists, left untouched"); continue
        with open(p, "w") as fh:
            for r in rs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  wrote outlines/{name}: {len(rs):,} rows")
    if got["drlx2_planAB_outlines.jsonl"] + got["drlx2_planC_outlines.jsonl"] != 33375:
        raise SystemExit("DetectRL-X outline split does not add back to 33,375")
    print("BUILD_OUTLINES_DONE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(W / "final_corpora"))
    ap.add_argument("--outlines", action="store_true", help="build the outline files instead")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.outlines:
        outlines(out); return

    ind = indomain()
    t4src = {r["src_id"] for r in rows(N / "t4alt_outlines.jsonl")}
    build = {
        "indomain_test.jsonl": ind,
        "t4_sources.jsonl": [r for r in ind if r["id"] in t4src],
        "t3_rungs0to5.jsonl": union([("t3_generated", W / "scaleup/t3_generated.jsonl"),
                                     ("t3_generated_rung0", W / "scaleup/t3_generated_rung0.jsonl")]),
        "t5_partial_consolidated.jsonl": union([
            ("partial_full", N / "partial_full_extract_input.jsonl"),
            ("partial_windows_only", N / "partial_windows_only_extract_input.jsonl"),
            ("t5b", N / "t5b_format_input.jsonl"),
            ("t5c", N / "t5c_format_input.jsonl")]),
        "hart_test_dev.jsonl": union([("hart_test", N / "hart_format_input.jsonl"),
                                      ("hart_dev", N / "hartdev_format_input.jsonl")]),
        "drlx2_planAB.jsonl": union([("drlx2", N / "drlx2_format_input.jsonl")],
                                    keep=lambda r: r.get("plan") in ("A", "B")),
        "drlx2_planC.jsonl": union([("drlx2", N / "drlx2_format_input.jsonl")],
                                   keep=lambda r: r.get("plan") == "C"),
    }
    EXPECT = {"indomain_test.jsonl": 48869, "t4_sources.jsonl": 625, "t3_rungs0to5.jsonl": 3000,
              "t5_partial_consolidated.jsonl": 4696, "hart_test_dev.jsonl": 31951,
              "drlx2_planAB.jsonl": 28000, "drlx2_planC.jsonl": 6500}
    manifest = {}
    for name, rs in build.items():
        ids = [r["id"] for r in rs]
        if len(ids) != len(set(ids)):
            raise SystemExit(f"{name}: duplicate ids")
        if len(rs) != EXPECT[name]:
            raise SystemExit(f"{name}: {len(rs):,} rows, expected {EXPECT[name]:,}")
        if any(not (r.get("text") or "").strip() for r in rs):
            raise SystemExit(f"{name}: a row has no text")
        p = out / name
        if p.exists():
            print(f"  {name}: exists, left untouched"); continue
        with open(p, "w") as fh:
            for r in rs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        manifest[name] = {"rows": len(rs), "parts": sorted({r["_part"] for r in rs})}
        print(f"  wrote {name}: {len(rs):,} rows from {manifest[name]['parts']}")
    mp = out / "MANIFEST.json"
    old = json.loads(mp.read_text()) if mp.exists() else {}
    mp.write_text(json.dumps({**old, **manifest}, indent=1))
    print("BUILD_FINAL_DONE")


if __name__ == "__main__":
    main()
