"""Stratified pilot slices of CoCoNUTS and PeerPrism, sized to a budget.

Both sets are far too large to extract in full at first pass, so take a slice that keeps
every split populated and spends the sample where the question is: the arms holding HUMAN
IDEAS IN MODEL PROSE (CoCoNUTS hwmt/hwmp, PeerPrism rewritten/extract_regenerate) and the
human control that gives them a false-positive rate to be measured against. The easy
all-model arms get a smaller share -- they are already near ceiling everywhere else.

Within each arm the sample is stratified by generator model (and, for PeerPrism, venue and
year) so no single generator can dominate a cell.
"""
import json, glob, os, random, collections, statistics as st
from pathlib import Path

W = Path("${WORK_DIR}/newevals")
CC = Path("${HF_HOME}/hub/datasets--khaaaaaan--CoCoNUTS/"
          "snapshots/ac418fb3dd2c2bbe0430683b0ab753a515de8315/test.jsonl")
PP = W / "peerprism"
SEED = 20260830

# arm -> target n. Hard cells and controls get the weight.
CC_TARGET = {"hw": 1200, "hwmt": 1500, "hwmp": 1500, "hwmg": 1200, "mgmp": 700, "mg": 700}
PP_TARGET = {"human": 674, "rewritten": 1500, "extract_regenerate": 1500,
             "expanded": 900, "hybrid": 900, "synthetic_reviews": 800}
# what each arm is, under OUR idea-level rule
CC_IDEA = {"hw": "human", "hwmt": "human", "hwmp": "human",
           "hwmg": "mixed", "mgmp": "ai", "mg": "ai"}
PP_IDEA = {"human": "human", "rewritten": "human", "extract_regenerate": "human",
           "expanded": "mixed", "hybrid": "mixed", "synthetic_reviews": "ai"}


def stratified(rows, n, keyfn, rng):
    """Take n rows, spread as evenly as possible across the strata keyfn defines."""
    if n >= len(rows):
        return list(rows)
    g = collections.defaultdict(list)
    for r in rows:
        g[keyfn(r)].append(r)
    for k in g:
        rng.shuffle(g[k])
    out, keys = [], sorted(g)
    while len(out) < n:
        progressed = False
        for k in keys:
            if g[k] and len(out) < n:
                out.append(g[k].pop()); progressed = True
        if not progressed:
            break
    return out


def build_coconuts(rng):
    rows = [json.loads(l) for l in open(CC)]
    out = []
    for lab, n in CC_TARGET.items():
        sub = [r for r in rows if r["label"] == lab]
        s = stratified(sub, n, lambda r: r["model"], rng)
        for r in s:
            out.append({"id": f"cc_{r['uid']}", "text": r["review"], "arm": lab,
                        "idea": CC_IDEA[lab], "y": 1 if CC_IDEA[lab] == "human" else 0,
                        "generator": r["model"], "src_class": r["class"],
                        "words": len(r["review"].split())})
        print(f"  coconuts {lab:6s} {len(s):5,d}/{len(sub):6,d}  "
              f"{len(set(r['model'] for r in s))} generators")
    return out


