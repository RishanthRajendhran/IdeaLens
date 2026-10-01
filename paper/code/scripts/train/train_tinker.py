#!/usr/bin/env python3
"""Train the Nemotron LoRA arm on the hosted Tinker service.

    python scripts/train/train_tinker.py --config nemotron_full --run v1m-r64-ep1

Training happens on the provider's hardware, so this process only drives the API
and needs no GPU — submit it to a CPU partition.

THE SCORING CONTRACT IS FIXED (prompts/training/contract.json) and training must
use it byte for byte, or every threshold fitted afterwards lands somewhere else.

    <|im_start|>system\\n{SYSTEM}<|im_end|>\\n<|im_start|>user\\n{text}<|im_end|>
    \\n<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n  -> one token: `human` or `ai`

Three operational facts, each learned the hard way:

* **Checkpoint names must be unique.** Reusing one raises, and that failure
  poisons the training client so every later request in the run also dies.
  Names are suffixed with the step.
* **Probes run on the stratified validation slice, never on a prefix of it.** A
  prefix is not the corpus: checkpoints once selected on a prefix that was 47%
  one format had to be discarded.
* **Prices are polled, never hard-coded**, and scoring bills the PREFILL meter
  because computing log-probabilities generates nothing.
"""
from __future__ import annotations

import argparse
import sys
import time

import _bootstrap  # noqa: F401

import numpy as np

from ideadet import config as C
from ideadet import paths, prompts as P
from ideadet import training as T
from ideadet.io import load_json, load_jsonl, load_npz, save_npz, write_json
from ideadet.llm.keys import require_key


