"""Strip PeerPrism's condition-naming headers before anything reads the text.

The transformation models emitted their own instruction as a title: 42.7% of `rewritten`,
50.6% of `expanded` and 49.9% of `hybrid` open with "## Rewritten Review", "## Expanded Peer
Review" or similar. Left in place, that is the arm label written into the document -- our
extractor would see it, and so would any detector, which makes the benchmark measure header
parsing rather than provenance. Remove leading markdown headers and any standalone header
line that names a condition, then verify the leak is gone.
"""
import json, re, collections
from pathlib import Path

N = Path("${WORK_DIR}/newevals")
COND = r"(rewritten|expanded|hybrid|regenerated|extracted|synthetic|revised|improved|polished)"
# A heading line. The earlier version anchored on the end of the line, so it missed
# "# Expanded Peer Review: RotoGrad" -- the condition plus the paper title.
HDR = re.compile(rf"^\s*#{{1,6}}\s*.*?({COND}|peer\s+review|review)\b.*$", re.I)
BOLD = re.compile(rf"^\s*\*\*\s*{COND}\s+(peer\s+)?review\s*\*\*\s*:?\s*$", re.I)
# The model announcing what it just did: "Here is the rewritten peer review:"
PRE = re.compile(rf"^\s*(here\s+is|below\s+is|this\s+is|the\s+final)\b.{{0,120}}?"
                 rf"({COND}|review)\b.{{0,120}}?[:.]?\s*$", re.I)
RULE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
COND_ANY = re.compile(COND, re.I)


def clean(t):
    lines = t.split("\n")
    i = 0
    # drop leading blank lines, horizontal rules, headings and announcement preambles,
    # stopping at the first line of real review content
    while i < len(lines):
        s = lines[i].strip()
        if not s or RULE.match(s) or HDR.match(s) or BOLD.match(s) or PRE.match(s):
            i += 1
            continue
        break
    body = lines[i:]
    # a few `expanded` documents repeat "The final expanded review is here." as filler
    body = [l for l in body if not PRE.match(l.strip())]
    return "\n".join(body).strip()


def main():
    f = N / "peerprism1_format_input.jsonl"
    rows = [json.loads(l) for l in open(f)]
    before = collections.Counter()
    after = collections.Counter()
    for r in rows:
        if COND_ANY.search(r["text"][:200]):
            before[r["arm"]] += 1
        r["text"] = clean(r["text"])
        if COND_ANY.search(r["text"][:200]):
            after[r["arm"]] += 1
        r["words"] = len(r["text"].split())
    n = collections.Counter(r["arm"] for r in rows)
    print(f"{'arm':22s}{'n':>6s}{'leaked before':>15s}{'leaked after':>14s}")
    for a in sorted(n):
        print(f"{a:22s}{n[a]:6d}{before[a]:14d} {after[a]:13d}")
    empty = [r for r in rows if len(r["text"].split()) < 30]
    print(f"\ndocuments left under 30 words by the strip: {len(empty)}")
    with open(f, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"rewrote {f.name}")
    print("\nnew first lines, by arm:")
    for a in ["rewritten", "expanded", "hybrid"]:
        c = collections.Counter(r["text"].split("\n")[0][:60] for r in rows if r["arm"] == a)
        print(f"  {a}: {[k for k,_ in c.most_common(3)]}")


if __name__ == "__main__":
    main()
