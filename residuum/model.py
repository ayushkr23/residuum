"""Load a small open-weight causal LM and find its decoder layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from residuum import DEFAULT_MODEL_ID, FALLBACK_MODEL_ID


@dataclass
class Vessel:
    model_id: str
    model: Any
    tokenizer: Any
    layers: list[Any]
    device: torch.device
    n_params: int
    fallback_used: bool = False

    @property
    def n_layers(self) -> int:
        return len(self.layers)

    @property
    def hidden_size(self) -> int:
        return int(self.model.config.hidden_size)

    def final_norm(self) -> Any:
        inner = getattr(self.model, "model", None)
        if inner is not None and hasattr(inner, "norm"):
            return inner.norm
        if hasattr(self.model, "transformer") and hasattr(self.model.transformer, "ln_f"):
            return self.model.transformer.ln_f
        return None

    def lm_head(self) -> Any:
        return self.model.lm_head


def get_decoder_layers(model: Any) -> list[Any]:
    inner = getattr(model, "model", None) or getattr(model, "transformer", None)
    if inner is None:
        raise RuntimeError("could not find decoder stack")
    for attr in ("layers", "h"):
        layers = getattr(inner, attr, None)
        if layers is not None:
            return list(layers)
    raise RuntimeError("could not find decoder layers")


def load_vessel(
    model_id: str = DEFAULT_MODEL_ID,
    device: str | None = None,
    fallback: bool = True,
) -> Vessel:
    torch_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    used_fallback = False
    try:
        tok = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
    except Exception as exc:  # noqa: BLE001 — we really do want any download/gate failure
        if not fallback or model_id == FALLBACK_MODEL_ID:
            raise
        print(f"[residuum] failed to load {model_id} ({exc!r}); falling back to {FALLBACK_MODEL_ID}")
        model_id = FALLBACK_MODEL_ID
        used_fallback = True
        tok = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)

    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
        tok.pad_token_id = tok.eos_token_id

    model.to(torch_device)
    model.eval()
    n_params = sum(p.numel() for p in model.parameters())
    layers = get_decoder_layers(model)
    return Vessel(
        model_id=model_id,
        model=model,
        tokenizer=tok,
        layers=layers,
        device=torch_device,
        n_params=int(n_params),
        fallback_used=used_fallback,
    )


def apply_chat(tokenizer: Any, system: str, user: str, assistant: str | None = None) -> str:
    """Build a prompt. Prefer the tokenizer chat template when it exists."""
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    if assistant is not None:
        messages.append({"role": "assistant", "content": assistant})
        add_gen = False
    else:
        add_gen = True

    if getattr(tokenizer, "chat_template", None):
        try:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=add_gen,
            )
        except Exception:
            pass
    # GPT-2 and other completion models.
    parts = []
    if system:
        parts.append(f"System: {system}")
    parts.append(f"User: {user}")
    parts.append("Assistant:")
    if assistant is not None:
        parts[-1] = f"Assistant: {assistant}"
    return "\n".join(parts)


def encode(vessel: Vessel, text: str) -> dict[str, torch.Tensor]:
    encoded = vessel.tokenizer(text, return_tensors="pt", add_special_tokens=True)
    return {k: v.to(vessel.device) for k, v in encoded.items()}
