"""Build a corpus.jsonl from the StoryScope test set for the outline pipeline.

One row per (prompt, author): the human story plus each model's response to the SAME
prompt. `pair_id` carries the prompt id, so the matched-prompt design survives into
every downstream analysis -- the same leverage the paper id gave us on aipr.

Everything here is Creative Writing, which is one of the eight WebOrganizer formats
the extraction prompt is conditioned on, so the format is asserted rather than
classified (as with every other eval set we build).
"""
import argparse, hashlib, json, collections
from pathlib import Path
import pandas as pd

SRC = Path("${AUX_DIR}/data/StoryScope/test.csv")
OUT = Path("${AUX_DIR}/detector/evals/storyscope")
FMT, ROLE_FMT = "Creative Writing", "creative_writing"
COLS = {"human": "human_story", "gpt_5_4": "response_gpt_5_4",
        "deepseek_v3_2": "response_deepseek_v3_2", "kimi_k2_5": "response_kimi_k2_5",
        "gemini": "response_gemini", "claude_sonnet_4_6": "response_claude_sonnet_4_6"}
FLOOR = 50          # a handful of rows are stubs; anything this short is not a story


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="prompts to keep (0 = all)")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = Path(a.out); (out).mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(SRC)
    if a.limit:
        df = df.head(a.limit)
    rows, labels, dropped = [], {}, collections.Counter()
    for _, r in df.iterrows():
        pid = str(r["prompt_id"])
        for model, col in COLS.items():
            txt = r.get(col)
            if not isinstance(txt, str) or len(txt.split()) < FLOOR:
                dropped[model] += 1
                continue
            src = "human" if model == "human" else "ai"
            did = hashlib.sha1(f"storyscope|{pid}|{model}".encode()).hexdigest()[:24]
            rows.append({"id": did, "source": src, "text": txt,
                         "format": FMT, "role_format": ROLE_FMT,
                         "model": model, "pair_id": pid,
                         "title": str(r.get("title") or ""),
                         "words": len(txt.split())})
            labels[did] = {"source": src, "model": model, "pair_id": pid,
                           "words": len(txt.split()), "format": FMT}

    (out / "corpus.jsonl").write_text(
        "".join(json.dumps(x) + "\n" for x in rows), encoding="utf8")
    (out / "labels.json").write_text(json.dumps(labels), encoding="utf8")
    c = collections.Counter(x["model"] for x in rows)
    s = collections.Counter(x["source"] for x in rows)
    w = sorted(x["words"] for x in rows)
    print(f"wrote {len(rows):,} docs from {len(df):,} prompts -> {out}/corpus.jsonl")
    print(f"  source: {dict(s)}")
    print(f"  model : {dict(c.most_common())}")
    print(f"  words : median {w[len(w)//2]:,}  p90 {w[int(len(w)*.9)]:,}  max {w[-1]:,}")
    if dropped:
        print(f"  dropped (null or <{FLOOR}w): {dict(dropped)}")
    print(f"  distinct prompts represented: {len({x['pair_id'] for x in rows}):,}")


if __name__ == "__main__":
    main()
