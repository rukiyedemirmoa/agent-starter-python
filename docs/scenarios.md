# Scenarios

**Stage 3 — Concrete end-to-end walkthroughs.** These are the stage-8 test checklist.

## Happy path

**Scenario: confirmed cover**
1. User runs the agent and is asked for a vibe → types
   `rainy 3am synthwave for driving through an empty city`.
2. The agent prints an original band name (e.g. *Neon Curfew*) and a numbered
   10-song tracklist that fits the mood.
3. The agent asks: *"Generate the album cover? [y/N]"*. User presses `y`.
4. The agent generates the cover, persists it to R2, and prints a durable URL.

**Expected:** valid name + exactly 10 fitting songs in a few seconds; cover only
generated after `y`; final URL still works later.

## Edge cases & tricky inputs

- **Skip the cover** (user presses `N` / Enter at the gate) → expected: prints name +
  tracklist, generates **no** image, spends **no** fal money, exits cleanly.
- **Vague / empty vibe** (`""`, `music`) → expected: still returns a concrete named
  band + 10 songs; never crashes or interrogates the user.
- **fal.ai down at the gate** (user said `y` but the call fails) → expected: a plain
  honest message; the name + tracklist already shown remain intact.

## Done = all scenarios pass

When every scenario behaves as written, the agent works. Add new cases here as you find
them, then make them pass.
