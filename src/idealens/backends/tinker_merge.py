"""Merge a Tinker LoRA archive (the adapter/ folder of each Nemotron repo) into a loaded transformers model.

Copied verbatim from the load_adapter.py shipped in the model repos, which was verified to give weights bit-identical
to the merged checkpoints. Do not edit it here without re-running that check. PEFT cannot load these archives: in
transformers, Nemotron fuses the Mamba gate and x projections into one in_proj and stores each MoE layer's routed
experts as a single 3D tensor, so PEFT silently skips most of the adapter.
"""
import json

import torch
from safetensors.torch import load_file


def apply_tinker_lora(model, adapter_dir):
    """Merge a Tinker LoRA archive for Nemotron-3.5 into `model` in place. Returns the parameter names changed."""
    cfg = json.load(open(f"{adapter_dir}/adapter_config.json"))
    scale = cfg["lora_alpha"] / cfg["r"]
    lora = load_file(f"{adapter_dir}/adapter_model.safetensors")
    params = dict(model.named_parameters())
    touched = []
    for key_a in sorted(k for k in lora if k.endswith(".lora_A.weight")):
        A, B = lora[key_a], lora[key_a.replace(".lora_A.", ".lora_B.")]
        if A.numel() == 0:  # the experts have no gate projection; Tinker keeps an empty w3 placeholder
            continue
        name = key_a.removeprefix("base_model.model.").removesuffix(".lora_A.weight")
        rows = None
        if name == "model.lm_head":  # Tinker nests the LM head under model.
            target = "lm_head.weight"
        elif name.endswith((".gate_proj", ".x_proj")):  # Mamba: in_proj rows are [gate | x | B | C | dt]
            layer, proj = name.rsplit(".", 1)
            target = f"{layer}.in_proj.weight"
            start = 0 if proj == "gate_proj" else lora[f"base_model.model.{layer}.gate_proj.lora_B.weight"].shape[0]
            rows = slice(start, start + B.shape[0])
        elif name.endswith(".experts.w1"):  # routed experts: w1 = up_proj, one (expert, out, in) tensor per layer
            target = name.removesuffix("w1") + "up_proj"
        elif name.endswith(".experts.w2"):  # w2 = down_proj
            target = name.removesuffix("w2") + "down_proj"
        else:  # attention, Mamba out_proj, shared experts
            target = name + ".weight"
        W = params[target]  # KeyError here means the adapter does not match this model
        # For experts one side is shared (leading dim 1) and broadcasts across the 128 experts.
        delta = scale * torch.matmul(B.to(W.device, torch.float32), A.to(W.device, torch.float32))
        with torch.no_grad():
            view = W.data if rows is None else W.data[rows]
            assert view.shape == delta.shape, (target, tuple(view.shape), tuple(delta.shape))
            view.copy_((view.float() + delta).to(W.dtype))
        touched.append(target)
    return touched
