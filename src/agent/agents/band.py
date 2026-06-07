"""The vibe → band agent.

Two atomic pieces (see docs/architecture.md):
  - `imagine_band(vibe)` — cheap LLM call; invents the concept. Runs every time.
  - `generate_cover(concept, vibe)` — costs fal.ai money; gated behind user confirmation
    in main.py. (Added in the next step.)

This file holds only the *first* piece for now, so the text half can be tested for free
before any spend is wired in.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from agent.services import media
from agent.services.llm import build_model

TRACK_COUNT = 10
COVER_PREFIX = "bandnamer"  # namespaces our files in the shared R2 bucket


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
        f"Album cover art for the band '{concept.band_name}'. "
        f"{concept.style_note} "
        f"Overall mood: {vibe.strip() or concept.band_name}. "
        "Square, high detail, no extra text or watermarks beyond the band name."
    )


async def generate_cover(concept: BandConcept, vibe: str) -> str:
    """Generate the album cover and return a durable (R2-persisted) URL.

    Spends fal.ai money — call this ONLY after the user confirms (the gate in main.py).
    Raises RuntimeError if the model returns no image so the caller can fail honestly.
    """
    result = await media.text_to_image(
        _cover_prompt(concept, vibe), persist=True, prefix=COVER_PREFIX
    )
    if not result.files:
        raise RuntimeError("The image model returned no image.")
    return result.files[0].url