def build_peerprism(rng):
    """Build review-level rows from the PER-MODEL files.

    The flattened files in data/baselines/flattened_data are one row per
    (paper, review, generating model) but do NOT carry the model, so an id built from
    forum_id + review_id collides six ways -- which is exactly what aborted the first run
    (1,748 ids covering 4,551 rows). Reading the per-model files instead gives a unique id
    AND lets the sample be stratified by generator, which the venue-year-only version was
    silently not doing.
    """
    import re
    def model_of(path):
        b = os.path.basename(path)[:-6]
        return re.sub(r"^(ICLR|NeurIPS)\d{4}_", "", b).split("_")[-1]

    out = []
    # human control
    hum = []
    for f in sorted(glob.glob(str(PP / "data/human_reviews/*.jsonl"))):
        for l in open(f):
            r = json.loads(l)
            for rv in r["reviews"]:
                hum.append({"id": f"pp_human_{r['forum_id']}_{rv['review_id']}",
                            "text": rv["full_review_text"], "arm": "human", "idea": "human",
                            "y": 1, "generator": "human", "idea_origin": "human",
                            "text_origin": "human", "venue": r["venue"], "year": r["year"],
                            "forum_id": r["forum_id"]})
    sel = stratified(hum, PP_TARGET["human"], lambda r: (r["venue"], r["year"]), rng)
    out += sel
    print(f"  peerprism {'human':20s} {len(sel):5,d}/{len(hum):6,d}  1 generator")

    # the four transformations
    for regime in ("rewritten", "extract_regenerate", "expanded", "hybrid"):
        rows = []
        for f in sorted(glob.glob(str(PP / "data/transformations" / regime / "*.jsonl"))):
            mdl = model_of(f)
            for l in open(f):
                r = json.loads(l)
                for rv in r["reviews"]:
                    txt = rv.get("text") or rv.get("full_review_text")
                    if not txt:
                        continue
                    rows.append({"id": f"pp_{regime}_{r['forum_id']}_{rv.get('review_id') or rv['id']}_{mdl}",
                                 "text": txt, "arm": regime, "idea": PP_IDEA[regime],
                                 "y": 1 if PP_IDEA[regime] == "human" else 0,
                                 "generator": rv.get("rewrite_model") or mdl,
                                 "idea_origin": rv.get("idea_origin"),
                                 "text_origin": rv.get("text_origin"),
                                 "venue": r["venue"], "year": r["year"], "forum_id": r["forum_id"]})
        sel = stratified(rows, PP_TARGET[regime], lambda r: (r["venue"], r["year"], r["generator"]), rng)
        out += sel
        print(f"  peerprism {regime:20s} {len(sel):5,d}/{len(rows):6,d}  "
              f"{len(set(r['generator'] for r in sel))} generators")

    # Fully synthetic. Its per-model files keep the text as JSON in raw_model_output for
    # 3,360 of 3,840 rows -- only 480 have a prose `review` field -- so read the authors'
    # own flattened file, which has already parsed it AND is the one flattened file that
    # carries the generator, in review_metadata.generation_model.
    rows = []
    for l in open(PP / "data/baselines/flattened_data/synthetic_reviews_flat.jsonl"):
        r = json.loads(l)
        pm, rm = r["paper_metadata"], r["review_metadata"]
        rows.append({"id": f"pp_synthetic_{pm['forum_id']}_{rm.get('review_idx',0)}_"
                           f"{rm.get('generation_model')}",
                     "text": r["text"], "arm": "synthetic_reviews", "idea": "ai", "y": 0,
                     "generator": rm.get("generation_model"),
                     "idea_origin": r["idea_origin"], "text_origin": r["text_origin"],
                     "venue": pm["venue"], "year": pm["year"], "forum_id": pm["forum_id"]})
    sel = stratified(rows, PP_TARGET["synthetic_reviews"],
                     lambda r: (r["venue"], r["year"], r["generator"]), rng)
    out += sel
    print(f"  peerprism {'synthetic_reviews':20s} {len(sel):5,d}/{len(rows):6,d}  "
          f"{len(set(r['generator'] for r in sel))} generators")

    for r in out:
        r["words"] = len(str(r["text"]).split())
    ids = [r["id"] for r in out]
    assert len(ids) == len(set(ids)), f"{len(ids)-len(set(ids))} duplicate ids remain"
    print(f"  all {len(ids):,} ids unique")
    return out


def cost(rows, label):
    """$/1k anchored on the runs we actually paid for, scaled by document length."""
    w = st.median([r["words"] for r in rows])
    rate = 13.69 * (1 + 0.0009 * (w - 260))          # large-batch regime, incl. format pass
    return len(rows) / 1000 * rate, w, rate


def main():
    rng = random.Random(SEED)
    print("CoCoNUTS slice:")
    cc = build_coconuts(rng)
    print("\nPeerPrism slice:")
    pp = build_peerprism(rng)
    for name, rows in (("coconut1", cc), ("peerprism1", pp)):
        f = W / f"{name}_format_input.jsonl"
        with open(f, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        c, w, rate = cost(rows, name)
        by = collections.Counter(r["idea"] for r in rows)
        print(f"\n{name}: {len(rows):,} docs -> {f.name}")
        print(f"   median {w:.0f} words, ${rate:.2f}/1k  ->  ${c:.0f}")
        print(f"   by idea label: {dict(by)}")
    tot = cost(cc, "")[0] + cost(pp, "")[0]
    print(f"\nslices total: ${tot:.0f}   (+ WildChat $27 + Epoch $22 = ${tot+49:.0f})")


if __name__ == "__main__":
    main()
