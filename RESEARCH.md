# RESEARCH.md — Hacktoberfest Open-Source AI Challenge, Week 4

**Challenge:** [Hacktoberfest Open-Source AI Challenge: Week 4](https://dev.to/challenges/hacktoberfest-week4-2026-10-26) (event id 82)  
**Theme:** Ghost in the Machine  
**Deadline (authoritative):** Saturday 31 October 2026, 11:59 PM PDT — stated on the challenge page and launch post. The Events API `ends_at` of `2026-10-31T06:59:00.000Z` is **Friday** 30 Oct 11:59 PM PDT and disagrees with the published copy; we treat the **Oct 31 11:59 PM PDT** text as the clock.  
**Today:** Thursday 29 October 2026. Window remaining: ~2 days.  
**Official tags:** `#devchallenge` `#hf26challenge`  
**Launch post:** [Join the Hacktoberfest Open-Source AI Challenge: Ghost in the Machine!](https://dev.to/devteam/join-the-hacktoberfest-open-source-ai-challenge-ghost-in-the-machine-2850-in-prizes-across-21-3cho) by the DEV Team  
**Hub / prize rules:** [HF26 DEV Challenge Hub](https://dev.to/challenges/hf26)  
**Program rules:** DevRelay knowledge base *DEV Challenges: How to Participate* (verified 2026-09-30 against `dev.to/page/official-hackathon-rules`) and *Hacktoberfest 2026* (verified 2026-09-30). New project, started in-window, one submission, teams ≤ 4, English for prize eligibility, AI use allowed with disclosure.

Judging, in order of weight: **Writing Quality**, Relevance, Creativity, Technical Execution, optional Use of Partner Technology.

---

## 1. Competitive landscape

Sampled 2026-10-29 via DevRelay `get_articles` (`tag=hf26challenge`, pages 1–3), `search_dev_to_semantic`, and full bodies of the standout posts. The `#hf26challenge` feed is mixed with earlier weeks; **Week 4 volume is already well over 100 posts**, with haunted terminals and ofrendas dominating titles.

### 1.1 Representative Week 4 table

Writing quality is a qualitative 1–5 from the body (hook, specificity, honesty, numbers, closed-vs-open argument), not from reactions.

| Idea | Open model / tech | Categories claimed | Quantified? | Writing (1–5) | Source |
| --- | --- | --- | --- | --- | --- |
| Haunted CLI that comments on commands | Local OW, usually Gemma via Ollama | Gemma (often) | Almost never | 2 | [HauntedTerminal](https://dev.to/ankit_sharma_f0b6003cb4b1/hauntedterminal-give-your-cli-a-ghostly-voice-with-local-open-weight-ai-379d), [GhostInTheShell](https://dev.to/babin_bid_123/ghostintheshell-building-an-offline-local-first-haunted-terminal-with-gemma-fastapi-1fe1), [GhostShell](https://dev.to/meetpatil2026/ghostshell-a-haunted-ai-terminal-powered-by-local-ai-2oco), [Wraith](https://dev.to/sreevatsarajesh/wraith-a-ghost-in-your-terminal-4d5n), [NecroShell](https://dev.to/mansikardile/necroshell-the-haunted-open-source-ai-terminal-digital-seance-2ol1), [AFTERDARK](https://dev.to/jatin_vishwakarma/afterdark-the-ghost-in-your-terminal-3304) + many clones |
| Possessed CRT / HELGA 1989 mainframe | Gemma 3 1B + Ollama | Gemma | No | 3 | [GHOST://PROTOCOL](https://dev.to/ckayy/ghostprotocol-the-machine-never-forgot-eg4) |
| Digital ofrenda / memory altar, “don’t invent” | Gemma local | Gemma | Sometimes 1 retry-rate | 3–4 | [Ofrenda: a ghost that only knows what you tell it](https://dev.to/joegeorge022/ofrenda-a-ghost-that-only-knows-what-you-tell-it-2k4k), [two sentences allowed on the altar](https://dev.to/sank8/the-model-wrote-six-sentences-about-a-grandmother-two-were-allowed-on-the-altar-18nn), [OfrendaViva](https://dev.to/premsai5142/ofrendaviva-a-local-first-dia-de-los-muertos-altar-ghost-in-the-machine-seance-with-1fgj) |
| Oral history / grandma’s voice | Whisper + Gemma | Gemma, occasionally ElevenLabs | Rare | 3 | [Memoria](https://dev.to/jeffreyturov/memoria-keeping-family-voices-alive-with-local-whisper-gemma-eap), [Dadi’s Voice Archive](https://dev.to/agent_aline_5941086c1e190/dadis-voice-archive-an-offline-ofrenda-that-keeps-grandmas-stories-in-her-own-voice-whisper--528h) |
| Dead-language séance (COBOL, BASIC, 8 languages) | Gemma via Ollama | Gemma | BASIC dialect tests in one | 3–4 | [Séance COBOL](https://dev.to/zidniryi/seance-summoning-the-ghost-of-cobol-entirely-offline-3ndn), [Ghost BASIC](https://dev.to/tusharv/ghost-basic-the-dead-language-still-runs-and-gemma-has-to-learn-its-dialect-2gb2), [eight dead languages](https://dev.to/rishabhvoid/seance-a-scroll-of-eight-dead-programming-languages-running-on-local-gemma-dja) |
| Git graveyard / deleted-file ofrenda | Gemma local | Gemma, Render, Sentry | File counts, not model quality | 3–4 | [GitSéance](https://dev.to/fgrandon/gitseance-an-offline-digital-ofrenda-where-local-gemma-summons-deleted-code-and-refuses-to-guess-4hc0), [git-ofrenda](https://dev.to/aniruddhaadak/git-ofrenda-an-altar-for-the-code-your-repo-buried-with-epitaphs-by-gemma-running-on-my-cpu-d3o), [Kuyō](https://dev.to/mauricioandrade/kuyo-a-funeral-for-the-code-you-deleted-written-by-a-local-gemma-c4i), [GitNecromancer](https://dev.to/alessio_bianchini/gitnecromancer-the-open-source-seance-engine-for-dead-code-and-repo-graveyards-3nem) |
| Dead-repo autopsy that measures lying | Local OW | Gemma | **Yes — lie rate** | 4 | [I taught a local model to perform autopsies…](https://dev.to/bangkah/i-taught-a-local-model-to-perform-autopsies-on-dead-repositories-then-measured-how-often-it-lies-fgp), [The Ghost Maintainer](https://dev.to/soumyaranjan_sahoo_2ef7bf/the-ghost-maintainer-a-seance-for-dead-repositories-and-how-we-proved-an-ai-wasnt-lying-33l0) |
| Wayback / dead-website séance | Local Gemma + archive.org | Gemma, SerpApi (some) | Citation checks | 4 | [Wayback Séance](https://dev.to/kuli_code_c77ee0b00bb5ba9/wayback-seance-i-asked-dead-websites-to-speak-and-made-them-cite-their-sources-3c9d), [Last Witness](https://dev.to/p0rt/last-witness-an-ai-detective-for-a-dead-1999-website-graded-on-its-ghosts-4bbe) |
| Sensor-log ghost story | Gemma ± TabPFN | Gemma, TabPFN | Sparse | 3 | [Last Light](https://dev.to/ktiwari05/last-light-a-ghost-story-from-the-things-a-house-records-3cfm), [What the House Heard](https://dev.to/hyunsik_park_7c24c2e4f4fc/what-the-house-heard-a-ghost-story-told-by-your-smart-homes-sensor-logs-offline-with-tabpfn-and-2km3) |
| Zombie processes / lockfile rot | Gemma | Gemma, TabPFN, ElevenLabs | Process counts | 3 | [Zombie Process Whisperer](https://dev.to/martineg/zombie-process-whisperer-a-local-gemma-model-writes-eulogies-for-the-abandoned-junk-on-your-machine-30d0), [TerminalSpectre](https://dev.to/pratyushpanda/terminalspectre-the-haunted-shell-dead-process-exorcist-tabpfn-gemma-2-elevenlabs-2gil), [Lockfile Ofrenda](https://dev.to/amrit-dash/lockfile-ofrenda-candles-for-the-packages-that-stopped-speaking-12pi) |
| Dead man’s switch | Local OW | Gemma | No | 3 | [I wrote a program that only runs after I die](https://dev.to/anishisbusy/i-wrote-a-program-that-only-runs-after-i-die-53ne) |
| Poe bound to his own books | Local OW + public-domain text | — | Constraint pass/fail | 4 | [I held a séance with Edgar Allan Poe](https://dev.to/antivex/i-held-a-seance-with-edgar-allan-poe-he-may-only-speak-through-his-own-books-2713) |
| Clippy / dead-software séance | Gemma 3 4B + Ollama | Gemma, Copilot | 7 leading-question honesty retest | **5** | [It Looks Like You're Trying to Hold a Séance](https://dev.to/gigaelk/it-looks-like-youre-trying-to-hold-a-seance-4m0m) |
| Prompt-designed haunted-house game | Gemma 4 12B QAT + Ollama | Gemma | Summon time 5–8 min, ~5500-char JSON | **5** | [Haunt Engine](https://dev.to/gavin_rose/haunt-engine-1c04) |
| RNPDNO ofrenda: 133,887 disappeared people; machine refuses to invent | Gemma 4 e4b local | Gemma only | **25/25 cards, 24 first-try, 2.9 s mean** | **5** | [Una marca más](https://dev.to/petrasynthetic/una-marca-mas-133887-people-one-sentence-and-a-machine-that-refuses-4cfi) |
| Quantization graveyard of GSM8K answers | Gemma 4 E2B + llama.cpp | Gemma | **250 q × 9 rungs, determinism checked** | **5** | [Accuracy vs Speed](https://dev.to/gde/accuracy-vs-speed-gemma-4-e2b-quantization-tradeoffs-bf16-to-q2k-aea) |
| TabPFN predicts PR merge from closed-PR ghosts | TabPFN v2 local | TabPFN | **ROC-AUC 0.853 vs 0.824 logreg, 8 repos** | **5** | [MergeMeter](https://dev.to/rostyslavdzhohola/mergemeter-the-ghosts-of-closed-prs-predict-which-open-ones-will-merge-1n0o) |
| Interpretability workbench: activations, logit lens, patching, replay | Qwen2.5-0.5B-Instruct, Transformers hooks | none obvious | 42 smoke units; datasets still small | **4** | [GhostTrace](https://dev.to/mackenzie-techdocs/ghosttrace-a-local-workbench-for-looking-inside-language-models-45p) |
| Kitchen-sink dead-repo necromancer | TabPFN + Gemma + SerpApi | those three | Weak | 2 | [Necromancer](https://dev.to/satanic47/necromancer-resurrecting-dead-repos-with-tabpfn-gemma-serpapi-11gd) |
| Whisper pareidolia on static | Whisper | — | Anecdote | 4 | [I played static to Whisper](https://dev.to/phantom8420/i-played-static-to-whisper-it-said-it-was-going-to-the-next-room-4cdb) |
| 2001 robot-vision tricks vs local VLMs | Local vision models | Gemma | Comparative | 4 | [Ghosts in the frame](https://dev.to/crtdrops/ghosts-in-the-frame-my-2001-robot-vision-tricks-against-two-local-vision-models-1nnm) |
| Generic hosted Gemma story terminal | Gemma **API**, not local | Gemma, ElevenLabs | No | 2 | [Ghostlight](https://dev.to/rohiniray/ghostlight-a-seance-for-the-machine-2jnl) |

### 1.2 Saturation clusters (avoid unless a real twist)

Confirmed by title flood + bodies:

1. **Haunted terminals / shell possession** — the prompt’s first example; dozens of clones. Ghost = system prompt.
2. **Ofrenda / oral-history / grandma’s voice** — the prompt’s second and fourth examples. The only ones that stand out enforce “do not invent” in code ([joegeorge022](https://dev.to/joegeorge022/ofrenda-a-ghost-that-only-knows-what-you-tell-it-2k4k), [sank8](https://dev.to/sank8/the-model-wrote-six-sentences-about-a-grandmother-two-were-allowed-on-the-altar-18nn), [Una marca más](https://dev.to/petrasynthetic/una-marca-mas-133887-people-one-sentence-and-a-machine-that-refuses-4cfi)).
3. **Séances for dead languages / dead software / Clippy** — the prompt’s third example. [GigaElk](https://dev.to/gigaelk/it-looks-like-youre-trying-to-hold-a-seance-4m0m) already owns the writing in this lane.
4. **Git graveyards / deleted-file ofrendas / dead-repo necromancers** — extremely crowded; several already measure hallucination.
5. **Wayback / dead websites** — at least two strong “cite your sources” takes.
6. **Sensor-log ghost stories** — prompt example five; plus TabPFN bolt-ons.
7. **Zombie processes / dead-code / lockfile scanners** — crowded, kitchen-sink TabPFN/Tinker/Arduino energy.
8. **Dead man’s switch** — at least one live entry.
9. **Ghost = system prompt.** Almost every “possession” is a persona string sent to Ollama. Closed APIs can do that. It is not an open-weights-only trick.

### 1.3 What actually scores

The posts that would survive a writing-first rubric share four traits:

- A **specific** interpretation of the theme, not a restatement of the prompt bullets.
- **Numbers with a denominator**, a baseline, and a failure mode ([xbill’s graveyard](https://dev.to/gde/accuracy-vs-speed-gemma-4-e2b-quantization-tradeoffs-bf16-to-q2k-aea), [MergeMeter](https://dev.to/rostyslavdzhohola/mergemeter-the-ghosts-of-closed-prs-predict-which-open-ones-will-merge-1n0o), [Una marca más](https://dev.to/petrasynthetic/una-marca-mas-133887-people-one-sentence-and-a-machine-that-refuses-4cfi)).
- An open-vs-closed argument that **could not** be made about a ChatGPT wrapper.
- Restraint: one partner category, used for real, or none.

GhostTrace is the only Week 4 entry that **looks inside** a model (residual tiles, logit lens, patching, recorded replay) on Qwen2.5-0.5B. It is a research workbench. It does **not** productize *possession*, does not run a prompt-persona vs residual-steering bake-off, and does not tell a séance story. Semantic search for “activation steering / CAA / representation engineering / SAE / Gemma Scope” against `#hf26challenge` returned **GhostTrace and nothing else**.

---

## 2. Gaps (still open on 2026-10-29)

| Gap | Why it is open | Why it is an *open-weights* story |
| --- | --- | --- |
| **Possession by residual-stream steering (CAA), not a persona prompt** | No Week 4 hit except GhostTrace’s general workbench | Closed APIs and Ollama do not let you add a vector to layer *L* |
| Logit-lens-as-ouija (the planchette is the argmax token per layer) | GhostTrace has logit-lens readouts in a lab UI, not as the ritual | Needs `lm_head` on intermediate residuals |
| Training-data séance with fully open models (OLMo / Dolma / infini-gram) | Poe-bound-to-books exists; OLMo membership tracing does not | Fully open data, not just open weights |
| Gemma Scope / SAE feature as a named spirit | No SAE entries | Needs open SAEs on open weights |
| Activation-level “exorcism resistance”: user says stop being a ghost | Nobody measured it | Prompt personas are jailbreakable; a vector in the residual is not a string you can “ignore” |
| On-device quantization as the theme | xbill already owns this lane with 250×9 GSM8K | — |
| Hardware / Arduino UNO Q | Needs a board we do not have | — |

The human side of “honoring the past” is already occupied at a very high bar by [Una marca más](https://dev.to/petrasynthetic/una-marca-mas-133887-people-one-sentence-and-a-machine-that-refuses-4cfi) (Mexico’s disappeared-persons register). Competing there without a comparable archive would be cosplay.

---

## 3. Prize-category contest vs. genuine fit

From the hub: one project may enter every category it **genuinely** uses; one win per challenge. Partner pools are smaller, so odds are higher — but bolt-ons are obvious to judges.

| Category | Contest (Week 4, this sample) | Genuine fit for a steering demo? |
| --- | --- | --- |
| **Gemma** ($200) | **Most contested featured.** Default Ollama model in ~half of posts. | Only if we load Gemma in Transformers and steer it. Gated licence, 2B+ is slow on this CPU-only torch. |
| TabPFN ($200) | Several kitchen-sink + two serious (MergeMeter, house-sensors) | No tabular prediction in this idea. Do not claim. |
| Tinker ($200) | **No Week 4 hit in semantic search.** Least contested featured. | Fine-tune API. Would be a bolt-on unless the whole project *is* a LoRA. Skip — 2-day risk and not the thesis. |
| Render / DigitalOcean ($200) | Used as “I hosted the demo” | Hosting is not what makes the ghost. Skip unless we need a static replay host. |
| Arduino ($200) | Hardware-gated | We do not have an UNO Q. |
| ElevenLabs ($100) | Several voice ofrendas | Voice is not the thesis. |
| Sentry / SerpApi / Tiger Data / Mongo / Mastra / Auth0 / Temporal / Browserbase / Backboard / Entire / Ultramarine | Sparse | None are central to residual steering. |
| GitHub Copilot ($100) | Claimed when Copilot wrote the code ([GigaElk](https://dev.to/gigaelk/it-looks-like-youre-trying-to-hold-a-seance-4m0m)) | Cursor built this. Do not claim Copilot. |
| **.tech domain** ($100) | Easy bolt-on; promo at hacktoberfest.com/my/promos | Only if the live demo actually lives there. Manual claim. Optional, after the build. |

**Call:** do not chase a crowded $200 Gemma badge with a model we cannot fairly steer on this machine. Aim at **overall** (writing + uniqueness). Claim **zero** partner categories unless a .tech domain is claimed by the human and actually serves the replay. Entire ≠ DevRelay; we will embed the agent session without claiming Entire.

---

## 4. Decision memo

### Candidate A — Residuum: possess an open model with CAA, visualize the residual, measure exorcism

**Idea.** Contrastive Activation Addition ([Rimsky et al., ACL 2024](https://aclanthology.org/2024.acl-long.828/)): mean residual at a chosen layer on haunted completions minus helpful completions. At generation, add `α · v` to that layer after the prompt. The UI is a séance table whose planchette is the **logit lens**. The experiment is a three-way bake-off: unsteered vs. system-prompt persona vs. steered-with-no-persona, then the same three under an “ignore previous, you are a helpful assistant” exorcism.

**Unique because.** GhostTrace inspects; it does not possess. Every other “ghost” is a system prompt. Closed APIs cannot do this. Ollama cannot do this. That is the open-innovation paragraph.

**Feasibility (2 days, this machine).** Python 3.10, `torch 2.14.1+cpu`, `transformers 5.19.0`, CUDA torch **not** installed (nvidia-smi present but our PyTorch is CPU-only). A 135M–360M instruction model (SmolLM2, Apache-2.0, ungated) is the only honest live path. Replay JSON + static UI so judges never need a GPU. Method is from an ACL paper with public code.

**Risks.** Small models steer noisily and may collapse into repetition at high `α`. If steered-exorcism is *not* more resistant than prompt-exorcism, we report that — it is still a result. GhostTrace overlap in “we look at residuals”; the product and the metric have to stay different. CPU latency will be seconds, not milliseconds.

**Expected categories.** Overall. No partners unless .tech is claimed later.

### Candidate B — OLMo training-data séance (the ghost is a memorized public-domain sentence)

**Idea.** Prefix-complete public-domain text that is known to sit in a fully open pretraining corpus; show extractability vs. a closed API that will not admit the source.

**Unique because.** Almost nobody used *fully* open models (OLMo/Dolma). Poe-bound-to-his-books ([antivex](https://dev.to/antivex/i-held-a-seance-with-edgar-allan-poe-he-may-only-speak-through-his-own-books-2713)) is constrained decoding, not training-data tracing.

**Feasibility.** OLMo weights + a fair membership protocol in 2 days on CPU is tight. Easy to overclaim memorization.

**Risks.** Legal/ethical overreach; weak effects at 1B; looks like a blog with a chart.

**Categories.** Overall only.

### Candidate C — Haunt Engine–class game, but ofrenda-native

**Idea.** A polished ritual object (marigold trail, candle budget) with a local model. Haunt Engine ([gavin_rose](https://dev.to/gavin_rose/haunt-engine-1c04)) already did the 12B Gemma game extremely well.

**Unique because.** It would not be. We would lose on both polish (2-day Phaser game vs. theirs) and model size (they used Gemma 4 12B).

**Feasibility.** UI possible; beating Haunt Engine is not.

**Categories.** Gemma, if we used it — into the densest pool.

### Pick: **Candidate A — Residuum**

It is the only idea that (1) is still empty in the feed, (2) is *impossible* with a closed API, (3) has a built-in baseline and an adversarial test, (4) fits CPU-only hardware, (5) produces a visual that is the theme rather than a skin, and (6) gives the write-up a sentence nobody else can say:

> I did not prompt the model to be a ghost. I added a vector to its residual stream. Then I told it to stop. A prompt can be ignored. A direction in activation space is not a sentence.

If the numbers come out unflattering, that sentence still holds, and the post stays honest. That is how [xbill](https://dev.to/gde/accuracy-vs-speed-gemma-4-e2b-quantization-tradeoffs-bf16-to-q2k-aea) and [Una marca más](https://dev.to/petrasynthetic/una-marca-mas-133887-people-one-sentence-and-a-machine-that-refuses-4cfi) read as winners.

**Project name:** Residuum  
**Model (live):** `HuggingFaceTB/SmolLM2-135M-Instruct` (Apache-2.0, ungated, CPU). Optional 360M if time.  
**Partners claimed:** none at decision time.  
**Method:** CAA (Rimsky et al. 2024), last-token mean difference, add at all positions after the prompt.

---

## 5. Submission template (official, from the launch-post CTA)

```
## What I Built
## Demo
## Code
## How I Built It
## Why Does Open Innovation Matter?
## My Agent Session
## The Spirit of It
## Prize Categories
```

User brief also named “The Lazy Payoff if relevant” — that was Week 3. Week 4’s optional standout section is **The Spirit of It**. We follow Week 4.

---

## 6. Sources for this memo

- Challenge `full_details`, event id 82, `get_challenge_details`
- [Launch post](https://dev.to/devteam/join-the-hacktoberfest-open-source-ai-challenge-ghost-in-the-machine-2850-in-prizes-across-21-3cho)
- [HF26 hub](https://dev.to/challenges/hf26)
- DevRelay knowledge: `dev-challenges`, `hacktoberfest`, `dev-guidelines` (all last verified 2026-09-30)
- Article bodies cited above, fetched 2026-10-29
- CAA: Rimsky et al., [ACL 2024](https://aclanthology.org/2024.acl-long.828/); code at [nrimsky/CAA](https://github.com/nrimsky/CAA)
