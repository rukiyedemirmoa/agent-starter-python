"""The vibe → band agent.

Two atomic pieces (see docs/architecture.md):
  - `imagine_band(vibe)` — cheap LLM call; invents the concept. Runs every time.
  - `generate_cover(concept, vibe)` — costs fal.ai money; gated behind user confirmation
    in main.py. (Added in the next step.)

This file holds only the *first* piece for now, so the text half can be tested for free
before any spend is wired in.
"""

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from agent.services import media
from agent.services.llm import build_model

TRACK_COUNT = 10
COVER_PREFIX = "bandnamer"  # namespaces our files in the shared R2 bucket
COVER_ASPECT_RATIO = "1:1"  # force a square cover; "auto" let the model stack panels


class BandConcept(BaseModel):
    """The invented band, returned (already validated) by the LLM.

    `tracklist` is pinned to exactly TRACK_COUNT entries via min/max_length — so "10
    songs" is a guarantee the model must satisfy (it retries on a miss), not a hope.
    `style_note` is emitted in the same call so the cover prompt later inherits a
    coherent art direction instead of re-deriving the vibe.
    """

    band_name: str = Field(description="An original, evocative band name. Never a real, known act.")
    tracklist: list[str] = Field(
        min_length=TRACK_COUNT,
        max_length=TRACK_COUNT,
        description=f"Exactly {TRACK_COUNT} song titles that clearly belong to the same record.",
    )
    style_note: str = Field(
        description="One vivid sentence describing the album's visual style, for the cover art."
    )


band_agent = Agent(
    build_model(),
    output_type=BandConcept,
    system_prompt=(
        "You invent fictional bands from a vibe. Given a mood or description, conjure an "
        "ORIGINAL band with a point of view: an evocative name (never a real, well-known "
        f"act) and exactly {TRACK_COUNT} song titles that sound like one cohesive record. "
        "Avoid generic filler like 'Song 1' or 'The Journey'. Also give a single vivid "
        "sentence describing the album's visual style. Output only the concept — no preamble."
    ),
)


async def imagine_band(vibe: str) -> BandConcept:
    """Invent a band concept from a vibe. Cheap (one LLM call); no media spend."""
    prompt = vibe.strip() or "anything — surprise me with something distinctive"
    result = await band_agent.run(f"Vibe: {prompt}")
    return result.output


def _cover_prompt(concept: BandConcept, vibe: str) -> str:
    """Compose the image prompt from the concept's own art direction plus the vibe."""
    return (
        f"A single album cover for the band '{concept.band_name}'. "
        f"{concept.style_note} "
        f"Overall mood: {vibe.strip() or concept.band_name}. "
        "One cohesive full-bleed image filling the whole square frame — NOT split into "
        "panels, NOT stacked, no repeated or mirrored halves, no grid, no borders. "
        "High detail, no text or watermarks other than the band name."
    )


class Cover(BaseModel):
    """A generated album cover. `persisted` is False when we fell back to fal's URL."""

    url: str
    persisted: bool  # True = durable R2 link; False = temporary fal URL (expires ~1h)


async def generate_cover(concept: BandConcept, vibe: str) -> Cover:
    """Generate the album cover and return its URL.

    Spends fal.ai money — call this ONLY after the user confirms (the gate in main.py).
    Persisting to R2 gives a durable link; if that upload fails (e.g. R2 misconfigured),
    we keep the freshly-generated image by falling back to fal's *temporary* URL rather
    than throwing the result away. Raises RuntimeError only if no image was produced.
    """
    result = await media.text_to_image(  # no persist yet — we persist best-effort below
        _cover_prompt(concept, vibe), aspect_ratio=COVER_ASPECT_RATIO
    )
    if not result.files:
        raise RuntimeError("The image model returned no image.")
    file = result.files[0]
    try:
        durable = await media.persist_file(file, prefix=COVER_PREFIX)
        return Cover(url=durable.url, persisted=True)
    except Exception as error:  # storage down/misconfigured — keep the temp URL we have
        logger.warning("Couldn't persist cover to R2, using temporary fal URL: {}", error)
        return Cover(url=file.url, persisted=False)
