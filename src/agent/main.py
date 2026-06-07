"""Entry point — the vibe → band CLI.

Run it:

    uv run agent "rainy 3am synthwave for driving through an empty city"
    uv run agent           # prompts you for a vibe

Flow (see docs/policy.md): read a vibe → invent the band + 10-song tracklist (cheap) →
show it → ask before generating the album cover (the only step that spends money).
"""

import asyncio
import sys

from loguru import logger
from rich.console import Console
from rich.panel import Panel

from agent.agents.band import BandConcept, generate_cover, imagine_band
from agent.logging_setup import setup_logging

console = Console()


def _read_vibe() -> str:
    """Vibe from the command line if given, else an interactive prompt."""
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return console.input("[bold]Describe a vibe:[/] ")


def _show_concept(concept: BandConcept) -> None:
    tracklist = "\n".join(f"  {i:2}. {t}" for i, t in enumerate(concept.tracklist, 1))
    body = f"[dim italic]{concept.style_note}[/]\n\n{tracklist}"
    console.print(Panel(body, title=f"🎸 [bold]{concept.band_name}[/]", expand=False))


def _wants_cover() -> bool:
    """The money gate: default No, so an accidental Enter never spends."""
    answer = console.input("\nGenerate the album cover? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


async def _run() -> None:
    vibe = _read_vibe()
    logger.info("Imagining a band for vibe: {!r}", vibe)
    concept = await imagine_band(vibe)
    _show_concept(concept)

    if not _wants_cover():
        console.print("[dim]Skipped the cover — no fal.ai spend. 👋[/]")
        return

    console.print("[dim]Generating cover…[/]")
    try:
        cover = await generate_cover(concept, vibe)
    except Exception as error:  # fal down/slow/empty — fail honestly, keep the concept
        logger.error("Cover generation failed: {}", error)
        console.print(f"[red]Couldn't generate the cover:[/] {error}")
        console.print("[dim]Your band and tracklist above still stand.[/]")
        return
    console.print(f"🖼  [bold]Album cover:[/] {cover.url}")
    if not cover.persisted:
        console.print("[yellow]Note: this is a temporary link (expires ~1h) — R2 save failed.[/]")


def main() -> None:
    """Entry point for `uv run agent`."""
    setup_logging()
    asyncio.run(_run())


if __name__ == "__main__":
    main()
