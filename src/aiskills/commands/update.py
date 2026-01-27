"""Update installed skills to newer versions."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..core.manager import get_manager
from ..sources.registry import RegistryClient, get_registry_client
from ..storage.lockfile import LockFileManager
from ..storage.paths import get_path_resolver
from ..utils.version import SemanticVersion, is_newer

console = Console()


def update(
    names: Optional[list[str]] = typer.Argument(
        None,
        help="Specific skill names to update (default: all)",
    ),
    check_only: bool = typer.Option(
        False,
        "--check",
        "-c",
        help="Only check for updates, don't install",
    ),
    include_prerelease: bool = typer.Option(
        False,
        "--prerelease",
        "-p",
        help="Include prerelease versions",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts",
    ),
    global_only: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Only update globally installed skills",
    ),
) -> None:
    """Check for and install skill updates.

    By default, checks all installed skills against their sources.
    Use --check to see available updates without installing.

    Examples:
        aiskills update                    # Update all skills
        aiskills update --check            # Check for updates only
        aiskills update my-skill           # Update specific skill
        aiskills update -y                 # Update all without confirmation
    """
    manager = get_manager()
    paths = get_path_resolver()

    # Get installed skills
    with console.status("[bold]Checking installed skills...[/bold]"):
        installed = manager.list_installed(
            global_only=global_only,
            project_only=not global_only and not names,  # Project only if no names
        )

    if not installed:
        console.print("[yellow]No skills installed[/yellow]")
        raise typer.Exit(0)

    # Filter by names if specified
    if names:
        name_set = set(names)
        installed = [s for s in installed if s.manifest.name in name_set]
        if not installed:
            console.print(f"[yellow]Skills not found: {', '.join(names)}[/yellow]")
            raise typer.Exit(1)

    # Build installed versions dict
    installed_versions = {s.manifest.name: s.manifest.version for s in installed}

    # Check for updates using registry
    updates_available: dict[str, tuple[str, str, str]] = {}  # name -> (current, latest, source)

    with console.status("[bold]Checking for updates...[/bold]"):
        # Try registry first
        try:
            client = get_registry_client()
            registry_updates = client.check_updates(
                installed_versions,
                include_prerelease=include_prerelease,
            )
            for name, (current, latest) in registry_updates.items():
                updates_available[name] = (current, latest, "registry")
            client.close()
        except Exception:
            pass  # Registry not available

        # Also check lock file for source-specific updates
        lock_mgr = LockFileManager(paths)
        try:
            lock_mgr.load(global_install=global_only, create=False)
            for skill in installed:
                name = skill.manifest.name
                if name in updates_available:
                    continue  # Already have registry update

                locked = lock_mgr.get_locked_skill(name)
                if locked and locked.source.startswith("github:"):
                    # For GitHub sources, we'd need to check the repo
                    # This is a placeholder for future enhancement
                    pass
        except FileNotFoundError:
            pass

    if not updates_available:
        console.print("\n[green]✓ All skills are up to date[/green]")
        raise typer.Exit(0)

    # Display available updates
    console.print(f"\n[bold]Updates available ({len(updates_available)}):[/bold]\n")

    table = Table(show_header=True)
    table.add_column("Skill", style="cyan")
    table.add_column("Current", style="yellow")
    table.add_column("Latest", style="green")
    table.add_column("Source")

    for name, (current, latest, source) in sorted(updates_available.items()):
        # Parse versions to check severity
        try:
            curr_ver = SemanticVersion.parse(current)
            new_ver = SemanticVersion.parse(latest)

            if new_ver.major > curr_ver.major:
                severity = "[red]major[/red]"
            elif new_ver.minor > curr_ver.minor:
                severity = "[yellow]minor[/yellow]"
            else:
                severity = "[green]patch[/green]"

            latest_display = f"{latest} ({severity})"
        except ValueError:
            latest_display = latest

        table.add_row(name, current, latest_display, source)

    console.print(table)

    if check_only:
        console.print(
            f"\n[dim]Run 'aiskills update' to install these updates[/dim]"
        )
        raise typer.Exit(0)

    # Confirm update
    if not yes:
        if not Confirm.ask(f"\nUpdate {len(updates_available)} skill(s)?"):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # Install updates
    console.print()
    updated = 0
    errors = 0

    for name, (current, latest, source) in updates_available.items():
        try:
            with console.status(f"[bold]Updating {name}...[/bold]"):
                # Fetch from source
                if source == "registry":
                    from ..sources.resolver import get_source_resolver
                    resolver = get_source_resolver()
                    fetched = resolver.fetch(f"registry:{name}@{latest}")

                    if fetched:
                        skill, status = manager.install_from_path(
                            fetched[0].path,
                            global_install=global_only,
                            force=True,  # Force update
                        )
                        if status in ("installed", "updated"):
                            console.print(
                                f"  [green]✓[/green] Updated {name}: "
                                f"{current} → {latest}"
                            )
                            updated += 1
                        else:
                            console.print(
                                f"  [dim]=[/dim] {name} unchanged"
                            )
                else:
                    console.print(
                        f"  [yellow]![/yellow] {name}: "
                        f"Update from {source} not yet supported"
                    )

        except Exception as e:
            console.print(f"  [red]✗[/red] Failed to update {name}: {e}")
            errors += 1

    # Summary
    console.print()
    parts = []
    if updated:
        parts.append(f"[green]{updated} updated[/green]")
    if errors:
        parts.append(f"[red]{errors} failed[/red]")

    unchanged = len(updates_available) - updated - errors
    if unchanged:
        parts.append(f"[dim]{unchanged} unchanged[/dim]")

    console.print(
        Panel(
            " | ".join(parts),
            title="[bold]Update Complete[/bold]",
            border_style="green" if not errors else "yellow",
        )
    )

    if errors:
        raise typer.Exit(1)


def check(
    names: Optional[list[str]] = typer.Argument(
        None,
        help="Specific skill names to check (default: all)",
    ),
    include_prerelease: bool = typer.Option(
        False,
        "--prerelease",
        "-p",
        help="Include prerelease versions",
    ),
    global_only: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Only check globally installed skills",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON",
    ),
) -> None:
    """Check for available skill updates without installing.

    Alias for 'aiskills update --check'.
    """
    import json as json_module

    manager = get_manager()

    # Get installed skills
    installed = manager.list_installed(
        global_only=global_only,
        project_only=not global_only and not names,
    )

    if not installed:
        if json_output:
            console.print(json_module.dumps({"updates": [], "total": 0}))
        else:
            console.print("[yellow]No skills installed[/yellow]")
        raise typer.Exit(0)

    # Filter by names if specified
    if names:
        name_set = set(names)
        installed = [s for s in installed if s.manifest.name in name_set]

    # Build installed versions dict
    installed_versions = {s.manifest.name: s.manifest.version for s in installed}

    # Check registry for updates
    updates: list[dict] = []
    try:
        client = get_registry_client()
        registry_updates = client.check_updates(
            installed_versions,
            include_prerelease=include_prerelease,
        )
        for name, (current, latest) in registry_updates.items():
            updates.append({
                "name": name,
                "current_version": current,
                "latest_version": latest,
                "source": "registry",
            })
        client.close()
    except Exception as e:
        if not json_output:
            console.print(f"[yellow]Warning: Could not check registry: {e}[/yellow]")

    if json_output:
        console.print(json_module.dumps({
            "updates": updates,
            "total": len(updates),
        }, indent=2))
    else:
        if updates:
            console.print(f"\n[bold]{len(updates)} update(s) available[/bold]")
            for u in updates:
                console.print(
                    f"  • {u['name']}: {u['current_version']} → {u['latest_version']}"
                )
            console.print("\n[dim]Run 'aiskills update' to install[/dim]")
        else:
            console.print("[green]✓ All skills are up to date[/green]")
