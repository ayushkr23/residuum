# UI audit — Residuum

One screen. No router. FastAPI serves `web/index.html` at `/` and the `web/` folder at `/static`.

## Stack (do not replace)

| Piece | What it is |
| --- | --- |
| Markup | `web/index.html` |
| Style | `web/styles.css`, custom properties, no preprocessor |
| Behavior | `web/app.js` (replay fetch, séance, logit lens, keyboard) |
| Data | `web/data/replay.json`, `web/data/facts.json`, `/api/health`, `/api/generate` |
| Dependencies | None on the front end. Python side is FastAPI. No React, no bundler. |

Framer Motion, Lenis, and GSAP are not added. They would replace this stack or hide content until hydration. Motion lives in `web/motion.css` (tokens) and `web/haunt.js` (springs on transform/opacity). `app.js` still owns data flow.

## Screen

`/` — the séance. Sections, in order:

1. Skip link
2. Mast (eyebrow, title, lede, sublede)
3. Number strip `#numbers` / `#strip-grid`
4. Controls (prompt, mode, coefficient, summon, exorcise, live hint)
5. Vessel table `#table` (three articles)
6. Spirit board `#ouija` + lens list
7. Exorcism panel `#exo-panel` (hidden until a session has those conditions)
8. Colophon
9. Help `#help` (hidden)

## Components and states

| Component | IDs / hooks | States that exist today | States that were missing |
| --- | --- | --- | --- |
| Skip link | `.skip` | focus | — |
| Grain | `.grain` | always on | pauses with reduced motion |
| Mast / title | `h1` | static | apparition, dust, triple-click |
| Number strip | `#n-un` `#n-pr` `#n-st` `#n-px` `#n-sx` `#n-bytes` | text set once, hover lift on `.stat` | count-up, loading skeleton, empty |
| Prompt select | `#prompt-select` | change → `showSession` | focus glow, empty options |
| Mode radios | `input[name=mode]` | replay default, live checks `/api/health` | pressed/focus distinct from summon |
| Coefficient | `#coeff` `#coeff-out` | input updates output; experiment sets value | flame thumb, bubble, keyboard |
| Summon | `#summon` | click → `summon(false)`; magnetic nudge | busy, success, disabled, focus ring |
| Exorcise | `#exorcise` | click → `summon(true)` | glitch label, press ring (must still click once) |
| Live hint | `#live-hint` | hidden unless live and model absent | error shiver |
| Vessels | `.vessel` `data-cond` | hover lift; `.possessed` on Residuum | levitate, tilt, drag-from-header, active from keys |
| Speech | `#speech-unsteered` `#speech-prompt_persona` `#speech-steered` | type-on via rAF; `aria-live=polite` | empty copy, haunted color |
| Tags | `#tag-*` | text meta | haunted vs clean color |
| Flame | `.flame` `.lit` | flicker keyframes | tied to theme candle |
| Board tabs | `.board-tabs button` `aria-selected` | selected fill | wisp; keys 1/2/3 did not move `aria-selected` |
| Letters | `#letters span` `.on` | planchette via left/top | develop-in |
| Planchette | `#planchette` | moves every 420ms | glow; jump when reduced motion |
| Lens list | `#lens-list` | rebuilt each session | stagger in |
| Exorcism panel | `#exo-panel` `[hidden]` | shown when session has exorcism text | curtain open |
| Exorcism cards | `#speech-prompt_exorcism` `#speech-steered_exorcism` | plain text | door light |
| Help | `#help` | `/` toggles, Esc closes | focus trap, curtain |
| Links | facts.json, code | color | underline draw |
| Keyboard | 1 2 3 E Enter / Esc | in `app.js` | hint chip, title change when hidden |

## Data flow that must survive

- `loadReplay` tries `/data/replay.json`, `/api/replay`, `./data/replay.json`.
- `fillStrip` / `fillPrompts` / `showSession` / `playLens` / `summon` / `checkLive` / `liveGenerate`.
- Replay mode never calls the network generate path.
- `prefers-reduced-motion` already skips the typewriter and the planchette interval.
