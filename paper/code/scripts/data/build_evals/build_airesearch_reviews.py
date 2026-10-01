"""AI-Researcher reviews -> extraction input. A contamination control, not a detection set.

Every one of these 518 reviews was written by a human expert, so under the idea-level rule
every row is HUMAN and every fire is a false positive. The point is not the level but the
GAP: the reviews are stratified by the origin of the thing reviewed, so if we fire more on
reviews of model-generated ideas than on reviews of human ones, the detector is reading
content bleed from the reviewed object rather than whose ideas the review itself commits to.
Criticising someone else's idea is not holding it. The null is a flat rate across conditions.

Each review's separate rationale fields are concatenated into one document -- a single
rationale is too short to yield a usable outline.
"""
import json, hashlib
from pathlib import Path
import numpy as np

E = Path("${WORK_DIR}/external/AI-Researcher")
N = Path("${WORK_DIR}/newevals")
OUT = N / "airreviews_extract_input.jsonl"
if OUT.exists():
    raise SystemExit(f"{OUT} exists -- refusing to overwrite")

SETS = [("reviews_ideation/data_points_all_anonymized.json", "ideation",
         ["novelty_rationale", "feasibility_rationale", "effectiveness_rationale",
          "excitement_rationale", "overall_rationale"]),
        ("reviews_execution/data_points_all_execution.json", "execution",
         ["novelty_rationale", "excitement_rationale", "soundness_rationale",
          "effectiveness_rationale", "overall_rationale", "faithfulness_rationale"])]
LABEL = {"novelty_rationale": "Novelty", "feasibility_rationale": "Feasibility",
         "effectiveness_rationale": "Effectiveness", "excitement_rationale": "Excitement",
         "overall_rationale": "Overall", "soundness_rationale": "Soundness",
         "faithfulness_rationale": "Faithfulness"}

rows = []
for f, stage, fields in SETS:
    d = json.load(open(E / f))
    n = len(next(iter(d.values())))
    for i in range(n):
        parts = []
        for k in fields:
            v = str(d[k][i] or "").strip()
            if v and v.lower() not in ("na", "n/a", "none", "-"):
                parts.append(f"{LABEL[k]}: {v}")
        txt = "\n\n".join(parts)
        if len(txt.split()) < 60:            # too thin to decompose into an outline
            continue
        cond = str(d["condition"][i]) if "condition" in d else "?"
        rows.append({
            "id": hashlib.sha1(f"airrev|{stage}|{i}".encode()).hexdigest()[:24],
            "text": txt[:30000],
            "source": "human",               # every review is written by a human expert
            "arm": f"{stage}_review_of_{cond.lower()}",
            "stage": stage, "reviewed_condition": cond,
            "topic": str(d["topic"][i]) if "topic" in d else "",
            "words": len(txt.split()),
            "format": "Academic Writing", "role_format": "academic_writing"})

with open(OUT, "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
import collections
w = np.array([r["words"] for r in rows])
print(f"wrote {len(rows):,} -> {OUT.name}")
for a, c in sorted(collections.Counter(r["arm"] for r in rows).items()):
    ww = [r["words"] for r in rows if r["arm"] == a]
    print(f"  {a:<34} n={c:>4}   median {np.median(ww):>4.0f}w")
print(f"  all rows are human-written; every fire is a false positive")
print(f"  overall median {np.median(w):.0f}w   est extraction ${len(rows)*0.03:,.2f}")
print("BUILD_AIRREVIEWS_DONE")
