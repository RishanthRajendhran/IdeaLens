#!/usr/bin/env python3
"""Train the local encoder arm (ModernBERT-large, or mmBERT for multilingual).

    python scripts/train/train_encoder.py --config modernbert_full --run v1m-lr2e5-ep1
    python scripts/train/train_encoder.py --config modernbert_docs --run v1m-docs --resume

Runs on one GPU. Use a bf16-capable GPU — on a mixed cluster some cards are old enough that bf16 misbehaves
silently rather than failing, and a silent numerical failure costs a whole run.

DYNAMIC BATCHING BY TOKEN COUNT, not by row count: outline lengths have a long
tail, and fixed row batches either waste most of the batch on padding or run out
of memory on the tail.

A CHECKPOINT IS SAVED AT EVERY PROBE, not only at the end. One epoch is enough
for every arm measured here, but the best step within that epoch is rarely the
last one, and re-running is far more expensive than the disk.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import config as C
from ideadet import paths
from ideadet import training as T
from ideadet.io import iter_outline_files, load_npz, save_npz, write_json


def batches(texts, labels, tok, token_budget: int, shuffle_seed=None):
    """Group rows so each batch holds roughly `token_budget` tokens."""
    order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
    if shuffle_seed is not None:
        rng = np.random.default_rng(shuffle_seed)
        # Shuffle in blocks: keeps similar lengths together (so padding stays
        # cheap) while removing the length ordering the model would otherwise see.
        blocks = [order[i:i + 64] for i in range(0, len(order), 64)]
        rng.shuffle(blocks)
        order = [i for b in blocks for i in b]
    batch, longest = [], 0
    for i in order:
        n = len(tok.encode(texts[i], truncation=True, max_length=8192))
        longest = max(longest, n)
        if batch and longest * (len(batch) + 1) > token_budget:
            yield batch
            batch, longest = [], n
        batch.append(i)
    if batch:
        yield batch


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_args(ap, "training")
    ap.add_argument("--run", required=True)
    ap.add_argument("--splits", default="data/calibration/splits.npz")
    ap.add_argument("--outlines", default="data/indomain/deleak")
    ap.add_argument("--out", default="", help="checkpoint directory; default under scratch")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()

    cfg = C.from_args(a, "training")
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    setting = cfg["setting"]
    z = load_npz(paths.REPO / a.splits)
    outlines = {d: r.get("data") for d, r in iter_outline_files(paths.REPO / a.outlines)}

    data = {}
    for name in ("train", "val", "test"):
        idx = np.flatnonzero(z["split"] == name)
        recs = [(str(z["ids"][i]), outlines.get(str(z["ids"][i])), int(z["y"][i]))
                for i in idx if str(z["ids"][i]) in outlines]
        texts, labels, owners = T.render_examples(recs, setting)
        if a.smoke:
            texts, labels, owners = texts[:512], labels[:512], owners[:512]
        data[name] = {"texts": texts, "y": np.asarray(labels), "owners": owners}
    print("corpus: " + "  ".join(f"{k}={len(v['texts']):,}" for k, v in data.items()))

    ckpt = Path(a.out) if a.out else paths.scratch("checkpoints",
                                                   f"encoder_{setting}_{a.run}")
    ckpt.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(cfg["base_model"])
    start = cfg["base_model"]
    if a.resume and (ckpt / "last").exists():
        start = str(ckpt / "last")
        print(f"resuming from {start}")
    model = AutoModelForSequenceClassification.from_pretrained(
        start, num_labels=2, attn_implementation="sdpa").cuda()

    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"])
    all_batches = list(batches(data["train"]["texts"], data["train"]["y"], tok,
                               cfg["token_budget"], shuffle_seed=cfg["seed"]))
    total = int(len(all_batches) * cfg["epochs"])
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=cfg["lr"], total_steps=max(total, 1),
        pct_start=cfg["warmup_frac"], anneal_strategy="linear")
    probe_every = max(1, total // max(cfg.get("probes", 10), 1))
    print(f"{total:,} steps, probing every {probe_every}")

    @torch.no_grad()
    def score(split):
        model.eval()
        d = data[split]
        p = np.zeros(len(d["texts"]))
        for b in batches(d["texts"], d["y"], tok, cfg["token_budget"]):
            enc = tok([d["texts"][i] for i in b], return_tensors="pt", padding=True,
                      truncation=True, max_length=cfg["max_length"]).to("cuda")
            probs = model(**enc).logits.softmax(-1)[:, cfg["human_index"]]
            for j, i in enumerate(b):
                p[i] = float(probs[j])
        model.train()
        return p

    best, history, t0 = {"sel": -1.0, "step": -1}, [], time.time()
    step = 0
    model.train()
    for _ in range(int(np.ceil(cfg["epochs"]))):
        for b in all_batches:
            if step >= total:
                break
            enc = tok([data["train"]["texts"][i] for i in b], return_tensors="pt",
                      padding=True, truncation=True,
                      max_length=cfg["max_length"]).to("cuda")
            labels = torch.tensor([int(data["train"]["y"][i]) for i in b]).cuda()
            loss = model(**enc, labels=labels).loss / cfg["grad_accum"]
            loss.backward()
            if (step + 1) % cfg["grad_accum"] == 0:
                opt.step()
                sched.step()
                opt.zero_grad(set_to_none=True)
            step += 1

            if step % probe_every == 0 or step == total:
                p = score("val")
                sel = T.sel_metric(p, data["val"]["y"])
                print(T.probe_report(step, p, data["val"]["y"]), flush=True)
                history.append({"step": step, "sel_metric": sel})
                model.save_pretrained(ckpt / "last")
                tok.save_pretrained(ckpt / "last")
                if cfg.get("save_every_probe"):
                    model.save_pretrained(ckpt / f"step{step}")
                if sel > best["sel"]:
                    best = {"sel": sel, "step": step}
                    model.save_pretrained(ckpt / "best")
                    tok.save_pretrained(ckpt / "best")

    print(f"\nbest: step {best['step']} sel={best['sel']:.4f} -> {ckpt/'best'}")

    out = paths.outputs("training", f"encoder_{setting}_{a.run}")
    out.mkdir(parents=True, exist_ok=True)
    for split in ("val", "test"):
        p = score(split)
        save_npz(out / f"preds_{split}.npz", p_human=p, y=data[split]["y"],
                 owners=np.asarray(data[split]["owners"], dtype=object))
    write_json(out / "run.json", C.stamp(cfg, {
        "run": a.run, "checkpoint": str(ckpt), "best": best, "history": history,
        "minutes": round((time.time() - t0) / 60, 1)}))
    print(f"wrote {out}\nAdd `checkpoint: {ckpt/'best'}` to configs/models.yaml.")


if __name__ == "__main__":
    sys.exit(main())
