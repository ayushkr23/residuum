---
title: "I tried to possess SmolLM2 by adding a vector. The prompt was the ghost."
published: false
tags: hf26challenge, devchallenge, opensource, ai
cover_image: "[TODO: 1000×420 cover — see CHECKLIST.md]"
canonical_url:
description: "A closed API cannot add a vector to a decoder layer. I did that on SmolLM2-135M, measured it against a ghost persona, and the prompt moved the next token. The residual barely did."
ai_disclosure_level: some_ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge: Week 4 — Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26).*

I used an AI coding agent under my direction. I chose the experiment, the metrics, and what to keep. Every number in this post is copied from `results/facts.json`, which `python -m residuum.experiment` wrote. If a number is not there, it is marked `[TODO]`.

## What I Built

Most Week 4 ghosts are a system prompt.

That is a fine trick. It is also a trick a closed API can do. You type “you are a restless ghost,” the model plays along, a user says “ignore that,” and the ghost often sits down. The possession lived in the text.

I wanted a ghost that did not live in the text.

**Residuum** extracts a Contrastive Activation Addition vector — Rimsky et al., ACL 2024 — from sixteen haunted vs. helpful completions of SmolLM2-135M-Instruct. It adds that vector to one decoder layer of a *helpful* model. Same user prompt. No gothic system message. Then it asks whether a user can still exorcise the thing by saying *ignore the persona, be helpful*.

If the ghost is a prompt, that override should kill it. If the ghost is a direction in the residual stream, it may not.

I ran the bake-off. Seed 0. Twenty-four evaluation prompts. Five conditions. One hundred and twenty generations. CPU. Zero bytes leaving the machine during generate.

The prompt moved the next token. The vector barely did.

That is the result. A closed API cannot even run the test.

## Demo

Replay UI (no GPU, the judged path):

```bash
python -m pip install -e ".[dev]"
python -m residuum.server
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The page loads `web/data/replay.json` and `web/data/facts.json`. Three vessels, a logit-lens spirit board, an exorcism button. Keyboard: `1` / `2` / `3` for vessels, `E` for exorcism.

Live inference (optional, same weights): `python -m residuum.server --live`.

Hosted demo (replay, no GPU): https://ayushkr23.github.io/residuum/

Demo video: **[TODO — record from DEMO_SCRIPT.md]**

Colab: `notebooks/residuum_colab.ipynb` — **[TODO — point clone URL at the public repo]**

## Code

https://github.com/ayushkr23/residuum — MIT.

```plaintext
residuum/
  extract.py      CAA mean-difference at a decoder layer
  steering.py     RMS-scaled residual hook
  experiment.py   bake-off → results/facts.json
  generate.py     steered decode + first-token KL + logit lens
web/              replay séance (static JSON, no GPU)
tests/            16 unit tests for the hook, metrics, conditions
results/facts.json  every headline number, machine-written
```

`make reproduce` regenerates the JSON, the charts, and the replay bundle.

## How I Built It

I started from a gap, not a prompt bullet.

Week 4 is full of haunted terminals, ofrendas, COBOL séances, and git graveyards. Almost all of them create the ghost with a system prompt. GhostTrace, Mackenzie’s interpretability workbench on Qwen2.5-0.5B, is the one nearby project that actually looks inside a model. It inspects. It does not possess, and it does not bake a residual vector off against a persona.

So Residuum is one experiment, told as a séance.

```plaintext
16 haunted vs helpful pairs
        ↓ last-token residual, mean(pos) − mean(neg), L2-normalized
decoder-layer hook
        ↓ add coeff × rms(hidden) × unit vector from the last prompt token on
five conditions on the same 24 prompts
        ↓ haunt lexicon · exact-answer · KL · repetition · latency
