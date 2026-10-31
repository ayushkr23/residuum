# Ethics and limitations

Residuum is a demonstration of **inference-time activation steering**. It does not summon, channel, or represent the dead. The “ghost” is a direction in a small language model’s residual stream, extracted from synthetic contrastive text that we wrote.

## What this is not

- It is not a medium, ofrenda, or memorial for a real person.
- It does not use family photos, voice recordings, or anyone’s private data.
- It does not claim that the model *believes* or *feels* anything. A steering vector is a mean difference of activations. A haunted sentence is a change in next-token probabilities.

## What can go wrong

- **Over-steering** can collapse fluency into repetition or nonsense. The UI exposes the coefficient so you can see the failure, not hide it.
- **Lexicon metrics are blunt.** A reply can be eerie without using our word list, and a reply can hit the word list while still being a normal sentence (“dead code”, “ghost process”). We report the metric and its holes.
- **Small models are suggestible.** SmolLM2-135M is not Llama-2-7B from the CAA paper. Effects will be noisier. If the steered model is *not* more exorcism-resistant than a prompt persona, that is a real result and we will print it.
- **Do not use this to impersonate a deceased person.** The contrastive pairs are fictional gothic prose, not a biography.

## Privacy

Live inference runs on the machine that loaded the weights. The replay demo is static JSON. The experiment records no user text. `bytes_leaving_machine` in `results/facts.json` is the count of payload bytes we observed leaving the process for inference, which is zero by construction (no HTTP client in the generate path). Tokenizer and model files may be fetched from Hugging Face **once**, at install time, if they are not already cached.
