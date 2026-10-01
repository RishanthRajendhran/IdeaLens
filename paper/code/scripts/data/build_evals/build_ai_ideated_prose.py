"""Stage A of the AI-ideated / human-written arm: generate the AI stories.

The arm this feeds asks the question the suite has no data for. Every existing
idea-provenance row pairs AI ideas with AI prose (Test 2 inverts it: human ideas,
AI prose). Nothing here carries AI ideas realised in HUMAN prose, which is the
exact class the labelling rule commits us to calling `ai`, and the class a
reviewer will ask about first.

The full arm is four stages:

  A. generate N stories from a bare genre prompt          <- this script
  B. extract + de-leak their outlines (the normal pipeline)
  C. hand the DE-LEAKED outlines to human writers, collect prose
  D. re-run the pipeline over the human prose and score it

Stage A deliberately keeps the user prompt naturalistic and verbatim -- the
literal thing someone would type -- so the ideas are not shaped by a
construction prompt of ours. The only enforcement is a floor:

  LENGTH IS A FLOOR, NOT A BAND. `data/schemas/corpus.schema.json` puts the
  practical floor for outline extraction at about 500 words, and the Creative
  Writing calibration humans run 536 words at p5 (median 1091), so a story that
  lands under 500 is both hard to extract from and scored against a cut fitted
  on much longer documents. Short draws are RESAMPLED with the identical prompt
  rather than regenerated with a "make it longer" instruction, which would put
  our wording into the ideas.

Batch by default, per the cost appendix: bulk generation is not latency-sensitive
and the batch meter is half price. `--mode sync` exists because at n=25 the batch
queue costs most of an hour to save about two dollars; it is a deliberate,
priced exception and not a licence to loop synchronous calls over a corpus.

Each generator writes its own `corpus_<tag>.jsonl`; `--merge` combines them into
the `corpus.jsonl` the pipeline reads. Ids carry the generator tag and `pair_id`
carries the genre, so the same prompt under two models joins across arms.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

for _p in Path(__file__).resolve().parents:      # same walk-up as scripts/_bootstrap.py
    if (_p / "src" / "ideadet").is_dir():
        sys.path.insert(0, str(_p / "src"))
        break

from ideadet.llm import pricing  # noqa: E402

# 25 genres, spread across register and mode rather than clustered in one
# neighbourhood of fiction. Genre is the ONLY axis of variation here; that is a
# known limit of the pilot, and StoryScope prompts are the intended second axis
# if this expands. Do not read 25 genres as 25 independent ideas.
GENRES = [
    "literary fiction", "hard science fiction", "high fantasy",
    "noir detective", "cozy mystery", "gothic horror", "cosmic horror",
    "psychological thriller", "espionage thriller", "western",
    "historical fiction", "romance", "magical realism", "dystopian fiction",
    "post-apocalyptic fiction", "cyberpunk", "steampunk", "space opera",
    "time travel", "absurdist comedy", "satire", "fable",
    "coming-of-age", "slice of life", "epistolary fiction",
]

PROMPT = "Write me a 500 word story in {genre}"


def slug(g: str) -> str:
    return g.replace(" ", "_").replace("-", "_")


def row(cid: str, genre: str, model: str, effort: str) -> dict:
    return {"custom_id": cid, "method": "POST", "url": "/v1/responses",
            "body": {"model": model, "reasoning": {"effort": effort},
                     "input": [{"role": "user",
                                "content": PROMPT.format(genre=genre)}]}}


def text_of(body: dict) -> str:
    """Pull assistant text out of a /v1/responses body, skipping reasoning items."""
    out = []
    for item in body.get("output", []) or []:
        for c in item.get("content", []) or []:
            if c.get("type") == "output_text":
                out.append(c.get("text", ""))
    return "".join(out).strip()


def submit(cl, rows: list[dict], desc: str, poll: int) -> tuple[dict, dict]:
    """Submit one batch, wait, return ({custom_id: text}, usage totals)."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        tmp = fh.name
    up = cl.files.create(file=open(tmp, "rb"), purpose="batch")
    Path(tmp).unlink(missing_ok=True)
    job = cl.batches.create(input_file_id=up.id, endpoint="/v1/responses",
                            completion_window="24h", metadata={"desc": desc})
    print(f"  batch {job.id}: {len(rows)} requests", flush=True)
    return wait_and_collect(cl, job.id, poll)


