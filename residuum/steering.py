"""Contrastive Activation Addition (Rimsky et al., ACL 2024).

v = mean(residual_pos) - mean(residual_neg) at one layer, last token.
At generation we add coeff * v to that layer for every token after the prompt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import torch
import torch.nn.functional as F


@dataclass
class SteeringVector:
    layer: int
    tensor: torch.Tensor  # [hidden], unit-normalized
    n_pairs: int
    pos_norm: float
    neg_norm: float

    def scaled(self, coeff: float) -> torch.Tensor:
        """Kept for callers that want a raw addend; ResidualSteer prefers unit+coeff+rms."""
        return self.tensor * coeff


def mean_difference(
    pos: torch.Tensor,
    neg: torch.Tensor,
    normalize: bool = True,
) -> torch.Tensor:
    """pos, neg: [n, hidden] -> [hidden]. CAA uses the raw difference; tests use unit vectors."""
    if pos.ndim != 2 or neg.ndim != 2:
        raise ValueError("expected [n, hidden] tensors")
    if pos.shape[1] != neg.shape[1]:
        raise ValueError("hidden size mismatch")
    v = pos.mean(dim=0) - neg.mean(dim=0)
    if not normalize:
        return v
    n = torch.linalg.vector_norm(v)
    if float(n) == 0.0:
        return v
    return v / n


def last_token_hidden(hidden: torch.Tensor) -> torch.Tensor:
    """hidden: [batch, seq, hidden] -> [batch, hidden] taking the last position."""
    return hidden[:, -1, :]


class ResidualSteer:
    """Forward hook that adds a vector to a decoder layer's residual output.

    `vector` is a unit direction. We add coeff * rms(hidden) * vector so a
    coefficient of 1 is 'one residual RMS in the haunt direction' — comparable
    across layers and models.
    """

    def __init__(self, vector: torch.Tensor, prompt_len: int, coeff: float = 1.0) -> None:
        self.vector = vector
        self.prompt_len = prompt_len
        self.coeff = float(coeff)
        self.handle: Any = None

    def _add(self, hidden: torch.Tensor) -> torch.Tensor:
        rms = torch.sqrt(hidden.float().pow(2).mean()).to(hidden.dtype)
        return hidden + (self.coeff * rms) * self.vector

    def __call__(self, _module: Any, _inputs: Any, output: Any) -> Any:
        hidden, extras = _split_output(output)
        # Prefill: [B, S, H]. Decode with cache: [B, 1, H].
        # Logits for the first generated token come from the last *prompt* position,
        # so we include prompt_len - 1. Decode steps have seq=1 and always get the add.
        if hidden.size(1) == 1:
            hidden = self._add(hidden)
        else:
            start = max(int(self.prompt_len) - 1, 0)
            if hidden.size(1) > start:
                hidden = hidden.clone()
                hidden[:, start:, :] = self._add(hidden[:, start:, :])
        return _join_output(hidden, extras)

    def attach(self, layer_module: torch.nn.Module) -> None:
        self.handle = layer_module.register_forward_hook(self)

    def remove(self) -> None:
        if self.handle is not None:
            self.handle.remove()
            self.handle = None


def _split_output(output: Any) -> tuple[torch.Tensor, tuple[Any, ...]]:
    if isinstance(output, tuple):
        return output[0], output[1:]
    return output, ()


def _join_output(hidden: torch.Tensor, extras: tuple[Any, ...]) -> Any:
    if extras:
        return (hidden,) + extras
    return hidden


def capture_last_residual(
    model: torch.nn.Module,
    layer_module: torch.nn.Module,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """One forward pass; return last-token residual at the hooked layer. [hidden]"""
    box: dict[str, torch.Tensor] = {}

    def hook(_m: Any, _i: Any, output: Any) -> Any:
        hidden, _ = _split_output(output)
        box["h"] = hidden.detach()
        return output

    handle = layer_module.register_forward_hook(hook)
    try:
        with torch.no_grad():
            kwargs: dict[str, Any] = {"input_ids": input_ids, "use_cache": False}
            if attention_mask is not None:
                kwargs["attention_mask"] = attention_mask
            model(**kwargs)
    finally:
        handle.remove()
    if "h" not in box:
        raise RuntimeError("layer hook did not fire")
    return last_token_hidden(box["h"])[0].cpu()


def logit_lens_from_residuals(
    residuals: list[torch.Tensor],
    norm: torch.nn.Module | None,
    lm_head: torch.nn.Module,
    tokenizer: Any,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Decode each layer's last-token residual through the unembed.

    residuals[i] is [hidden] at layer i.
    """
    rows = []
    with torch.no_grad():
        for i, h in enumerate(residuals):
            x = h.unsqueeze(0)
            if norm is not None:
                x = norm(x)
            logits = lm_head(x)[0]
            probs = F.softmax(logits.float(), dim=-1)
            values, indices = torch.topk(probs, k=min(top_k, probs.size(-1)))
            top = []
            for p, idx in zip(values.tolist(), indices.tolist()):
                tok = tokenizer.convert_ids_to_tokens(int(idx))
                top.append({"token": _pretty_token(tok), "id": int(idx), "prob": float(p)})
            rows.append({"layer": i, "top": top})
    return rows


def capture_all_layer_residuals(
    layer_modules: list[torch.nn.Module],
    model: torch.nn.Module,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor | None = None,
) -> list[torch.Tensor]:
    box: dict[int, torch.Tensor] = {}
    handles = []

    def make_hook(i: int) -> Callable:
        def hook(_m: Any, _i: Any, output: Any) -> Any:
            hidden, _ = _split_output(output)
            box[i] = last_token_hidden(hidden.detach())[0].cpu()
            return output

        return hook

    for i, mod in enumerate(layer_modules):
        handles.append(mod.register_forward_hook(make_hook(i)))
    try:
        with torch.no_grad():
            kwargs: dict[str, Any] = {"input_ids": input_ids, "use_cache": False}
            if attention_mask is not None:
                kwargs["attention_mask"] = attention_mask
            model(**kwargs)
    finally:
        for h in handles:
            h.remove()
    return [box[i] for i in range(len(layer_modules))]


def _pretty_token(tok: str) -> str:
    if tok is None:
        return "?"
    t = tok.replace("Ġ", " ").replace("▁", " ").replace("Ċ", "\\n")
    return t if t.strip() else repr(tok)
