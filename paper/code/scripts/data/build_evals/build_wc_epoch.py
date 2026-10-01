"""Format-pass inputs for the two full sets: the re-filtered WildChat pairs and Epoch's
author-imitation corpus.

WildChat: `human_ideas` means the user supplied the story ARC -- ordered events and ending --
and the model wrote the prose. That is rung 5, so the idea label is human. `ai_ideation` is a
few-word request the model built everything from: rung 1, model ideas.

Epoch: `style_transfer` is a frontier model given five real passages by a named author and
told to imitate them. The ideas are the model's however well it wears the voice, so it is AI.
It is the cleanest surface-attack arm we have, and every passage already carries Pangram,
GPTZero and Originality.ai verdicts, so the comparison is on identical documents.
"""
import csv, glob, json, os
from pathlib import Path

W = Path("${WORK_DIR}/newevals")
EP = W / "epoch_imitation"
WCF = Path("${AUX_DIR}/data/WildChat/"
           "idea_provenance_pairs_1.json")


def wildchat():
    P = json.load(open(WCF))["pairs"]
    out = []
    for r in P:
        lab = r["provenance_label"]
        out.append({"id": f"wc2_{r['id']}_{r['conversation_hash'][:12]}",
                    "text": r["response"], "arm": lab,
                    "y": 1 if lab == "human_ideas" else 0,
                    "generator": r["model"], "structure": r["structure"],
                    "prompt_wc": r["prompt_wc"], "words": r["response_wc"],
                    "eval_score": r.get("eval_score")})
    return out


def epoch():
    # commercial-detector verdicts, keyed by the repo-relative path
    det = {}
    with open(EP / "results/all_detectors.csv") as fh:
        for row in csv.DictReader(fh):
            det[row["file"]] = row
    out = []
    for f in sorted(glob.glob(str(EP / "corpus/*/*/snippet_*.txt"))):
        rel = os.path.relpath(f, EP)
        _, genre, author, fn = rel.split(os.sep)
        d = det.get(rel, {})
        out.append({"id": f"ep_human_{genre}_{author}_{fn[:-4]}", "text": open(f).read().strip(),
                    "arm": "human", "y": 1, "genre": genre, "author": author,
                    "generator": "human", "pangram_pred": d.get("pangram_pred"),
                    "gptzero_pred": d.get("gptzero_pred"), "originality_pred": d.get("originality_pred")})
    for arm in ("vanilla", "style_transfer"):
        for f in sorted(glob.glob(str(EP / f"stages/{arm}/*/*/*.txt"))):
            rel = os.path.relpath(f, EP)
            _, _, genre, author, fn = rel.split(os.sep)
            d = det.get(rel, {})
            out.append({"id": f"ep_{arm}_{genre}_{author}_{fn[:-4]}",
                        "text": open(f).read().strip(), "arm": arm, "y": 0,
                        "genre": genre, "author": author, "generator": fn[:-4],
                        "pangram_pred": d.get("pangram_pred"),
                        "gptzero_pred": d.get("gptzero_pred"),
                        "originality_pred": d.get("originality_pred")})
    return out


def main():
    import collections, statistics as st
    for name, rows in (("wildchat2", wildchat()), ("epochimit", epoch())):
        for r in rows:
            r.setdefault("words", len(str(r["text"]).split()))
        f = W / f"{name}_format_input.jsonl"
        with open(f, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        w = st.median([r["words"] for r in rows])
        rate = 18.27 * (1 + 0.0009 * (w - 260))       # small-batch regime, incl. format pass
        print(f"{name}: {len(rows):,} docs -> {f.name}")
        print(f"   arms: {dict(collections.Counter(r['arm'] for r in rows))}")
        print(f"   generators: {dict(collections.Counter(r['generator'] for r in rows))}")
        print(f"   median {w:.0f} words, ${rate:.2f}/1k -> ${len(rows)/1000*rate:.0f}")
        det = sum(1 for r in rows if r.get("pangram_pred"))
        if det: print(f"   commercial-detector verdicts attached: {det:,}/{len(rows):,}")


if __name__ == "__main__":
    main()