def wait_and_collect(cl, job_id: str, poll: int) -> tuple[dict, dict]:
    """Poll a batch to completion and pull its results.

    Split out of submit() so a batch that outlived its polling process can be
    re-attached with --resume-batch. The batch runs server-side; a dead poller
    costs nothing but the wait.
    """
    t0 = time.time()
    while True:
        j = cl.batches.retrieve(job_id)
        c = j.request_counts
        print(f"    [{(time.time()-t0)/60:5.1f}m] {j.status:12s} "
              f"completed={getattr(c,'completed',0)} failed={getattr(c,'failed',0)}",
              flush=True)
        if j.status in ("completed", "failed", "expired", "cancelled"):
            break
        time.sleep(poll)
    if j.status != "completed":
        raise SystemExit(f"batch {job_id} ended {j.status}: {j.errors}")

    got, usage = {}, {"input": 0, "output": 0, "reasoning": 0}
    for line in cl.files.content(j.output_file_id).text.splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        body = (rec.get("response") or {}).get("body") or {}
        txt = text_of(body)
        if txt:
            got[rec["custom_id"]] = txt
        u = body.get("usage") or {}
        usage["input"] += u.get("input_tokens", 0)
        usage["output"] += u.get("output_tokens", 0)
        det = u.get("output_tokens_details") or {}
        usage["reasoning"] += det.get("reasoning_tokens", 0)
    return got, usage


def run_sync(cl, jobs: list[tuple[str, str]], model: str, effort: str,
             workers: int, retries: int = 3) -> tuple[dict, dict]:
    """Synchronous fan-out. Priced at 2x batch; see the module docstring."""
    got, usage = {}, {"input": 0, "output": 0, "reasoning": 0}

    def one(job):
        cid, genre = job
        for attempt in range(1, retries + 1):
            try:
                r = cl.responses.create(
                    model=model, reasoning={"effort": effort},
                    input=[{"role": "user", "content": PROMPT.format(genre=genre)}])
                return cid, r.output_text.strip(), r.usage
            except Exception as e:                      # transient 429/5xx
                if attempt == retries:
                    print(f"    {cid}: FAILED after {retries} tries: "
                          f"{type(e).__name__}: {e}", flush=True)
                    return cid, None, None
                time.sleep(5 * attempt)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, (cid, txt, u) in enumerate(ex.map(one, jobs), 1):
            if txt:
                got[cid] = txt
                usage["input"] += u.input_tokens
                usage["output"] += u.output_tokens
                det = getattr(u, "output_tokens_details", None)
                usage["reasoning"] += getattr(det, "reasoning_tokens", 0) or 0
            print(f"    [{(time.time()-t0)/60:5.1f}m] {i}/{len(jobs)}  {cid}: "
                  f"{len(txt.split()) if txt else 'FAILED'}w", flush=True)
    return got, usage


