"""Export HART (Bao et al., 2025) into our format-classification input.

HART is the closest prior work: the same content x expression decomposition, the same
hypothesis that content survives surface change. Scoring it lets us compare head-to-head
against their Table 3, where the best level-2 (is the CONTENT AI?) result is AUROC 0.855.

Their level-2 task is our label rule exactly: content origin decides, expression rides along.
So y = 1 when content_source is human, whatever was done to the prose afterwards. We verify
that against their own `task_level2` flag rather than trusting the mapping.

We score `generation`, the actual document. Their `content` and `language` fields are their
own decompositions and are kept only as metadata -- feeding those to our pipeline would be
scoring their method, not ours.
"""
import json, glob, re
from pathlib import Path

SRC = Path("${WORK_DIR}/hart/truth-mirror-main/"
           "benchmark/hart")
OUT = Path("${WORK_DIR}/newevals/"
           "hart_format_input.jsonl")


def prose(r):
    l = r["language_source"]
    if l == "human": return "human_original"
    if l.startswith("rephrase"): return "model_rephrase"
    if l.startswith("machine"): return "model_wrote"
    if l == "humanize:human": return "human_edited"
    if l == "humanize:tool": return "tool_humanized"
    if l.startswith("humanize"): return "model_humanized"
    return "other"


ARM = {("human", "human_original"): "human",
       ("human", "model_rephrase"): "h2l_rephrase",
       ("human", "model_wrote"): "h2l_rewritten",
       ("model", "model_wrote"): "ai_plain",
       ("model", "model_humanized"): "ai_humanized",
       ("model", "tool_humanized"): "ai_tool_humanized",
       ("model", "human_edited"): "ai_human_edited"}


def nwords(txt):
    """Chinese is not whitespace-delimited: counting split() tokens on a 590-character
    Chinese article yields a handful and silently drops the whole language. Count CJK
    codepoints as words, which is the convention HART's own length table uses."""
    cjk = sum(1 for c in txt if "\u4e00" <= c <= "\u9fff")
    return max(len(txt.split()), cjk)


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT} exists -- refusing to overwrite")
    rows, short, mismatch = [], 0, 0
    for f in sorted(glob.glob(str(SRC / "*.test.json"))):
        split = Path(f).stem.replace(".test", "")
        for r in json.load(open(f)):
            txt = re.sub(r"\s+", " ", r.get("generation") or "").strip()
            nw = nwords(txt)
            if nw < 30:
                short += 1; continue
            ideas = "human" if r["content_source"] == "human" else "model"
            y = 1 if ideas == "human" else 0
            # their own level-2 flag must agree with our reading of content origin
            if bool(r.get("task_level2")) != (y == 0):
                mismatch += 1; continue
            rows.append({"id": f"hart_{r['id']}", "text": txt, "words": nw,
                         "y": y, "arm": ARM.get((ideas, prose(r)), "other"),
                         "hart_domain": r.get("domain"), "hart_split": split,
                         "content_source": r["content_source"],
                         "language_source": r["language_source"],
                         "generator": r["content_source"].split(":")[-1],
                         "lang": r.get("language") and split})
    with open(OUT, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    import collections, statistics as st
    print(f"wrote {OUT}\n  {len(rows):,} documents kept; "
          f"{short} too short, {mismatch} level-2 flag disagreed")
    print(f"\n  {'arm':20s} {'y':>3s} {'n':>7s} {'median words':>13s}")
    for a in sorted({r["arm"] for r in rows}):
        g = [r for r in rows if r["arm"] == a]
        print(f"  {a:20s} {g[0]['y']:>3} {len(g):>7,} "
              f"{int(st.median([x['words'] for x in g])):>13}")
    print(f"\n  by domain: {dict(collections.Counter(r['hart_split'] for r in rows))}")
    w = sorted(r["words"] for r in rows)
    print(f"  words: median {w[len(w)//2]}, under 500 "
          f"{100*sum(1 for x in w if x<500)/len(w):.0f}%")
    print(f"\n  extraction only at $15.07/1k = ${len(rows)/1000*15.07:,.0f}"
          f"   (paraphrase deferred, would add ${len(rows)/1000*24.89:,.0f})")


main()
