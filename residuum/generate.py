"""Generate text with an optional residual-stream steering vector."""

from __future__ import annotations

from typing import Any

import torch

from residuum.model import Vessel, apply_chat, encode
from residuum.steering import ResidualSteer, SteeringVector, capture_all_layer_residuals, logit_lens_from_residuals


def generate(
    vessel: Vessel,
    user: str,
    *,
    system: str,
    vector: SteeringVector | None = None,
    coeff: float = 0.0,
    max_new_tokens: int = 64,
    temperature: float = 0.0,
    seed: int = 0,
) -> dict[str, Any]:
    prompt = apply_chat(vessel.tokenizer, system, user)
    inputs = encode(vessel, prompt)
    prompt_len = int(inputs["input_ids"].shape[1])

    steer = None
    if vector is not None and coeff != 0.0:
        steer = ResidualSteer(vector.tensor.to(vessel.device), prompt_len=prompt_len, coeff=coeff)
        steer.attach(vessel.layers[vector.layer])

    gen_kwargs: dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": vessel.tokenizer.pad_token_id,
        "eos_token_id": vessel.tokenizer.eos_token_id,
    }
    if temperature and temperature > 0:
        gen_kwargs["do_sample"] = True
        gen_kwargs["temperature"] = temperature
        torch.manual_seed(seed)
    else:
        gen_kwargs["do_sample"] = False

    try:
        with torch.no_grad():
            out = vessel.model.generate(**inputs, **gen_kwargs)
    finally:
        if steer is not None:
            steer.remove()

    new_ids = out[0, prompt_len:]
    text = vessel.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
    return {
        "prompt": prompt,
        "text": text,
        "n_prompt_tokens": prompt_len,
        "n_new_tokens": int(new_ids.numel()),
    }


def first_token_probs(
    vessel: Vessel,
    user: str,
    *,
    system: str,
    vector: SteeringVector | None = None,
    coeff: float = 0.0,
) -> torch.Tensor:
    """Softmax over the next-token logits after the prompt. [vocab]"""
    prompt = apply_chat(vessel.tokenizer, system, user)
    inputs = encode(vessel, prompt)
    prompt_len = int(inputs["input_ids"].shape[1])
    steer = None
    if vector is not None and coeff != 0.0:
        steer = ResidualSteer(vector.tensor.to(vessel.device), prompt_len=prompt_len, coeff=coeff)
        steer.attach(vessel.layers[vector.layer])
    try:
        with torch.no_grad():
            out = vessel.model(**inputs)
            logits = out.logits[0, -1].float()
            return torch.softmax(logits, dim=-1).cpu()
    finally:
        if steer is not None:
            steer.remove()


def lens_for_prompt(
    vessel: Vessel,
    user: str,
    *,
    system: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    prompt = apply_chat(vessel.tokenizer, system, user)
    inputs = encode(vessel, prompt)
    residuals = capture_all_layer_residuals(
        vessel.layers,
        vessel.model,
        inputs["input_ids"],
        inputs.get("attention_mask"),
    )
    return logit_lens_from_residuals(
        residuals,
        vessel.final_norm(),
        vessel.lm_head(),
        vessel.tokenizer,
        top_k=top_k,
    )
