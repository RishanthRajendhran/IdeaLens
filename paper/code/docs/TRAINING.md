# Training

Four arms, one shared scoring contract, one shared split.

```bash
# 0. freeze the corpus and its splits, once, before anything is scored
python scripts/data/prepare_training_corpus.py \
    --source data/indomain --out data/calibration --name deleaked_outlines_1m

# 1. train
python scripts/train/train_tinker.py  --config nemotron_full   --run v1m-r64-ep1
python scripts/train/train_encoder.py --config modernbert_full --run v1m-ep1
python scripts/train/train_qwen.py      # the trainer used for the reported Qwen3.5-9B model; see its header
python scripts/eval/embed.py --eval indomain --out .scratch/cache/emb.npz
python scripts/train/fit_logistic.py  --config logistic_full --run v1m-lr \
    --embeddings .scratch/cache/emb.npz

# 2. calibrate, then score
python scripts/calibrate/score_calibration.py --config outline_1m --model nemotron_1m_full
python scripts/calibrate/derive_thresholds.py --config outline_1m
```

Record the resulting checkpoint path in `configs/models.yaml` before scoring
anything with it.

## The scoring contract

`prompts/training/contract.json` is the authority, and training must match it
byte for byte or every threshold fitted afterwards lands somewhere else.

```
<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{text}<|im_end|>
\n<|im_start|>assistant\n<think>\n\n</think>\n\n
```

Score = softmax over **only the two label tokens** at the final position.

- It is a **two-way** readout, not `exp(logprob)` of `human` alone. The two are
  monotone-related per prompt but not globally, so a threshold fitted under one
  does not carry to the other.
- Around 99% of mass sits on those two tokens after fine-tuning. **P(human) is
  therefore conditional on the answer being one of the two words, not a
  calibrated posterior** — say so in any write-up.
- Batches are **left-padded** so the final position is a real token in every row.
- For local decoders the label token ids come from **that model's own
  tokenizer**, never from the contract file's ids: those belong to a different
  vocabulary, and reading off the wrong row gives a confident number rather than
  an error.

## Things that will bite

**One epoch is enough** for every arm measured so far; val-to-test retention runs
0.64 / 0.72 / 0.80 across the three architectures.

**Checkpoint selection uses `sel_metric`** = mean TPR at {0.5%, 1%, 2%}, on the
val-select slice only. A single operating point is too noisy to rank correlated
checkpoints from one epoch.

**Probe on the stratified validation slice, never a prefix of it.** Checkpoints
once selected on a prefix that was 47% one format had to be discarded.

**Checkpoint names must be unique** on the hosted trainer. Reusing one raises,
and that failure poisons the training client so every later request in the run
also dies. Names are suffixed with the step.

**Save at every probe.** Scratch is cheap; the best step is rarely the last.

**Do not cap input length below what the data needs.** These arms emit one token,
so truncation only discards information. Measured on 4,000 in-domain outlines:
median 593 tokens, p99 1,860, max 3,538. The local decoder is the only arm whose
memory is genuinely bounded by input length.

**`--constraint=bf16` is not optional** on a mixed cluster: some partitions
include cards old enough that bf16 misbehaves silently rather than failing.

**Qwen pins the effective batch** and derives accumulation from `WORLD_SIZE`, so
the 4- and 8-GPU launches train identically. Do not "match" them by hand.
