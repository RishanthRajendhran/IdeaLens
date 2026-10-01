"""Sample the missing Saha et al. Table 2 cells into a corpus.jsonl.

We already hold, for the EASY subset only: AI-BP, H-AI and H (as
detector/evals/{aipr,aipr_x2}). Table 2 additionally needs easy AI-EP and AI-HI,
and the whole HARD subset (AI-BP, AI-EP, AI-HI, H-AI).

LENGTH. Saha's FPR classes are short -- H-AI medians 284-301 words and pure H 286
-- against our corpus's 501-word floor. Reporting only a random draw would leave
the >=500 bucket of hard H-AI at ~64 rows, too thin to read. So each cell is drawn
as a random sample (which is what the `full` column must be estimated from, and it
must stay unfiltered or it is not a random sample any more) plus a top-up drawn
from that cell's >=500 pool, used only to thicken the >=500 column. `draw` records
which is which so the two columns are never accidentally mixed.

Output schema matches detector/evals/aipr/corpus.jsonl so the existing extract ->
deleak -> eval_ood391 path consumes it unchanged.
"""

import argparse, hashlib, json, random
from pathlib import Path

FILES = {"easy": "easy-subset-consolidated.jsonl",
         "hard": "hard-subset-consolidated.jsonl"}
REPO = "rounaksaha12/ai-in-peer-review"
NEED = [("easy", "AI-EP"), ("easy", "AI-HI"),
        ("hard", "AI-BP"), ("hard", "AI-EP"), ("hard", "AI-HI"), ("hard", "H-AI")]
FLOOR = 500


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400, help="random draw per cell")
    ap.add_argument("--topup", type=int, default=200,
                    help="extra rows per cell drawn from the >=500-word pool")
    ap.add_argument("--topup-cells", default="hard:H-AI,easy:H-AI",
                    help="cells whose >=500 pool is too thin under a random draw")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    from huggingface_hub import hf_hub_download
    rng = random.Random(a.seed)
    topup_for = {t for t in a.topup_cells.split(",") if t}
    out, seen = [], set()

    for sub, lev in NEED:
        rows = [json.loads(l) for l in
                open(hf_hub_download(REPO, FILES[sub], repo_type="dataset"))
                ]
        pool = [r for r in rows if r["level"] == lev]
        for r in pool:
            r["_w"] = len(r["review_text"].split())
        rng.shuffle(pool)
        picked = pool[: a.n]
        got = {id(r) for r in picked}
        extra = []
        if f"{sub}:{lev}" in topup_for:
            long_pool = [r for r in pool if r["_w"] >= FLOOR and id(r) not in got]
            extra = long_pool[: a.topup]
        n_long = sum(1 for r in picked if r["_w"] >= FLOOR)
        print(f"{sub:<5} {lev:<6} pool={len(pool):>6}  random={len(picked)} "
              f"(>={FLOOR}w: {n_long})  topup={len(extra)}", flush=True)

        for draw, group in (("random", picked), ("topup", extra)):
            for r in group:
                key = f"{sub}|{lev}|{r['conference']}|{r['paper_number']}|" \
                      f"{r['reviewer_id']}|{r['prompt_id']}|{r['generating_model']}"
                did = hashlib.sha1(key.encode()).hexdigest()[:24]
                if did in seen:
                    continue
                seen.add(did)
                out.append({
                    "id": did, "text": r["review_text"],
                    "source": "human" if lev in ("H", "H-AI") else "ai",
                    "level": lev, "subset": sub, "draw": draw,
                    "humanized": False, "model": r["generating_model"],
                    "paper": f"{r['conference']}/{r['paper_number']}",
                    "format": "Academic Writing", "role_format": "academic_writing",
                    "words": r["_w"]})

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    nl = sum(1 for r in out if r["words"] >= FLOOR)
    print(f"\nwrote {len(out):,} docs -> {a.out}")
    print(f"  >={FLOOR} words: {nl:,} ({nl/len(out):.1%})")
    print(f"  est pipeline cost: ${len(out)*0.1674:,.2f}")
    print("BUILD_SAHA_CORPUS_DONE", flush=True)


if __name__ == "__main__":
    main()
