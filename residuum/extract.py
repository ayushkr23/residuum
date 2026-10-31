"""Build a CAA steering vector from contrastive chat pairs."""

from __future__ import annotations

import torch

from residuum.model import Vessel, apply_chat, encode
from residuum.prompts import HELPFUL_SYSTEM, PAIRS
from residuum.steering import SteeringVector, capture_last_residual, mean_difference


def extract_vector(vessel: Vessel, layer: int, n_pairs: int | None = None) -> SteeringVector:
    pairs = PAIRS if n_pairs is None else PAIRS[:n_pairs]
    pos_rows = []
    neg_rows = []
    for pair in pairs:
        pos_text = apply_chat(vessel.tokenizer, HELPFUL_SYSTEM, pair.user, assistant=pair.haunted)
        neg_text = apply_chat(vessel.tokenizer, HELPFUL_SYSTEM, pair.user, assistant=pair.helpful)
        pos_ids = encode(vessel, pos_text)
        neg_ids = encode(vessel, neg_text)
        pos_rows.append(
            capture_last_residual(
                vessel.model,
                vessel.layers[layer],
                pos_ids["input_ids"],
                pos_ids.get("attention_mask"),
            )
        )
        neg_rows.append(
            capture_last_residual(
                vessel.model,
                vessel.layers[layer],
                neg_ids["input_ids"],
                neg_ids.get("attention_mask"),
            )
        )
    pos = torch.stack(pos_rows, dim=0)
    neg = torch.stack(neg_rows, dim=0)
    vec = mean_difference(pos, neg, normalize=True)
    return SteeringVector(
        layer=layer,
        tensor=vec,
        n_pairs=len(pairs),
        pos_norm=float(torch.linalg.vector_norm(pos.mean(0))),
        neg_norm=float(torch.linalg.vector_norm(neg.mean(0))),
    )
