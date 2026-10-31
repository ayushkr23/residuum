# Submission checklist — Residuum, Week 4

Deadline: **Saturday 31 October 2026, 11:59 PM PDT** (challenge page text; treat that as the clock).  
Challenge: [Hacktoberfest Open-Source AI Challenge: Week 4](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)

## Tags (required)

- `#hf26challenge` — required by the challenge
- `#devchallenge` — required by the brief
- Also in front matter: `opensource`, `ai` (DEV max **four** tags)

## Cover image

- Size: **1000 × 420** (DEV Editor Guide).
- Idea: black-brown field, gold “RESIDUUM” in the same serif as the UI, a faint 30-layer stack with layer 6 marked, planchette on a spirit-board token. Do **not** put the only copy of the title on the image — the post title still has to be written out.
- File: **[TODO — design and upload to DEV or the repo]**

## Links to paste into SUBMISSION.md

| Slot | Status |
| --- | --- |
| GitHub repo | https://github.com/ayushkr23/residuum |
| Replay / hosted demo | https://ayushkr23.github.io/residuum/ (GitHub Pages). Local: `http://127.0.0.1:8765` |
| YouTube demo (75s) | **[TODO — record from DEMO_SCRIPT.md]** |
| README GIF | **[TODO]** |
| Colab clone URL | `notebooks/residuum_colab.ipynb` points at https://github.com/ayushkr23/residuum |
| Agent session embed | **[TODO]** `{% agent_session <id> %}` after Make Public |
| Cover image URL | **[TODO]** |

## Prize categories claimed

**None.** Overall prize only.

| Category | Claim? | Evidence (one sentence) |
| --- | --- | --- |
| Overall ($250) | yes | Open-weight CAA hook + measured prompt-vs-residual bake-off on SmolLM2-135M, numbers from `results/facts.json`. |
| Gemma ($200) | **no** | Vessel is SmolLM2, not Gemma. |
| Render / TabPFN / Tinker / Arduino / DigitalOcean | **no** | Unused. |
| Auth0 / Backboard / Browserbase / ElevenLabs / Entire / Copilot / Mastra / MongoDB / Ultramarine / Sentry / SerpApi / Temporal / Tiger Data | **no** | Unused. |
| .tech domain ($100) | **no, unless registered** | Only claim after the demo actually answers on a `.tech` host. |

## Manual steps only you can do

1. **GitHub repo and Pages** are live: https://github.com/ayushkr23/residuum and https://ayushkr23.github.io/residuum/ (Pages can take a minute after a push).
2. **Record the 75s video** from `DEMO_SCRIPT.md` (replay UI is already running locally). Upload unlisted YouTube.
3. **Optional GIF** of the three vessels typing, for the README hero.
4. **Optional .tech**: claim at [hacktoberfest.com/my/promos](https://hacktoberfest.com/my/promos) only if you will point it at a hosted replay. Do not list the category until DNS works.
5. **Save the agent session** with DevRelay, **Make Public**, embed in the post. Redact secrets first. Week 4 says this is optional but helps judges.
6. **Cover image** 1000×420, upload in the DEV editor.
7. **Paste `SUBMISSION.md` into a DEV draft.** Keep `published: false` until you click Publish. Set **AI Disclosure** to match the post (`some_ai`).
8. **Do not publish until you say yes.** DevRelay `create_article` can stage the draft; it will not publish without you.
9. Confirm you are **18+**, in an eligible country, and the repo was started inside the entry window (this project was).
10. After publish: verify the post has both required tags, the template headings, a demo a judge can click without a GPU, and no partner category you did not actually use.

## Pre-flight already done

- [x] `results/facts.json` machine-written (seed 0, 2026-10-29T16:49:46Z)
- [x] Replay UI verified at `http://127.0.0.1:8765` (Summon, prompt change, Attempt exorcism, logit-lens board)
- [x] 16 unit tests
- [x] MIT `LICENSE`, `ETHICS.md`, `README.md`, `make reproduce`
- [x] Honest negative result kept (steer haunt 0%, KL 0.00427 vs persona 1.746)
- [x] `prefers-reduced-motion` + skip link + keyboard 1/2/3/E in the UI
- [x] No Gemma bait-and-switch

## Numbers the post may use (only these)

From `results/facts.json` headline + conditions. Do not round into a new claim.

- Haunt: unsteered 0%, persona 12.5% (CI 4.2–25%), steered 0%, persona+exorcism 4.2% (0–12.5%), steered+exorcism 0%
- KL: 1.746 vs 0.00427 (~409×)
- Exact-answer n=12: 75% / 67% / 75% / 67% / 83%
- Latency mean: 1.80 s / 2.40 s / 1.72 s / 1.94 s / 1.52 s
- Repeat-3gram: 0.011 / 0.138 / 0.006 / 0.142 / 0.082
- 16 pairs, 24 prompts, 120 generations, layer 6, α 0.3, 30 layers, 134,515,008 params
- Peak RSS 837 MiB, 0 bytes leaving machine, 356 s wall, CPU, torch 2.14.1+cpu, seed 0
- Sweep: 25 cells, all exorcism-resist 0
