"""The trainer used for the reported IdeaLens-Qwen3.5-9B model (full fine-tuning with a two-way classification
head; batch 64 documents, learning rate 1e-5 with a cosine schedule, maximum length 8,192 tokens; the reported
checkpoint is step 12,056 of 13,161, selected on the full validation split). It is standalone: it takes its
settings on the command line rather than from configs/training/qwen_full.yaml."""
"""Qwen3.5-9B full-parameter SFT with a 2-way SEQUENCE-CLASSIFICATION head.

WHY A CLASSIFICATION HEAD, NOT THE LM HEAD. We tested the generative framing on
the already-trained 170k Nemotron: given an open `<think>` block it emits the
same label token 350 times in a row, on all 8 probe documents, with mass 1.0000
on {human, ai} and the third-place token 20 logits below. Single-position SFT
destroys generation entirely, so the LM head buys nothing that a purpose-built
head does not. Measured consequences of the swap, at bs=2 / seq=2048:

    logits per rank   (B,T,248320) 2.03 GB  ->  (B,2) 8 KB   [16.3 GB across 8 ranks]
    lm_head params    1.02 B (12% of the 8.21B text tower) -> 8,192

WHAT IS KEPT. The INPUT is still the Nemotron chat template via
`apply_chat_template(..., enable_thinking=False)`, byte-identical to the Tinker
arm. So Nemotron-vs-Qwen differs in exactly two things -- LoRA vs full SFT, and
LM head vs classification head -- rather than also differing in input format.
Qwen3.5-9B is instruction-tuned, so feeding it bare text would be off-distribution
even with a classification head; the head pools the final position, whose hidden
state has attended over the whole outline.

CONVENTIONS (detector/train/metrics.py). AI is the positive class, but stored y
is 1 for HUMAN, so the training label is `1 - y` and p_human = softmax(...)[:, 0].
A previous project run flipped the label and missed the predict() index, giving
AUC 0.276.

FSDP. The layer classes come from the model's own `_no_split_modules`
(`['Qwen3_5DecoderLayer', 'Qwen3_5VisionBlock']`) rather than a hardcoded string,
which is the pattern verl uses. HF Trainer owns wrapping, gradient checkpointing,
distributed eval gather and length grouping, so none of the four failure modes
from the hand-rolled loop can recur (checkpointing silently off,
all_gather_object on ragged lists, 4 GPUs marginal, NCCL deadlock from ranks
getting different forward counts under length grouping).

Qwen3.5-9B is multimodal (775 tensors: 426 language_model + 333 visual + mtp +
lm_head). `Qwen3_5TextForSequenceClassification` loads the ~8.2B text tower only;
the vision tower is never instantiated.
"""

import argparse, glob, json, os, sys
from pathlib import Path
import numpy as np
import torch
from transformers import (AutoTokenizer, Qwen3_5TextForSequenceClassification,
                          Trainer, TrainingArguments)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import metrics as M
import artifacts as A
import splits391 as S
from tinker391 import SYSTEM_BY_SETTING  # local copy, see train/tinker391.py

# PORTABLE: AID_QWEN may be a local snapshot directory or a hub id. The origin
# cluster pinned a snapshot path; here it defaults to the hub id so a fresh
# machine works with no edits.
SNAP = os.environ.get("AID_QWEN", "Qwen/Qwen3.5-9B")


class OutlineDS(torch.utils.data.Dataset):
    """Pre-tokenised chat-template prompts. `lengths()` feeds the length sampler."""

    def __init__(self, prompts, y_human, max_len):
        self.p, self.y, self.max_len = prompts, y_human, max_len

    def __len__(self):
        return len(self.p)

    def lengths(self):
        return [min(len(x), self.max_len) for x in self.p]

    def __getitem__(self, i):
        ids = self.p[i][: self.max_len]
        return {"input_ids": ids,
                "labels": int(1 - self.y[i])}      # AI is the positive class


