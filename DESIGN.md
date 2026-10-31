# Design — Residuum, friendly haunting

The page is a measured séance, not a haunted house. Warm, a little playful, never gory. The honest result (the prompt haunted, the vector did not) stays in bone-white sentences. The ghost is the chrome.

## Why this stack

`web/` is static HTML, CSS, and one script. Framer Motion needs React and ships `opacity: 0` until hydration ([The 129 elements that only existed once JavaScript loaded](https://dev.to/samuelfmedeiros/the-129-elements-that-only-existed-once-javascript-loaded-k23)). A single séance page does not need Lenis or GSAP; the platform already has WAAPI and a short spring ([Animations without GSAP](https://dev.to/commonlayer/animations-without-gsap-what-111-free-components-use-instead-1364)). Tokens live in **one file**, `web/motion.css`. `web/haunt.js` reads them. Decorative motion is opt-in under `@media (prefers-reduced-motion: no-preference)` so a failed media query stays still ([prefers-reduced-motion](https://dev.to/parsajiravand/youre-animating-for-everyone-prefers-reduced-motion-fixes-that-2ond)).

## Palette

| Token | Dark (default, candle lit) | Light (moonlit paper) |
| --- | --- | --- |
| Background | `#100c14` midnight | `#efe4d2` |
| Surface | `#1c1724` fog | `#f7f1e6` |
| Ink | `#f4ecdf` bone | `#241c16` |
| Muted | `#a89888` | `#6d6258` |
| Accent | `#f0b45a` candle amber | `#b86a12` |
| Success | `#e8872a` marigold | `#c46a14` |
| Spectral | `#7ed0c8` ghost teal | `#1d6f68` |
| Danger | `#d4654e` warm ember | `#9c3b2e` |
| Line | `rgba(244,236,223,.14)` | `rgba(36,28,22,.14)` |

Dark is the séance. Light is the morning after, same type, cooler fog, amber turned to dried marigold. Toggled by blowing out the candle. Stored in `localStorage` key `residuum-theme`.

## Type

Self-hosted (OFL), so the judged replay does not call Google at view time.

- Display: Fraunces, optical size up, for the name and section titles.
- Body: Outfit, for lede and controls.
- Mono: IBM Plex Mono, for percents, tags, kbd.

Scale: 0.72 / 0.85 / 1 / 1.15 / 1.35 / clamp(3.2rem, 8vw, 6.6rem). Line height 1.45 body, 1.05 display.

## Space, radius, shadow, edge

- Space: 4, 8, 12, 16, 24, 40, 64.
- Radius: 2px tickets, 14px cards, 999px the wisp and the flame thumb. Buttons are not pills.
- Shadow: candle glow `0 0 24px rgba(240,180,90,.28)` and a contact shadow under levitating cards. No hard comic offset (that is RTO’s signature, not ours).
- Borders: 1px fog line. The spirit board keeps a thicker wood frame because it is an object.
- Texture: SVG film grain at 7% opacity, a vignette, three fog layers translating on a slow loop.

## Voice

Short, a little shy, still precise. The lede stays the experiment. Chrome copy can blink.

- Summon stays “Summon”. Exorcise stays “Attempt exorcism”.
- Live asleep: “The live vessel is asleep. Replay still has the whole séance.”
- Empty replay: “Nothing here but dust… and me.”
- Whispers (random, not a marquee): “the prompt was louder”, “layer six was a tie”, “zero bytes left”.

## Motion tokens (`web/motion.css`)

| Name | Value | Use |
| --- | --- | --- |
| `--ease-out` | `cubic-bezier(.16, 1, .3, 1)` | reveals |
| `--ease-in-out` | `cubic-bezier(.4, 0, .2, 1)` | theme fade |
| `--spring-soft` | `cubic-bezier(.22, 1.15, .36, 1)` | cards settling |
| `--spring-snappy` | `cubic-bezier(.2, 1.4, .4, 1)` | wisp, flame |
| `--spring-bouncy` | `cubic-bezier(.34, 1.56, .64, 1)` | mascot spin |
| `--dur-micro` | 160ms | glitch |
| `--dur-press` | 220ms | press |
| `--dur-panel` | 480ms | curtains, doors |
| `--dur-reveal` | 700ms | apparition |
| `--stagger` | 40ms | lens rows |
| `--lift` | 10px | card rise |
| `--dust` | 14px | letter scatter |

JS springs in `haunt.js` use the same durations as settle times (critically damped, closed form). They do not invent a second ease.

## Signature table

No two families share a hover or a press. Reduced motion keeps the state (color, text, opacity) and drops travel.

| Component | Signature | Token | Reduced motion | Touch |
| --- | --- | --- | --- | --- |
| Lantern cursor | Lagging candle glow, flicker, sleepy shrink after 5s, wisp trail | `--spring-soft` | System cursor | Hidden after touch; tap-hold shines secrets |
| Summon | Ectoplasm blob stretches toward the pointer, splat on press, heartbeat while busy, condenses to marigold on success | `--spring-snappy` | Label + opacity, no blob travel | Same, blob rests center |
| Exorcise | Chromatic glitch on hover (~160ms), spectral ring fills on press. Click still fires immediately | `--dur-micro` | Color change, no jitter | Press ring via `:active` |
| Title | Letters apparate from blur, then dust away from the pointer | `--dur-reveal` / `--dust` | Full opacity text | No dust; apparition is a fade |
| Stats | Flicker-count, then a lock-in glow. No lift | `--dur-panel` | Final number at once | Same |
| Vessels | Slow bob, contact shadow, tilt toward pointer, drag the header and throw | `--spring-soft` | No bob, no tilt; border shows focus | Tap header focuses; no drag inertia |
| Board | Polaroid develop (blur to sharp once) | `--dur-reveal` | Sharp immediately | Same |
| Tabs | Will-o’-the-wisp orb, not a pill | `--spring-snappy` | Selected fill only | Tap selects, as now |
| Scroll | Side candle burns down; flare at the end | `--dur-micro` | Hidden | Hidden under 720px height |
| Theme | Blow-out: vignette, smoke, theme crossfade | `--dur-panel` | Instant theme swap | Tap the cord |
| Links | Underline draws from the left | `--dur-press` | Underline always on focus | Underline on `:focus-visible` |
| Select | Ink-bleed focus, label lifts like smoke | `--dur-press` | Border color only | Native select |
| Slider | Flame thumb, wobbling value bubble | `--spring-snappy` | Number updates, no wobble | Native range |
| Radios | Small door-swing of the knob (rotate), not a scale | `--dur-press` | Filled dot | Native radio |
| Help | Curtain with spill light, focus trap | `--dur-panel` | Fade opacity | Same |
| Exorcism cards | Door perspective, warm spill when the panel opens | `--dur-panel` | Shown, no swing | Same |
| Toasts | Spirit: float, bob, mist out. Error shivers once | `--spring-soft` | Fade only | Same |
| Tooltips | Planchette spells the label | `--dur-micro` | `title` plus visible text | Long-press shows the label |
| Whispers | Phrases fade in place at random | `--dur-reveal` | One static line | Same |
| Mascot | Blink, look, peek, flinch, sleep | `--spring-bouncy` | Static ghost | Static ghost |
| Intro | Fog sheet, under 1.2s, click or Esc skips. Not in the HTML, so the page is born visible | `--dur-reveal` | Skipped | Tap to skip |
| Lens rows | Fade + 6px rise, staggered | `--stagger` | Instant list | Same |
| Secrets | Chalk only inside the lantern mask | — | Hidden (decorative) | Tap-hold on the board |

## Easter eggs

- Type `boo` outside a field: a few ghosts cross the screen.
- Konami: every flame flares.
- Triple-click the wordmark: the mascot spins once.
- Hidden tab: document title becomes “the candle is still lit”.
- Sound is off. A mute control can arm a tiny whoosh; the visual always happens anyway.

## What I will not change

- Replay JSON shape, generate API, metrics, or the experiment.
- The three-vessel comparison and the logit-lens walk.
- Hold-to-confirm that swallows the first click. Exorcism must stay one click and the `E` key, or judges lose the result.
- A delete animation. Nothing in this UI is removed from a list.
