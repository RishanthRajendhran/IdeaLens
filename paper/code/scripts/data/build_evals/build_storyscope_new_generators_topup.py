"""Top up the StoryScope new-generator arms (Test 32) from 138 to 250 prompts per generator.

random.Random(0).sample(prompts, 250) keeps the first 138 of random.Random(0).sample(prompts, 138) as its prefix
(verified), so the existing stories stay and only prompts 139-250 are generated. Everything else is identical to
build_storyscope_new_generators.py: same models, reasoning effort high, the StoryScope prompt sent as-is through the
Responses API, no length enforcement, the same 50-word stub floor, the same id scheme.

Writes NEW files only (corpus.jsonl / labels.json / generation_meta.json are left untouched):
  corpus_topup250.jsonl, labels_topup250.json, generation_meta_topup250.json, stories/<id>.txt (new ids),
  corpus_250.jsonl (existing 276 + new rows), batches_topup250.json (batch ids; a rerun resumes, never resubmits).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_storyscope_new_generators as B  # noqa: E402

for _p in HERE.parents:
    if (_p / "src" / "ideadet").is_dir():
        sys.path.insert(0, str(_p / "src"))
        break
from ideadet.llm import pricing  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--have", type=int, default=138)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--effort", default="high")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = B.OUT
    import random
    import pandas as pd
    df = pd.read_csv(B.SRC)
    rows = [(str(r.prompt_id), str(r.prompt)) for r in df.itertuples() if isinstance(r.prompt, str)]
    big, small = random.Random(a.seed).sample(rows, a.n), random.Random(a.seed).sample(rows, a.have)
    assert [p for p, _ in big[:a.have]] == [p for p, _ in small], "the 250-sample does not extend the 138-sample"
    have = {json.loads(l)["pair_id"] for l in open(out / "corpus.jsonl")}
    assert have <= {p for p, _ in small}, "existing corpus has prompts outside the 138-sample"
    new = big[a.have:]
    print(f"{len(new)} new prompts per model (existing corpus covers {len(have)} prompts)")

    idf = out / "batches_topup250.json"
    for f in ("corpus_topup250.jsonl", "corpus_250.jsonl"):
        if (out / f).exists():
            raise SystemExit(f"{out / f} exists -- refusing to overwrite")
    from openai import OpenAI
    cl = OpenAI()
    if idf.exists():
        jobs = json.loads(idf.read_text()); print(f"resuming {jobs}")
    else:
        if a.dry_run:
            print(json.dumps({"custom_id": f"gpt_6_astra|{new[0][0]}", "body": {"model": "gpt-6-astra",
                  "reasoning": {"effort": a.effort}, "input": [{"role": "user", "content": new[0][1][:300] + "..."}]}}, indent=1))
            return
        jobs = {}
        for tag, model in B.MODELS.items():
            fp = out / f"batch_in_topup250_{tag}.jsonl"
            with open(fp, "w") as fh:
                for pid, pr in new:
                    fh.write(json.dumps({"custom_id": f"{tag}|{pid}", "method": "POST", "url": "/v1/responses",
                                         "body": {"model": model, "reasoning": {"effort": a.effort},
                                                  "input": [{"role": "user", "content": pr}]}}, ensure_ascii=False) + "\n")
            up = cl.files.create(file=open(fp, "rb"), purpose="batch")
            job = cl.batches.create(input_file_id=up.id, endpoint="/v1/responses", completion_window="24h",
                                    metadata={"description": f"storyscope topup250 {tag}"})
            jobs[tag] = job.id
            print(f"  {model}: batch {job.id} ({len(new)} requests)", flush=True)
        idf.write_text(json.dumps(jobs))

    corpus, labels, usage_all = [], {}, {}
    for tag, bid in jobs.items():
        model = B.MODELS[tag]
        t0 = time.time()
        while True:
            job = cl.batches.retrieve(bid)
            c = job.request_counts
            print(f"  {model} [{(time.time()-t0)/60:.0f}m] {job.status} completed={getattr(c, 'completed', 0)} "
                  f"failed={getattr(c, 'failed', 0)}", flush=True)
            if job.status == "completed":
                break
            if job.status in ("failed", "expired", "cancelled"):
                raise SystemExit(f"batch {bid} ended {job.status}: {job.errors}")
            time.sleep(120)
        usage = {"input": 0, "output": 0, "reasoning": 0}
        kept = dropped = failed = 0
        for line in cl.files.content(job.output_file_id).text.splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            body = (rec.get("response") or {}).get("body")
            if body is None:
                failed += 1; continue
            pid = rec["custom_id"].split("|", 1)[1]
            txt = "".join(c.get("text", "") for item in (body.get("output") or [])
                          for c in (item.get("content") or []) if c.get("type") == "output_text").strip()
            u = body.get("usage") or {}
            usage["input"] += u.get("input_tokens", 0)
            usage["output"] += u.get("output_tokens", 0)
            usage["reasoning"] += (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
            n = len(txt.split())
            if n < B.FLOOR:
                dropped += 1; continue
            did = B.doc_id(pid, tag)
            corpus.append({"id": did, "source": "ai", "text": txt, "format": B.FMT, "role_format": B.ROLE_FMT,
                           "model": tag, "pair_id": pid, "title": "", "words": n})
            labels[did] = {"source": "ai", "model": tag, "pair_id": pid, "words": n, "format": B.FMT}
            (out / "stories" / f"{did}.txt").write_text(txt)
            kept += 1
        usage_all[model] = usage
        spend = pricing.estimate(model, input_tokens=usage["input"], output_tokens=usage["output"], mode="batch")["usd"]
        print(f"  {model}: kept {kept}, dropped {dropped} under {B.FLOOR}w, failed {failed}; ${spend:.2f}", flush=True)

    (out / "corpus_topup250.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in corpus))
    (out / "labels_topup250.json").write_text(json.dumps(labels, indent=1))
    old = [json.loads(l) for l in open(out / "corpus.jsonl")]
    (out / "corpus_250.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in old + corpus))
    total = sum(pricing.estimate(m, input_tokens=u["input"], output_tokens=u["output"], mode="batch")["usd"]
                for m, u in usage_all.items())
    (out / "generation_meta_topup250.json").write_text(json.dumps(
        {"models": B.MODELS, "effort": a.effort, "mode": "batch", "seed": a.seed, "n_prompts_total": a.n,
         "n_prompts_new": len(new), "n_written_new": len(corpus), "batches": jobs, "usage": usage_all,
         "cost_usd": round(total, 2), "extends": "generation_meta.json (138 prompts, same seed)"}, indent=1))
    print(f"wrote {len(corpus)} new stories; corpus_250.jsonl has {len(old) + len(corpus)}; total ${total:.2f}\nTOPUP_DONE")


if __name__ == "__main__":
    main()
