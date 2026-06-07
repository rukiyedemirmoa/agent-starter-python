# Architecture

**Stage 5 — Break it into atomic modules.**

Two atomic pieces plus thin wiring. The split exists for one reason: the **text** piece is
cheap and the **image** piece costs money, so they must be independently callable — text
runs every time, image runs only after the gate.

## The pieces

| Module | Does one thing | Input → Output |
|--------|----------------|----------------|
| `imagine_band` (in `agents/band.py`) | invent the concept | `vibe: str` → `BandConcept` (name, 10 songs, style note) |
| `generate_cover` (in `agents/band.py`) | make the album art | `BandConcept` + `vibe` → `Cover` (URL + whether it's persisted to R2 or a temp fallback) |
| `main.py` (CLI wiring + UX) | run the flow + the gate | user vibe → printed concept, then gated cover |
| `web.py` (web wiring + UX) | same flow over HTTP | vibe form → band + tracklist page; a **button** POSTs back to generate the cover (the gate) |

Both `main.py` and `web.py` are thin UX layers over the *same* two modules. The web app
is stateless: the band concept is round-tripped to the browser as a hidden field and
POSTed back when the cover button is clicked, so no database is needed. A password gate
(`APP_PASSWORD`) protects the deployed app, and cover generation lives on its own POST
endpoint that only fires on the button — never on a page visit — so it can't auto-spend.

`BandConcept` is a Pydantic model: `band_name: str`, `tracklist: list[str]` (validator:
len == 10), `style_note: str`. The validator is what makes "exactly 10 songs" a guarantee
rather than a hope.

## Which starter services does each use?

- `llm` — `imagine_band` only: a pydantic-ai `Agent` with `output_type=BandConcept`.
- `media` (fal) — `generate_cover` only: `text_to_image(..., persist=True, prefix="bandnamer")`.
- `storage` (R2) — indirectly, via `persist=True` inside `generate_cover`.
- `db` (Neon) — none.

## Data flow

```
vibe ──▶ imagine_band ──▶ BandConcept ──▶ print name + tracklist
                                          │
                                   [gate: confirm? ]
                                          │ yes
                                          ▼
                       generate_cover(concept, vibe) ──▶ cover URL ──▶ print
```

The gate sits in `main.py` *between* the two modules — neither module knows about it.
That keeps each piece pure and testable in isolation (stage 6): `imagine_band` with no
spend, `generate_cover` only when we mean to.

## Data you store (if any)

None yet. The cover is persisted to R2 (UUID key under the `bandnamer/` prefix) via
`persist=True`, but no database tables. If we later want a gallery of past concepts,
that's a new migration (`bandnamer_concepts`) — out of scope for now.
