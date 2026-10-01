"""Item-count distribution of the 1M training corpus.

Testing whether StealthGPT evades by being OUT OF DISTRIBUTION on outline length rather
than by disguising ideas. If the corpus sits at ~13 items and stealth at ~8.7, "too short"
is a candidate mechanism -- but only if SHORT AI outlines also evade, which is the control.

n_items comes from text_items.npz's `offsets` (one entry per document boundary), which is
exact and is a separate npz member, so the 4 GB item array itself is never read. Labels and
word counts are joined from the prediction files, which carry ids, y, fmt and word_count.
"""
import numpy as np, json, glob
from pathlib import Path
W = Path("${WORK_DIR}")

z = np.load(W / "v1m/text_items.npz", allow_pickle=True)
off = z["offsets"]; ids = z["ids"]
n_items = np.diff(off)
print(f"{len(n_items):,} documents from offsets (ids {len(ids):,})", flush=True)

# labels / word counts from the stored prediction splits
meta = {}
for f in glob.glob(str(W / "v1m/preds/nemotron_full_v1m-r64-ep1_*.npz")):
    p = np.load(f, allow_pickle=True)
    if not {"ids", "y", "word_count"} <= set(p.keys()): continue
    for i, y_, w in zip(p["ids"], p["y"], p["word_count"]):
        meta[str(i)] = (int(y_), int(w))
    print(f"  {Path(f).name}: {len(p['ids']):,}", flush=True)
print(f"labelled documents available: {len(meta):,}", flush=True)

idx = [(k, int(n_items[j])) for j, k in enumerate(map(str, ids)) if k in meta]
ni = np.array([x[1] for x in idx]); yy = np.array([meta[x[0]][0] for x in idx])
ww = np.array([meta[x[0]][1] for x in idx])
out = {"corpus_all": {"n": int(len(n_items)), "mean": float(n_items.mean()),
                      "median": float(np.median(n_items)),
                      "p10": float(np.percentile(n_items, 10)),
                      "p90": float(np.percentile(n_items, 90))}}
def desc(m, lab):
    v = ni[m]
    if len(v) < 25: return
    d = {"n": int(len(v)), "mean": float(v.mean()), "median": float(np.median(v)),
         "p10": float(np.percentile(v, 10)), "p25": float(np.percentile(v, 25)),
         "p75": float(np.percentile(v, 75)), "p90": float(np.percentile(v, 90))}
    out[lab] = d
    print(f"{lab:24s} n={d['n']:8,} mean {d['mean']:6.2f} median {d['median']:5.1f} "
          f"p10 {d['p10']:5.1f} p90 {d['p90']:6.1f}", flush=True)
a = out["corpus_all"]
print(f"\n{'WHOLE CORPUS':24s} n={a['n']:8,} mean {a['mean']:6.2f} median {a['median']:5.1f} "
      f"p10 {a['p10']:5.1f} p90 {a['p90']:6.1f}\n")
desc(np.ones(len(ni), bool), "labelled subset")
desc(yy == 1, "human")            # arrays use y=1 for HUMAN
desc(yy == 0, "ai")
for lab, m in (("≥500 words", ww >= 500), ("<500 words", ww < 500)):
    desc(m, lab); desc(m & (yy == 1), f"{lab} · human"); desc(m & (yy == 0), f"{lab} · ai")
out["hist_long"] = np.histogram(ni[ww >= 500], bins=np.arange(0, 62))[0].tolist()
out["hist_all"]  = np.histogram(n_items, bins=np.arange(0, 62))[0].tolist()
json.dump(out, open(W / "newevals/corpus_items.json", "w"), indent=1)
print("\nCORPUS_ITEMS_DONE", flush=True)
