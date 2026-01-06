"""Sync command - sync AGENTS.md with installed skills."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def sync(
    output: Path = typer.Option(
        Path("AGENTS.md"),
        "--output",
        "-o",
        help="Output path for AGENTS.md",
    ),
    include_global: bool = typer.Option(
        True, "--global/--no-global", help="Include global skills"
    ),
    include_project: bool = typer.Option(
        True, "--project/--no-project", help="Include project skills"
    ),
    categories: list[str] = typer.Option(
        None, "--category", "-c", help="Filter by category"
    ),
) -> None:
    """Generate/update AGENTS.md from installed skills.

    AGENTS.md provides structured instructions for AI agents
    working with this project. It lists all available skills
    with their descriptions, usage context, and variables.

    Examples:
        aiskills sync
        aiskills sync -o docs/AGENTS.md
        aiskills sync --no-global
        aiskills sync -c development -c testing
    """
    from ..integrations.agents_md import generate_agents_md

    console.print(f"[dim]Generating {output}...[/dim]")

    try:
        content = generate_agents_md(
            include_global=include_global,
            include_project=include_project,
            categories=categories,
            output_path=output,
        )

        # Count skills
        skill_count = content.count("### ") - 2  # Subtract section headers
        if skill_count < 0:
            skill_count = 0

        console.print(f"[green]✓[/green] Generated {output} with {skill_count} skills")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
