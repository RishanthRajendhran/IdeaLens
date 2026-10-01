# Running things

A task-oriented walkthrough. `README.md` says what the project is;
`docs/CONVENTIONS.md` says what must not drift. This says which command to type.

Everything is config-driven: `--config <name>` resolves under `configs/<kind>/`,
and repeatable `--set key.path=value` overrides any field. Every script writes a
`run.json` beside its output recording the resolved config and the git revision,
so a result can always be traced back to what produced it.

```bash
conda activate ideadet          # see env/README.md; a second env is needed only
                                # for the hosted Nemotron arm
```

---

## 0. First run on a new machine

```bash
$EDITOR configs/paths.yaml            # the only file with machine paths in it
$EDITOR configs/data_sources.yaml     # where your copies of the data are
python scripts/data/link_sources.py   # --dry-run first if you like
python scripts/data/write_dataset_docs.py
python scripts/data/validate.py --all
python -m ideadet.llm.keys            # which providers you can reach
python scripts/selfcheck.py           # exits non-zero on any inconsistency
```

Then `python scripts/report/build_manifest.py` to see what is present and what is
missing. It warns rather than guessing.

---

## 1. "What do we have, and what do the numbers say?"

```bash
python scripts/report/report_suite.py                    # every eval, every arm
python scripts/report/report_eval.py --eval test5_peer_review
python scripts/report/report_eval.py --eval test3_collaboration_ladder --markdown
```

Reading the output:

- Every TPR is printed beside its **realised** FPR. A nominal 1% cut landing at
  2.4% is not a 1% number.
- `[UNTREATED OUTLINES]` means the de-leak stage never ran on that set. Upper
  bound; do not pool it with the de-leaked sets.
- `not calibrated` means that arm has scores but no calibration split, so no
  deployed number exists for it. It is not an error and not a zero.
- Unscored evals appear as named gaps rather than vanishing.

Add `--n-boot 0` for a fast pass; the bootstrap is what makes the large sets slow.

---

## 2. "Score an existing eval with an existing model"

```bash
python scripts/eval/score.py --eval test8_storyscope --model nemotron_1m_full
python scripts/report/report_eval.py --eval test8_storyscope
```

Many at once, skipping what is already done:

```bash
python scripts/eval/run_suite.py --models nemotron_1m_full,modernbert_1m_full
python scripts/eval/run_suite.py --group "Idea provenance" --dry-run
```

`score.py` deliberately does **not** threshold. Cuts are applied at report time,
so a score file can be re-read under a new operating point without re-scoring.

Useful flags: `--stage extract` (the untreated-outline side of a pair),
`--stage document` (feed prose instead of outlines), `--limit N` for a smoke test.

---

## 3. "Add a new eval set"

1. Get the documents into `corpus.jsonl` — one JSON object per line with at least
   `id`, `text`, `source`. See `data/schemas/corpus.schema.json`. If it comes from
   an outside release, write a builder in `scripts/data/build_evals/` and put the
   construction decisions in its docstring.
2. Write `configs/evals/<id>.yaml`, extending `_base.yaml`.
3. Run the pipeline:

```bash
python scripts/pipeline/classify_format.py --eval <id> --config format_llm_flash
python scripts/pipeline/run_pipeline.py    --eval <id> --dry-run    # cost first
python scripts/pipeline/run_pipeline.py    --eval <id>
python scripts/data/validate.py --eval <id>
python scripts/data/write_dataset_docs.py --only <id>
```

4. Score and report as in §2.

**Classify the format even when it is obvious.** The extraction prompt carries
that format's role vocabulary and the response schema's role enum is per format,
so a wrong label produces an outline that looks entirely valid and was extracted
against the wrong vocabulary.

The pipeline is **resumable**: it writes one file per document and a rerun
continues from what is on disk. A job killed at 90% costs the last 10%.

---

## 4. "Train a model"

See `docs/TRAINING.md` for the details. The short version:

```bash
python scripts/data/prepare_training_corpus.py \
    --source data/indomain --out data/calibration --name deleaked_outlines_1m

python scripts/train/train_encoder.py --config modernbert_full --run v1m-ep1
conda activate ideadet-tinker
python scripts/train/train_tinker.py --config nemotron_full --run v1m-r64-ep1
```

Record the resulting checkpoint in `configs/models.yaml` before scoring with it.

---

## 5. "Calibrate, so numbers can be reported"

```bash
python scripts/calibrate/score_calibration.py --config outline_1m --model <arm>
python scripts/calibrate/derive_thresholds.py --config outline_1m
```

This is the only producer of deployed cuts. Everything else reads
`outputs/calibration/thresholds.json`. Running it for a second config merges
rather than replaces, so outline and document calibrations coexist.

Outline cuts and document cuts are **not interchangeable**: a column reporting
document scores needs a cut fitted on documents scored by the same model.

---

## 6. "What is the detector keying on?"

```bash
# free: computed features only
python scripts/features/report_bank.py --tier programmatic
python scripts/features/report_bank.py --tier all

# feature families, with the format-controlled numbers that say what generalises
python scripts/features/run_probes.py --eval indomain

# propose new features from contrast sets
python scripts/features/sample_contrast.py --config item_corpus_labels
python scripts/features/run_discovery.py   --config item_corpus_labels --contrast <file>
python scripts/features/consolidate.py     --glob 'outputs/feature_discovery/proposals/item_corpus_*.json'
```

Read the **format-controlled** and **leave-one-format-out** columns from
`run_probes.py`, not the pooled one: a pooled lexical AUC is mostly corpus topic.

---

## 7. "Run the surface baseline"

```bash
python scripts/eval/score.py --eval test1_source_paraphrase --model pangram_4
```

The paper counts a text as AI when Pangram's AI fraction plus half its AI-assisted fraction is at least 0.5.

---

## 8. Before spending money

```bash
python scripts/pipeline/run_pipeline.py  --eval <id> --dry-run
```

Then run one or two **real** trial jobs, take the measured usage, and extrapolate
with `ideadet.llm.pricing.extrapolate` before launching a sweep. Estimates from
token counts alone have been wrong in both directions. The paper's cost appendix has the
per-stage figures and the caching rule that has repeatedly been a several-fold
difference.

---

## 9. On a cluster

Never run heavy work on a login node; GPU jobs need a bf16-capable GPU.

---

## When something looks wrong

| symptom | likely cause |
|---|---|
| AUC well below 0.5 | labels or scores passed inverted. `metrics.check_orientation` raises on this |
| `no calibration for <arm>` | that arm has scores but no calibration split; run §5 |
| a scheme reports `skipped` | those scores carry no column for that grouping |
| TPR looks impossibly good | check the eval is not `[UNTREATED OUTLINES]`, and that the cut is deployed rather than in-set |
| a format's cut is missing | it is filtered and counted, never given the global cut. Check `n_filtered` |
| an unfilled `{{PLACEHOLDER}}` error | intended: an unfilled prompt slot produces output that looks valid and is not |

`python scripts/selfcheck.py` catches most structural problems in a few seconds.
