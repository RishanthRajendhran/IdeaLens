"""ELLIPSE -> extraction input. The non-native English fairness eval.

WHAT IS BEING TESTED. Liang et al. found surface detectors fire far more often on non-native
English writing. Their result is a GAP, not a level, so the reportable quantity is FPR on
these essays against FPR on length- and format-matched NATIVE writing at the same deployed
cut. The native side is free: our 1M corpus is already extracted, so only this side costs
anything.

WHY ELLIPSE RATHER THAN A PLAIN L2 SET. Every essay carries a 1-5 holistic proficiency score
plus analytic sub-scores. That turns a single FPR number into a slope: if outline extraction
discards the L2 surface markers that drive the bias, FPR should be roughly FLAT across
proficiency, while a surface reader's should climb as proficiency falls. A flat line is a far
stronger claim than a low average, and it cannot be faked by a conservative threshold.

Every row is HUMAN, so this set has no AI arm and no TPR -- it is FPR-only, like the human
side of OpAI-Bench.

CC BY-NC-SA 4.0, non-commercial research use.
"""
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

SRC = Path("${WORK_DIR}/external/ELLIPSE-Corpus/"
           "ELLIPSE_Final_github_train.csv")
OUT = Path("${WORK_DIR}/newevals/ellipse1_extract_input.jsonl")
if OUT.exists():
    raise SystemExit(f"{OUT} exists -- refusing to overwrite")

d = pd.read_csv(SRC)
rows = []
for r in d.itertuples(index=False):
    t = str(r.full_text or "").strip()
    n = len(t.split())
    if n < 50:                    # below this an outline has nothing to decompose
        continue
    band = int(round(float(r.Overall)))
    rows.append({
        "id": hashlib.sha1(f"ellipse|{r.text_id_kaggle}".encode()).hexdigest()[:24],
        "text": t,
        "source": "human",        # every row; this set is FPR-only by construction
        "arm": f"prof_{band}",
        "proficiency": float(r.Overall), "prof_band": band,
        "cohesion": float(r.Cohesion), "syntax": float(r.Syntax),
        "vocabulary": float(r.Vocabulary), "grammar": float(r.Grammar),
        "conventions": float(r.Conventions),
        "grade": int(r.grade), "words": n,
        # school argumentative essays on a set prompt
        "format": "Academic Writing", "role_format": "academic_writing"})

with open(OUT, "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
import collections
w = np.array([r["words"] for r in rows])
print(f"wrote {len(rows):,} -> {OUT}   (dropped {len(d)-len(rows)} under 50 words)")
print(f"  words: med {np.median(w):.0f}  mean {w.mean():.0f}  >=300w {100*(w>=300).mean():.0f}%")
print("  by proficiency band:")
for b, n in sorted(collections.Counter(r["prof_band"] for r in rows).items()):
    ww = [r["words"] for r in rows if r["prof_band"] == b]
    print(f"    {b}  n={n:>5,}  median {np.median(ww):>4.0f}w")
print(f"  est extraction @ $0.021/doc: ${len(rows)*0.021:,.0f}")
print("BUILD_ELLIPSE_DONE")
