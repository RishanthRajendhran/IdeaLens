# Scripts

Thin, config-driven executables over `src/ideadet`. Nothing that varies between
runs lives in a script; a new eval or model arm is a YAML file, not new code.

Every script takes `--config <name>` (resolved under `configs/<kind>/`) and
repeatable `--set key.path=value` overrides, and writes a `run.json` provenance
stamp beside whatever it produces.

## By stage

### Data — `scripts/data/`
| script | what |
|---|---|
| `link_sources.py` | point `data/<eval>/` at your copies of the corpora |
| `materialize.py` | replace those links with real copies, for transfer or archiving |
| `validate.py` | check disk against the schemas; reports everything, exits non-zero |
| `write_dataset_docs.py` | regenerate every `data/<eval>/README.md` from config + disk |
| `prepare_training_corpus.py` | deduplicate, split, freeze |
| `import_results.py` | one-way import of predictions made before this repo existed |
| `build_evals/` | one builder per eval: how that corpus was made from its upstream |

### Pipeline — `scripts/pipeline/`
| script | what |
|---|---|
| `classify_format.py` | stage 0. Run on **every** new corpus, no exceptions |
| `run_pipeline.py` | stages 1 and 2. Resumable, batch only, `--dry-run` costs it first |

### Training — `scripts/train/`
`train_tinker.py` (hosted LoRA, no GPU needed), `train_encoder.py` (ModernBERT /
mmBERT), `train_qwen.py` (local decoder, multi-GPU), `fit_logistic.py`. See
`docs/TRAINING.md`.

### Evaluation — `scripts/eval/`
| script | what |
|---|---|
| `score.py` | one eval x one arm. Does **not** threshold: cuts are applied at report time |
| `run_suite.py` | many pairs; collects failures instead of stopping at the first |
| `embed.py` | embed once, cache, reuse — the cache is the expensive artifact |

### Calibration — `scripts/calibrate/`
`score_calibration.py` then `derive_thresholds.py`. The only producer of deployed
cuts; everything else reads `outputs/calibration/thresholds.json`.

### Reporting — `scripts/report/`
`report_eval.py` (one eval, every arm, both conventions), `report_suite.py` (the
cross-eval payload), `build_manifest.py` (what is on disk and what is missing).

### Analysis — `scripts/features/`
`sample_contrast.py` -> `run_discovery.py` -> `consolidate.py` proposes features;
`run_probes.py` measures feature FAMILIES; `report_bank.py` fits the interpretable
classifier over the 201 named features and prints what it weights.
`assign/` holds the ported scripts that scored the bank at 50k.

## Two habits worth keeping

**`--dry-run` before anything that spends.** `run_pipeline.py` costs the job without submitting it. Then run one or two
real trial jobs and extrapolate before a sweep — see the paper's cost appendix.

**Rerun rather than restart.** The pipeline writes one file per document and
resumes from what is already on disk; `run_suite.py` skips pairs already scored.
A job killed at 90% costs the last 10%, not the whole thing.
