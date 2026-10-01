"""Turn the 240 Test-3 generations into an eval set the extraction pipeline can run.

One eval set, five conditions, keyed so a per-condition breakdown survives scoring:
`level` carries the condition, which is what eval_ood391's subgroup reporting splits on.

Every document here is AI-written by construction -- the question is not whether it is
AI but whether a detector reading only its IDEAS still says so once the human brief
that seeded it gets richer. There are therefore no human rows and no in-set threshold;
score it against a calibration-derived per-format cut.
"""
import json, collections
from pathlib import Path
V = Path("${WORK_DIR}/v391")
OUT = Path("${AUX_DIR}/detector/evals/test3_v2")
OUT.mkdir(parents=True, exist_ok=True)
ROLE = {"Academic Writing":"academic_writing","Creative Writing":"creative_writing",
        "Knowledge Article":"knowledge_article","News Article":"news_article",
        "Nonfiction Writing":"nonfiction_writing","Personal About Page":"personal_about_page",
        "Personal Blog":"personal_blog","User Reviews":"user_reviews"}
rows = [json.loads(l) for l in open(V/"test3_generations.jsonl")]
corpus, labels = [], {}
for r in rows:
    cid = f"t3v2_{r['condition'].split('_')[1]}_{r['id'][:40]}"
    corpus.append({"id": cid, "ext_id": cid, "source": "ai", "model": "gpt-5.6-sol",
                   "level": r["condition"], "format": r["format"],
                   "role_format": ROLE.get(r["format"], "nonfiction_writing"),
                   "topic": r["topic"], "words": r["words"],
                   "target_words": r["target_words"], "src_doc": r["id"],
                   "text": r["document"]})
    labels[cid] = {"source": "ai", "model": "gpt-5.6-sol", "level": r["condition"]}
(OUT/"corpus.jsonl").write_text("".join(json.dumps(c)+"\n" for c in corpus))
(OUT/"labels.json").write_text(json.dumps(labels, indent=1))
print(f"wrote {len(corpus)} rows -> {OUT}")
print("  by condition:", dict(collections.Counter(c['level'] for c in corpus)))
print("  by format:   ", dict(collections.Counter(c['format'] for c in corpus)))
