"""Two new author arms on StoryScope prompts: gpt-5.6-sol and gpt-6-astra.

StoryScope is 1,384 prompts x 6 authors (one human, five models), joined by
`pair_id`. This adds authors 7 and 8 on a 10% sample of the prompts, which turns
the 25-genre pilot finding (sol flagged at 96%, astra at 56%) into a test on
diverse prompts with a matched human story behind every one.

WHY NO LENGTH ENFORCEMENT HERE, unlike Test 2 and the genre pilot: 1,165 of the
1,384 StoryScope prompts already state their own target ("Your story must be
approximately 6000 words long"), and the five existing model arms were built by
sending the prompt as-is -- their lengths spread from a 2,659-word median
(deepseek) to 6,569 (gpt_5_4) against 4,965 for the human. Adding enforcement to
our two arms alone would make them the only length-controlled rows in the set and
not comparable with the five they exist to be compared against.

The human arm is NOT regenerated. Every sampled prompt already has its human
story in Test 8, already extracted, de-leaked and scored, so the control joins on
`pair_id` for free.

Ids follow build_storyscope.py exactly -- sha1("storyscope|<pid>|<model>")[:24] --
so nothing collides and `pair_id` joins straight to the existing rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

for _p in Path(__file__).resolve().parents:
    if (_p / "src" / "ideadet").is_dir():
        sys.path.insert(0, str(_p / "src"))
        break

from ideadet.llm import pricing  # noqa: E402

SRC = Path("${AUX_DIR}/data/StoryScope/test.csv")
OUT = Path("${AUX_DIR}/detector/evals/"
           "storyscope_new_generators")
FMT, ROLE_FMT = "Creative Writing", "creative_writing"
# Asserted, not classified, exactly as build_storyscope.py does: the upstream set
# is Creative Writing throughout and Test 8 was built on that assertion.

MODELS = {"gpt_5_6_sol": "gpt-5.6-sol", "gpt_6_astra": "gpt-6-astra"}
FLOOR = 50          # same stub floor as build_storyscope.py


def doc_id(pid: str, model: str) -> str:
    return hashlib.sha1(f"storyscope|{pid}|{model}".encode()).hexdigest()[:24]


def sample_prompts(n_frac: float, seed: int) -> list[tuple[str, str, int]]:
    import pandas as pd
    df = pd.read_csv(SRC)
    rows = [(str(r.prompt_id), str(r.prompt),
             len(str(r.human_story).split()) if isinstance(r.human_story, str) else 0)
            for r in df.itertuples() if isinstance(r.prompt, str)]
    k = max(1, round(len(rows) * n_frac))
    return random.Random(seed).sample(rows, k)


def gen_sync(cl, jobs, model, effort, workers, retries=3):
    """(key, prompt) -> {key: (text, usage)}. Used for the trial pass."""
    got = {}

    def one(job):
        key, prompt = job
        for attempt in range(1, retries + 1):
            try:
                r = cl.responses.create(model=model, reasoning={"effort": effort},
                                        input=[{"role": "user", "content": prompt}])
                return key, r.output_text.strip(), r.usage
            except Exception as e:
                if attempt == retries:
                    print(f"    {key}: FAILED {type(e).__name__}: {e}", flush=True)
                    return key, None, None
                time.sleep(5 * attempt)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for key, txt, u in ex.map(one, jobs):
            if txt:
                got[key] = (txt, u)
            print(f"    [{(time.time()-t0)/60:5.1f}m] {key}: "
                  f"{len(txt.split()) if txt else 'FAILED'}w", flush=True)
    return got


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frac", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--effort", default="high")
    ap.add_argument("--trial", type=int, default=0,
                    help="generate this many prompts per model synchronously, "
                         "measure real tokens, extrapolate, and stop")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()

    picks = sample_prompts(a.frac, a.seed)
    print(f"{len(picks)} prompts ({a.frac:.0%} of StoryScope, seed {a.seed})")
    hw = sorted(p[2] for p in picks)
    print(f"  human story words: median {hw[len(hw)//2]:,}  "
          f"p10 {hw[len(hw)//10]:,}  p90 {hw[-len(hw)//10]:,}")

    if a.trial:
        from openai import OpenAI
        cl = OpenAI()
        trial = picks[:a.trial]
        print(f"\nTRIAL: {a.trial} prompt(s) x {len(MODELS)} models, sync\n")
        per_model = {}
        for tag, model in MODELS.items():
            print(f"  {model}:")
            got = gen_sync(cl, [(f"{tag}|{pid}", pr) for pid, pr, _ in trial],
                           model, a.effort, a.workers)
            if not got:
                print(f"    no successful draws for {model}"); continue
            tin = sum(u.input_tokens for _, u in got.values()) / len(got)
            tout = sum(u.output_tokens for _, u in got.values()) / len(got)
            tre = sum(getattr(getattr(u, "output_tokens_details", None),
                              "reasoning_tokens", 0) or 0 for _, u in got.values()) / len(got)
            words = sum(len(t.split()) for t, _ in got.values()) / len(got)
            per_model[model] = (tin, tout, tre, words)
            print(f"    mean: {words:,.0f} words, in {tin:,.0f} tok, "
                  f"out {tout:,.0f} tok ({tre:,.0f} reasoning = {100*tre/tout:.0f}%)")

        print(f"\nEXTRAPOLATED to {len(picks)} prompts per model:")
        tot = 0.0
        for model, (tin, tout, _, _) in per_model.items():
            for mode in ("batch", "standard"):
                c = pricing.estimate(model, input_tokens=int(tin * len(picks)),
                                     output_tokens=int(tout * len(picks)), mode=mode)
                print(f"  {model:14s} {mode:9s} ${c['usd']:7.2f}")
                if mode == "batch":
                    tot += c["usd"]
        print(f"  {'TOTAL':14s} {'batch':9s} ${tot:7.2f}   "
              f"({len(picks)*len(MODELS)} stories)")
        print("\ntrial only; nothing written. Re-run without --trial to generate.")
        return

    from openai import OpenAI
    from ideadet.llm.openai_batch import run_batch
    cl = OpenAI()
    out = Path(a.out)
    (out / "stories").mkdir(parents=True, exist_ok=True)

    prompt_of = {pid: pr for pid, pr, _ in picks}
    corpus, labels, usage_all = [], {}, {}
    for tag, model in MODELS.items():
        print(f"\n=== {model} ({tag}) ===", flush=True)
        rows = [{"custom_id": f"{tag}|{pid}", "method": "POST", "url": "/v1/responses",
                 "body": {"model": model, "reasoning": {"effort": a.effort},
                          "input": [{"role": "user", "content": pr}]}}
                for pid, pr, _ in picks]
        got = run_batch(rows, description=f"storyscope 10% {tag}")

        usage = {"input": 0, "output": 0, "reasoning": 0}
        kept = dropped = 0
        for cid, body in got.items():
            pid = cid.split("|", 1)[1]
            txt = "".join(c.get("text", "")
                          for item in (body.get("output") or [])
                          for c in (item.get("content") or [])
                          if c.get("type") == "output_text").strip()
            u = body.get("usage") or {}
            usage["input"] += u.get("input_tokens", 0)
            usage["output"] += u.get("output_tokens", 0)
            usage["reasoning"] += (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
            n = len(txt.split())
            if n < FLOOR:                       # same stub floor as build_storyscope.py
                dropped += 1
                continue
            did = doc_id(pid, tag)
            corpus.append({"id": did, "source": "ai", "text": txt,
                           "format": FMT, "role_format": ROLE_FMT,
                           "model": tag, "pair_id": pid,
                           "title": "", "words": n})
            labels[did] = {"source": "ai", "model": tag, "pair_id": pid,
                           "words": n, "format": FMT}
            (out / "stories" / f"{did}.txt").write_text(txt)
            kept += 1
        usage_all[model] = usage
        spend = pricing.estimate(model, input_tokens=usage["input"],
                                 output_tokens=usage["output"], mode="batch")["usd"]
        w = sorted(r["words"] for r in corpus if r["model"] == tag)
        print(f"  kept {kept}, dropped {dropped} under {FLOOR}w, missing "
              f"{len(picks) - len(got)}")
        if w:
            print(f"  words: median {w[len(w)//2]:,}  p10 {w[len(w)//10]:,}  p90 {w[-len(w)//10]:,}")
        print(f"  actual ${spend:.2f}")

    (out / "corpus.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in corpus), encoding="utf8")
    (out / "labels.json").write_text(json.dumps(labels, indent=1), encoding="utf8")
    total = sum(pricing.estimate(m, input_tokens=u["input"], output_tokens=u["output"],
                                 mode="batch")["usd"] for m, u in usage_all.items())
    (out / "generation_meta.json").write_text(json.dumps(
        {"models": MODELS, "effort": a.effort, "mode": "batch", "frac": a.frac,
         "seed": a.seed, "n_prompts": len(picks), "n_written": len(corpus),
         "usage": usage_all, "cost_usd": round(total, 2),
         "length_enforcement": "none; the StoryScope prompts state their own target "
                               "and the five existing model arms were built the same way",
         "human_arm": "not regenerated; joins to test8_storyscope on pair_id"}, indent=1))
    print(f"\nwrote {len(corpus)} stories -> {out}/corpus.jsonl   total ${total:.2f}")


if __name__ == "__main__":
    main()
