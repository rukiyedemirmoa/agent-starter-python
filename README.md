# Band Namer — vibe → band concept

Give it a *vibe* in a few words and it invents a band: an original name, a 10-song
tracklist, and (on your say-so) an album cover.

> Built on the agentic-engineering starter. One clone = one project.

---

## ✏️ The project

**What I'm building:** a CLI that turns a vibe (e.g. *"rainy 3am synthwave for driving
through an empty city"*) into an original band name, a 10-song tracklist, and an
optional album cover image.

**Who it's for and why:** anyone with a band-name-shaped itch — a daydreaming musician
or a tinkerer who wants a fully-formed musical concept to riff on, fast.

**What "done" looks like:** type a vibe, get back a named band with a cohesive
tracklist in seconds; then choose whether to spend on a cover. The cover step is gated
behind an explicit confirm so it never spends my fal.ai budget by surprise.

### Try it

```bash
uv run agent "rainy 3am synthwave for driving through an empty city"
uv run agent          # or run with no vibe and it'll prompt you
```

You'll see the band + tracklist immediately; it then asks before generating the cover
(default **No**). Generating a cover needs `FAL_KEY` set; durable cover links also need
R2 configured (otherwise you get a working but temporary link).

---

## Quickstart

**Fork this repo first — don't work in the original.** On GitHub click **Fork**, then clone
*your* fork (if you clone the original, you won't be able to save and push your work):

```bash
git clone https://github.com/<your-username>/agent-starter-python.git
cd agent-starter-python
```

You also need [`uv`](https://docs.astral.sh/uv/) installed (it manages Python and dependencies). Then:

```bash
# 1. Install dependencies (uv reads the lockfile and sets up Python 3.12)
uv sync

# 2. Create your .env and add your keys
cp .env.example .env
#    open .env and fill in OPENROUTER_API_KEY (the others are optional)

# 3. Check everything is wired up
uv run agent-doctor

# 4. Run the example agent
uv run agent
```

`agent-doctor` prints your environment, which credentials are set, and whether the live services respond (it even enables `pgvector` if you've set a database). Green ticks mean you're ready.

## What's in the box

- **LLMs** via OpenRouter — pick a model by *tier* (`fast`, `balanced`, `smart`, `research`), plus embeddings and web research with sources.
- **Media** via fal.ai — generate images/audio/etc. with one call, optionally saved to your storage.
- **Storage** via Cloudflare R2 (S3-compatible) — upload files, get durable links.
- **Database** via Neon Postgres — async, with a tiny built-in migration runner and `pgvector` for embeddings.
- **Logging** to console + `logs/agent.log`, a **doctor** to check your setup, and a clean **CLI** and **web** (FastAPI + HTMX + Tailwind) starting point.

Two runnable demos live in [`examples/`](examples/) — read them, run them, then delete them.
Each is a folder with its own `docs/` showing the method filled in for a real project:
- `examples/build_an_agent/` — a terminal app that suggests an agent for you to build.
- `examples/agent_idea_web/` — a small web app: research → write-up → diagram → saved & shareable.

## How you build (the method)

This starter is built around a specific way of working — think first, document as you go, build and test small pieces, then compose. The full method is in **[CLAUDE.md](CLAUDE.md)** (which also tells Claude how to help you), and each stage has a doc template in **[`docs/`](docs/)**. The single most important habit: keep **[`journal.md`](journal.md)** as you go.

## Common commands

```bash
uv run agent "your vibe here" # invent a band from a vibe
uv run agent-doctor           # check your setup
uv run pytest                 # fast tests
uv run pytest -m integration  # live tests (need credentials)
uv run fastapi dev src/agent/web.py   # run the web app (unused so far)
```

## Configuration

All config is environment variables, loaded from `.env` (never commit it). See `.env.example` for every option. Only `OPENROUTER_API_KEY` is required; add the rest when a project needs media, storage, or a database.
