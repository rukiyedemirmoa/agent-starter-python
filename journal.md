# Journal

This is the running trace of your thinking as you build. It's the most important
document in the project — more than any single piece of code.

**How to use it**
- Add an entry at *meaningful* moments: a decision (and **why**), something you
  learned, a dead end you backed out of, a milestone reached.
- **Not** every edit. Capture the thinking, not the keystrokes.
- Always **timestamp** with date **and** time. Newest entries go at the bottom.
- Both you and Claude should add entries.

Format:

```
## YYYY-MM-DD HH:MM — Short title
What you were trying to do, what you decided, and why. What you learned.
```

---

## 2026-05-29 12:00 — Project initialized from the agent starter
Cloned the starter. Next: fill in `docs/problem.md` (what can't I do today?) and the
"Your project" section of `README.md` (what am I building?). Then design before coding.

## 2026-06-06 16:00 — Chose the project: a vibe → band concept generator
Decided what to build: give it a *vibe* (a few words), get an original band name, a
10-song tracklist, and an album cover. Drafted the stage-3 docs (user stories, failure
modes, scenarios) and stage-4/5 docs (policy, architecture) before any code, per the
method. The interesting failure modes for an agent like this: a name that's secretly a
real band, the wrong number of songs, and spending fal.ai money the user didn't intend.

## 2026-06-06 16:30 — Split text from image, with the cover gated as *code*
Key architecture decision: two atomic modules — `imagine_band` (cheap LLM call, runs
every time) and `generate_cover` (costs fal money, runs only on confirmation). The
budget gate (`[y/N]`, default No) lives in `main.py` *between* them, not inside either
module and **not** as something the model decides. The money rule must be control flow,
not a sentence in a system prompt the model might ignore. Bonus: keeping the modules
pure means I can hammer on `imagine_band` for free and only call `generate_cover` when I
mean to spend. Also had `BandConcept` emit a `style_note` in the same LLM call, so the
cover prompt later inherits coherent art direction for free instead of re-deriving it.

## 2026-06-07 11:00 — R2 was broken; chose a temporary-URL fallback over hard failure
First real cover generation failed — but at the *R2 upload* step, not generation:
`SignatureDoesNotMatch`. `agent-doctor` confirmed R2 fails even a plain list call, and
the credential *shapes* are all correct (right lengths, no quotes/whitespace), so the
secret simply doesn't match the access key — a `.env` credential issue to fix in the
Cloudflare dashboard, not a code bug.

The deeper lesson was a design one: `generate_cover` originally required `persist=True`,
so a storage hiccup threw away an image we'd *already paid fal to generate*. Reworked it
to generate first, then persist best-effort — on R2 failure, fall back to fal's temporary
URL and flag that it expires (~1h). Returns `Cover(url, persisted)` so the CLI can warn.
Exposed `media.persist_file()` to separate generation from persistence cleanly. fal
outputs are real money; throwing them away on a storage error is waste.

## 2026-06-07 11:40 — Stacked-panel glitch was aspect_ratio="auto"
The first clean cover had a duplicated top half stacked at the bottom — looked like a
bug, was actually image-model behavior. Read nano-banana-2's `llms.txt`: `aspect_ratio`
defaults to `"auto"`, letting the model pick dimensions from the prompt; for a cinematic
scene it went tall and tiled the composition. Pinned `aspect_ratio="1:1"` and tightened
the prompt against panels/stacking. Regenerated → clean 1024×1024 single image. Lesson:
when a media model misbehaves, read its `llms.txt` before touching the prompt — the
default parameters are often the real cause.
