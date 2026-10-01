# Environments

**Two conda environments, because no single one covers everything.** The hosted
trainer's SDK and the provider SDKs have not coexisted cleanly here, so they are
kept apart. Which one you need depends only on what you are running.

| env | use it for | has |
|---|---|---|
| `ideadet` (from `environment-ideadet.yml`) | **almost everything**: the pipeline, scoring the local arms, calibration, reporting, feature discovery, Pangram | `openai`, `google-genai`, `google-cloud-storage`, `pangram-sdk`, `torch`, `transformers`, `spacy` |
| `ideadet-tinker` (from `environment-ideadet-tinker.yml`) | **only** the hosted Nemotron arm: `train_tinker.py`, and `score.py` with a `nemotron_*` model | `tinker`, `torch`, `transformers` |

## Create them

```bash
conda env create -n ideadet        -f env/environment-ideadet.yml
conda env create -n ideadet-tinker -f env/environment-ideadet-tinker.yml
```

The `environment-*.yml` files are exported without build strings, so they solve
across platforms. If a solve fails, or you want an exact byte-for-byte match of
what produced the current results, use the pip lockfiles instead:

```bash
conda create -n ideadet python=3.10 && conda activate ideadet
pip install -r env/requirements-lock-ideadet.txt
```

`requirements.txt` at the repo root is the loose, hand-maintained set — good for
a fresh install on a different machine. The files here are the exact captured
state of the environments these results were produced in. Prefer the root file
for new work and these for reproduction.

## Which interpreter runs which script

```bash
conda activate ideadet          # the default for everything below
python scripts/pipeline/run_pipeline.py --eval <id>
python scripts/eval/score.py --eval <id> --model modernbert_1m_full
python scripts/report/report_suite.py

conda activate ideadet-tinker   # only for the hosted Nemotron arm
python scripts/train/train_tinker.py --config nemotron_full --run <tag>
python scripts/eval/score.py --eval <id> --model nemotron_1m_full
```


## Versions these results were produced under

Python 3.10.19 (`ideadet`) and 3.11.15 (`ideadet-tinker`); numpy 2.2.6,
scikit-learn 1.7.2, torch 2.10.0, transformers 4.57.6, openai 2.8.1,
google-genai 1.63.0, pangram-sdk 1.0.0, tinker 0.25.0.

Nothing in the codebase pins a version. `scripts/selfcheck.py` is the fastest way
to confirm a new environment works:

```bash
python scripts/selfcheck.py     # exits non-zero on any problem
```

## A note on GPUs

Only the local arms need one: `train_encoder.py`, `train_qwen.py`, the
WebOrganizer format encoder, and `score.py` for `modernbert_*` / `qwen_*`. The
hosted Nemotron arm trains and scores on the provider's hardware, so its jobs
belong on a **CPU** partition — asking for a GPU there wastes an allocation and
queues longer.

On a mixed cluster, always pass `--constraint=bf16`: some cards are old enough
that bf16 misbehaves silently rather than failing, which costs a whole run before
anyone notices.
