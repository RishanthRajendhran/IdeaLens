"""Assemble the UNIQUE SOURCE documents of DetectionAI and OpAI-Bench for format labelling.

Format is a property of the source record, not of an arm. Every DetectionAI record has one
human passage plus 4 AI and 4 StealthGPT arms written from the same topic; every OpAI-Bench
trajectory is nine revisions of one human document. Labelling the source once and
propagating covers the whole dataset, costs an eighth to a ninth as much, and cannot do
what a per-arm run demonstrably did -- assign two arms of the same document different
formats.

The document sent for labelling is the HUMAN original in both cases (DetectionAI's `text`,
OpAI-Bench's v0), because that is what the format describes.
"""
import argparse, csv, glob, json, collections
from pathlib import Path

W = Path("${WORK_DIR}")
csv.field_size_limit(10**9)


def detectionai(out, all_arms=True):
    """Every arm, not just the human side.

    Propagating one label per record is cheaper and cannot self-contradict, but at ~$9
    cached for the whole corpus the extra spend buys a MEASUREMENT: the human, AI and
    StealthGPT arms of a record are the same document type, so whether 3.7 Flash gives
    them the same label is a direct robustness check on the labelling itself. Disagreement
    within a record is the classifier being unstable, not the documents differing."""
    rows = [json.loads(l) for l in open(W / "detectionai/corpus.jsonl")]
    keep = rows if all_arms else [r for r in rows if r["arm"] == "human"]
    with open(out, "w") as fh:
        for r in keep:
            fh.write(json.dumps({"id": r["id"], "pair_id": r["pair_id"], "arm": r["arm"],
                                 "model": r["model"], "url": "", "text": r["text"],
                                 "genre": r["genre"], "len": r["words"],
                                 "genre_role_format": r["role_format"]},
                                ensure_ascii=False) + "\n")
    print(f"  DetectionAI: {len(keep):,} documents across "
          f"{len({r['pair_id'] for r in keep}):,} records "
          f"({len({r['arm'] for r in keep})} arms each)")
    return len(keep)


def opai(out, split="test", full=False):
    """OpAI-Bench trajectories, all nine versions of each.

    `full=True` reads every shard of default/test -- 4 domains x 4 generators, the same
    4,754 trajectories Pangram's Table 29 reports. The default reads only the news+essays
    gpt-5.4 slice from opai/, which is what the first scored run used.

    The nine versions of a trajectory are one document revised, so they must share a
    format. A label that drifts across v0->v8 is the classifier reacting to paraphrase,
    which is exactly what we would need to know before trusting it -- so all nine are
    labelled and the majority is propagated, rather than labelling v0 alone.

    Documents already extracted are skipped: re-running them would re-pay for outlines
    we hold. That is keyed on record_id against the existing outlines file.
    """
    pat = str(W / "opai_full/default/test/*.csv") if full else str(W / "opai/*gpt-5.4.csv")
    done = set()
    prev = W / "newevals/opai_outlines.jsonl"
    if full and prev.exists():
        done = {json.loads(l)["id"] for l in open(prev)}
        print(f"  skipping {len(done):,} documents already extracted")
    seen, n_rows, skipped = {}, 0, 0
    for f in sorted(glob.glob(pat)):
        dom, _, gen = Path(f).stem.partition("_")
        if not full and dom not in ("news", "essays"):
            continue
        for r in csv.DictReader(open(f, encoding="utf-8", errors="replace")):
            n_rows += 1
            if r["record_id"] in done:
                skipped += 1
                continue
            seen[r["record_id"]] = {"id": r["record_id"],
                                    "pair_id": r["document_hash_id"], "arm": r["version"],
                                    "model": gen if full else "gpt-5.4", "url": "",
                                    "text": r["text"], "genre": dom,
                                    "len": len(r["text"].split())}
    with open(out, "w") as fh:
        for v in seen.values():
            fh.write(json.dumps(v, ensure_ascii=False) + "\n")
    print(f"  OpAI-Bench: {n_rows:,} rows read, {skipped:,} already done, "
          f"{len(seen):,} documents across "
          f"{len({v['pair_id'] for v in seen.values()}):,} trajectories")
    return len(seen)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--which", required=True, choices=["detectionai", "opai", "opaifull"])
    a = ap.parse_args()
    (W / "newevals").mkdir(exist_ok=True)
    out = W / f"newevals/{a.which}_format_input.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists -- refusing to overwrite")
    n = (detectionai(out) if a.which == "detectionai"
         else opai(out, full=a.which == "opaifull"))
    print(f"  -> {out}   estimated format cost ${n*0.00225:,.2f} (batch, uncached)")


main()
