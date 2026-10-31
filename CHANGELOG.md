# UI changelog

Motion and chrome only. Replay loading, séance conditions, the logit lens, and the generate API are the same paths as before.

## Tokens and type

- `web/motion.css` is the only motion-token file: easings, durations, distances, palette, type.
- Fraunces, Outfit, and IBM Plex Mono are self-hosted latin subsets (`web/fonts/`).
- Decorative motion is opt-in under `prefers-reduced-motion: no-preference`. Reduced motion keeps state changes and drops travel. The planchette still moves; it just jumps.

## Interaction layer (`web/haunt.js`)

| Piece | What it does |
| --- | --- |
| Lantern cursor | Spring-lagged glow, hotter over buttons, dimmer over text, sleepy after 5s, fading trail. Off for touch and reduced motion. |
| Flashlight | Chalk notes on the spirit board are masked to the lantern. Touch-and-hold shows them. |
| Ectoplasm summon | Blob stretches toward the pointer, splats on press, heartbeats while busy, settles marigold on success. |
| Exorcise | Chromatic glitch on hover, ring fill on press. Still one click, and `E` still works. |
| Apparition + dust | The wordmark fades up letter by letter, then letters shy away from the pointer. |
| Flicker counts | Percents count in and lock with a glow. Zeros stay put. |
| Levitating cards | Bob, contact shadow, tilt, throw-and-settle from the header. Double-click flips to a back face. |
| Wisp tabs | An orb rests on the selected lens tab. Keys 1/2/3 now move that selection too. |
| Candle | Side candle burns down with scroll and flares at the end. Hidden on short screens. |
| Theme | “Blow out the candle” swaps midnight for moonlit paper, with a vignette. Saved locally. |
| Sound | Off until the button is pressed. A whoosh only plays then. |
| Whispers | Short lines fade in place. Not a scrolling marquee. |
| Mascot | Looks at the pointer, blinks, flinches at a fast swipe, sleeps when idle, peeks when clicked. |
| Intro | A veil for 1.1s, skippable, created in script so the page is readable if script never runs. Once per tab session. |
| Help | Curtain dialog, focus trap, Esc and backdrop click close it. |
| Toasts | A small ghost line when the live vessel is asleep or a generate call fails. |
| Tooltips | Planchette spells `data-tip` labels. |
| Easter eggs | `boo` releases a flock. Konami flares every flame. Triple-click the wordmark spins the mascot. A hidden tab retitles itself. |

## Markup and copy

- Candle, fog, grain, vignette, lantern, mascot, theme, and sound controls added around the existing sections.
- Vessel backs added. Speech and tag ids are unchanged.
- Empty replay line and the live-asleep hint rewritten.
- Magnetic button nudge removed from `app.js` so it no longer fights the ectoplasm blob.
- Summon and exorcise pick up busy and success classes. They are not hold-to-confirm.

## Left alone, on purpose

- No React, Framer Motion, Lenis, or GSAP. Those would replace a static page or hide it until hydration.
- No second route, so there is no page-to-page ghost sheet. The intro veil is the one sweep.
- No delete animation. The séance does not remove rows.
- Exorcism stays one click. A hold-to-banish that swallowed the click would hide the result from the keyboard and from judges.
- Experiment numbers, metrics, and `results/facts.json` were not regenerated.
