# Conventions that must not drift

Short, and all of them load-bearing. Each is here because breaking it produces a
number that looks reasonable rather than an error.

## Labels and orientation

```
y_human  1 = HUMAN, 0 = AI      (how labels are stored)
p_human  P(human), in [0, 1]
```

**AI is the positive class for every reported metric.** So `y_ai = 1 - y_human`,
`score_ai = 1 - p_human`, and a detector **fires below the threshold**.
Thresholds are therefore LOW quantiles of the human score distribution.

Getting this backwards is the most common error in this project's history — one
early run reported AUC 0.276 from it. `metrics.check_orientation` raises when the
arrays look flipped.

## The labelling rule

**Human ideas make a document human, however much of its surface an AI wrote.**
A set where every row is human-conceived is a false-positive curve, not an
accuracy test, and every fire on it is an error.

Where a rung is genuinely mixed, report it as its own row and never fold it into
an aggregate. One external benchmark's mixed rung measures as roughly 17-18%
human-derived under two independently trained detectors; a binary label fits it
badly and the write-up should say so.

## Thresholds

**Two conventions, always labelled, never mixed silently.**

- **deployed** (primary) — one cut per model, fitted once on a human-only
  calibration split, carried onto every eval unchanged. The only convention used
  in domain.
- **in-set** (secondary, OOD only) — the cut re-derived from the eval's own
  humans. Reported *beside* the deployed number, never instead of it. The two
  diverge by roughly 4x out of domain, and that divergence is a finding about
  deployment rather than a nuisance.

**Three calibration-derived schemes**: `global`, `format`, `topic`. All fitted on
the calibration split only. **A group with no calibrated cut is filtered and
counted, never given the global cut as a fallback** — a fallback silently mixes
two operating points in one column.

**Estimability**: a target FPR of `q` needs `q x n_humans >= 25`. Below that the
cut rests on a handful of documents and its own sampling error exceeds the
differences being reported. `derive` refuses to emit an unestimable cut.

**Per-group cuts are shrunk** toward the pooled cut with weight `n/(n+2500)`.
Raw per-format cuts overshoot the nominal FPR when a cell holds a dozen humans.

**Threshold uncertainty belongs in the interval.** `bootstrap_deployed_tpr`
resamples the calibration humans and refits the cut per draw.

## Metrics

**TPR at a fixed low FPR is the headline. AUC may accompany it, never replace
it** — two arms with the same AUC can differ by 30 points of TPR at the operating
point that matters. **Every TPR is printed beside its realised FPR.**

Sets where every row carries the same true label have no TPR. The reading is the
**fire rate** as the construction varies, and reporting a TPR there is a category
error.

## Outline rendering

**Items are joined by newline, never by space** — the space-joined variant scores
about 0.067 lower at 1% FPR. Always render through `ideadet.outlines.render`.

`document_description` and `global_themes` are kept in the stored record and
**dropped from every detector input**: they are written in the extractor's own
voice with no source text to paraphrase, so they carry almost no authorship
signal while adding tokens.

**Role labels stay in English** in every language variant. They are a small
closed vocabulary the classifier keys on heavily.

**Item scores pool by the mean of the log-odds** (`logit_mean`), adopted
2026-08-24 because it is the pooling under which ladder rungs come out monotone.

## The pipeline

**Never assert a format.** The extraction prompt is format-conditioned and the
response schema's role enum is per format, so a wrong label extracts against the
wrong vocabulary and produces an outline that looks entirely valid. Classify
every new corpus, including ones that "obviously" contain one kind of document.

**De-leak every eval.** A set scored on stage-1 outlines is not comparable with
one scored on de-leaked outlines. Sets where it has not run carry
`deleak_status: not_run` and are flagged everywhere they appear.

**Batch, never online, for anything bulk.** Batch is half price and the two bulk
stages dominate spend. Order rows so identical system prefixes sit consecutively:
that earns the cached-input discount and has been a several-fold cost difference.

**Record `extractor` and `paraphraser` on every outline.** Outlines built by
different models are a distribution difference and must never be pooled silently.

## Splits

Three **disjoint** slices, each with exactly one job: val-select (checkpoint
selection), calibration (**human only**, thresholds), test (reporting). Using one
slice for two jobs is a leak, and the usual version is letting the test set
supply both the threshold and the number.

**Disjointness holds at the source-document level, not the outline level.**
Deduplicate first: a duplicate spanning calibration and test leaks the threshold
into the test humans, and nothing downstream can detect it.

Stratify by format x label, seed it, and freeze it **before anything is scored**.

## Data

**Ids are stable across conditions and unique within a corpus.** Stability is
what makes paired analysis possible; uniqueness matters because every batch API
returns results keyed by id and a duplicate silently drops rows.

**Keep raw outputs.** Logits and per-item scores exist only at scoring time;
re-scoring is expensive and a summary written today cannot answer tomorrow's
question. Never replace a score file with an aggregate.

**Keep a checkpoint at every probe step.** Scratch is cheap; re-running a 30B
LoRA is not, and the best step is rarely the last.

## Cost

**Poll prices, never hard-code them.** Provider rates have moved more than once
during this project; `configs/pricing.yaml` carries an `as_of` date that is
checked at run time. For the hosted trainer, fetch live rates — and note that
**scoring bills the prefill meter**, because computing log-probabilities
generates nothing.

**Reasoning tokens bill at the output rate** and are reported separately from
completion tokens. A cost model reading only completions undercounts several-fold
at high thinking levels.

**Run one or two trial jobs and extrapolate before any sweep.**
