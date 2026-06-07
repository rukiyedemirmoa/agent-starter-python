# User Stories

**Stage 3 — Operationalize success as UX.** (Pair with `failure_modes.md` and `scenarios.md`.)

The agent: give it a **vibe**, get back a **band name**, a **10-song tracklist**, and —
after you confirm — an **album cover image**.

## Stories

1. As a daydreaming musician, I want to describe a vibe in a few words and get an
   original band name + 10-song tracklist, so that I have a concept to riff on.
2. As a budget-conscious tinkerer, I want to see the name and tracklist *before* any
   image is made, so that I only spend fal.ai money on covers I actually like.
3. As that same tinkerer, I want to confirm (or skip) the cover with one keypress, so
   that I stay in control of when money is spent.
4. As someone who'll come back to this, I want the cover saved to a durable URL, so
   that the link still works tomorrow.
5. As someone sharing this with friends, I want a simple web page where I type a vibe and
   see the band + tracklist, with a button to generate the cover, so that no one needs the
   terminal — and the cover only generates (and spends) when someone clicks the button.

## What "good" feels like

Fast and a little magical: a vague vibe becomes a *named* band with songs that sound
like they belong together, in a few seconds. The money moment (the cover) never happens
by surprise — it always waits for a yes.

## Out of scope (for now)

- Actual audio / generated music.
- Multiple variations or a "regenerate" loop (one concept per run is fine to start).
- Saving concepts to a database or a web UI — this is a CLI first.
