"""Build a corpus.jsonl from DetectRL-X for the outline pipeline.

Why this benchmark and not RAID: RAID's AI generations are almost all short (0.0-0.7%
clear our 501-word corpus floor) AND its human/AI length distributions diverge sharply
(24.5% vs 0.7% at >=500w in books), so any length-filtered subset hands the detector a
near-perfect length cue. DetectRL-X pairs a human and an LLM text per record from the
same source, and the two sides are length-matched (median 318 vs 310 words), so
filtering to >=500w on BOTH sides keeps the comparison honest.

Selection: english, and both `human_written_text` and `llm_generated_text` >= 500
words. Each surviving record contributes TWO documents, one per class, sharing a
`pair_id` so paired analysis stays possible downstream.

Domains are mapped onto the eight WebOrganizer formats, because the extraction prompt
is format-conditioned (it injects that format's role set). A wrong mapping silently
extracts with the wrong role vocabulary.

Attack files carry the same records with one side perturbed. `--attacks` adds them,
and rows are tagged with `attack` so the surface-attack-immunity claim can be read off
directly. Loading is one file at a time: three at once OOM-killed a login node.
"""

import argparse, hashlib, json, sys
from pathlib import Path

REPO = "WUJUNCHAO/DetectRL-X"
FLOOR = 500
FMT = {"Academic": "Academic Writing", "News": "News Article",
       "Novel": "Creative Writing", "Wiki": "Knowledge Article",
       "Webtext": "Nonfiction Writing", "SEO": "Nonfiction Writing"}


def slugfmt(f):
    return f.lower().replace(" ", "_")


def load(fname):
    from huggingface_hub import hf_hub_download
    return json.load(open(hf_hub_download(REPO, fname, repo_type="dataset")))


def emit(rows, attack, lang, out, seen):
    kept = 0
    for r in rows:
        if str(r.get("lang", "")).lower() != lang:
            continue
        h, a = str(r.get("human_written_text", "")), str(r.get("llm_generated_text", ""))
        if len(h.split()) < FLOOR or len(a.split()) < FLOOR:
            continue
        dom = r.get("domain", "")
        fmt = FMT.get(dom)
        if fmt is None:
            continue
        pid = hashlib.sha1(f"{dom}|{r.get('model')}|{h[:200]}".encode()).hexdigest()[:20]
        for side, txt, src in (("human", h, "human"), ("ai", a, "ai")):
            did = hashlib.sha1(f"{attack}|{pid}|{side}".encode()).hexdigest()[:24]
            if did in seen:
                continue
            seen.add(did)
            out.append({"id": did, "text": txt, "source": src,
                        "pair_id": pid, "attack": attack, "domain": dom,
                        "model": r.get("model"), "lang": lang,
                        "words": len(txt.split()),
                        "format": fmt, "role_format": slugfmt(fmt)})
            kept += 1
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default="english")
    ap.add_argument("--attacks", default="",
                    help="comma-separated, e.g. character_substitution,polishing")
    ap.add_argument("--per-attack", type=int, default=0,
                    help="cap pairs per attack file (0 = all)")
    a = ap.parse_args()

    out, seen = [], set()
    files = [("none", "Binary/binary_general_open.json")]
    for at in [x for x in a.attacks.split(",") if x]:
        files.append((at, f"Binary/binary_{at}_open.json"))

    for tag, fn in files:
        try:
            rows = load(fn)
        except Exception as e:
            print(f"  {tag}: SKIP ({type(e).__name__}: {str(e)[:90]})", flush=True)
            continue
        before = len(out)
        emit(rows, tag, a.lang, out, seen)
        del rows                                  # one file resident at a time
        n = len(out) - before
        if a.per_attack and tag != "none" and n > a.per_attack * 2:
            keep, drop, byp = [], 0, {}
            for r in out[before:]:
                byp.setdefault(r["pair_id"], []).append(r)
            for i, (_, rs) in enumerate(byp.items()):
                if i < a.per_attack:
                    keep.extend(rs)
                else:
                    drop += len(rs)
            out = out[:before] + keep
            print(f"  {tag}: {n:,} docs -> capped to {len(keep):,} "
                  f"({a.per_attack} pairs), dropped {drop:,}", flush=True)
        else:
            print(f"  {tag}: {n:,} docs kept", flush=True)

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    import collections
    print(f"\nwrote {len(out):,} documents -> {a.out}")
    print("  by attack:", dict(collections.Counter(r["attack"] for r in out)))
    print("  by format:", dict(collections.Counter(r["format"] for r in out)))
    print("  by source:", dict(collections.Counter(r["source"] for r in out)))
    print("  by model :", dict(collections.Counter(str(r["model"]) for r in out)))
    print(f"  est pipeline cost @ $0.0460/doc: ${len(out)*0.046:,.0f}")
    print("BUILD_DETECTRL_DONE", flush=True)


if __name__ == "__main__":
    main()
