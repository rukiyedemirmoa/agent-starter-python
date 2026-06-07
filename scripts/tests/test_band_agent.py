"""Tests for the band agent.

- UNIT: the concept constructs and the exactly-10-songs rule is enforced (offline).
- INTEGRATION: a real vibe yields a valid concept (marked `integration`, needs a key).

  uv run pytest scripts/tests/test_band_agent.py                 # unit only
  uv run pytest -m integration scripts/tests/test_band_agent.py  # live
"""

import pytest
from pydantic import ValidationError

# NOTE: unlike the smoke test, we do NOT set a fake key here — a fake env var would
# override the real one in .env and make the integration test below silently skip.
# Agent construction in the unit tests relies on the real key being present in .env.


def _llm_ready() -> bool:
    from agent.config import get_settings

    try:
        return bool(get_settings().openrouter_api_key)
    except Exception:
        return False


requires_llm = pytest.mark.skipif(not _llm_ready(), reason="OPENROUTER_API_KEY not set")


# --- unit: the typed contract (no network) ----------------------------------


def test_agent_and_concept_construct() -> None:
    from pydantic_ai import Agent

    from agent.agents.band import TRACK_COUNT, BandConcept, band_agent

    assert isinstance(band_agent, Agent)
    concept = BandConcept(
        band_name="Neon Curfew",
        tracklist=[f"Track {i}" for i in range(TRACK_COUNT)],
        style_note="Rain-slicked neon over an empty freeway.",
    )
    assert len(concept.tracklist) == TRACK_COUNT


@pytest.mark.parametrize("n", [9, 11, 0])
def test_tracklist_must_be_exactly_ten(n: int) -> None:
    from agent.agents.band import BandConcept

    with pytest.raises(ValidationError):
        BandConcept(
            band_name="Wrong Count",
            tracklist=[f"Track {i}" for i in range(n)],
            style_note="n/a",
        )


# --- integration: a real concept from a real vibe ---------------------------


@pytest.mark.integration
@requires_llm
async def test_imagine_band_returns_valid_concept() -> None:
    from agent.agents.band import TRACK_COUNT, imagine_band

    concept = await imagine_band("rainy 3am synthwave for driving through an empty city")
    assert concept.band_name.strip()
    assert len(concept.tracklist) == TRACK_COUNT
    assert all(title.strip() for title in concept.tracklist)
    assert concept.style_note.strip()
