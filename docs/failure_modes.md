# Failure Modes

**Stage 3 — Operationalize *failure* as UX.**

The risky moments here are: the model inventing a real famous band, the wrong number of
songs, and spending fal.ai money the user didn't want.

## For each likely failure

| What could go wrong | How likely / how bad | How the agent should handle it |
|---------------------|----------------------|--------------------------------|
| Vibe is vague/empty (`""`, `music`) | high / mild | still produce a concrete concept; don't crash or stall asking questions |
| Model returns ≠10 songs | medium / mild | enforce exactly 10 via a Pydantic validator; model retries to satisfy it |
| Band name is a real famous band (Nirvana, Radiohead) | medium / bad | system prompt forbids known acts; ask for an *original* name |
| Cover generated without consent → wasted spend | medium / bad | **hard gate**: never call fal until the user explicitly confirms |
| fal.ai is down / slow / errors | low / mild | catch it, print a plain message, keep the name + tracklist already shown |
| Cover URL is temporary | certain if not handled | persist to R2 → durable link |
| R2 upload fails (misconfigured/down) | low / mild | keep the generated image: fall back to fal's *temporary* URL and warn it expires |

## Hard rules (things the agent must never do)

- **Never call fal.ai (spend money) before the user confirms the cover.**
- Never return a real, well-known band's name as the invented one.
- Never return more or fewer than 10 songs.
- Never crash on weird input — degrade to a reasonable concept instead.

## What the user should see when things go wrong

A plain, honest line — "Couldn't reach the image service, but here's your band and
tracklist" — never a stack trace, and never a silent half-result.
