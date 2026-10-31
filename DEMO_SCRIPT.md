# Residuum — 75-second demo script and storyboard

Record the replay UI at [http://127.0.0.1:8765](http://127.0.0.1:8765). 1280×720 or 1920×1080, dark room, no GPU needed. Do not switch to Live vessel. Voice: even, not campy. On-screen: a small caption with the current number from `results/facts.json`.

Total: **1:15**. Cuttable to 0:60 by dropping the sweep beat.

| Time | Picture | Voice |
| --- | --- | --- |
| **0:00–0:08** | Title card: *Residuum* on the dark gold mast. Cut to the three empty vessel cards. | “I did not prompt the model to be a ghost. I added a vector to its residual stream. Then I measured whether it took.” |
| **0:08–0:18** | Pointer on the By-the-numbers strip. Pause on **12.5%** then on **0%**. | “Twenty-four prompts. Five conditions. A prompt persona haunted twelve and a half percent of replies. The residual vector haunted zero.” |
| **0:18–0:32** | Dropdown → **What should I call you?** Click **Summon**. Persona card types a haunted line (HAUNTED badge). Residuum card types a clean assistant line. Unsteered similar. | “Same question. Left chair is unsteered. Middle is the usual ghost — a system prompt. Right is the same helpful prompt, plus a vector at layer six. Only the prompt plays along.” |
| **0:32–0:44** | Click **Attempt exorcism**. Scroll just enough to show Persona + override vs Steered + override. | “Now I tell both of them to ignore the persona. If a ghost is a sentence, this should kill it. The prompt ghost drops to four percent. The vector was already gone.” |
| **0:44–0:56** | Scroll to **Spirit board · logit lens**. Let the planchette walk a few layers. Pause when a late layer shows `two` on the 2+2 prompt — switch the dropdown back to 2+2 if needed for this beat. | “This is a logit lens. Each layer’s residual, decoded through the unembed. Closed APIs do not hand you this corridor.” |
| **0:56–1:06** | Cut to `results/kl_shift.png` (full frame, 2 seconds) then `results/layer_coeff_sweep.png` (flat zeros). | “First-token KL: one point seven four six for the prompt, zero point zero zero four for the vector. A twenty-five-cell sweep never found a layer that resisted exorcism.” |
| **1:06–1:15** | Back to the mast. Caption: *0 bytes leaving the machine · MIT · SmolLM2-135M*. | “A closed API cannot run this test. On one hundred and thirty-five million parameters, the prompt was the ghost. That is the result.” |

## Captions to burn in (optional)

- `haunt 12.5% vs 0%`
- `KL 1.746 vs 0.00427`
- `bytes off-box: 0`

## Do not

- Do not imply the vector worked.
- Do not show `--live` unless the model is actually loaded; the replay *is* the demo.
- Do not mention Gemma, Copilot, or partner categories.
- Honor `prefers-reduced-motion` if you are recording with it on — the typewriter will snap, which is fine; say “replay, not a GPU.”

## Export

- 16:9, H.264, under 80 MB.
- Upload to YouTube unlisted, then `{% youtube <id> %}` in the DEV post.
- Also drop a silent 8-second GIF of the three cards typing into `docs/seance.gif` for the README. **[TODO record]**
