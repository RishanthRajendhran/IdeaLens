# ideadet: the IdeaLens codebase

The package (`src/ideadet`), configs and scripts behind the paper's numbers. It documents exactly what ran; the trained
models, the training corpus (WildOutlines) and the evaluation sets we constructed are on Hugging Face. To score new
documents, use the `idealens` package at the root of this repository instead.

- `src/ideadet/pipeline/`: the format gate and the outline extractor; `src/ideadet/prompts.py` renders the prompts.
- `src/ideadet/detectors/`: IdeaLens and ProseLens (Nemotron via Tinker), the ModernBERT, Qwen and logistic-regression
  variants, and Pangram 4.
- `src/ideadet/calibration.py`, `scripts/calibrate/`: the global and per-format cuts on the human calibration split.
- `scripts/train/`: training for every reported model (`train_qwen.py` is the standalone trainer of the Qwen model).
- `scripts/data/build_evals/`: the builders of the evaluation sets; `configs/evals/`: one config per evaluation (the
  repository README maps their ids to the paper's names).
- `scripts/features/`: the item-level feature discovery of the paper's analysis section.
- `docs/`: setup, running, training, conventions and a glossary; `env/`: environments and lockfiles.

The code reads its prompts from the repository's top-level `prompts/` folder (`configs/paths.yaml`); `scripts/selfcheck.py`
checks that every prompt it references exists and renders.

Absolute paths are written as `${WORK_DIR}` (data and outputs), `${AUX_DIR}` (an earlier codebase some builders import
helpers from, not included), `${PROJECT_ROOT}`, `${HF_HOME}` and `${CONDA_PREFIX}`. They are not read from environment
variables: replace them with your own paths. Provider keys are read from the environment (`docs/RUNNING.md`).