class Collate:
    """Right-pad. The classification head pools the last non-pad position, which
    it locates from attention_mask, so right-padding is correct here."""

    def __init__(self, pad):
        self.pad = pad

    def __call__(self, feats):
        n = max(len(f["input_ids"]) for f in feats)
        ids = torch.full((len(feats), n), self.pad, dtype=torch.long)
        att = torch.zeros((len(feats), n), dtype=torch.long)
        for k, f in enumerate(feats):
            L = len(f["input_ids"])
            ids[k, :L] = torch.tensor(f["input_ids"]); att[k, :L] = 1
        return {"input_ids": ids, "attention_mask": att,
                "labels": torch.tensor([f["labels"] for f in feats], dtype=torch.long)}


# LENGTH GROUPING REMOVED, DELIBERATELY.
#
# transformers 5.15 dropped TrainingArguments.group_by_length, and a custom
# _get_train_sampler returning LengthGroupedSampler was added to replace it. That
# sampler is NOT distributed-aware, and on 4 ranks it desynchronised them: rank 0
# reached NCCL work 38004 while ranks 1-3 reached 38006, and the collective watchdog
# killed the run after 30 minutes (job <id>, ~57 min into training). This is the
# exact deadlock this module's docstring said HF Trainer was chosen to avoid --
# "ranks getting different forward counts under length grouping".
#
# Length grouping only saves padding compute. It is not worth reintroducing a
# distributed correctness hazard for, so the default sampler is used. If padding
# waste ever matters, the fix is DistributedLengthGroupedSampler, not this.


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setting", default="full", choices=A.SETTINGS)
    ap.add_argument("--run-tag", dest="run", required=True)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--bs", type=int, default=4)
    # EFFECTIVE BATCH IS FIXED, ACCUM IS DERIVED. optimizer-step batch is
    # world_size x bs x accum, so a fixed --accum silently halves the effective
    # batch when the same command lands on 4 GPUs instead of 8 -- which a
    # resumable run chained across allocations will do. Pin the effective batch
    # and solve for accum, so 4- and 8-GPU runs share one LR schedule and one
    # step count. --accum 0 (default) means "derive"; pass a positive value to
    # override deliberately.
    ap.add_argument("--eff-batch", type=int, default=64)
    ap.add_argument("--accum", type=int, default=0)
    ap.add_argument("--eval-bs", type=int, default=8)
    # Qwen is the one arm where the cap is bounded by GPU MEMORY rather than by the
    # model (context is 262,144) -- activation cost grows with sequence length on
    # 4x A100-80G. 4096 covers 100% of observed in-domain outlines (max 3,538), so
    # it is 'uncapped' in every sense that matters for this corpus, where 2048 was
    # truncating 0.75% for no benefit. Raise further only if a corpus needs it.
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--probes", type=int, default=4)
    # Each checkpoint is ~112 GB with optimizer state. Keeping every probe is right for
    # a 12-probe run (it answers the calibration-transfer question) but not for a run
    # that needs frequent checkpoints purely to survive 4-hour preemptible slices.
    # 0 = keep everything, matching the previous hardcoded behaviour.
    ap.add_argument("--save-limit", type=int, default=0)
    ap.add_argument("--n-train", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--resume", action="store_true",
                    help="continue from the newest checkpoint in the run dir")
    # --dry-run parses the REAL argv and exits. Two runs have now died after a
    # queue wait on a flag typo (--run for --run-tag, --n_train for --n-train)
    # because the preflight validated a hardcoded flag list instead of what the
    # launcher actually passes. qwen*.sh calls this with "$@" before torchrun.
    ap.add_argument("--dry-run", action="store_true",
                    help="parse args, print them, exit 0")
    a = ap.parse_args()
    _world = int(os.environ.get("WORLD_SIZE", 1))
    if not a.accum:
        per_step = a.bs * _world
        if a.eff_batch % per_step:
            raise SystemExit(f"--eff-batch {a.eff_batch} is not divisible by "
                             f"bs {a.bs} x world {_world} = {per_step}")
        a.accum = a.eff_batch // per_step
    eff = a.bs * a.accum * _world
    if eff != a.eff_batch:
        print(f"WARNING: effective batch {eff} != --eff-batch {a.eff_batch}",
              flush=True)
    if a.dry_run:
        print(f"  world={_world} bs={a.bs} accum={a.accum} -> effective {eff}")
        print("ARGS OK: " + json.dumps({k: v for k, v in vars(a).items()
                                        if k != "dry_run"}, default=str))
        return
    cfg = vars(a).copy()

    tk = AutoTokenizer.from_pretrained(SNAP)
    meta = S.load(); y_all = S.labels(meta)
    probe_rows = S.probe_idx(meta)

    tag = "items" if a.setting == "items" else a.setting
    z = np.load(A.TEXT / f"text_{tag}.npz", allow_pickle=True)
    row = S.align_to(np.asarray([str(x) for x in z["ids"]]), meta)
    if a.setting == "items":
        doc_row = np.repeat(row, np.diff(z["offsets"]))
        texts = np.asarray([str(x) for x in z["items"]], dtype=object)
    else:
        doc_row, texts = row, np.asarray([str(x) for x in z["texts"]], dtype=object)
    split_of, y_of = meta["split"][doc_row], y_all[doc_row]
    SYSTEM = SYSTEM_BY_SETTING[a.setting]

    def prompt_ids(t):
        s = tk.apply_chat_template(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": t}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return tk.encode(s, add_special_tokens=False)

    tr_i = np.where(split_of == "train")[0]
    if a.n_train:
        tr_i = np.sort(np.random.default_rng(0).choice(tr_i, a.n_train, replace=False))
    pb_i = np.where(np.isin(doc_row, probe_rows))[0]
    if len(pb_i) > 4000:
        pb_i = np.sort(np.random.default_rng(0).choice(pb_i, 4000, replace=False))

    is_main = int(os.environ.get("RANK", 0)) == 0
    if is_main:
        print(f"setting={a.setting} train={len(tr_i):,} probe={len(pb_i):,}", flush=True)
        print("PROMPT (first 300 chars of the decoded template):", flush=True)
        print("  " + tk.decode(prompt_ids(str(texts[tr_i[0]])))[:300].replace("\n", "\\n"),
              flush=True)

    enc = lambda idx: [prompt_ids(str(texts[i])) for i in idx]
    train_ds = OutlineDS(enc(tr_i), y_of[tr_i], a.max_len)
    probe_ds = OutlineDS(enc(pb_i), y_of[pb_i], a.max_len)

    model = Qwen3_5TextForSequenceClassification.from_pretrained(
        SNAP, num_labels=2, dtype=torch.bfloat16, attn_implementation="sdpa")
    model.config.pad_token_id = tk.pad_token_id or 0
    model.config.id2label, model.config.label2id = ({0: "human", 1: "ai"},
                                                    {"human": 0, "ai": 1})

    # ZERO-INIT THE SCORE HEAD. from_pretrained initialises the new head from
    # config.initializer_range (0.02) over a 4096-d hidden state whose post-norm
    # magnitude is large, which put initial logits at O(50). That gave loss ~54 and
    # grad_norm ~956; with max_grad_norm=1.0 every step was then scaled down ~956x,
    # so the effective LR was ~2e-8 and the model barely moved (job <id>:
    # train_loss 45.33, eval_loss plateaued at 2.23 vs ln2=0.693, test AUC 0.830).
    # Zeroing the head starts logits at exactly 0 -> loss = ln2 and grad norms O(1),
    # so clipping stops binding. Safe for a final linear layer: the two output units
    # get different gradients from different labels, so symmetry breaks on step 1.
    with torch.no_grad():
        model.score.weight.zero_()
        if getattr(model.score, "bias", None) is not None:
            model.score.bias.zero_()
    if is_main:
        print(f"score head zero-initialised: {tuple(model.score.weight.shape)}, "
              f"initial logits = 0, expected initial loss = {np.log(2):.4f}", flush=True)
    # The model's own _no_split_modules lists ['Qwen3_5DecoderLayer',
    # 'Qwen3_5VisionBlock'], but Qwen3_5TextForSequenceClassification instantiates
    # the text tower ONLY -- the vision block never exists, and FSDP raises
    # "Could not find the transformer layer class Qwen3_5VisionBlock in the model"
    # for any named class it cannot locate. Keep only classes actually present.
    present = {type(m).__name__ for m in model.modules()}
    wrap = [c for c in (getattr(model, "_no_split_modules", None) or []) if c in present]
    wrap = wrap or ["Qwen3_5DecoderLayer"]
    if is_main:
        print(f"FSDP wrapping {wrap} (present classes checked)", flush=True)

    def compute_metrics(ev):
        lg = ev.predictions[0] if isinstance(ev.predictions, tuple) else ev.predictions
        p_human = torch.softmax(torch.tensor(np.asarray(lg), dtype=torch.float32), -1)[:, 0].numpy()
        y_h = 1 - np.asarray(ev.label_ids)              # back to y=1 for HUMAN
        s = M.summarize(p_human, y_h, None, n_boot=0)
        t = s["point"]["tpr_at"]
        return {"sel": float(np.mean([t["0.005"], t["0.01"], t["0.02"]])),
                "auc": s["point"]["auc"], "tpr01": t["0.01"], "tpr005": t["0.005"]}

    # --resume MUST imply permission to write into the existing checkpoint dir.
    # artifacts.ckpt_dir() otherwise refuses a non-empty dir unless force=True or
    # SLURM_RESTART_COUNT>0. That second escape only covers an in-place Slurm REQUEUE;
    # this arm is chained as SEPARATE jobs via --dependency=afternotok, which always
    # start with SLURM_RESTART_COUNT=0. So every slice after the first died on
    # FileExistsError before training began -- 2026-08-19, three chains lost this way.
    # Resuming is not overwriting: the guard exists to stop a fresh run clobbering a
    # finished one, which --resume explicitly is not.
    out = A.ckpt_dir("qwen35", a.setting, a.run, config=cfg, force=(a.force or a.resume))
    world = int(os.environ.get("WORLD_SIZE", 1))
    spe = max(1, len(train_ds) // (a.bs * a.accum * world))
    every = max(1, spe // max(1, a.probes))

    # transformers 5.15 removed warmup_ratio and save_safetensors (safetensors is
    # now the only save format). Keep the same 3% warmup by computing the steps.
    targs = TrainingArguments(
        output_dir=str(out), num_train_epochs=a.epochs, learning_rate=a.lr,
        per_device_train_batch_size=a.bs, per_device_eval_batch_size=a.eval_bs,
        gradient_accumulation_steps=a.accum, bf16=True,
        # 3% warmup, but with a floor: on the 4k smoke there were only 31 optimizer
        # steps, so int(0.03*31)=0 collapsed to max(1,0)=1 -- effectively no warmup.
        # Floor at 10 steps, itself capped at 10% of the run so a tiny run does not
        # spend a third of itself warming up.
        warmup_steps=max(int(0.03 * spe * a.epochs),
                         min(10, max(1, int(spe * a.epochs) // 10))),
        lr_scheduler_type="cosine", weight_decay=0.01,
        # logging_steps=25 emitted exactly ONE loss line on the 31-step smoke, which
        # is why the blow-up could only be seen in the epoch average. Scale it.
        max_grad_norm=1.0, logging_steps=max(1, min(25, int(spe * a.epochs) // 20)),
        eval_strategy="steps", eval_steps=every,
        save_strategy="steps", save_steps=every,
        save_total_limit=(a.save_limit or None),
        # keep EVERY probe checkpoint: with save_total_limit=1 the Trainer deletes
        # earlier ones, and we then cannot check whether an earlier step matched the
        # final TPR with smaller logit margins (the calibration-transfer question).

        load_best_model_at_end=True, metric_for_best_model="sel", greater_is_better=True,
        fsdp="full_shard auto_wrap",
        fsdp_config={"transformer_layer_cls_to_wrap": wrap,
                     # FSDP-native checkpointing: transformers warns that
                     # gradient_checkpointing under FSDP adds a redundant
                     # AllGather in the backward pass.
                     "activation_checkpointing": True},
        report_to=[], seed=0, dataloader_num_workers=4, remove_unused_columns=False,
    )
    trainer = Trainer(model=model, args=targs, train_dataset=train_ds,
                        eval_dataset=probe_ds, compute_metrics=compute_metrics,
                        data_collator=Collate(tk.pad_token_id or 0))
    # RESUMABLE: a 339k-sample epoch is ~8h on 4 GPUs against qos=short's 4h wall,
    # so the run is designed to be chained across several short jobs rather than
    # needing one long superpod allocation. Every probe step already writes a full
    # Trainer checkpoint (save_total_limit=None), which carries optimizer, scheduler
    # and dataloader state, so resuming continues the same schedule exactly. The
    # launcher passes --resume; with no checkpoint present it starts fresh, so the
    # same command can be submitted repeatedly until training completes.
    ck = sorted(out.glob("checkpoint-*"), key=lambda q: int(q.name.split("-")[1]))
    resume = str(ck[-1]) if (a.resume and ck) else None
    if is_main:
        print(f"resume: {resume or 'none (fresh start)'}"
              + (f"   [{len(ck)} checkpoints on disk]" if ck else ""), flush=True)
    trainer.train(resume_from_checkpoint=resume)
    # save_model() and evaluate() are COLLECTIVE under FSDP -- save_model must
    # all-gather the sharded parameters and evaluate runs a distributed eval loop.
    # Calling them inside `if is_world_process_zero()` makes rank 0 issue collectives
    # the other ranks never join, and the run deadlocks until the 30-min NCCL
    # watchdog kills it (job <id>: rank 0 stuck at work 38004, ranks 1-3 at
    # 38006, AFTER training had completed cleanly). Every rank must call them; only
    # the file writes are rank-0 work.
    trainer.save_model(str(out / "best"))
    final_metrics = trainer.evaluate()
    if trainer.is_world_process_zero():
        tk.save_pretrained(out / "best")
        (out / "final_metrics.json").write_text(json.dumps(final_metrics, indent=2))

    # ---- FULL val + test: calibration needs all of val, never the probe subset ----
    for nm in ("val", "test"):
        idx = np.where(split_of == nm)[0]
        pr = trainer.predict(OutlineDS(enc(idx), y_of[idx], a.max_len))
        if not trainer.is_world_process_zero():
            continue
        lg = np.asarray(pr.predictions[0] if isinstance(pr.predictions, tuple)
                        else pr.predictions, dtype=np.float64)
        p_human = torch.softmax(torch.tensor(lg, dtype=torch.float32), -1)[:, 0].numpy()
        dr = doc_row[idx]
        A.save_preds("qwen35", a.setting, a.run, nm,
                     ids=(meta["ids"][dr] if a.setting != "items"
                          else np.array([f"{meta['ids'][d]}#{k}" for k, d in enumerate(dr)])),
                     logits=lg, p_human=p_human, y=y_of[idx], fmt=meta["format"][dr],
                     topic=meta["topic"][dr], word_count=meta["word_count"][dr],
                     doc_ids=meta["ids"][dr] if a.setting == "items" else None,
                     config=cfg, force=a.force)
        print("  " + M.fmt_row(nm, M.summarize(p_human, y_of[idx], meta["format"][dr],
                                               n_boot=0)), flush=True)
    print("QWEN391_DONE", flush=True)


if __name__ == "__main__":
    main()
