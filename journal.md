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

## 2026-06-07 14:30 — Added a web UX over the same agent, kept cover gated
Built `src/agent/web.py` (FastAPI + Jinja2 + HTMX + Tailwind via CDN) as a second thin
UX over the *same* `imagine_band` / `generate_cover` modules — no agent logic duplicated.
Decisions:
- **Stateless** (chose this over a DB): the `BandConcept` is round-tripped to the browser
  as a single hidden JSON field and POSTed back when the cover button is clicked. No Neon
  table, no migration. Safe enough because the whole app is behind the password gate.
- **Spend stays gated**: cover generation is its own POST endpoint (`/band/cover`) that
  only fires on the button — never on a page visit. POST `/band` (the cheap LLM call) is
  all a visit triggers. Copied the example's `password_gate` middleware (httponly cookie).
- **Slow-call UX**: HTMX `hx-indicator` spinner + `hx-disabled-elt` on the buttons, rather
  than the example's heavier background-job+polling — fine at 6s/15s latencies.
Verified locally end-to-end (gate opened just for the test run): GET / renders the form,
POST /band returns the band + tracklist with the hidden concept and NO fal call, and the
stateless round-trip to /band/cover produced a real 1.7MB PNG. Pointed `railway.toml` at
`fastapi run src/agent/web.py` (the Dockerfile default entrypoint). Next: deploy.

## 2026-06-07 15:00 — Deployed to Railway
Live at https://band-namer-production.up.railway.app. Drove it with the Railway CLI:
`railway init` → `railway up --detach` → `railway variables --set` (OPENROUTER_API_KEY,
FAL_KEY, APP_PASSWORD — the three required ones; R2 left out until its credential is
fixed) → `railway domain`. The `$PORT` gotcha didn't bite — `fastapi run` read Railway's
injected PORT and bound 0.0.0.0:8080 with no start-command flags, exactly as docs/deploy.md
warns to rely on. Verified live: the password gate redirects `/` and `/band` to `/login`
for unauthenticated requests (so strangers can't spend), and the authenticated happy path
produced a band + 10 tracks with the cover button un-clicked (no fal spend on a visit).
Note: covers on the deployed app are temporary links until R2 is fixed.

## 2026-06-14 13:49 — Restyled the web UI: retro record-shop theme
Reskinned all six templates (base, index, login, _result, _cover, _error) from the dark
slate / fuchsia look to a warm 1970s record-shop aesthetic. **Styling only** — every
`hx-*` attribute, form name/id/action, the password gate, and the agent modules are
untouched. Decisions:
- **Theme lives in `base.html`** via a Tailwind v4 `@theme` block (aged cream, coffee
  brown, mustard/amber, burnt orange, faded red as named utilities) so the palette is
  defined once and reused, not sprinkled as ad-hoc hex across templates.
- **Type**: Alfa Slab One (chunky display) + Bitter (warm slab body), loaded with one
  Google Fonts `<link>`. Picked a slab display over a groovy script — reads as a record
  sleeve without tipping into kitsch.
- **Texture without assets**: page grain is an inline SVG `feTurbulence` data-URI plus a
  soft amber/red vignette; the vinyl record is pure CSS (concentric grooves + spindle
  hole). No image files to ship or host.
- **Vertical balance**: `main` uses `my-auto` inside a `min-h-screen` flex column. Chose
  this over `justify-center` deliberately — short pages center, but a tall band+cover
  result collapses the auto-margins and scrolls normally instead of clipping the top.
- **Record-sleeve panel** wraps the content block in `base.html`, so the framing applies
  to full pages *and* every HTMX fragment swapped into them, consistently.
After a first preview the user asked for three tweaks (done in a second pass): bigger and
fully *static* vinyl (dropped the spin animation entirely — no `@keyframes`, no
`prefers-reduced-motion` needed), the vertical centering above, and the sleeve panel.
Verified locally end-to-end behind the gate (GET /login, POST /login, GET / all render
the new markup; no spin classes remain). Lesson: keeping the theme as `@theme` variables
+ a wrapping panel in `base.html` made the second-pass tweaks a few small edits instead
of a hunt-and-replace across six files.
