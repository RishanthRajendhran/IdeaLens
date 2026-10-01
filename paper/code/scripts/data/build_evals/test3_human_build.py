"""Build the human control arm for Test 3 from the published 391k dataset.

Test 3 as generated has no human documents, so neither arm's realised FPR is measurable
on it and the per-condition fire rates float at an unknown operating point. These are the
SAME 48 source documents the five conditions were derived from, so adding their own
de-leaked outlines pins FPR and makes the ladder readable as TPR at a measured FPR.

source_text and the dataset's own pangram4_* columns come along for the artifact.
"""
import json, collections
from pathlib import Path
import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

V = Path("${WORK_DIR}/v391")
E = Path("${AUX_DIR}/detector/evals/test3_human")
(E / "deleak").mkdir(parents=True, exist_ok=True)

want = {json.loads(l)["id"] for l in open(V / "test3_sample.jsonl")}
print(f"looking for {len(want)} source documents", flush=True)

COLS = ["id", "source", "format", "role_format", "topic", "word_count", "split",
        "source_text", "deleaked_outline", "extractor", "paraphraser",
        "pangram4_prediction", "pangram4_fraction_ai", "pangram4_fraction_ai_assisted",
        "pangram4_fraction_human"]
fs = HfFileSystem()
# The corpus in its pre-release layout. The released WildOutlines renames these columns (source_text -> text,
# deleaked_outline -> paraphrased_outline; the Pangram labels sit under metadata).
base = "datasets/anonymous/idealens-corpus/data"
rows = {}
for f in sorted(fs.ls(base, detail=False)):
    if len(rows) == len(want):
        break
    with fs.open(f, "rb") as fh:
        t = pq.ParquetFile(fh).read(columns=COLS).to_pydict()
    for k in range(len(t["id"])):
        if t["id"][k] in want and t["id"][k] not in rows:
            rows[t["id"][k]] = {c: t[c][k] for c in COLS}
    print(f"  {Path(f).name}: {len(rows)}/{len(want)}", flush=True)

missing = want - set(rows)
if missing:
    print(f"  MISSING {len(missing)}: {sorted(missing)[:5]}", flush=True)

labels = {}
for did, r in rows.items():
    o = r["deleaked_outline"] or {}
    rid = f"t3human_{did}"
    doc = {"id": rid, "data": {"document_description": o.get("document_description") or "",
                               "global_themes": list(o.get("global_themes") or []),
                               "items": [dict(i) for i in (o.get("items") or [])]},
           "format": r["format"], "role_format": r["role_format"],
           "extractor": r["extractor"], "paraphraser": r["paraphraser"],
           "source": "human", "level": "condition_0_human_original",
           "subset": None, "draw": None, "humanized": False, "model": None}
    (E / "deleak" / f"{rid}.json").write_text(json.dumps(doc))
    labels[rid] = {"source": "human", "model": None,
                   "level": "condition_0_human_original"}
(E / "labels.json").write_text(json.dumps(labels, indent=1))

# source_text + the dataset's own Pangram 4 verdict, for the artifact
with open(V / "test3_originals.jsonl", "w") as fh:
    for did, r in rows.items():
        fh.write(json.dumps({
            "id": did, "format": r["format"], "topic": r["topic"],
            "word_count": r["word_count"], "source_text": r["source_text"],
            "deleaked_outline": {
                "document_description": (r["deleaked_outline"] or {}).get("document_description"),
                "global_themes": list((r["deleaked_outline"] or {}).get("global_themes") or []),
                "items": [dict(i) for i in ((r["deleaked_outline"] or {}).get("items") or [])]},
            "pangram4": {k.replace("pangram4_", ""): r[k] for k in COLS
                         if k.startswith("pangram4_")}}) + "\n")
print(f"wrote {len(rows)} deleak files + test3_originals.jsonl", flush=True)
print("pangram4 on originals:",
      dict(collections.Counter(r["pangram4_prediction"] for r in rows.values())), flush=True)
