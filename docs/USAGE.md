# Using idealens: step-by-step scenarios

This guide walks through common situations end to end: what to install, which keys you need, the exact commands,
and how to read the result. The [README](../README.md) has the reference material (every option, model and
threshold scheme); this page is the "how do I actually do X" companion.

| Scenario | GPU | Keys you need | Section |
|---|---|---|---|
| Check one or two documents | none | none | [1](#1-check-a-few-documents-in-the-browser) |
| Score documents from a laptop | none | Tinker + one LLM provider | [2](#2-score-documents-from-a-laptop-no-gpu) |
| Score on your own GPU server | one 80 GB GPU | one LLM provider | [3](#3-score-on-your-own-gpu-server) |
| Score with a small GPU or a CPU | optional | one LLM provider | [4](#4-score-with-a-small-gpu-or-only-a-cpu) |
| Thousands to millions of documents | one 80 GB GPU (or Tinker) | one LLM provider | [5](#5-score-a-large-collection) |
| Documents that must not leave your machines | one 80 GB GPU | none | [6](#6-keep-documents-on-your-own-machines) |
| Documents not in English | as above | as above | [7](#7-documents-in-other-languages) |
| Ideas vs. prose: who did what | as above | as above | [8](#8-who-wrote-the-ideas-and-who-wrote-the-prose) |
| A domain unlike web text (essays, reviews, ...) | as above | as above | [9](#9-calibrate-on-your-own-domain) |
| Work in Python or a notebook | as above | as above | [10](#10-from-python-or-a-notebook) |

Before you start, two things hold in every scenario:

- **The models are gated.** Request access on each model's Hugging Face page (for example
  [IdeaLens](https://huggingface.co/rishanthrajendhran/IdeaLens)), then run `huggingface-cli login` once. With the
  Tinker backend (scenario 2) you need access only to download the thresholds.
- **Input is JSONL**, one document per line, with a `text` field. `id` is optional but recommended; `format` and
  `topic` are optional (see [Formats](../README.md#formats)).

```json
{"id": "essay-001", "text": "Full text of the first document ..."}
{"id": "essay-002", "text": "Full text of the second document ..."}
```

To make that file from a CSV with pandas: `pd.read_csv("docs.csv").rename(columns={"body": "text"}).to_json("docs.jsonl", orient="records", lines=True)`.
If your text column has another name, you can also pass `--text-field body` instead of renaming it.

---

## 1. Check a few documents in the browser

The [IdeaLens & ProseLens demo](http://ideadetector.ai/) scores pasted text with both detectors, with nothing to install and no keys.
Use it to get a feel for the detectors; use the package below for anything you need to record or repeat.

---

## 2. Score documents from a laptop (no GPU)

IdeaLens and ProseLens are published on [Tinker](https://thinkingmachines.ai/tinker/), which runs them on its own
servers. Your laptop only sends the outline and reads back a score.

**Step 1: accounts and keys.**

1. Sign up at [auth.thinkingmachines.ai/sign-up](https://auth.thinkingmachines.ai/sign-up) and create an API key in
   the Tinker console.
2. Get a key for the LLM that writes the outlines. The default is Gemini 3.7 Flash, the extractor the published
   thresholds were fitted with: create a key in [Google AI Studio](https://aistudio.google.com/). Any other provider
   works too (see [scenario 6](#6-keep-documents-on-your-own-machines) and the
   [Credentials](../README.md#credentials) table).

**Step 2: install** (Python 3.10 or later):

```bash
python -m venv idealens-env && source idealens-env/bin/activate
pip install "idealens[tinker]"
huggingface-cli login
export TINKER_API_KEY=...
export GEMINI_API_KEY=...
```

**Step 3: price it, then run it.**

```bash
idealens run docs.jsonl -o scores.jsonl --backend tinker --dry-run   # sends nothing; prints the expected cost
idealens run docs.jsonl -o scores.jsonl --backend tinker
```

**Step 4: read the result.** Each line of `scores.jsonl` is your input record plus:

| Field | Meaning |
|---|---|
| `p_human` | probability that the ideas are human |
| `verdict.ai` | `true` if flagged as AI-ideated at the default operating point (1% false-positive rate) |
| `verdict.cut` | the threshold used: flagged when `p_human` is below it |
| `format`, `forced_format` | the format the document was assigned; `forced_format: true` means it was outside the eight formats and mapped to the closest |
| `outline` | the outline that was scored |
| `warnings` | anything that weakens the calibrated false-positive rate, such as a different extractor model |

A quick summary in Python:

```python
import pandas as pd
df = pd.read_json("scores.jsonl", lines=True)
df["ai"] = df["verdict"].map(lambda v: v and v["ai"])
print(df[["id", "p_human", "ai", "format"]])
```

**Cost.** Scoring on Tinker costs about $0.50 per 1,000 documents for IdeaLens at list price. Outline extraction is
the larger cost (about $0.03 per document with Gemini in batch mode); `--dry-run` prices both before you send
anything. ProseLens reads the document directly and needs no extraction:
`idealens score docs.jsonl -o prose.jsonl --model ProseLens --backend tinker`.

---

## 3. Score on your own GPU server

IdeaLens, ProseLens and IdeaLens-NoParaphrase run locally on vLLM on one 80 GB GPU (A100 80GB or H100 80GB). The
weights are a 66 GB download, cached after the first run.

```bash
pip install "idealens[vllm]"
huggingface-cli login
export GEMINI_API_KEY=...
idealens run docs.jsonl -o scores.jsonl
```

Loading the model takes a few minutes; after that, scoring is fast (hundreds of outlines in seconds), so put all your
documents in one run rather than many small ones. On a smaller GPU the package stops before loading and says why;
use `--backend tinker` (scenario 2) or a smaller model (scenario 4) instead. To split one model over two GPUs, use
Python: `il.Detector("IdeaLens", tensor_parallel_size=2)`.

**On a Slurm cluster**, run it as a batch job, not on a login node:

```bash
#!/bin/bash
#SBATCH --job-name=idealens
#SBATCH --gres=gpu:1            # one 80 GB GPU (A100 80GB or H100)
#SBATCH --cpus-per-task=8
#SBATCH --mem=100G              # loading the weights needs ~60 GB of CPU RAM
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
source idealens-env/bin/activate
export HF_HOME=/path/with/space/huggingface   # the weights are 66 GB; keep them off a small home quota
idealens run docs.jsonl -o scores.jsonl
```

The command can be re-run after a preemption or time limit: finished records are skipped.

---

## 4. Score with a small GPU or only a CPU

The ModernBERT and logistic detectors read the same outlines as IdeaLens and are much smaller. They are less accurate
than IdeaLens (see the paper), but need little or no GPU.

| Model | Runs on | Install |
|---|---|---|
| `IdeaLens-ModernBERT-L` | any GPU; a CPU for small jobs | `pip install "idealens[hf]"` |
| `IdeaLens-Qwen3.5-9B` | one GPU with room for 16 GB of weights plus inputs | `pip install "idealens[hf]"` |
| `IdeaLens-LogisticClassifier` | CPU only (embeds outlines with OpenAI) | `pip install "idealens[openai]"`, `OPENAI_API_KEY` |

```bash
idealens run docs.jsonl -o scores.jsonl --model IdeaLens-ModernBERT-L
```

If you already extracted outlines for IdeaLens, reuse them instead of extracting again:

```bash
idealens score outlines.jsonl -o modernbert.jsonl --model IdeaLens-ModernBERT-L
```

---

## 5. Score a large collection

For tens of thousands of documents or more, the steps are the same; what changes is cost control and robustness.

**1. Price it first.** `--dry-run` estimates tokens and dollars for every step without sending anything:

```bash
idealens run docs.jsonl -o scores.jsonl --mode batch --dry-run
```

**2. Use batch mode** for the LLM steps. It costs half as much where the provider has a batch API (Gemini on Vertex,
OpenAI, Anthropic); jobs take minutes to hours. Vertex batch also needs a Cloud Storage bucket:

```bash
export GOOGLE_CLOUD_PROJECT=my-project      # and: gcloud auth application-default login
idealens run docs.jsonl -o scores.jsonl --provider vertex --mode batch --gcs-bucket my-bucket
```

Not every model is served by every batch API (for example, OpenAI's Batch API does not serve gpt-6.1-sol); a batch
the provider rejects stops the run with the provider's message.

**3. Split the steps** so a failure in one doesn't cost the others, and so you can score with several detectors:

```bash
idealens classify docs.jsonl     -o formats.jsonl  --provider vertex --mode batch --gcs-bucket my-bucket
idealens extract  formats.jsonl  -o outlines.jsonl --provider vertex --mode batch --gcs-bucket my-bucket
idealens score    outlines.jsonl -o scores.jsonl
```

**4. Re-run to resume.** Every command appends to its output and skips records already there. Records whose provider
call failed are retried on the next run; the failed attempts are kept in `<output>.failed.jsonl`.

**5. Total the real cost** of a finished run: `idealens cost outlines.jsonl`.

---

## 6. Keep documents on your own machines

If your documents can't be sent to a commercial API, run the outline extractor yourself on any OpenAI-compatible
server (vLLM, Ollama, ...) and score locally on vLLM. Nothing leaves your machines.

```bash
# in one terminal: serve an open model with an OpenAI-compatible API
vllm serve <open-model> --port 8000
# in another
idealens run docs.jsonl -o scores.jsonl --provider compatible --base-url http://localhost:8000/v1 --llm-model <open-model>
```

Two caveats. The published thresholds were fitted on Gemini 3.7 Flash outlines, so with another extractor every
record carries a warning and the 1% false-positive rate is no longer guaranteed; calibrate on your own human documents
to restore it ([scenario 9](#9-calibrate-on-your-own-domain)). And the extractor must follow a long, structured
prompt; small models may produce outlines that fail validation (the package retries, then records the error).

---

## 7. Documents in other languages

IdeaLens was trained only on English, but the extractor writes an **English** outline of a document in any language,
and IdeaLens scores that outline. Nothing changes in the commands: pass the documents as they are.

```bash
idealens run spanish_docs.jsonl -o scores.jsonl
```

In the paper's 24-language evaluation, IdeaLens flags 86–98% of AI-ideated documents per language and at most
2.4% of documents written from a human's outline. Prose detectors, including ProseLens, are much less reliable on
low-resource languages. Format classification works the same way with the default LLM classifier; WebOrganizer's
encoder (`--method weborganizer`) was trained on English web pages, so keep the default for other languages.

---

## 8. Who wrote the ideas, and who wrote the prose?

IdeaLens answers "whose ideas?"; ProseLens answers "whose words?". Running both on the same documents separates the
four cases:

```bash
idealens run   docs.jsonl -o ideas.jsonl                      # IdeaLens
idealens score docs.jsonl -o prose.jsonl --model ProseLens    # ProseLens reads the text; no extraction
```

```python
import pandas as pd
ideas = pd.read_json("ideas.jsonl", lines=True).set_index("id")
prose = pd.read_json("prose.jsonl", lines=True).set_index("id")
both = pd.DataFrame({"ai_ideas": ideas["verdict"].map(lambda v: v and v["ai"]),
                     "ai_prose": prose["verdict"].map(lambda v: v and v["ai"])})
print(pd.crosstab(both["ai_ideas"], both["ai_prose"]))
```

| IdeaLens flags | ProseLens flags | Reading |
|---|---|---|
| no | no | human ideas, human prose |
| no | yes | a person's ideas, written or polished by AI |
| yes | no | AI ideas, written up by a person |
| yes | yes | AI ideas, AI prose |

Both are model predictions at a 1% false-positive rate, not proof of how a document was written; use them as one
signal among others, never as the sole basis for a decision about a person.

---

## 9. Calibrate on your own domain

The published thresholds were fitted on English web documents. On a different kind of text (student essays, product
reviews, legal briefs) the false-positive rate can differ. Fit your own thresholds on **human-written documents from
your domain**, then score against them. A threshold at a false-positive rate *q* needs at least 25/*q* human
documents (25 expected false positives): 2,500 for 1%, 500 for 5%.

```bash
idealens calibrate my_humans.jsonl --model IdeaLens --save-as essays
idealens run new_docs.jsonl -o scores.jsonl --thresholds essays
```

- `my_humans.jsonl` can hold raw documents, outlines or already-scored records; missing steps are run first.
  `--scored-out humans_scored.jsonl` keeps the scored records so you can refit later without paying again.
- With a mixed file, mark the label and calibrate on the human rows: `--label-field label --human-value human`. The AI
  rows then give a detection-rate report.
- Separate thresholds per subgroup (for example per course or per source):
  `--group-by course` at calibration, then `--thresholds essays --group-by course --scheme group:course` when scoring
  (each group needs at least 200 human documents).
- A threshold is only fitted where there are enough documents to estimate it; otherwise that verdict is `None` with a
  reason, never silently replaced by another threshold.
- Profiles live in `~/.config/idealens/thresholds` (or `$IDEALENS_HOME/thresholds`); `--out file.json` writes one to
  a file you can share.

---

## 10. From Python or a notebook

```python
import idealens as il

texts = [open(p).read() for p in ["a.txt", "b.txt"]]

formats = il.classify(texts)                  # one of eight formats per document
outlines = il.extract(texts, formats)         # role-labelled outlines (Gemini 3.7 Flash by default)
with il.Detector("IdeaLens", backend="tinker") as det:    # or backend="vllm" on an 80 GB GPU
    records = det.score_outlines(outlines, format=formats)

for r, o in zip(records, outlines):
    print(round(r["p_human"], 3), r["verdict"]["ai"])
    print(o.render())                         # the outline that was scored, one "[Role] content" line per item
```

- **Another LLM provider:** `from idealens.providers import make`, then pass `provider=make("openai", "gpt-6-sol")`
  (or `"anthropic"`, `"vertex"`, `"openrouter"`, `"compatible"` with `base_url=...`) to `classify` and `extract`.
- **One call:** `il.run(texts, det)` does all three steps.
- **Other operating points:** every record's `verdicts` holds the verdict at each calibrated false-positive rate
  (0.1% to 5% for every model; 10% and 20% for some) under the `global`, `per_format` and `per_topic` schemes;
  `il.Detector("IdeaLens", fpr=0.005, scheme="per_format")` changes the default `verdict`.
- **Close the detector** (the `with` block does it): vLLM keeps a background process running otherwise.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `401` / `GatedRepoError` when loading a model | request access on the model page, then `huggingface-cli login` |
| "the weights take 59 GiB, but vLLM may use ..." | the GPU is too small: use an 80 GB GPU, `--backend tinker`, or a smaller model |
| "no Vertex credentials" | `gcloud auth application-default login` and `GOOGLE_CLOUD_PROJECT`, or set `VERTEX_API_KEY` |
| every record has a `warnings` entry about the extractor | you are not using Gemini 3.7 Flash; results are still valid, but calibrate on your domain for a guaranteed false-positive rate |
| `forced_format: true` on many documents | the documents are outside the eight long-form formats (e.g. forum posts, ads); verdicts still use the global threshold, but the detector was not trained on such text |
| a record has an `error` in `outline.meta` | the extractor never produced a valid outline; re-run the same command to retry it |
| the job was killed or preempted | re-run the same command: finished records are skipped |
