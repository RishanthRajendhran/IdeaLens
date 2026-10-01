# idealens

`idealens` detects whether a document's **ideas** came from a person or an AI model, whoever wrote the words. It runs
the IdeaLens pipeline end to end:

1. **Classify** the document into one of eight long-form formats (an LLM with WebOrganizer's annotation prompt, or
   WebOrganizer's encoder).
2. **Extract** an outline: an LLM writes a role-labelled list of the document's ideas, using the same prompt and six
   worked examples the detector was trained with.
3. **Score** the outline with a detector, which returns P(human) and a verdict at a calibrated false-positive rate.

The same package also scores the prose-level detector ProseLens and the baselines released with the paper.

Models: [IdeaLens](https://huggingface.co/rishanthrajendhran/IdeaLens) and the other detectors listed under
[Models](#models). Data: [WildOutlines](https://huggingface.co/datasets/rishanthrajendhran/WildOutlines) (training
corpus), [IdeaShift](https://huggingface.co/datasets/rishanthrajendhran/IdeaShift),
[IdeaShift-X](https://huggingface.co/datasets/rishanthrajendhran/IdeaShift-X) and
[TwiceTold](https://huggingface.co/datasets/rishanthrajendhran/TwiceTold) (evaluation sets).

## Install

```bash
pip install "idealens[vllm]"          # the default scoring backend (Nemotron models, one 80 GB GPU)
pip install "idealens[hf]"            # transformers backend; needed for the ModernBERT and Qwen models
pip install "idealens[openai]"        # OpenAI, OpenRouter or any OpenAI-compatible endpoint (also the logistic models)
pip install "idealens[anthropic]"     # Claude
pip install "idealens[vertex]"        # Gemini on Vertex AI (batch mode also needs a GCS bucket)
pip install "idealens[weborganizer]"  # WebOrganizer's encoder for format classification
pip install "idealens[all]"
```

Python 3.10 or later. The vLLM extra pins `vllm==0.21.*`, `transformers>=5.15` and `xgrammar==0.2.1`.

The model repos are gated: request access on the model's Hugging Face page, then `huggingface-cli login`.

## Credentials

| Provider (`--provider`) | Variable |
|---|---|
| `gemini` (default) | `GEMINI_API_KEY` or `GOOGLE_API_KEY` |
| `vertex` | `GOOGLE_CLOUD_PROJECT` and application-default credentials; `IDEALENS_GCS_BUCKET` for batch mode |
| `openai` | `OPENAI_API_KEY` |
| `anthropic` | `ANTHROPIC_API_KEY` |
| `openrouter` | `OPENROUTER_API_KEY` |
| `compatible` | `--base-url` and, if the endpoint needs one, `--api-key` |

The logistic models embed outlines with OpenAI's `text-embedding-3-large`, so they also need `OPENAI_API_KEY`.

## Quick start

Input is JSONL with a `text` field and, optionally, `id`, `url`, `format` and `topic`.

```bash
idealens run docs.jsonl -o scores.jsonl --dry-run   # estimate tokens and cost; sends nothing
idealens run docs.jsonl -o scores.jsonl             # classify, extract and score with IdeaLens
```

Or one step at a time, which lets you extract once and score with several models:

```bash
idealens classify docs.jsonl     -o formats.jsonl
idealens extract  formats.jsonl  -o outlines.jsonl
idealens score    outlines.jsonl -o scores.jsonl --model IdeaLens
idealens score    outlines.jsonl -o scores_np.jsonl --model IdeaLens-NoParaphrase
```

Every command keeps the input record's fields and appends to its output. Re-running a command resumes it: records
already in the output are skipped, and records whose provider call failed are retried (the failed attempts are
moved to `<output>.failed.jsonl`).

In Python:

```python
import idealens as il

texts = ["...", "..."]
formats = il.classify(texts)                   # gemini-3.7-flash by default
outlines = il.extract(texts, formats)
with il.Detector("IdeaLens") as det:           # vLLM; the repo's published thresholds
    records = det.score_outlines(outlines, format=formats)

for r in records:
    print(r["p_human"], r["verdict"]["ai"])
```

`il.run(texts, det)` does all three steps. Any provider can be passed as an object:

```python
from idealens.providers import make
prov = make("openai", "gpt-6-sol")
outlines = il.extract(texts, formats, provider=prov, mode="batch")
```

## Models

`idealens models` lists them. All read the output of the same extraction step, except the two ProseLens models,
which read the document itself.

| Model | Reads | Backends |
|---|---|---|
| **IdeaLens** (default) | outline | vllm, hf |
| ProseLens | document | vllm, hf |
| IdeaLens-NoParaphrase | outline | vllm, hf |
| IdeaLens-Qwen3.5-9B | outline | hf |
| IdeaLens-Qwen3.5-9B-PerItem | each outline item | hf |
| IdeaLens-ModernBERT-L | outline | hf |
| IdeaLens-ModernBERT-L-NoParaphrase | outline | hf |
| IdeaLens-ModernBERT-L-RolesOnly | the outline's role sequence | hf |
| IdeaLens-ModernBERT-L-PerItem | each outline item | hf |
| ProseLens-ModernBERT-L | document | hf |
| IdeaLens-LogisticClassifier | outline | logistic |
| IdeaLens-LogisticClassifier-PerItem | each outline item | logistic |

Per-item models score each item and pool the item scores by their mean log-odds. Each model uses its own backend
unless you pass `--backend`.

The package does not paraphrase outlines. IdeaLens was trained and calibrated on paraphrased outlines;
IdeaLens-NoParaphrase was trained on outlines as extracted, and is the closer match to what this package produces.

## Verdicts and thresholds

A document is flagged as AI when its P(human) is **strictly below** the cut. The default verdict uses the 1% global
cut: the score below which 1% of the human calibration documents fall. Each record carries:

| Field | Contents |
|---|---|
| `p_human` | the detector's P(human) |
| `verdict` | the default verdict: `fpr`, `scheme`, `cut`, `ai` |
| `verdicts` | every calibrated false-positive rate (0.1%, 0.5%, 1%, 2%, 5%) under each scheme: `global`, `per_format`, `per_topic`, and `group:<field>` for cuts you fitted yourself |
| `warnings` | departures from how the cuts were fitted, such as a different extractor model |
| `item_p_human` | per-item scores (per-item models) |

Choose another operating point with `--fpr 0.005 --scheme per_format`. When a document has no cut under a scheme
(its format or topic was not calibrated, or its format was force-fitted), that verdict is `None` with a reason. It
never falls back to the global cut.

The published cuts were fitted on 80,000 human documents with outlines extracted by `gemini-3.7-flash` with the six
worked examples. Other extractor models work, but their outlines can shift the score distribution, so the
calibrated false-positive rate is no longer guaranteed. Every record says so in `warnings`.

### Calibrating on your own data

If your documents differ from web text, fit cuts on human documents from your own domain:

```bash
idealens calibrate my_humans.jsonl --save-as my_domain --model IdeaLens
idealens score outlines.jsonl -o scores.jsonl --thresholds my_domain
```

The input can be scored records, outlines or documents; the missing steps are run first. `--group-by FIELD` fits a
cut per value of a field, and `--label-field` / `--human-value` let you pass a mixed file and calibrate on its human
rows. A cut is fitted only where there are enough documents to estimate it (at least 25 expected below the cut and
200 in the group). Profiles are saved under `~/.config/idealens/thresholds` (or `$IDEALENS_HOME/thresholds`).

## Formats

The detectors were trained on eight formats: Academic Writing, Creative Writing, Knowledge Article, News Article,
Nonfiction Writing, Personal About Page, Personal Blog and User Reviews. A document in another format is assigned
the closest of the eight by a second LLM pass (or by the encoder's probabilities). Such a document has
`forced_format: true`, keeps its original label in `original_format`, and gets no per-format verdict.

If you know a document's format, give it in the record's `format` field or with `--format`; classification is then
skipped. `idealens run --check-format` classifies anyway and reports disagreements.

## Cost

`--dry-run` estimates the tokens and cost of a run before anything is sent, and `idealens cost output.jsonl` totals
a finished one. Extraction dominates: the prompt carries six worked examples, and reasoning tokens make up most of
the output. Batch mode (`--mode batch`) costs half as much where the provider has a batch API (Gemini on Vertex,
OpenAI, Anthropic); not every model is served by it.

## Hardware

| Model | Needs |
|---|---|
| IdeaLens, ProseLens, IdeaLens-NoParaphrase | one 80 GB GPU (A100 80GB or H100 80GB); the weights take 59 GiB; about 60 GiB of CPU RAM while loading |
| IdeaLens-Qwen3.5-9B models | one GPU; the weights take about 19 GB in bf16 (tested on 80 GB GPUs) |
| ModernBERT models | any GPU; a CPU works for small jobs |
| Logistic models | CPU only |

The vLLM backend checks that the weights fit before it starts, and stops with a message otherwise. Use
`tensor_parallel_size` (`Detector(..., tensor_parallel_size=2)`) to spread a model over two smaller GPUs.

## Development

```bash
pip install -e ".[dev]"
pytest tests
```

The tests need no GPU, network or API key.

## License

The code is released under the Apache License 2.0. Each model has its own license, given on its model page.

## Citation

A citation will be added here once the paper is on arXiv.
