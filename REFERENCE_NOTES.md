# Reference notes

Studied 2026-10-30 in the browser: hover was limited where the site hides the cursor, so timing comes from DevTools `cssRules`, not from guessing. Nothing here is a layout to copy.

## Said It — https://ayushkr23.github.io/said-it/

**Alive because the page behaves like an object, not a document.**

- Intro is a full-bleed count, “0 promises found”, with “click anywhere to skip” in tiny italic at the bottom. The real page is already in the DOM underneath.
- Custom cursor: `cursor: none` on the body, a 7px accent dot plus a ring (`.cursor-dot`, `.cursor-ring`), both `position: fixed; translate: -50% -50%`.
- Nav items are `.roll-host` with `transition: color 0.25s` only. The label swaps by rolling, not by scaling the pill.
- Hero title is `.split`. Display size measured at 118px. Accent phrase is a second color, not a gradient.
- Sticky notes are the product: slight rotations, washi-tape strips, stamped “9D LATE”. A sloth mascot (`.board-sloth`) sits in the cluster and is easy to miss beside the cards.
- Hand note in Caveat: “psst — this runs on your laptop, wifi off” with a curved arrow. The whisper is smaller than the headline and placed like a margin scribble.
- Bottom ticker (`.ticker-track`) runs `marquee` for **38s**, translating -50%. A live pill can read offline in red while the rest of the tape stays ink.
- Scroll progress is a fixed bar (`.scroll-progress`), easy to miss against the paper.
- Tokens from `:root`: paper `#f2ebdd`, ink `#1e1b17`, accent `#f2542d`, ease `cubic-bezier(.7, 0, .2, 1)`. Selection is accent on paper-hi.
- Type: Bricolage Grotesque (400–800), Caveat for asides, JetBrains Mono for the tape.
- Reduced motion only kills the ticker and sets `scroll-behavior: auto`. It does not blanket-remove every transition. That restraint is the detail.

## RTO Shield — https://www.rtoshield.tech/

**Alive because the chrome is stamped, not shaded.**

- Paper `#faf6ee` / ink near `#1b1712`. Body font Archivo with Inter Tight. Cursor is `none` again.
- Hero is a stacked wordmark: black “RTO”, then “SHIELD” knocked out of a hard yellow block. A hot-pink starburst sits off-axis (“most RTO is predictable!”). A loose ink scribble of a face floats at the left edge.
- Background is a faint ledger of order rows, not a gradient mesh.
- Primary button is a flat lime rectangle with a hard offset shadow (no blur). Secondary is white with a hairline. A spiral doodle and a script “psst — drag the levers below” sit under the buttons.
- The “live scan” card is a tilted ticket: thick black border, pink and orange tape, status pills in green/red. It looks pinned, not elevated.
- Loading state (hit while the page re-settled): “GETTING THE SERVERS READY”, “Warming up the risk model…”, a lime bar, elapsed `0:20`, and a hard offset border. The wait is designed. It is not a spinner in the corner.
- Section labels are slash-wrapped (`/Introducing/`), which makes the page feel annotated.

## lowkey — https://lowkey.nirajlabs.tech/

**Alive because small things have jobs.**

- Tokens: `--bg #F3EEE3`, `--paper #FFFDF7`, `--ink #111`, lime `#B8FF3B`, pink `#FF7AD9`, `--line: 3px solid`, `--shadow: 6px 6px 0`, `--spring: cubic-bezier(.34, 1.56, .64, 1)` plus a linear() spring. Dot-grid paper, not noise-only.
- Display is Bricolage again, but the italic “written” is a pink scribble (`stroke-dashoffset` draw, 0.75s, `cubic-bezier(.3, 0, .2, 1)`).
- Buttons are pills with hard shadows. “bill it” is lime; “nah” is quiet. They do not share one hover.
- The product preview is a physical stack: dark island, white review card, a pink “0 bytes leave your laptop” sticker overlapping the corner.
- A guide chip in the nav (“ask me about this page”) is a separate object from the links.
- Creatures are described in the copy as cursor-following blobs that blink, sleep, and morph. The mascot is a feature with rules, not a sticker.
- Reduced motion here is the blunt version: `animation: none !important; transition: none !important` on everything, and `.rise` forced visible. That keeps content, and it also freezes functional motion. Noted as a caution, not a pattern to copy.
- Cursor stays `auto`. Craft here is type, sticker, and shadow, not a pointer.

## What I am taking (craft, not skin)

- An intro you can skip, with the page already readable if script never runs.
- One ease family and one accent, used with discipline.
- Micro-copy in the margin, smaller than the argument.
- A mascot with behavior (look, blink, sleep), used once.
- Loading and empty states that look designed.
- Selection color, a progress mark, and a reduced-motion path that does not hide content.
- Different press physics per control. Said It rolls labels. RTO stamps. lowkey uses a spring overshoot. None of them scale-and-shadow everything.
