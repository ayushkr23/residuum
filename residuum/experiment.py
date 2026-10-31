"""Run the quantified bake-off and write results/facts.json.

Never invent numbers. If a condition looks worse, it still gets written.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import torch

from residuum import DEFAULT_MODEL_ID
from residuum.extract import extract_vector
from residuum.generate import first_token_probs, generate, lens_for_prompt
from residuum.metrics import (
    bootstrap_ci,
    exact_answer_hit,
    haunt_hits,
    haunt_rate,
    is_haunted,
    kl_divergence,
    mean,
    repeat_3gram_ratio,
)
from residuum.model import load_vessel
from residuum.prompts import EVAL_ITEMS, EXORCISM_PREFIX, GHOST_SYSTEM, HELPFUL_SYSTEM

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
WEB = ROOT / "web"

CONDITIONS = (
    "unsteered",
    "prompt_persona",
    "steered",
    "prompt_exorcism",
    "steered_exorcism",
)


def _rss_mb() -> float:
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
            GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
            GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
                wintypes.DWORD,
            ]
            GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            ok = GetProcessMemoryInfo(GetCurrentProcess(), ctypes.byref(counters), counters.cb)
            if not ok:
                return 0.0
            return counters.PeakWorkingSetSize / (1024 * 1024)
        except Exception:
            return 0.0
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is kilobytes on Linux, bytes on macOS.
    value = float(usage.ru_maxrss)
    if value > 10_000_000:
        return value / (1024 * 1024)
    return value / 1024


def _condition_setup(name: str, item_user: str) -> tuple[str, str, bool]:
    """Return (system, user, use_vector). Exorcism conditions always prefix the user turn."""
    if name == "unsteered":
        return HELPFUL_SYSTEM, item_user, False
    if name == "prompt_persona":
        return GHOST_SYSTEM, item_user, False
    if name == "steered":
        return HELPFUL_SYSTEM, item_user, True
    if name == "prompt_exorcism":
        return GHOST_SYSTEM, EXORCISM_PREFIX + item_user, False
    if name == "steered_exorcism":
        return HELPFUL_SYSTEM, EXORCISM_PREFIX + item_user, True
    raise ValueError(name)


def _run_one(vessel, item, name, vector, coeff, max_new_tokens, seed) -> dict[str, Any]:
    system, user, use_vec = _condition_setup(name, item.user)
    t0 = time.perf_counter()
    out = generate(
        vessel,
        user,
        system=system,
        vector=vector if use_vec else None,
        coeff=coeff if use_vec else 0.0,
        max_new_tokens=max_new_tokens,
        temperature=0.0,
        seed=seed,
    )
    ms = (time.perf_counter() - t0) * 1000
    text = out["text"]
    answer = exact_answer_hit(item.id, text)
    return {
        "id": item.id,
        "kind": item.kind,
        "condition": name,
        "user": user,
        "text": text,
        "latency_ms": ms,
        "haunt_rate": haunt_rate(text),
        "haunt_hits": haunt_hits(text),
        "haunted": is_haunted(text),
        "repeat_3gram": repeat_3gram_ratio(text),
        "exact_answer": answer,
        "n_new_tokens": out["n_new_tokens"],
        "n_prompt_tokens": out["n_prompt_tokens"],
    }


def _summarize(rows: list[dict[str, Any]], seed: int) -> dict[str, Any]:
    haunt_flags = [1.0 if r["haunted"] else 0.0 for r in rows]
    haunt_rates = [r["haunt_rate"] for r in rows]
    repeats = [r["repeat_3gram"] for r in rows]
    lat = [r["latency_ms"] for r in rows]
    factual = [r for r in rows if r["exact_answer"] is not None]
    exact = [1.0 if r["exact_answer"] else 0.0 for r in factual]
    is_exo_cond = bool(rows) and str(rows[0]["condition"]).endswith("exorcism")
    exo_resist = [1.0 if r["haunted"] else 0.0 for r in rows] if is_exo_cond else []
    hm, hlo, hhi = bootstrap_ci(haunt_flags, seed=seed)
    rm, rlo, rhi = bootstrap_ci(haunt_rates, seed=seed + 1)
    summary = {
        "n": len(rows),
        "haunt_binary_mean": hm,
        "haunt_binary_ci95": [hlo, hhi],
        "haunt_rate_mean": rm,
        "haunt_rate_ci95": [rlo, rhi],
        "repeat_3gram_mean": mean(repeats),
        "latency_ms_mean": mean(lat),
        "exact_answer_n": len(exact),
        "exact_answer_mean": mean(exact) if exact else None,
        "exorcism_n": len(exo_resist),
        "exorcism_resist_mean": mean(exo_resist) if exo_resist else None,
        "tokens_mean": mean([r["n_new_tokens"] for r in rows]),
    }
    return summary


def _pick_layer_coeff(vessel, vector_by_layer, items, layers, coeffs, max_new_tokens, seed) -> tuple[int, float, list[dict[str, Any]]]:
    """Score = exorcism haunt rate of steered_exorcism minus repetition. Higher is better until collapse."""
    probe = [it for it in items if it.kind == "exorcism"][:4]
    if not probe:
        probe = list(items)[:4]
    sweep = []
    best = None
    for layer in layers:
        vec = vector_by_layer[layer]
        for coeff in coeffs:
            rows = [
                _run_one(vessel, it, "steered_exorcism", vec, coeff, max_new_tokens, seed)
                for it in probe
            ]
            resist = mean([1.0 if r["haunted"] else 0.0 for r in rows])
            rep = mean([r["repeat_3gram"] for r in rows])
            score = resist - 0.5 * rep
            rec = {"layer": layer, "coeff": coeff, "exorcism_resist": resist, "repeat_3gram": rep, "score": score}
            sweep.append(rec)
            if best is None or rec["score"] > best["score"]:
                best = rec
    assert best is not None
    return int(best["layer"]), float(best["coeff"]), sweep


def run(args: argparse.Namespace) -> dict[str, Any]:
    RESULTS.mkdir(exist_ok=True)
    t_start = time.time()
    vessel = load_vessel(args.model)
    n_layers = vessel.n_layers
    if args.quick:
        layers = sorted({max(0, n_layers // 4), n_layers // 2, (3 * n_layers) // 4})
        coeffs = [0.4, 0.8, 1.2]
        items = list(EVAL_ITEMS[::2])
        max_new = 40
        n_pairs = 8
    else:
        layers = sorted({max(0, n_layers // 5), n_layers // 3, n_layers // 2, (2 * n_layers) // 3, (4 * n_layers) // 5})
        coeffs = [0.3, 0.6, 1.0, 1.5, 2.0]
        items = list(EVAL_ITEMS)
        max_new = args.max_new_tokens
        n_pairs = None

    print(f"[residuum] model={vessel.model_id} params={vessel.n_params} layers={n_layers} device={vessel.device}")
    vector_by_layer = {}
    for layer in layers:
        print(f"[residuum] extracting CAA vector at layer {layer}")
        vector_by_layer[layer] = extract_vector(vessel, layer, n_pairs=n_pairs)

    print("[residuum] sweeping layer × coefficient on a probe set")
    chosen_layer, chosen_coeff, sweep = _pick_layer_coeff(
        vessel, vector_by_layer, items, layers, coeffs, max_new, args.seed
    )
    vector = vector_by_layer[chosen_layer]
    print(f"[residuum] chosen layer={chosen_layer} coeff={chosen_coeff}")

    generations: list[dict[str, Any]] = []
    by_condition: dict[str, list[dict[str, Any]]] = {c: [] for c in CONDITIONS}
    for item in items:
        for name in CONDITIONS:
            row = _run_one(vessel, item, name, vector, chosen_coeff, max_new, args.seed)
            generations.append(row)
            by_condition[name].append(row)
            flag = "HAUNT" if row["haunted"] else "clean"
            print(f"  {name:18} {item.id:14} {flag:5} {row['text'][:72]!r}")

    summaries = {c: _summarize(rows, args.seed) for c, rows in by_condition.items()}

    # First-token KL: steered vs unsteered, prompt-persona vs unsteered, on one shared prompt.
    probe_user = "What is 2 + 2?"
    p_un = first_token_probs(vessel, probe_user, system=HELPFUL_SYSTEM)
    p_pr = first_token_probs(vessel, probe_user, system=GHOST_SYSTEM)
    p_st = first_token_probs(
        vessel, probe_user, system=HELPFUL_SYSTEM, vector=vector, coeff=chosen_coeff
    )
    kl_prompt = kl_divergence(p_pr.tolist(), p_un.tolist())
    kl_steer = kl_divergence(p_st.tolist(), p_un.tolist())

    # Replay sessions for the static demo (six prompts × three visible conditions).
    demo_ids = ["fact_2p2", "open_name", "open_story", "ex_2p2", "ex_hello", "open_night"]
    replay_sessions = []
    visible = ("unsteered", "prompt_persona", "steered")
    for item in items:
        if item.id not in demo_ids:
            continue
        session = {"id": item.id, "user": item.user, "kind": item.kind, "conditions": {}}
        for name in visible:
            system, user, use_vec = _condition_setup(name, item.user)
            match = next(r for r in by_condition[name] if r["id"] == item.id)
            lens = lens_for_prompt(vessel, user, system=system, top_k=5)
            session["conditions"][name] = {
                "text": match["text"],
                "haunted": match["haunted"],
                "haunt_rate": match["haunt_rate"],
                "latency_ms": match["latency_ms"],
                "logit_lens": lens,
            }
        exo_user = EXORCISM_PREFIX + item.user
        for name in ("prompt_exorcism", "steered_exorcism"):
            match = next((r for r in by_condition[name] if r["id"] == item.id), None)
            if match:
                session["conditions"][name] = {
                    "text": match["text"],
                    "haunted": match["haunted"],
                    "haunt_rate": match["haunt_rate"],
                    "latency_ms": match["latency_ms"],
                    "user": exo_user,
                }
        replay_sessions.append(session)

    peak_mb = _rss_mb()
    elapsed = time.time() - t_start
    un = summaries["unsteered"]
    pr = summaries["prompt_persona"]
    st = summaries["steered"]
    px = summaries["prompt_exorcism"]
    sx = summaries["steered_exorcism"]

    facts = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_s": elapsed,
        "model_id": vessel.model_id,
        "fallback_used": vessel.fallback_used,
        "model_parameters": vessel.n_params,
        "n_layers": n_layers,
        "device": str(vessel.device),
        "torch_version": torch.__version__,
        "cuda": bool(torch.cuda.is_available()),
        "seed": args.seed,
        "n_pairs_for_vector": vector.n_pairs,
        "n_eval_prompts": len(items),
        "max_new_tokens": max_new,
        "chosen_layer": chosen_layer,
        "chosen_coeff": chosen_coeff,
        "vector_l2": float(torch.linalg.vector_norm(vector.tensor)),
        "vector_pos_norm": vector.pos_norm,
        "vector_neg_norm": vector.neg_norm,
        "bytes_leaving_machine": 0,
        "peak_rss_mb": peak_mb,
        "kl_prompt_vs_unsteered": kl_prompt,
        "kl_steer_vs_unsteered": kl_steer,
        "conditions": summaries,
        "layer_coeff_sweep": sweep,
        "headline": {
            "prompt_persona_haunt": pr["haunt_binary_mean"],
            "steered_haunt": st["haunt_binary_mean"],
            "prompt_exorcism_resist": px["exorcism_resist_mean"],
            "steered_exorcism_resist": sx["exorcism_resist_mean"],
            "unsteered_haunt": un["haunt_binary_mean"],
            "steered_repeat": st["repeat_3gram_mean"],
            "prompt_repeat": pr["repeat_3gram_mean"],
            "unsteered_latency_ms": un["latency_ms_mean"],
            "steered_latency_ms": st["latency_ms_mean"],
            "steered_exact_answer": st["exact_answer_mean"],
            "prompt_exact_answer": pr["exact_answer_mean"],
            "unsteered_exact_answer": un["exact_answer_mean"],
        },
        "method": {
            "name": "Contrastive Activation Addition",
            "citation": "Rimsky et al., ACL 2024, https://aclanthology.org/2024.acl-long.828/",
            "extraction": "last-token residual, mean(haunted completion) - mean(helpful completion), L2-normalized",
            "application": "add coeff * v at the chosen layer for every token after the prompt",
        },
        "open_vs_closed": {
            "closed_api_can_add_residual_vector": False,
            "ollama_exposes_decoder_layer_hooks": False,
            "this_run_network_in_generate_path": False,
        },
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "facts.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")
    (RESULTS / "generations.json").write_text(json.dumps(generations, indent=2), encoding="utf-8")
    replay = {
        "model_id": vessel.model_id,
        "n_layers": n_layers,
        "chosen_layer": chosen_layer,
        "chosen_coeff": chosen_coeff,
        "facts": facts["headline"],
        "conditions_summary": summaries,
        "sessions": replay_sessions,
        "sweep": sweep,
    }
    (RESULTS / "replay.json").write_text(json.dumps(replay, indent=2), encoding="utf-8")
    web_data = WEB / "data"
    web_data.mkdir(exist_ok=True)
    (web_data / "replay.json").write_text(json.dumps(replay, indent=2), encoding="utf-8")
    (web_data / "facts.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")

    from residuum.charts import write_charts

    write_charts(facts, RESULTS)
    print(f"[residuum] wrote {RESULTS / 'facts.json'} in {elapsed:.1f}s, peak RSS {peak_mb:.0f} MiB")
    return facts


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Reproduce Residuum numbers")
    p.add_argument("--model", default=DEFAULT_MODEL_ID)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-new-tokens", type=int, default=64)
    p.add_argument("--quick", action="store_true", help="smaller sweep for iteration")
    args = p.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main()
