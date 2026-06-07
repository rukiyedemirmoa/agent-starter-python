# Policy

**Stage 4 — Describe the target agent behavior, step by step.**

The rulebook. The *creative* part becomes the LLM system prompt; the *gate* part becomes
control flow in `main.py` (it is code, not the model's choice).

## The agent's job, in one line

Turn a vibe into an original band name + a 10-song tracklist, then — only on the user's
say-so — an album cover.

## Step by step

1. Read a **vibe** from the user (CLI arg, or a prompt if none given).
2. Ask the LLM for a `BandConcept`: an original band name, exactly 10 song titles, and a
   short visual style note (for the cover prompt later).
3. Print the band name and the numbered tracklist.
4. **Gate (code, not the model):** ask *"Generate the album cover? [y/N]"*.
   - No / Enter → print nothing more, spend nothing, exit cleanly.
   - Yes → continue.
5. Build an image prompt from the band name + vibe + style note.
6. Call `media.text_to_image(..., persist=True, prefix="bandnamer")`.
7. Print the durable cover URL. On failure, print a plain message; the name + tracklist
   already shown stay intact.

## Tools it can use

- **LLM** (`build_model` + a pydantic-ai `Agent`) — step 2, the only creative call. No web
  research needed; this is invention, not fact-finding.
- **`media.text_to_image()`** (fal) — step 6, and **only after** the step-4 confirmation.
- **`storage`** (R2) — indirectly, via `persist=True`, to make the cover URL durable.
- No `db` — nothing is persisted between runs yet.

## Tone & style

The band concept should read like a real act with a point of view: an evocative,
*original* name and song titles that clearly belong to the same record. Playful and
confident, not generic ("Song 1", "The Journey"). No explanation or preamble in the
output — just the goods.

## Rules & boundaries

- **Never call fal.ai before the user confirms** (the money rule).
- Exactly **10** songs — enforced by a Pydantic validator, not just asked for.
- The band name must be **original** — never a real, well-known act.
- Always produce a concept, even for a vague or empty vibe — never interrogate the user.
- On any fal error, fail honestly and keep the already-shown concept.
