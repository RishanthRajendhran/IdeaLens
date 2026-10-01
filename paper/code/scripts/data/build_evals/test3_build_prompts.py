"""Stage A: turn each source brief into four matched prompts (Conditions 1-4).

One gpt-5.6-sol call per source document, via the OpenAI BATCH API (50% cheaper, and
this is not latency-sensitive). The system prompt is prompts/eval/test3_four_stage.system.txt
verbatim; the user prompt fills its four placeholders from the brief.

Condition 5 is Test 2 and needs no construction call -- it is a fixed template filled
from the same brief, so all five conditions reuse one sample.
"""
import argparse, json, sys, time
from pathlib import Path

REPO = Path("${AUX_DIR}")
V = Path("${WORK_DIR}/v391")
SYS = (REPO/"prompts/eval/test3_four_stage.system.txt").read_text()
USR = (REPO/"prompts/eval/test3_four_stage.user.txt").read_text()

def render_user(b):
    outline = "\n".join(f"{i+1}. [{it['role_name']}] {it['content']}"
                        for i, it in enumerate(b["items"]))
    themes = "\n".join(f"- {t}" for t in b["global_themes"])
    return (USR.replace("{{DOCUMENT_DESCRIPTION}}", b["document_description"])
               .replace("{{GLOBAL_THEMES}}", themes)
               .replace("{{FULL_OUTLINE}}", outline)
               .replace("{{TARGET_WORD_COUNT}}", str(b["target_words"])))

ap = argparse.ArgumentParser()
ap.add_argument("--sample", default=str(V/"test3_sample.jsonl"))
ap.add_argument("--out", default=str(V/"test3_prompts.jsonl"))
ap.add_argument("--model", default="gpt-5.6-sol")
ap.add_argument("--effort", default="high")
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()

briefs = [json.loads(l) for l in open(a.sample)]
print(f"{len(briefs)} source briefs", flush=True)
if a.preview:
    b = briefs[0]
    print(f"\n=== SYSTEM ({len(SYS):,} chars) ===\n{SYS[:900]}\n   ... truncated ...")
    print(f"\n=== USER for {b['id'][:16]} ({b['format']}, {b['target_words']}w) ===")
    print(render_user(b))
    raise SystemExit(0)

from openai import OpenAI
cl = OpenAI()
rows = []
for b in briefs:
    rows.append({"custom_id": b["id"], "method": "POST", "url": "/v1/responses",
                 "body": {"model": a.model, "reasoning": {"effort": a.effort},
                          "input": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": render_user(b)}]}})
tmp = V/"test3_prompts_batch_in.jsonl"
tmp.write_text("\n".join(json.dumps(r) for r in rows))
up = cl.files.create(file=open(tmp, "rb"), purpose="batch")
job = cl.batches.create(input_file_id=up.id, endpoint="/v1/responses",
                        completion_window="24h",
                        metadata={"desc": "test3 four-stage prompt construction"})
print(f"batch {job.id} submitted ({len(rows)} requests)", flush=True)
(V/"test3_prompts_batch_id.txt").write_text(job.id)
while True:
    j = cl.batches.retrieve(job.id)
    print(f"  {j.status}  {getattr(j.request_counts,'completed',0)}/"
          f"{getattr(j.request_counts,'total',0)}", flush=True)
    if j.status in ("completed", "failed", "expired", "cancelled"):
        break
    time.sleep(60)
if j.status != "completed":
    raise SystemExit(f"batch ended {j.status}")
txt = cl.files.content(j.output_file_id).text
got, bad = {}, 0
for line in txt.splitlines():
    if not line.strip(): continue
    r = json.loads(line)
    body = (r.get("response") or {}).get("body") or {}
    out = ""
    for o in body.get("output", []):
        for c in o.get("content", []) or []:
            if c.get("type") == "output_text": out += c.get("text", "")
    try:
        got[r["custom_id"]] = json.loads(out[out.index("{"):out.rindex("}")+1])
    except Exception:
        bad += 1
print(f"parsed {len(got)}/{len(rows)}  (unparseable {bad})")
with open(a.out, "w") as fh:
    for b in briefs:
        if b["id"] in got:
            fh.write(json.dumps({**b, "prompts": got[b["id"]]}) + "\n")
print(f"wrote {a.out}")