def load_corpus(cfg, setting, split_file, outlines_dir):
    z = load_npz(split_file)
    outlines = {d: r.get("data") for d, r in
                __import__("ideadet.io", fromlist=["x"]).iter_outline_files(outlines_dir)}
    out = {}
    for name in ("train", "val", "test"):
        idx = np.flatnonzero(z["split"] == name)
        recs = [(str(z["ids"][i]), outlines.get(str(z["ids"][i])), int(z["y"][i]))
                for i in idx if str(z["ids"][i]) in outlines]
        texts, labels, owners = T.render_examples(recs, setting)
        out[name] = {"texts": texts, "y": np.asarray(labels), "owners": owners}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_args(ap, "training")
    ap.add_argument("--run", required=True, help="run tag; names the checkpoints")
    ap.add_argument("--splits", default="data/calibration/splits.npz")
    ap.add_argument("--outlines", default="data/indomain/deleak")
    ap.add_argument("--smoke", action="store_true",
                    help="a few hundred examples, to prove the plumbing before spending")
    ap.add_argument("--dry-run", action="store_true", help="cost estimate only")
    a = ap.parse_args()

    cfg = C.from_args(a, "training")
    require_key("tinker")
    import tinker
    from tinker import types

    setting = cfg["setting"]
    system = P.training_system(setting)
    contract = P.scoring_contract()
    # contract.json calls this `suffix`; accept either rather than KeyError on run 1
    suffix = contract.get("suffix") or contract["assistant_suffix"]
    tok_human = int(contract["label_tokens"]["human"])
    tok_ai = int(contract["label_tokens"]["ai"])

    data = load_corpus(cfg, setting, paths.REPO / a.splits, paths.REPO / a.outlines)
    if a.smoke:
        for k in data:
            data[k]["texts"] = data[k]["texts"][:256]
            data[k]["y"] = data[k]["y"][:256]
    print(f"corpus: " + "  ".join(f"{k}={len(v['texts']):,}" for k, v in data.items()))
    print(f"setting={setting}  base={cfg['base_model']}  lora_rank={cfg['lora_rank']}")

    if a.dry_run:
        from ideadet.llm import pricing
        try:
            live = pricing.refresh_tinker()
            print(f"live rates: {live}")
        except Exception as e:
            print(f"could not poll live rates ({e}); do not quote a cost from a "
                  f"hard-coded table for this provider")
        return 0

    service = tinker.ServiceClient()
    client = service.create_lora_training_client(
        base_model=cfg["base_model"], rank=cfg["lora_rank"])
    tokenizer = client.get_tokenizer()

    def build(text: str, y: int):
        prompt = (f"<|im_start|>system\n{system}<|im_end|>\n"
                  f"<|im_start|>user\n{text}<|im_end|>\n{suffix}")
        ptoks = tokenizer.encode(prompt)[: cfg["max_len"]]
        answer = tok_human if y == 1 else tok_ai
        # Loss on the answer token only: the prompt is context, not a target.
        weights = [0.0] * len(ptoks) + [1.0]
        # model_input and target_tokens must agree in LENGTH (the API rejects the
        # mismatch): input is the sequence minus its last token, targets are it
        # shifted left by one, and the only 1.0 weight is the answer token.
        full = ptoks + [answer]
        return types.Datum(
            model_input=types.ModelInput.from_ints(full[:-1]),
            loss_fn_inputs={"weights": weights[1:], "target_tokens": full[1:]})

    train = [build(t, y) for t, y in zip(data["train"]["texts"], data["train"]["y"])]
    rng = np.random.default_rng(cfg["seed"])
    rng.shuffle(train)

    bs = cfg["batch_size"]
    steps = max(1, int(len(train) * cfg["epochs"]) // bs)
    probe_every = max(1, steps // max(cfg.get("probes", 10), 1))
    print(f"{steps:,} steps at batch {bs} ({cfg['epochs']} epoch(s)); "
          f"probing every {probe_every} steps")

    def score(texts, weights_path, n=None):
        sampler = service.create_sampling_client(model_path=weights_path)
        tk = sampler.get_tokenizer()
        sel = texts if n is None else texts[:n]
        futures = [sampler.compute_logprobs_async(
            types.ModelInput.from_ints(tk.encode(
                f"<|im_start|>system\n{system}<|im_end|>\n"
                f"<|im_start|>user\n{t}<|im_end|>\n{suffix}")[: cfg['max_len']]))
            for t in sel]
        p = []
        for f in futures:
            lp = np.asarray(f.result().logprobs[-1], dtype=np.float64)
            pair = np.array([lp[tok_human], lp[tok_ai]])
            e = np.exp(pair - pair.max())
            p.append(float((e / e.sum())[0]))
        return np.asarray(p)

    best = {"sel": -1.0, "step": -1, "path": None}
    history, t0 = [], time.time()
    for step in range(steps):
        batch = train[step * bs:(step + 1) * bs]
        if not batch:
            break
        client.forward_backward(batch, loss_fn="cross_entropy").result()
        client.optim_step(types.AdamParams(
            learning_rate=cfg["lr"] * min(1.0, (step + 1) /
                                          max(1, cfg["warmup_frac"] * steps)))).result()

        if (step + 1) % probe_every == 0 or step == steps - 1:
            # Names must be UNIQUE across the run, hence the step suffix.
            name = f"{cfg.get('name', 'run')}_{a.run}_s{step + 1}"
            path = client.save_weights_for_sampler(name=name).result().path
            n_probe = min(cfg.get("probe_n", 4000), len(data["val"]["texts"]))
            p = score(data["val"]["texts"], path, n_probe)
            sel = T.sel_metric(p, data["val"]["y"][:n_probe])
            print(T.probe_report(step + 1, p, data["val"]["y"][:n_probe]), flush=True)
            history.append({"step": step + 1, "sel_metric": sel, "path": path})
            # Keep a checkpoint at every probe: scratch is cheap, re-running is not,
            # and the best step is rarely the last one.
            if sel > best["sel"]:
                best = {"sel": sel, "step": step + 1, "path": path}

    print(f"\nbest checkpoint: step {best['step']} sel={best['sel']:.4f}\n  {best['path']}")

    out = paths.outputs("training", f"nemotron_{setting}_{a.run}")
    out.mkdir(parents=True, exist_ok=True)
    for split in ("val", "test"):
        p = score(data[split]["texts"], best["path"])
        save_npz(out / f"preds_{split}.npz",
                 p_human=p, y=data[split]["y"],
                 owners=np.asarray(data[split]["owners"], dtype=object))
    write_json(out / "run.json", C.stamp(cfg, {
        "run": a.run, "steps": steps, "best": best, "history": history,
        "minutes": round((time.time() - t0) / 60, 1),
        "weights_note": "record this path in configs/models.yaml under `weights:`"}))
    print(f"wrote {out}\nAdd the best path to configs/models.yaml before scoring.")


if __name__ == "__main__":
    sys.exit(main())
