"""Build format-classification inputs for ARB and CoAuthor.

ARB carries content_origin and surface_origin as ground truth, so y follows CONTENT origin
-- the idea-level rule -- and surface_origin rides along as metadata for the quadrant plot.

CoAuthor has no document-level gold label and should not be given one by fiat: at ~20% AI
share the writer supplies every idea, at ~77% the model supplies the premise. y is set only
for the low band, where "human ideas" is safe; everything else is -1 (unlabelled) and is
used through the continuous ai_share covariate instead. The seed prompt is stripped from
the scored text -- neither the writer nor the model wrote it.
"""
import ast, json, glob
from pathlib import Path
import numpy as np, pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

N = Path("${WORK_DIR}/newevals")
CO = Path("${WORK_DIR}/coauthor/coauthor-v1.0")
LOW = 0.20            # below this, the ideas are the writer's; see the worked examples

# ---------------------------------------------------------------- ARB
p = hf_hub_download("giper45/ARB-Dataset", repo_type="dataset", filename="data/arb.parquet")
d = pq.read_table(p).to_pydict()
rows = []
for i in range(len(d["id"])):
    t = d["text"][i] or ""
    if not t.strip(): continue
    rows.append({"id": f"arb_{d['id'][i]}", "text": t, "words": len(t.split()),
                 "y": 1 if d["content_origin"][i] == "human" else 0,
                 "arm": d["regime"][i], "pair_id": f"arb_{d['pair_id'][i]}",
                 "generator": d["generator_model"][i], "domain": d["source_dataset"][i],
                 "content_origin": d["content_origin"][i],
                 "surface_origin": d["surface_origin"][i]})
with open(N / "arb_format_input.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
w = np.array([r["words"] for r in rows])
print(f"ARB      {len(rows):,} rows  ids unique={len({r['id'] for r in rows})==len(rows)}  "
      f"median {np.median(w):.0f}w  >=500w {100*(w>=500).mean():.1f}%")
import collections
print(f"         arms {dict(collections.Counter(r['arm'] for r in rows))}")
print(f"         y (1=human ideas) {dict(collections.Counter(r['y'] for r in rows))}")

# ---------------------------------------------------------------- CoAuthor
def replay(path):
    doc, prompt = [], ""
    for line in open(path):
        e = json.loads(line)
        if e.get("eventName") == "system-initialize":
            prompt = e.get("currentDoc") or ""
            doc = [[c, "P"] for c in prompt]; continue
        td = e.get("textDelta")
        if td in (None, "", {}): continue
        ops = td.get("ops", []) if isinstance(td, dict) else ast.literal_eval(td).get("ops", [])
        tag = "A" if e.get("eventSource") == "api" else "H"
        i = 0
        for op in ops:
            if "retain" in op: i += int(op["retain"])
            elif "insert" in op:
                t = op["insert"]
                if not isinstance(t, str): continue
                doc[i:i] = [[c, tag] for c in t]; i += len(t)
            elif "delete" in op: del doc[i:i + int(op["delete"])]
    return doc, prompt

rows = []
for f in sorted(glob.glob(str(CO / "*.jsonl"))):
    doc, prompt = replay(f)
    body = [(c, s) for c, s in doc if s != "P"]          # the seed prompt is neither party's
    if not body: continue
    txt = "".join(c for c, _ in body)
    if len(txt.split()) < 50: continue
    share = sum(1 for _, s in body if s == "A") / len(body)
    rows.append({"id": f"coauthor_{Path(f).stem}", "text": txt, "words": len(txt.split()),
                 # labelled human only where the ideas are demonstrably the writer's
                 "y": 1 if share < LOW else -1,
                 "arm": "low_ai" if share < LOW else ("high_ai" if share >= 0.50 else "mid_ai"),
                 "ai_share": round(float(share), 4), "seed_prompt": prompt.strip()[:400]})
with open(N / "coauthor_format_input.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
w = np.array([r["words"] for r in rows]); a = np.array([r["ai_share"] for r in rows])
print(f"\nCoAuthor {len(rows):,} rows  median {np.median(w):.0f}w  >=500w {100*(w>=500).mean():.1f}%")
print(f"         ai_share median {100*np.median(a):.1f}%  bands "
      f"{dict(collections.Counter(r['arm'] for r in rows))}")
print(f"         labelled human (ai_share<{LOW:.0%}): {sum(1 for r in rows if r['y']==1):,}"
      f"   unlabelled: {sum(1 for r in rows if r['y']==-1):,}")