def merge(out: Path) -> None:
    """Combine every corpus_<tag>.jsonl into the corpus.jsonl the pipeline reads."""
    # Carry forward anything the pipeline wrote back into corpus.jsonl. The
    # per-generator files are snapshots from generation time and do not have the
    # format label that `classify_format.py --apply` adds later; rebuilding from
    # them blindly drops it, and extraction then silently skips those rows.
    prior = {}
    cur = out / "corpus.jsonl"
    if cur.exists():
        for line in cur.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                keep = {k: r[k] for k in ("format", "role_format", "topic")
                        if r.get(k) is not None}
                if keep:
                    prior[r["id"]] = keep

    rows, seen = [], set()
    for f in sorted(out.glob("corpus_*.jsonl")):
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r["id"] in seen:
                raise SystemExit(f"duplicate id {r['id']} in {f.name}; "
                                 "duplicate ids silently drop rows in every batch join")
            seen.add(r["id"])
            r.update(prior.get(r["id"], {}))
            rows.append(r)
    if not rows:
        raise SystemExit(f"no corpus_*.jsonl in {out}")
    (out / "corpus.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    (out / "labels.json").write_text(json.dumps(
        {r["id"]: {"source": "ai", "model": r["model"], "level": r["level"]}
         for r in rows}, indent=1))
    by_model: dict[str, list[int]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r["words"])
    print(f"merged {len(rows)} rows -> {out}/corpus.jsonl")
    for m, wc in sorted(by_model.items()):
        wc.sort()
        print(f"  {m:14s} n={len(wc):3d}  words min {wc[0]} median {wc[len(wc)//2]} max {wc[-1]}")
    pairs = {}
    for r in rows:
        pairs.setdefault(r["pair_id"], []).append(r["model"])
    unpaired = [g for g, ms in pairs.items() if len(ms) < len(by_model)]
    if unpaired:
        print(f"  !! {len(unpaired)} genre(s) missing an arm: {', '.join(sorted(unpaired))}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25, help="stories; <= len(GENRES)")
    ap.add_argument("--model", default="gpt-5.6-sol")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--min-words", type=int, default=500,
                    help="hard floor; short draws are resampled, never re-prompted")
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--out", default="${AUX_DIR}/detector/evals/ai_ideated_prose")
    ap.add_argument("--poll", type=int, default=60)
    ap.add_argument("--mode", default="batch", choices=["batch", "sync"],
                    help="sync is 2x the price; see the module docstring")
    ap.add_argument("--workers", type=int, default=6, help="sync fan-out width")
    ap.add_argument("--tag", default=None,
                    help="generator tag in ids and filenames; defaults from --model")
    ap.add_argument("--resume-batch", default=None,
                    help="attach to an already-submitted round-1 batch id instead "
                         "of paying for a second submission")
    ap.add_argument("--merge", action="store_true",
                    help="only rebuild corpus.jsonl from the corpus_<tag>.jsonl on disk")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--genres-file", default=None,
                    help="one genre per line; replaces the built-in 25 (use a new --tag so ids stay unique)")
    a = ap.parse_args()

    if a.merge:
        merge(Path(a.out))
        return

    tag = a.tag or a.model.replace("gpt-", "").replace(".", "").split("-")[-1]
    pool = ([g.strip() for g in open(a.genres_file) if g.strip()] if a.genres_file else GENRES)
    if a.genres_file:
        clash = sorted(set(pool) & set(GENRES))
        if clash: raise SystemExit(f"--genres-file repeats built-in genres: {clash}")
        if len(set(pool)) != len(pool): raise SystemExit("--genres-file has duplicate genres")
        a.n = len(pool) if a.n == 25 else a.n
    genres = pool[:a.n]
    if a.n > len(pool):
        raise SystemExit(f"--n {a.n} exceeds {len(pool)} genres; add more first")

    # Cost first, per the cost appendix. Reasoning tokens bill at the OUTPUT rate.
    est_in, est_out = 15, 3000          # ~700 story tokens + ~2300 reasoning at high
    c = pricing.estimate(a.model, input_tokens=est_in * a.n,
                         output_tokens=est_out * a.n, mode=a.mode)
    print(f"{a.n} stories, {a.model} (effort={a.effort}), {a.mode}, tag={tag}")
    print(f"  estimate: ~${c['usd']:.2f} at {est_out} output tok/story "
          f"(reasoning bills at the output rate and is included)")
    print(f"  rates/Mtok: {c['rates_per_mtok']}")
    if a.dry_run:
        print("\nprompt sent verbatim, no system message:")
        print(f'  "{PROMPT.format(genre=genres[0])}"')
        print(f"\ngenres: {', '.join(genres)}")
        return

    from openai import OpenAI
    cl = OpenAI()

    out = Path(a.out)
    (out / "stories" / tag).mkdir(parents=True, exist_ok=True)

    stories: dict[str, str] = {}
    rounds: list[dict] = []
    pending = list(genres)
    total_usage = {"input": 0, "output": 0, "reasoning": 0}

    for rnd in range(1, a.max_rounds + 1):
        if not pending:
            break
        print(f"\nround {rnd}: {len(pending)} to draw", flush=True)
        keys = [(f"{slug(g)}__r{rnd}", g) for g in pending]
        if a.resume_batch and rnd == 1:
            print(f"  re-attaching to {a.resume_batch}", flush=True)
            got, usage = wait_and_collect(cl, a.resume_batch, a.poll)
        elif a.mode == "batch":
            rows = [row(cid, g, a.model, a.effort) for cid, g in keys]
            got, usage = submit(cl, rows, f"ai_ideated_prose {tag} round {rnd}", a.poll)
        else:
            got, usage = run_sync(cl, keys, a.model, a.effort, a.workers)
        for k in total_usage:
            total_usage[k] += usage[k]

        short, missing = [], []
        for g in pending:
            txt = got.get(f"{slug(g)}__r{rnd}")
            if txt is None:
                missing.append(g)
                continue
            n = len(txt.split())
            if n < a.min_words:
                short.append((g, n))
                # keep the longest draw seen so far as the fallback
                if g not in stories or n > len(stories[g].split()):
                    stories[g] = txt
            else:
                stories[g] = txt
        rounds.append({"round": rnd, "drawn": len(pending),
                       "accepted": len(pending) - len(short) - len(missing),
                       "short": short, "missing": missing})
        print(f"  accepted {len(pending)-len(short)-len(missing)}, "
              f"under {a.min_words}w: {len(short)}, missing: {len(missing)}", flush=True)
        pending = [g for g, _ in short] + missing

    # Write corpus.jsonl. `source` is IDEA-level ground truth and stays `ai` for
    # every stage of this arm, including the human-written prose in stage D.
    corpus, meta = [], []
    for g in genres:
        txt = stories.get(g)
        if txt is None:
            continue
        n = len(txt.split())
        cid = f"aiip_{tag}_{slug(g)}"
        corpus.append({"id": cid, "source": "ai", "text": txt,
                       "model": a.model, "words": n, "generator_tag": tag,
                       "pair_id": slug(g),          # joins to the human-prose row
                       "arm": "ai_prose",           # stage D rows will be human_prose
                       "level": "ai_ideas_ai_prose",
                       "lang": "en", "domain": "fiction", "topic": g,
                       "ext_id": None, "url": ""})
        meta.append({"id": cid, "genre": g, "prompt": PROMPT.format(genre=g),
                     "words": n, "under_floor": n < a.min_words})
        (out / "stories" / tag / f"{cid}.txt").write_text(txt)

    (out / f"corpus_{tag}.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in corpus) + "\n")
    (out / f"generation_meta_{tag}.json").write_text(json.dumps(
        {"model": a.model, "effort": a.effort, "mode": a.mode, "tag": tag,
         "prompt_template": PROMPT, "min_words": a.min_words, "rounds": rounds,
         "usage": total_usage, "n_requested": a.n, "n_written": len(corpus),
         "cost_usd": pricing.estimate(a.model, input_tokens=total_usage["input"],
                                      output_tokens=total_usage["output"],
                                      mode=a.mode)["usd"]}, indent=1))

    wc = sorted(r["words"] for r in corpus)
    under = [r["id"] for r in corpus if r["words"] < a.min_words]
    print(f"\nwrote {len(corpus)} stories -> {out}/corpus_{tag}.jsonl")
    print(f"  words: min {wc[0]}  median {wc[len(wc)//2]}  max {wc[-1]}")
    if under:
        print(f"  !! {len(under)} still under {a.min_words}w after {a.max_rounds} "
              f"rounds: {', '.join(under)}")
        print("     these are below the extraction floor; report or drop, do not "
              "silently pool")
    spend = pricing.estimate(a.model, input_tokens=total_usage["input"],
                             output_tokens=total_usage["output"], mode=a.mode)["usd"]
    print(f"  usage: in {total_usage['input']:,}  out {total_usage['output']:,} "
          f"(reasoning {total_usage['reasoning']:,})   actual ${spend:.2f}")
    merge(out)


if __name__ == "__main__":
    main()
