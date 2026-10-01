"""AI-Researcher (Si, Yang & Hashimoto) -> extraction inputs.

TWO SETS, TWO DIFFERENT CELLS.

airesearch1 -- the ideation study, 147 proposals. The authors standardised the writing style
of EVERY proposal with an LLM so that style could not be a decisive factor for their human
reviewers. That makes the human condition expert ideas wearing model prose (HM), and it is
the hardest version of that cell we have: the surface was laundered deliberately, by people
trying to remove exactly the cue a surface detector reads, for reasons that have nothing to
do with our argument.

airesearch2 -- the execution study, 43 full papers. A researcher spent weeks running and
writing up an idea that came from either an expert or an LLM, so the AI-condition papers are
model ideas in a person's prose at full paper length (MH). Our MH cell otherwise holds three
post-edit sources plus 141-word stories.

Condition is assigned by matching each executed paper's title against the three idea
archives, which reproduces the review data's 24 AI / 19 Human split exactly -- not by
elimination.
"""
import json, re, zipfile, glob, os, hashlib, difflib, sys
from pathlib import Path
import numpy as np

E = Path("${WORK_DIR}/external/airesearcher")
N = Path("${WORK_DIR}/newevals")

def norm(s): return re.sub(r"\s+", " ", s).strip()
def title_of(t):
    """Title from a .txt idea, where the title is its own first line."""
    m = re.match(r"\s*Title:\s*(.+)", t)
    return norm(m.group(1) if m else t[:80]).lower()

def title_of_flat(t):
    """Title from a FLATTENED docx, where newlines are gone and a greedy match would
    swallow the whole document. Stop at the first section marker."""
    m = re.match(r"\s*Title:\s*(.+?)\s*(?:\d\.\s|Problem Statement)", t)
    return norm(m.group(1) if m else t[:80]).lower()

# ---- ideation ----------------------------------------------------------------
ARMS = {"human_ideas": ("human", "expert_idea"),          # HM: expert ideas, LLM-styled prose
        "ai_ideas": ("ai", "model_idea"),
        "ai_rerank_ideas": ("ai", "model_idea_reranked")}
rows1, pools = [], {}
for d, (src, arm) in ARMS.items():
    pools[d] = {}
    for f in sorted(glob.glob(str(E / d / "*" / "*.txt"))):
        t = open(f, encoding="utf8", errors="replace").read().strip()
        pools[d][title_of(t)] = os.path.basename(f)
        if len(t.split()) < 50: continue
        rows1.append({"id": hashlib.sha1(f"air1|{d}|{os.path.basename(f)}".encode()).hexdigest()[:24],
                      "text": t[:30000], "source": src, "arm": arm, "condition": d,
                      "words": len(t.split()),
                      "format": "Academic Writing", "role_format": "academic_writing"})

# ---- execution ---------------------------------------------------------------
from pypdf import PdfReader
P = E / "execution/PaperSubmissions2"
rows2, unmatched = [], 0
for f in sorted(glob.glob(str(P / "Idea#*.docx"))):
    n = os.path.basename(f).split("#")[1].split(".")[0]
    x = zipfile.ZipFile(f).read("word/document.xml").decode("utf8", "replace")
    k = title_of_flat(norm(re.sub(r"<[^>]+>", " ", x)))
    hit = None
    for d, pool in pools.items():
        if k in pool: hit = d; break
        c = difflib.get_close_matches(k, pool, n=1, cutoff=0.82)
        if c: hit = d; break
    if hit is None: unmatched += 1; continue
    pdf = P / f"Paper#{n}.pdf"
    if not pdf.exists(): continue
    try:
        txt = norm(" ".join((pg.extract_text() or "") for pg in PdfReader(str(pdf)).pages))
    except Exception as e:
        print(f"  Paper#{n}: PDF read failed ({type(e).__name__})"); continue
    if len(txt.split()) < 200: print(f"  Paper#{n}: only {len(txt.split())} words, skipped"); continue
    src = "human" if hit == "human_ideas" else "ai"
    rows2.append({"id": hashlib.sha1(f"air2|paper{n}".encode()).hexdigest()[:24],
                  "text": txt[:30000], "source": src,
                  # the executor also edited the idea, so the AI arm is model idea +
                  # human revision + human execution, not purely model-originated
                  "arm": "paper_from_model_idea" if src == "ai" else "paper_from_expert_idea",
                  "paper": f"Paper#{n}", "condition": hit, "words": len(txt.split()),
                  "format": "Academic Writing", "role_format": "academic_writing"})

import collections
for name, rows in (("airesearch1", rows1), ("airesearch2", rows2)):
    p = N / f"{name}_extract_input.jsonl"
    if p.exists(): print(f"  {p.name} exists, skipping"); continue
    with open(p, "w") as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    w = np.array([r["words"] for r in rows])
    print(f"\nwrote {len(rows):,} -> {p.name}")
    for a, c in sorted(collections.Counter(r["arm"] for r in rows).items()):
        ww = [r["words"] for r in rows if r["arm"] == a]
        s = [r["source"] for r in rows if r["arm"] == a][0]
        print(f"  {a:<26} n={c:>4}  ideas={s:<6} median {np.median(ww):>6.0f}w")
    print(f"  overall median {np.median(w):.0f}w   est extraction ${len(rows)*0.03:,.2f}")
if unmatched: print(f"\n  {unmatched} executed papers could not be matched to a condition")
print("BUILD_AIRESEARCHER_DONE")
