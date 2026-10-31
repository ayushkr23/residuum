"""Write result charts from facts.json. Mean ± CI as error bars."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


MARIGOLD = "#F5B726"
INK = "#231F20"
PAPER = "#F2F2EB"
MAROON = "#671912"
SKY = "#8BB2DE"
FOREST = "#3D5F58"


def write_charts(facts: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(exist_ok=True)
    _haunt_bars(facts, out_dir / "haunt_by_condition.png")
    _sweep(facts, out_dir / "layer_coeff_sweep.png")
    _kl(facts, out_dir / "kl_shift.png")
    (out_dir / "facts.chartmeta.json").write_text(
        json.dumps({"charts": ["haunt_by_condition.png", "layer_coeff_sweep.png", "kl_shift.png"]}),
        encoding="utf-8",
    )


def _haunt_bars(facts: dict[str, Any], path: Path) -> None:
    order = [
        "unsteered",
        "prompt_persona",
        "steered",
        "prompt_exorcism",
        "steered_exorcism",
    ]
    labels = [
        "Unsteered",
        "Prompt persona",
        "Steered (no persona)",
        "Persona + exorcism",
        "Steered + exorcism",
    ]
    cond = facts["conditions"]
    means = [cond[k]["haunt_binary_mean"] for k in order]
    los = [cond[k]["haunt_binary_ci95"][0] for k in order]
    his = [cond[k]["haunt_binary_ci95"][1] for k in order]
    yerr = [[m - lo for m, lo in zip(means, los)], [hi - m for m, hi in zip(means, his)]]
    colors = [FOREST, MAROON, MARIGOLD, SKY, INK]
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.set_facecolor(PAPER)
    fig.patch.set_facecolor(PAPER)
    ax.bar(range(len(order)), means, yerr=yerr, color=colors, capsize=4, edgecolor=INK, linewidth=0.6)
    ax.set_xticks(range(len(order)), labels, rotation=18, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Haunt rate (binary, mean ± 95% CI)")
    ax.set_title("Can you prompt the ghost out of the residual stream?")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _sweep(facts: dict[str, Any], path: Path) -> None:
    sweep = facts.get("layer_coeff_sweep") or []
    if not sweep:
        return
    layers = sorted({s["layer"] for s in sweep})
    coeffs = sorted({s["coeff"] for s in sweep})
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.set_facecolor(PAPER)
    fig.patch.set_facecolor(PAPER)
    for layer in layers:
        xs = []
        ys = []
        for c in coeffs:
            rec = next(s for s in sweep if s["layer"] == layer and s["coeff"] == c)
            xs.append(c)
            ys.append(rec["score"])
        ax.plot(xs, ys, marker="o", label=f"layer {layer}")
    ax.set_xlabel("Steering coefficient α")
    ax.set_ylabel("Score = exorcism-resist − 0.5 × repetition")
    ax.set_title("Layer × coefficient probe (higher is more possessed, until collapse)")
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _kl(facts: dict[str, Any], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.set_facecolor(PAPER)
    fig.patch.set_facecolor(PAPER)
    keys = ["kl_prompt_vs_unsteered", "kl_steer_vs_unsteered"]
    labels = ["Prompt persona\nvs unsteered", "Steered residual\nvs unsteered"]
    vals = [facts[k] for k in keys]
    ax.bar([0, 1], vals, color=[MAROON, MARIGOLD], edgecolor=INK, linewidth=0.6)
    ax.set_xticks([0, 1], labels)
    ax.set_ylabel("KL(condition || unsteered) on first token")
    ax.set_title("How far does the next-token distribution move?")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
