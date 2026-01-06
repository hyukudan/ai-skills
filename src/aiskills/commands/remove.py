"""Remove installed skills."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm

from ..core.manager import get_manager

console = Console()


def remove(
    name: str = typer.Argument(
        ...,
        help="Name of skill to remove",
    ),
    global_only: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Only remove from global location",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation",
    ),
) -> None:
    """Remove an installed skill.

    By default, removes from the first location found (project before global).
    Use --global to only remove from global location.

    Examples:
        aiskills remove my-skill
        aiskills remove my-skill --global
        aiskills remove my-skill -y
    """
    manager = get_manager()

    # Check if skill exists
    skill = manager.get(name)
    if skill is None:
        console.print(f"[red]Error:[/red] Skill '{name}' not found")
        raise typer.Exit(1)

    # Show what will be removed
    console.print(f"\n[bold]Skill:[/bold] {skill.manifest.name}")
    console.print(f"[dim]Version:[/dim] {skill.manifest.version}")
    console.print(f"[dim]Location:[/dim] {skill.path}")

    # Confirm
    if not yes:
        if not Confirm.ask(f"\nRemove skill '{name}'?"):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # Remove
    if manager.remove(name, global_only=global_only):
        console.print(f"\n[green]✓[/green] Removed {name}")
    else:
        console.print(f"\n[red]Error:[/red] Failed to remove {name}")
        raise typer.Exit(1)
