"""Assemble extraction inputs for DetectionAI and OpAI-Bench using the Flash format labels.

One label per RECORD, by majority across its arms. The per-arm labels are only 44.6%
unanimous, but the median winning label holds 8 of 9 arms -- so the instability is a
dissenting arm or two, not a coin flip, and a vote resolves it. Voting also removes a
methodological problem the per-arm labels would create: a record's human arm and its
StealthGPT arm could otherwise be extracted with DIFFERENT role vocabularies, which would
confound the humanizer comparison with a format change.

For OpAI-Bench the same vote spans v0..v8 and neutralises a drift worth naming: per-version,
"Nonfiction Writing" rose from 150 to 192 as AI coverage went 0% to 100%, i.e. the
classifier was partly reading AI-ness. One label per trajectory cannot drift by construction.

Records whose majority label falls outside our eight corpus formats are DROPPED, not
coerced -- they have no role vocabulary and no per-format calibration cut.
"""
import argparse, collections, json
from pathlib import Path

W = Path("${WORK_DIR}")
KEEP = {"Academic Writing": "academic_writing", "Creative Writing": "creative_writing",
        "Knowledge Article": "knowledge_article", "News Article": "news_article",
        "Nonfiction Writing": "nonfiction_writing", "Personal About Page": "personal_about_page",
        "Personal Blog": "personal_blog", "User Reviews": "user_reviews"}


def idea_label(which, arm):
    """Label by IDEA provenance, not surface authorship. y=1 means HUMAN (array convention).

    Our task defines a document as human when its IDEAS are the person's, regardless of
    how much of the surface text an AI realized. OpAI-Bench sweeps only the surface: all
    nine versions v0..v8 are successive AI rewrites of the SAME human-written seed, so the
    ideas are the person's in every one and every row is human. That makes OpAI-Bench a
    pure human control for us -- FPR only, no TPR, no AUC. Do not relabel it from
    ai_sentence_ratio; that column measures characters, which is not our task.

    DetectionAI does contrast idea provenance (its AI arms are AI-conceived), so the
    arm-based rule is correct there.
    """
    if which in ("opai", "opaifull"):
        return 1
    return 1 if arm == "human" else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", required=True, choices=["detectionai", "opai", "opaifull"])
    a = ap.parse_args()
    out = W / f"newevals/{a.which}_extract_input.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists -- refusing to overwrite")

    fmt = [json.loads(l) for l in open(W / f"newevals/{a.which}_format.jsonl")]
    src = {r["id"]: r for r in
           (json.loads(l) for l in open(W / f"newevals/{a.which}_format_input.jsonl"))}
    by = collections.defaultdict(list)
    for r in fmt:
        by[r["pair_id"]].append(r)

    maj, drop = {}, collections.Counter()
    for pid, v in by.items():
        c = collections.Counter(r["llm_label"] for r in v if r["llm_label"])
        if not c:
            drop["unparsed"] += 1; continue
        top = c.most_common(1)[0][0]
        if top not in KEEP:
            drop[top] += 1; continue
        maj[pid] = KEEP[top]

    n = 0
    with open(out, "w") as fh:
        for r in fmt:
            rf = maj.get(r["pair_id"])
            if rf is None:
                continue
            s = src.get(r["id"])
            if not s:
                continue
            fh.write(json.dumps({"id": r["id"], "pair_id": r["pair_id"], "arm": r["arm"],
                                 "model": r["model"], "genre": r["genre"],
                                 "role_format": rf, "words": r["len"],
                                 "y": idea_label(a.which, r["arm"]),
                                 "text": s["text"]}, ensure_ascii=False) + "\n")
            n += 1
    print(f"{a.which}: {len(maj):,}/{len(by):,} records in scope, {n:,} documents -> {out.name}")
    if drop:
        print(f"  dropped records by majority label: {dict(drop.most_common(6))}")
    kept = collections.Counter(maj.values())
    print(f"  role_format mix: {dict(kept.most_common())}")
    print(f"  extraction at $0.01876/doc: ${n*0.01876:,.0f}")


main()
