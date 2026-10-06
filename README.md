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
[TwiceTold](https://huggingface.co/datasets/rishanthrajendhran/TwiceTold) (evaluation sets). All of them are in the
[IdeaLens collection](https://huggingface.co/collections/rishanthrajendhran/idealens-6abee785ce6196fc0be9200f).

**Try it in your browser:** the [IdeaLens & ProseLens demo](http://ideadetector.ai/) scores your own text, with no installation or keys.

**Paper:** [IdeaLens: Detecting AI Ideas in Long-form Writing](https://arxiv.org/abs/2610.06778) (arXiv:2610.06778).

## Install

```bash
pip install "idealens[vllm]"          # the default scoring backend (Nemotron models, one 80 GB GPU)
pip install "idealens[hf]"            # transformers backend; needed for the ModernBERT and Qwen models
pip install "idealens[openai]"        # OpenAI, OpenRouter or any OpenAI-compatible endpoint (also the logistic models)
pip install "idealens[anthropic]"     # Claude
pip install "idealens[vertex]"        # Gemini on Vertex AI (batch mode also needs a GCS bucket)
pip install "idealens[weborganizer]"  # WebOrganizer's encoder for format classification
pip install "idealens[tinker]"        # score IdeaLens and ProseLens on Tinker's servers: no GPU needed
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
Tinker scoring (`--backend tinker`) needs `TINKER_API_KEY`.

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

## Ways to use idealens

**Step-by-step scenarios** (laptop without a GPU, your own GPU server or Slurm cluster, large collections, keeping
documents on your own machines, other languages, ideas vs. prose, calibrating on your own domain, notebooks, and
troubleshooting) are in the [usage guide](https://github.com/RishanthRajendhran/IdeaLens/blob/main/docs/USAGE.md). The summary below lists the building blocks.

### Without a GPU: Tinker

IdeaLens and ProseLens are also published on [Tinker](https://thinkingmachines.ai/tinker/), which runs the models on
its own servers, so any laptop works. Tinker bills your account per token: scoring with IdeaLens costs about $0.50 per
1,000 documents at list price (the outline extraction costs more; `--dry-run` prices both).

1. Sign up at [auth.thinkingmachines.ai/sign-up](https://auth.thinkingmachines.ai/sign-up) and create an API key in the
   Tinker console.
2. Install and run:

```bash
pip install "idealens[tinker]"
export TINKER_API_KEY=...       # your Tinker key
export GEMINI_API_KEY=...       # for outline extraction (or another provider, see Credentials)
idealens run docs.jsonl -o scores.jsonl --backend tinker
```

In Python, `il.Detector("IdeaLens", backend="tinker")`. ProseLens works the same way (`--model ProseLens`).

### Which detector?

| You want | Use |
|---|---|
| The paper's main idea-level detector | `IdeaLens` (one 80 GB GPU, or no GPU with `--backend tinker`) |
| The idea-level detector trained on outlines exactly as this package extracts them | `IdeaLens-NoParaphrase` |
| Idea-level detection on a small GPU or a CPU | `IdeaLens-ModernBERT-L` (or `-NoParaphrase`) |
| Idea-level detection with no GPU at all | `IdeaLens-LogisticClassifier` (needs OpenAI embeddings) |
| A score for every outline item, not just the document | the `-PerItem` models (`item_p_human` in each record) |
| How much the outline's structure alone gives away | `IdeaLens-ModernBERT-L-RolesOnly` (reads only the role sequence) |
| Who wrote the prose, for comparison | `ProseLens`, `ProseLens-ModernBERT-L` (no outline, no LLM calls) |

### 1. From documents, end to end

`idealens run` classifies each document's format, extracts its outline and scores it. This is the route the published
thresholds assume when the extractor is `gemini-3.7-flash` (the default).

```bash
idealens run docs.jsonl -o scores.jsonl --model IdeaLens
```

### 2. Extract once, score with several detectors

Extraction is the expensive step. Keep its output and score it with as many outline models as you like:

```bash
idealens classify docs.jsonl     -o formats.jsonl
idealens extract  formats.jsonl  -o outlines.jsonl
idealens score outlines.jsonl -o idealens.jsonl  --model IdeaLens
idealens score outlines.jsonl -o modernbert.jsonl --model IdeaLens-ModernBERT-L
idealens score outlines.jsonl -o per_item.jsonl   --model IdeaLens-ModernBERT-L-PerItem
```

### 3. Score outlines you already have

The `outline` field (or the field named by `--input-field`) can hold the extractor's JSON object or plain text with one
`[Role] content` line per item:

```json
{"id": "doc1", "format": "News Article", "outline": "[Central Development] The council approved the new pipeline.\n[Background Context] The reservoir has been shrinking for three summers."}
```

```python
with il.Detector("IdeaLens-NoParaphrase") as det:
    records = det.score_outlines(["[Central Development] ...\n[Background Context] ..."], format=["News Article"])
```

Roles must come from the format's role vocabulary for the scores to mean what they meant in training; the extractor
in this package uses it.

### 4. Score documents directly

The prose detectors read the document itself, so no outline and no LLM call is needed:

```bash
idealens score docs.jsonl -o prose.jsonl --model ProseLens
```

### 5. Choose the LLM that classifies and extracts

Any provider in [Credentials](#credentials) works for `classify`, `extract`, `run` and `calibrate`, online or as a batch
job (`--mode batch`, half price where the provider has a batch API). That includes a model you serve yourself behind an
OpenAI-compatible endpoint (vLLM, Ollama, ...):

```bash
idealens run docs.jsonl -o scores.jsonl --provider openai   --llm-model gpt-6-sol --mode batch
idealens run docs.jsonl -o scores.jsonl --provider compatible --base-url http://localhost:8000/v1 --llm-model <served model>
```

The published thresholds were fitted on `gemini-3.7-flash` outlines. With another extractor every record carries a
warning, and calibrating on your own human documents (step 8) restores a known false-positive rate.

### 6. Give formats yourself, or classify locally

A record's `format` field, or `--format` for the whole file, skips classification. A format outside the eight is
refused unless you pass `--force-fit`, which maps it to the closest one. `--method weborganizer` classifies with
WebOrganizer's encoder on your own machine instead of an LLM (`pip install "idealens[weborganizer]"`).

```bash
idealens run reviews.jsonl -o scores.jsonl --format "User Reviews"
idealens classify docs.jsonl -o formats.jsonl --method weborganizer --device cuda
```

### 7. Choose how the model runs

| Backend | When |
|---|---|
| `vllm` (default for the Nemotron models) | fastest; one 80 GB GPU |
| `tinker` | IdeaLens and ProseLens on Tinker's servers; no GPU, billed per token to your Tinker account |
| `hf` | transformers; for the Nemotron models, `--hf-mode adapter` downloads the base model plus a 3 GB adapter instead of the merged weights |
| `logistic` | the two logistic models; `Detector(..., embed=fn)` takes your own `text-embedding-3-large` vectors (for example, cached ones) instead of calling OpenAI |

`--weights PATH` scores with a local copy of a model's weights instead of downloading them (a directory, or the
`.npz` file for the logistic models). In Python, `Detector`
passes extra keyword arguments to the backend, e.g. `il.Detector("IdeaLens", tensor_parallel_size=2)`.

### 8. Choose the operating point, or calibrate your own

Every record carries verdicts at all calibrated false-positive rates and schemes (see
[Verdicts and thresholds](#verdicts-and-thresholds)); `--fpr` and `--scheme` pick the default one. For a new domain,
fit cuts on human documents from it and score against them:

```bash
idealens calibrate my_humans.jsonl --save-as my_domain --model IdeaLens --group-by source
idealens score outlines.jsonl -o scores.jsonl --thresholds my_domain --group-by source --scheme group:source
```

### 9. Large jobs

`--dry-run` prices a run before anything is sent; `idealens cost out.jsonl` totals a finished one. Every command
appends to its output and can be re-run after an interruption: finished records are skipped and failed provider calls
are retried. `--chunk` sets how many records are scored per write, `--workers` how many online requests run at once.

### 10. Without this package

Each model card on Hugging Face shows how to load the weights with transformers or vLLM and read P(human) directly,
and each model repo holds its `thresholds.json`.

## Models

`idealens models` lists them. All read the output of the same extraction step, except the two ProseLens models,
which read the document itself.

| Model | Reads | Backends |
|---|---|---|
| **[IdeaLens](https://huggingface.co/rishanthrajendhran/IdeaLens)** (default) | outline | vllm, hf |
| [ProseLens](https://huggingface.co/rishanthrajendhran/ProseLens) | document | vllm, hf |
| [IdeaLens-NoParaphrase](https://huggingface.co/rishanthrajendhran/IdeaLens-NoParaphrase) | outline | vllm, hf |
| [IdeaLens-Qwen3.5-9B](https://huggingface.co/rishanthrajendhran/IdeaLens-Qwen3.5-9B) | outline | hf |
| [IdeaLens-Qwen3.5-9B-PerItem](https://huggingface.co/rishanthrajendhran/IdeaLens-Qwen3.5-9B-PerItem) | each outline item | hf |
| [IdeaLens-ModernBERT-L](https://huggingface.co/rishanthrajendhran/IdeaLens-ModernBERT-L) | outline | hf |
| [IdeaLens-ModernBERT-L-NoParaphrase](https://huggingface.co/rishanthrajendhran/IdeaLens-ModernBERT-L-NoParaphrase) | outline | hf |
| [IdeaLens-ModernBERT-L-RolesOnly](https://huggingface.co/rishanthrajendhran/IdeaLens-ModernBERT-L-RolesOnly) | the outline's role sequence | hf |
| [IdeaLens-ModernBERT-L-PerItem](https://huggingface.co/rishanthrajendhran/IdeaLens-ModernBERT-L-PerItem) | each outline item | hf |
| [ProseLens-ModernBERT-L](https://huggingface.co/rishanthrajendhran/ProseLens-ModernBERT-L) | document | hf |
| [IdeaLens-LogisticClassifier](https://huggingface.co/rishanthrajendhran/IdeaLens-LogisticClassifier) | outline | logistic |
| [IdeaLens-LogisticClassifier-PerItem](https://huggingface.co/rishanthrajendhran/IdeaLens-LogisticClassifier-PerItem) | each outline item | logistic |

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
| `verdicts` | every calibrated false-positive rate (0.1% to 5% for every model, also 10% and 20% for some) under each scheme: `global`, `per_format`, `per_topic`, and `group:<field>` for cuts you fitted yourself |
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
| IdeaLens, ProseLens, IdeaLens-NoParaphrase | one 80 GB GPU (A100 80GB or H100 80GB); the weights take 59 GiB; about 60 GiB of CPU RAM while loading. IdeaLens and ProseLens also run on Tinker with no GPU (`--backend tinker`) |
| IdeaLens-Qwen3.5-9B models | one GPU; the weights take about 16 GB in bf16 (tested on 80 GB GPUs) |
| ModernBERT models | any GPU; a CPU works for small jobs |
| Logistic models | CPU only |

The vLLM backend checks that the weights fit before it starts, and stops with a message otherwise. Use
`tensor_parallel_size` (`Detector(..., tensor_parallel_size=2)`) to spread a model over two smaller GPUs.

## The paper's code, prompts and results

[`paper/`](paper/) holds what the paper's appendix points to: the full result table of every evaluation
([`paper/results/`](paper/results/)), the prompts, role vocabularies and worked examples
([`paper/prompts/`](paper/prompts/)), and the research code that built the corpus, trained the models and ran the
evaluations ([`paper/code/`](paper/code/)). The package above is the way to run the detectors; `paper/code/` documents
exactly what ran for the paper.

## Development

```bash
pip install -e ".[dev]"
pytest tests
```

The tests need no GPU, network or API key.

## License

The code, prompts and results in this repository are released under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/):
free to share and adapt for non-commercial purposes, with attribution and under the same license. Versions 0.1.0 to
0.1.3 were released under Apache 2.0. Each model and dataset has its own license, given on its page.

## Citation

If you use IdeaLens, ProseLens or the datasets, please cite the paper ([arXiv:2610.06778](https://arxiv.org/abs/2610.06778)):

```bibtex
@article{idealens2026,
  title         = {IdeaLens: Detecting AI Ideas in Long-form Writing},
  author        = {Rajendhran, Rishanth and Choi, Minjoon and Russell, Jenna and Namuduri, Ramya and B{\"o}l{\"o}ni-Turgut, Deniz and Karpinska, Marzena and Wieting, John and Iyyer, Mohit},
  journal       = {arXiv preprint arXiv:2610.06778},
  year          = {2026},
  eprint        = {2610.06778},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/2610.06778}
}
```
