"""Show detailed information about a skill."""

from __future__ import annotations

import json
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from ..core.manager import get_manager
from ..storage.lockfile import LockFileManager
from ..storage.paths import get_path_resolver
from ..utils.version import SemanticVersion

console = Console()


def info(
    name: str = typer.Argument(
        ...,
        help="Skill name to show info for",
    ),
    global_skill: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Look in global skills only",
    ),
    show_content: bool = typer.Option(
        False,
        "--content",
        "-c",
        help="Show full skill content",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON",
    ),
) -> None:
    """Show detailed information about an installed skill.

    Displays:
    - Manifest information (version, description, author)
    - Install source and status
    - Dependencies
    - Scope configuration
    - Resources available
    - Optionally, full content

    Examples:
        aiskills info my-skill
        aiskills info python-debugging --content
        aiskills info code-review --json
    """
    manager = get_manager()
    paths = get_path_resolver()

    # Get the skill
    skill = manager.get(name)
    if not skill:
        console.print(f"[red]Skill not found: {name}[/red]")
        console.print("\n[dim]Use 'aiskills list' to see installed skills.[/dim]")
        raise typer.Exit(1)

    # Get lock info if available
    lock_mgr = LockFileManager(paths)
    locked_skill = None
    try:
        lock_mgr.load(global_install=global_skill, create=False)
        locked_skill = lock_mgr.get_locked_skill(name)
    except FileNotFoundError:
        pass

    if json_output:
        # Build JSON output
        output = {
            "name": skill.manifest.name,
            "version": skill.manifest.version,
            "description": skill.manifest.description,
            "author": skill.manifest.author,
            "category": skill.manifest.category,
            "tags": skill.manifest.tags,
            "path": str(skill.path),
            "content_hash": skill.content_hash,
            "tokens_est": skill.tokens_est,
        }

        if skill.manifest.scope:
            output["scope"] = {
                "paths": skill.manifest.scope.paths,
                "languages": skill.manifest.scope.languages,
                "triggers": skill.manifest.scope.triggers,
            }

        if skill.manifest.dependencies:
            output["dependencies"] = skill.manifest.dependencies

        if locked_skill:
            output["install"] = {
                "source": locked_skill.source,
                "installed_at": locked_skill.installed_at,
                "resolved_dependencies": locked_skill.resolved_dependencies,
            }

        if skill.references:
            output["references"] = list(skill.references.keys())

        if show_content:
            output["content"] = skill.content

        console.print(json.dumps(output, indent=2))
        return

    # Rich output
    manifest = skill.manifest

    # Header
    console.print()
    console.print(f"[bold cyan]{manifest.name}[/bold cyan] v{manifest.version}")

    if manifest.description:
        console.print(f"[dim]{manifest.description}[/dim]")

    console.print()

    # Main info table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold")
    table.add_column("Value")

    if manifest.author:
        table.add_row("Author", manifest.author)

    if manifest.category:
        table.add_row("Category", manifest.category)

    if manifest.tags:
        table.add_row("Tags", ", ".join(manifest.tags))

    table.add_row("Path", str(skill.path))
    table.add_row("Hash", skill.content_hash[:16] + "...")
    table.add_row("Est. Tokens", str(skill.tokens_est))

    # Version info
    try:
        semver = SemanticVersion.parse(manifest.version)
        if semver.is_prerelease:
            table.add_row("Stability", "[yellow]Pre-release[/yellow]")
        elif semver.is_stable:
            table.add_row("Stability", "[green]Stable[/green]")
        else:
            table.add_row("Stability", "[dim]Development[/dim]")
    except ValueError:
        pass

    console.print(table)

    # Install info
    if locked_skill:
        console.print()
        console.print("[bold]Install Info[/bold]")

        install_table = Table(show_header=False, box=None, padding=(0, 2))
        install_table.add_column("Key", style="bold")
        install_table.add_column("Value")

        install_table.add_row("Source", locked_skill.source)

        from datetime import datetime
        installed_dt = datetime.fromtimestamp(locked_skill.installed_at)
        install_table.add_row("Installed", installed_dt.strftime("%Y-%m-%d %H:%M"))

        if locked_skill.resolved_dependencies:
            install_table.add_row(
                "Dependencies",
                ", ".join(locked_skill.resolved_dependencies),
            )

        console.print(install_table)

    # Scope configuration
    if manifest.scope:
        console.print()
        console.print("[bold]Scope[/bold]")

        scope_table = Table(show_header=False, box=None, padding=(0, 2))
        scope_table.add_column("Key", style="bold")
        scope_table.add_column("Value")

        if manifest.scope.paths:
            scope_table.add_row("Paths", ", ".join(manifest.scope.paths))
        if manifest.scope.languages:
            scope_table.add_row("Languages", ", ".join(manifest.scope.languages))
        if manifest.scope.triggers:
            scope_table.add_row("Triggers", ", ".join(manifest.scope.triggers))

        console.print(scope_table)

    # Dependencies
    if manifest.dependencies:
        console.print()
        console.print("[bold]Dependencies[/bold]")
        for dep in manifest.dependencies:
            console.print(f"  • {dep}")

    # Resources
    if skill.references:
        console.print()
        console.print("[bold]Resources[/bold]")
        for ref_name in skill.references.keys():
            console.print(f"  • {ref_name}")

    # Content (if requested)
    if show_content:
        console.print()
        console.print("[bold]Content[/bold]")
        console.print(Panel(
            Markdown(skill.content),
            title=f"SKILL.md",
            border_style="dim",
        ))

    console.print()
