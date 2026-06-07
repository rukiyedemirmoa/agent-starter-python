"""Web UX for the band-namer — type a vibe, see the band + tracklist, button for a cover.

Run it locally (auto-reload):

    uv run fastapi dev src/agent/web.py

It's a thin wiring layer over the SAME two modules the CLI uses (`imagine_band` and
`generate_cover`); see docs/architecture.md. Two design choices matter:

  - STATELESS: the band concept is round-tripped to the browser as a hidden field and
    POSTed back when the cover button is clicked — no database needed.
  - GATED SPEND: cover generation lives on its own POST endpoint that only fires on the
    button click, never on a page visit. And the whole app sits behind an APP_PASSWORD
    login (set it before deploying), so strangers can't run up your fal.ai bill.

FastAPI docs: https://fastapi.tiangolo.com/  ·  HTMX: https://htmx.org/docs/
"""

import secrets
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import ValidationError

from agent.agents.band import BandConcept, generate_cover, imagine_band
from agent.config import get_settings
from agent.logging_setup import setup_logging

HERE = Path(__file__).parent
templates = Jinja2Templates(directory=str(HERE / "templates"))

AUTH_COOKIE = "bandnamer_auth"  # holds the app password once you've logged in

setup_logging()
app = FastAPI(title="Band Namer")


# --- auth: a simple password gate (Pattern C) -------------------------------


@app.middleware("http")
async def password_gate(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """If APP_PASSWORD is set, require login before any page. No password set = open
    (fine for local dev). The httponly cookie is sent automatically with every request
    and isn't readable by JavaScript."""
    password = get_settings().app_password
    if password and request.url.path != "/login":
        cookie = request.cookies.get(AUTH_COOKIE, "")
        if not secrets.compare_digest(cookie, password):
            return RedirectResponse("/login", status_code=303)
    return await call_next(request)


@app.get("/login")
async def login_form(request: Request) -> Response:
    if not get_settings().app_password:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": False})


@app.post("/login")
async def login(request: Request, password: Annotated[str, Form()]) -> Response:
    expected = get_settings().app_password or ""
    if expected and secrets.compare_digest(password, expected):
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(
            AUTH_COOKIE, password, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 7
        )
        return response
    return templates.TemplateResponse(request, "login.html", {"error": True}, status_code=401)


# --- the app ----------------------------------------------------------------


@app.get("/")
async def index(request: Request) -> Response:
    return templates.TemplateResponse(request, "index.html", {})


@app.post("/band")
async def band(request: Request, vibe: Annotated[str, Form()]) -> Response:
    """Invent the band (cheap LLM call). Returns the result fragment HTMX swaps in.
    No fal spend here — only the cover button (below) spends."""
    try:
        concept = await imagine_band(vibe)
    except Exception as error:  # LLM down/slow — show it honestly, don't 500
        logger.exception("imagine_band failed")
        return templates.TemplateResponse(
            request, "_error.html", {"message": f"Couldn't dream up a band: {error}"}
        )
    return templates.TemplateResponse(
        request,
        "_result.html",
        {"concept": concept, "concept_json": concept.model_dump_json(), "vibe": vibe},
    )


@app.post("/band/cover")
async def cover(
    request: Request,
    concept: Annotated[str, Form()],  # the BandConcept, round-tripped as JSON
    vibe: Annotated[str, Form()],
) -> Response:
    """Generate the album cover. THIS is the only endpoint that spends fal.ai money,
    and it only runs when the user clicks the button — never on a page visit."""
    try:
        parsed = BandConcept.model_validate_json(concept)
    except ValidationError:
        return templates.TemplateResponse(
            request, "_error.html", {"message": "That band concept looks malformed."}
        )
    try:
        result = await generate_cover(parsed, vibe)
    except Exception as error:  # fal down/empty — keep the concept already on the page
        logger.exception("generate_cover failed")
        return templates.TemplateResponse(
            request, "_error.html", {"message": f"Couldn't generate the cover: {error}"}
        )
    return templates.TemplateResponse(
        request, "_cover.html", {"url": result.url, "persisted": result.persisted}
    )