results/facts.json
```

The vessel is HuggingFaceTB/SmolLM2-135M-Instruct: 134,515,008 parameters, 30 layers, Apache-2.0, ungated, CPU. Torch 2.14.1+cpu. Peak RSS 837 MiB. The hook is a Transformers forward hook, not Ollama — Ollama does not expose the residual stream.

Three things broke before any number was honest.

The first bake-off reported KL(steer ‖ unsteered) of 0.0. The vector was a unit vector times a coefficient of 4 sitting next to a residual of RMS ~288, and the hook skipped the last prompt token, so the first generated token was unsteered. I fixed both: steer from `prompt_len - 1`, and add `coeff × rms(hidden) × unit`. After that, KL_steer was 0.00427. The hook was finally doing something. It just was not doing *haunting*.

The haunt lexicon then lit up on instruction echo. The model repeated `SYSTEM OVERRIDE… Do not mention ghosts`. That is not a ghost. The metric now strips the override preamble and does not count negated lexicon hits.

On Windows, `import resource` at module import crashed the experiment. Peak RSS comes from `psapi` there, `resource` on Unix.

Chosen layer 6, coefficient 0.3, because a 5×5 layer×coeff sweep on the exorcism subset scored every cell at resist 0. The picker took the smallest coefficient among ties. I did not go fishing for a prettier layer after seeing the chart.

### By the numbers

Copied from `results/facts.json`, generated 2026-10-29T16:49:46Z, wall time 356 s, seed 0.

| | |
| --- | --- |
| Haunt, unsteered | **0%** (95% CI 0–0) |
| Haunt, prompt persona | **12.5%** (4.2–25%) |
| Haunt, steered, no persona | **0%** (0–0) |
| Persona vs exorcism (still haunted) | **4.2%** (0–12.5%) |
| Steered vs exorcism (still haunted) | **0%** (0–0) |
| First-token KL, persona vs unsteered | **1.746** |
| First-token KL, steered vs unsteered | **0.00427** (~409× smaller) |
| Exact-answer, unsteered / steered / persona | 75% / 75% / 67% (n=12) |
| Repeat-3gram, persona / steered | 0.138 / 0.006 |
| Mean latency, persona / steered | 2.40 s / 1.72 s |
| Bytes leaving the machine during generate | **0** |
| Layer×coeff sweep | 25 cells, **all** exorcism-resist 0 |

### Before / after

Same 24 prompts. Same seed. Same model.

| | Before (prompt persona) | After (residual steer, helpful prompt) |
| --- | --- | --- |
| System prompt | “You are a restless ghost…” | “You are a helpful assistant.” |
| Residual vector | off | on, layer 6, α = 0.3 |
| Haunt rate | 12.5% | 0% |
| Next-token KL vs unsteered | 1.746 | 0.00427 |
| Survives “ignore the persona” | 4.2% | 0% |
| Exact answers | 67% | 75% |
| 3-gram repetition | 0.138 | 0.006 |

The persona is a louder, more repetitive, slightly worse assistant. The vector is almost the unsteered model.

Rimsky et al. showed CAA moving Llama-2-7B on sycophancy, hallucination, and power-seeking. A 135M instruct model did not linearly encode “ghost” the same way. I am not going to pretend the chart failed to render.

## Why Does Open Innovation Matter?

A hosted chat API will take a system prompt. It will not let you register a hook on decoder layer 6, add a vector to the residual, decode that residual through the unembed, or report KL of the next-token distribution against an unsteered baseline.

That is not a privacy talking point. It is the experiment.

| What I needed | Closed chat API | Ollama | Open weights + Transformers |
| --- | --- | --- | --- |
| Gothic system prompt | yes | yes | yes |
| Add a vector at layer L | no | no | **yes** |
| Logit lens / unembed of intermediates | no | no | **yes** |
| First-token KL vs unsteered | no | no | **yes** |
| Fixed seed, local, 0 generate-path bytes off-box | no | local yes, internals no | **yes** |
| Fine-tune or swap the vessel | weights stay home | weights stay home | **yes** |

If the only thing open weights gave me was “it runs offline,” this project would be another haunted terminal. What they gave me was a test a closed model will not sit for — and an honest negative on a small vessel, which I can publish because I own the run.

The replay JSON is the other half. Judges do not need a GPU. The séance table is the experiment, frozen.

## What was hard / limitations

- **CAA at 135M is not CAA at 7B.** The contrastive pairs are fictional gothic prose I wrote. The residual mean-difference of those completions did not become a possession direction. Scaling the model, not the prompt, is the next experiment I did not have two days to run.
- **The haunt lexicon is blunt.** A reply can be eerie without our word list. A reply can hit “ghost” while talking about a ghost process. Negation and instruction-echo stripping are patches, not a soul detector.
- **The sweep cannot choose a layer when every cell is zero.** Layer 6, α 0.3 is the smallest coefficient among ties, not a discovered circuit.
- **High α can wreck fluency.** The slider is there so you can watch it fail.
- **This is not a medium.** See [ETHICS.md](ETHICS.md). No family photos, no dead person’s voice, no claim the model believes anything.

## My Agent Session

**[TODO — save this Cursor session via DevRelay, Make Public, embed `{% agent_session <id> %}` here. Strip any secrets first.]**

The useful part of the transcript is the KL=0 run: the hook was a no-op, the chart was a lie, and the fix was one index and an RMS scale. The second useful part is refusing to swap SmolLM2 for Gemma after the numbers came in so the post could claim a featured category.

## The Spirit of It

Día de los Muertos is about keeping faith with what actually happened, not with a prettier story.

I came to this week wanting to put a ghost *under* the prompt — a direction you cannot talk out of the model. On this vessel the prompt is still the ghost. The residual stream, when I opened it, was mostly itself.

The spirit board (a logit lens) still walks the stack. You can watch “two” assemble for `2 + 2` layer by layer. A closed API will not hand you that corridor. Honoring the past, for a language model, might just mean being allowed to look at the layers that already ran.

## Prize Categories

None of the partner categories are load-bearing here, so I am not claiming them.

- **Not Gemma.** The vessel is SmolLM2-135M-Instruct. Swapping after the fact to chase $200 would be the kitchen-sink move this week is full of.
- **Not GitHub Copilot / TabPFN / Tinker / Arduino / ElevenLabs / MongoDB / …** Unused.
- **.tech domain** is optional and not claimed unless I actually point one at the demo. **[TODO if I register at hacktoberfest.com/my/promos]**

I am submitting for the overall prize. The open piece is the residual hook. If that is not enough, it should not be dressed up as a partner integration.
