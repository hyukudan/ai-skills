"""Install skills from various sources."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..core.loader import get_loader
from ..core.manager import SkillManager, get_manager
from ..core.registry import get_registry
from ..sources.base import FetchError
from ..sources.resolver import SourceResolver, get_source_resolver
from ..storage.lockfile import LockFileManager
from ..storage.paths import get_path_resolver

console = Console()


def install(
    source: str = typer.Argument(
        ...,
        help="Source: local path, git URL, or owner/repo",
    ),
    global_install: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Install globally (~/.aiskills/skills/)",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force overwrite without hash check",
    ),
    select: Optional[str] = typer.Option(
        None,
        "--select",
        "-s",
        help="Install only specific skills (comma-separated names)",
    ),
) -> None:
    """Install skills from a source.

    Sources can be:
    - Local path: ./my-skill, /path/to/skills
    - Git URL: https://github.com/owner/repo.git
    - GitHub shorthand: owner/repo, owner/repo/skill-name

    Examples:
        aiskills install ./my-skill
        aiskills install owner/repo
        aiskills install owner/repo/specific-skill
        aiskills install https://github.com/owner/repo.git --global
    """
    resolver = get_source_resolver()
    manager = get_manager()
    loader = get_loader()

    # Fetch skills from source
    with console.status(f"[bold]Fetching from {source}...[/bold]"):
        try:
            fetched = resolver.fetch(source)
        except FetchError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if not fetched:
        console.print("[yellow]No skills found at source[/yellow]")
        raise typer.Exit(0)

    # Filter if --select provided
    if select:
        selected_names = {n.strip() for n in select.split(",")}
        fetched = [s for s in fetched if s.name in selected_names]

        if not fetched:
            console.print(f"[yellow]No skills matching: {select}[/yellow]")
            raise typer.Exit(0)

    # Show skills to install
    console.print(f"\n[bold]Found {len(fetched)} skill(s):[/bold]\n")

    table = Table(show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Status")
    table.add_column("Action")

    skills_to_install: list[tuple[Path, str, str]] = []  # (path, source_str, status)

    for skill_info in fetched:
        try:
            # Load to validate and check existing
            skill = loader.load(skill_info.path, source="cache")
            existing = manager.get(skill.manifest.name)

            if existing:
                if existing.content_hash == skill.content_hash:
                    status = "[dim]identical[/dim]"
                    action = "[dim]skip[/dim]"
                else:
                    status = f"[yellow]v{existing.manifest.version} → v{skill.manifest.version}[/yellow]"
                    action = "[yellow]update[/yellow]"
                    skills_to_install.append(
                        (skill_info.path, skill_info.source_string, "update")
                    )
            else:
                status = f"[green]v{skill.manifest.version}[/green]"
                action = "[green]install[/green]"
                skills_to_install.append(
                    (skill_info.path, skill_info.source_string, "install")
                )

            table.add_row(skill.manifest.name, status, action)

        except Exception as e:
            table.add_row(skill_info.name, f"[red]error[/red]", f"[red]{e}[/red]")

    console.print(table)

    if not skills_to_install:
        console.print("\n[dim]Nothing to install (all skills up to date)[/dim]")
        raise typer.Exit(0)

    # Confirm
    if not yes:
        install_count = sum(1 for _, _, s in skills_to_install if s == "install")
        update_count = sum(1 for _, _, s in skills_to_install if s == "update")

        msg_parts = []
        if install_count:
            msg_parts.append(f"{install_count} new")
        if update_count:
            msg_parts.append(f"{update_count} update")

        location = "globally" if global_install else "in project"
        if not Confirm.ask(
            f"\nInstall {' + '.join(msg_parts)} {location}?"
        ):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # Install
    console.print()
    installed = 0
    updated = 0
    errors = 0

    for skill_path, source_str, expected_status in skills_to_install:
        try:
            skill, status = manager.install_from_path(
                skill_path,
                global_install=global_install,
                force=force,
            )

            if status == "installed":
                console.print(f"  [green]✓[/green] Installed {skill.manifest.name}")
                installed += 1
            elif status == "updated":
                console.print(f"  [yellow]↑[/yellow] Updated {skill.manifest.name}")
                updated += 1
            else:
                console.print(f"  [dim]=[/dim] Unchanged {skill.manifest.name}")

        except Exception as e:
            console.print(f"  [red]✗[/red] Failed: {e}")
            errors += 1

    # Rebuild search index if any skills were installed
    if installed + updated > 0:
        try:
            registry = get_registry()
            count = registry.sync_from_manager(manager)
            console.print(f"\n  [green]✓[/green] Search index updated ({count} skills)")
        except Exception:
            # Silently skip if search extras not installed
            pass

    # Summary
    console.print()
    parts = []
    if installed:
        parts.append(f"[green]{installed} installed[/green]")
    if updated:
        parts.append(f"[yellow]{updated} updated[/yellow]")
    if errors:
        parts.append(f"[red]{errors} failed[/red]")

    location = "~/.aiskills" if global_install else "./.aiskills"
    console.print(
        Panel(
            f"{' | '.join(parts)}\n[dim]Location: {location}/skills/[/dim]",
            title="[bold]Installation Complete[/bold]",
            border_style="green" if not errors else "yellow",
        )
    )

    if errors:
        raise typer.Exit(1)
