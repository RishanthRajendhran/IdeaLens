# Setup

## 1. Environment

```bash
pip install -r requirements.txt        # or: pip install -e '.[providers,local]'
```

`torch`, `transformers` and the local-model extras are only needed for the local
encoder and decoder arms. Every provider import in `ideadet.llm` is lazy, so a
missing SDK costs nothing until a script actually calls that provider.

## 2. Credentials

**Nothing resembling a key belongs in this repository.** Everything reads from
the environment. Check what you can reach:

```bash
python -m ideadet.llm.keys
```

| variable | needed for |
|---|---|
| `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=global`, `GOOGLE_GENAI_USE_VERTEXAI=1` | extraction, de-leak, eval generation |
| `OPENAI_API_KEY` | feature discovery, embeddings, GPT arms |
| `ANTHROPIC_API_KEY` | Claude generation arms |
| `TINKER_API_KEY` | the hosted LoRA trainer and its scorer |
| `PANGRAM_API_KEY` | the surface-detector baseline |
| `HF_TOKEN` | dataset and model downloads |

Vertex batch also needs a GCS bucket you can write to; set `IDEADET_GCS_BUCKET`.
**Include the scheme**: `gs://my-bucket`, not `my-bucket`. The URIs are parsed
with `gcs_uri[len("gs://"):]`, so a bare name silently loses its first five
characters and the upload 404s against a bucket that does not exist.
Point `HF_HOME` somewhere with space — model caches are large and home
directories usually are not.

## 3. Paths

Edit `configs/paths.yaml` once. It is the only file with machine-specific paths
in it. Every root can also be overridden per run:

```bash
IDEADET_SCRATCH_ROOT=/fast/disk python scripts/eval/score.py ...
python -m ideadet.paths          # print the resolved roots
```

Put `scratch` on a large filesystem: it holds checkpoints, token caches and raw
batch payloads. **`data` and `outputs` must be durable** — predictions that
existed only on an expiring scratch allocation have been lost before.

## 4. Data

The repository carries no dataset copies: several are large and several are
redistributable only under their upstream licence.

```bash
$EDITOR configs/data_sources.yaml     # point at your copies
python scripts/data/link_sources.py --dry-run
python scripts/data/link_sources.py
python scripts/data/write_dataset_docs.py     # regenerate the per-eval READMEs
python scripts/data/validate.py --all
```

Each eval directory then holds three levels: `raw/` (the untouched upstream
archive), `corpus.jsonl` (documents as fed to the pipeline), and the outline
stages. To move the tree somewhere the originals are not visible,
`scripts/data/materialize.py` replaces the links with copies — **check each
upstream licence first**.

## 5. Checkpoints

Model weights are not in the repository either. Fill in the paths in
`configs/models.yaml`, or export the environment variables it references
(`IDEADET_NEMO_1M_FULL_WEIGHTS`, `IDEADET_MB_1M_FULL_CKPT`, and so on).

To retrain instead, see `docs/TRAINING.md`.

## 6. Check it works

```bash
python scripts/report/build_manifest.py        # what is on disk, and what is missing
python scripts/report/report_suite.py          # every eval, scored or not
```

The manifest warns rather than guessing: unrecorded provenance, an incomplete
pipeline, a score file with no raw logits, a missing calibration.
