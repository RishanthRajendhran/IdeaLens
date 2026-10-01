"""Build the RAID and DetectRL extraction samples.

BOTH ARE PAIRED. The attack arms are only worth buying if each attacked document can be
compared against its own unattacked source: an attack delta read across two independent
samples carries the variance of both, and at 400-550 documents per arm that variance is
larger than the effects we are looking for. RAID gives the link through `adv_source_id`,
DetectRL through record position within each attack file (its human side is byte-identical
across files, which is how we know the records align and why the human arm is bought once).

NO LENGTH FLOOR. Our 501-word floor exists because the training corpus starts there, but
RAID's AI generations are 99.98% below it, so filtering leaves 937 documents out of 5.4M and
manufactures a length gap that is not in the benchmark: unfiltered, the medians are 225
human against 232 AI. Short documents will score badly, and that is the finding, not an
artifact to filter away.
"""
import argparse, glob, hashlib, json, collections
from pathlib import Path
import numpy as np

W = Path("${WORK_DIR}/newevals")
# RAID domains onto the eight WebOrganizer formats. The extraction prompt is
# format-conditioned -- it injects that format's role set -- so a wrong mapping silently
# extracts with the wrong role vocabulary.
RAID_FMT = {"abstracts": "Academic Writing", "books": "Creative Writing",
            "news": "News Article", "poetry": "Creative Writing",
            "recipes": "Knowledge Article", "reddit": "Personal Blog",
            "reviews": "User Reviews", "wiki": "Knowledge Article"}
DETECTRL_FMT = {"Academic": "Academic Writing", "News": "News Article",
                "Novel": "Creative Writing", "Wiki": "Knowledge Article",
                "Webtext": "Nonfiction Writing", "SEO": "Nonfiction Writing"}
def slugfmt(f): return f.lower().replace(" ", "_")
def did(*parts): return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:24]


def build_raid(n_human, n_ai, n_paired, seed=0):
    import pandas as pd
    f = sorted(glob.glob("${HF_HOME}/hub/"
                         "datasets--liamdugan--raid/snapshots/*/*.csv"))[0]
    rng = np.random.default_rng(seed)
    use = ["id", "adv_source_id", "model", "attack", "domain", "generation"]
    # pass 1: index the unattacked rows only, so the sample is drawn without holding 11GB
    idx = {"human": collections.defaultdict(list), "ai": collections.defaultdict(list)}
    for c in pd.read_csv(f, usecols=use, chunksize=200_000):
        c = c[c["attack"].astype(str) == "none"]
        for r in c.itertuples(index=False):
            k = "human" if str(r.model) == "human" else "ai"
            idx[k][(r.domain, str(r.model))].append(r.id)
    def draw(k, n):
        cells = sorted(idx[k]); per = max(1, n // len(cells)); want = set()
        for cell in cells:
            ids = idx[k][cell]
            take = min(per, len(ids))
            want.update(rng.choice(ids, size=take, replace=False).tolist())
        return want
    keep_h, keep_a = draw("human", n_human), draw("ai", n_ai)
    # the paired subset: attacks are re-bought for these AI sources only
    paired = set(rng.choice(sorted(keep_a), size=min(n_paired, len(keep_a)), replace=False).tolist())
    print(f"  RAID: {len(keep_h):,} human + {len(keep_a):,} AI unattacked; "
          f"{len(paired):,} AI sources also taken under every attack", flush=True)
    # pass 2: emit
    out = []
    for c in pd.read_csv(f, usecols=use, chunksize=200_000):
        for r in c.itertuples(index=False):
            at = str(r.attack)
            if at == "none":
                if r.id not in keep_h and r.id not in keep_a: continue
            else:
                if r.adv_source_id not in paired: continue
            fmt = RAID_FMT.get(str(r.domain))
            if fmt is None: continue
            src = "human" if str(r.model) == "human" else "ai"
            txt = str(r.generation)
            out.append({"id": did("raid", r.id), "text": txt, "source": src,
                        "pair_id": str(r.adv_source_id), "attack": at,
                        "arm": f"{src}_{at}", "domain": str(r.domain),
                        "model": str(r.model), "words": len(txt.split()),
                        "format": fmt, "role_format": slugfmt(fmt)})
    return out


def build_detectrl(n_pairs, lang="english", seed=0):
    S = sorted(glob.glob("${HF_HOME}/hub/"
                         "datasets--WUJUNCHAO--DetectRL-X/snapshots/*/Binary/"))[0]
    rng = np.random.default_rng(seed)
    base = json.load(open(S + "binary_general_open.json"))
    ok = [i for i, r in enumerate(base)
          if str(r.get("lang", "")).lower() == lang and DETECTRL_FMT.get(r.get("domain"))]
    pick = sorted(rng.choice(ok, size=min(n_pairs, len(ok)), replace=False).tolist())
    print(f"  DetectRL: {len(ok):,} english records with a mapped format; taking {len(pick):,}", flush=True)
    out = []
    for i in pick:                       # human side once -- identical across attack files
        r = base[i]; fmt = DETECTRL_FMT[r["domain"]]; t = str(r["human_written_text"])
        out.append({"id": did("drl", i, "human"), "text": t, "source": "human",
                    "pair_id": f"drl{i}", "attack": "none", "arm": "human",
                    "domain": r["domain"], "model": r.get("model"), "words": len(t.split()),
                    "format": fmt, "role_format": slugfmt(fmt)})
    del base
    for p in sorted(glob.glob(S + "binary_*_open.json")):
        at = Path(p).name.replace("binary_", "").replace("_open.json", "")
        if at.startswith("general") and at != "general": continue
        rows = json.load(open(p))
        tag = "none" if at == "general" else at
        for i in pick:
            r = rows[i]; fmt = DETECTRL_FMT.get(r.get("domain"))
            if fmt is None: continue
            t = str(r["llm_generated_text"])
            out.append({"id": did("drl", i, "ai", tag), "text": t, "source": "ai",
                        "pair_id": f"drl{i}", "attack": tag, "arm": f"ai_{tag}",
                        "domain": r["domain"], "model": r.get("model"),
                        "words": len(t.split()), "format": fmt, "role_format": slugfmt(fmt)})
        del rows
        print(f"    {at:26s} +{len(pick):,}", flush=True)
    return out


def report(out, name, rate):
    p = W / f"{name}_extract_input.jsonl"
    if p.exists(): raise SystemExit(f"{p} exists -- refusing to overwrite")
    with open(p, "w") as fh:
        for r in out: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    w = np.array([r["words"] for r in out])
    print(f"\nwrote {len(out):,} -> {p}")
    print(f"  by source: {dict(collections.Counter(r['source'] for r in out))}")
    print(f"  by format: {dict(collections.Counter(r['format'] for r in out))}")
    print(f"  attacks  : {len(set(r['attack'] for r in out))} distinct")
    print(f"  words    : med {np.median(w):.0f}  mean {w.mean():.0f}")
    print(f"  est extraction @ ${rate}/doc: ${len(out)*rate:,.0f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--what", required=True)
    a = ap.parse_args()
    if a.what == "raid":
        report(build_raid(1500, 1500, 410), "raid1", 0.020)
    else:
        report(build_detectrl(550), "detectrl2", 0.021)
    print("BUILD_DONE", flush=True)
