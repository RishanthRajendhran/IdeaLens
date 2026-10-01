"""Partial-document pilot: random windows of at least 500 words, on sentence boundaries.

Sampling is uniform over source label x document format, with topic spread as far as the
cell allows (topic is balanced, not enforced -- 16 cells x 23 topics is too fine for 600 docs).

Each source contributes three rows: two random windows and the full document, so the
comparison is within-document. Windows start anywhere, so they have neither the opening
nor the ending -- an excerpt, not a truncation.
"""
import json, re, sys, collections
from pathlib import Path
import numpy as np
W=Path("${WORK_DIR}"); N=W/"newevals"
REPO=Path("${AUX_DIR}")
MIN_W, N_SRC, N_WIN, SEED = 500, 600, 2, 0

z=np.load(W/"v1m/preds/nemotron_full_v1m-r64-ep1_test.npz",allow_pickle=True)
ids=np.asarray([str(x) for x in z["ids"]]); wc=np.asarray(z["word_count"],float)
y=np.asarray(z["y"]).astype(int); fmt=np.asarray([str(x) for x in z["fmt"]])
top=np.asarray([str(x) for x in z["topic"]])
# indomain_test_docs.jsonl carries 19,974 of the split's 48,869 documents, so the
# sampling pool must be intersected with it first or most picks have no text to window.
avail=set()
with open(N/"indomain_test_docs.jsonl") as fh:
    for l in fh: avail.add(json.loads(l)["id"])
inset=np.array([i in avail for i in ids])
elig=np.where(inset&(wc>=1200))[0]
print(f"pool: {len(elig):,} documents at 1,200+ words with text available "
      f"(of {int((wc>=1200).sum()):,} eligible in the split)")
rng=np.random.default_rng(SEED)

cells=collections.defaultdict(list)
for i in elig: cells[(int(y[i]), fmt[i])].append(i)
per=N_SRC//len(cells)
picked=[]
for k in sorted(cells):
    pool=cells[k]
    bytopic=collections.defaultdict(list)
    for i in pool: bytopic[top[i]].append(i)
    order=sorted(bytopic, key=lambda t:-len(bytopic[t]))
    for t in order: rng.shuffle(bytopic[t])
    take=[]                                   # round-robin across topics = spread without enforcing
    while len(take)<per:
        added=False
        for t in order:
            if bytopic[t] and len(take)<per: take.append(bytopic[t].pop()); added=True
        if not added: break
    picked+=take
print(f"sampled {len(picked)} sources across {len(cells)} label x format cells ({per} each)")
print("  topic spread:", len({top[i] for i in picked}), "distinct topics")

need={ids[i] for i in picked}
text={}
with open(N/"indomain_test_docs.jsonl") as fh:
    for l in fh:
        r=json.loads(l)
        if r["id"] in need:
            text[r["id"]]=r.get("text")
            if len(text)==len(need): break
print(f"  recovered text for {len(text)}/{len(need)}")

SENT=re.compile(r'(?<=[.!?])["\')\]]*\s+')
def windows(t, k):
    parts=[p for p in SENT.split(t) if p.strip()]
    lens=[len(p.split()) for p in parts]
    tot=sum(lens)
    if tot < MIN_W*1.6: return []
    out=[]
    for _ in range(k*12):
        if len(out)>=k: break
        s=int(rng.integers(0, max(1,len(parts)-2)))
        acc=0; e=s
        while e<len(parts) and acc<MIN_W: acc+=lens[e]; e+=1
        if acc<MIN_W: continue
        span=(s,e)
        if any(abs(span[0]-o[0])<3 for o in out): continue   # keep the two windows apart
        out.append(span)
    return [(" ".join(parts[a:b]), a, b, sum(lens[a:b])) for a,b in out[:k]]

rows=[]; dropped=0
for i in picked:
    did=ids[i]; t=text.get(did)
    if not t: dropped+=1; continue
    ws=windows(t, N_WIN)
    if len(ws)<N_WIN: dropped+=1; continue
    base={"src_id":did,"y":int(y[i]),"arm":"human" if y[i]==1 else "ai",
          "fmt":fmt[i],"topic":top[i],"src_words":int(wc[i])}
    rows.append({**base,"id":f"{did}|full","window":"full","text":t,"words":int(wc[i])})
    for j,(wt,a,b,n) in enumerate(ws):
        rows.append({**base,"id":f"{did}|w{j}","window":f"w{j}","text":wt,"words":n,
                     "sent_start":a,"sent_end":b})
f=N/"partial_windows.jsonl"
with open(f,"w") as fh:
    for r in rows: fh.write(json.dumps(r)+"\n")
c=collections.Counter(r["window"] for r in rows)
ww=[r["words"] for r in rows if r["window"]!="full"]
print(f"\nwrote {f}")
print(f"  {len(rows):,} rows from {len({r['src_id'] for r in rows})} sources ({dropped} sources dropped)")
print(f"  arms: {dict(c)}")
print(f"  window length: median {int(np.median(ww))} words, min {min(ww)}, max {max(ww)}")
print(f"  label balance: {collections.Counter(r['arm'] for r in rows)}")
print(f"  formats: {len({r['fmt'] for r in rows})}, topics: {len({r['topic'] for r in rows})}")
