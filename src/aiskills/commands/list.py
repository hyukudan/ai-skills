"""List installed skills."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..core.loader import SkillLoader, get_loader
from ..models.skill import SkillIndex
from ..storage.paths import PathResolver, get_path_resolver

console = Console()


def list_skills(
    global_only: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Only show globally installed skills",
    ),
    project_only: bool = typer.Option(
        False,
        "--project",
        "-p",
        help="Only show project-level skills",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output as JSON",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show more details",
    ),
) -> None:
    """List all installed skills.

    Shows skills from both project and global locations,
    with project skills taking priority.

    Examples:
        aiskills list
        aiskills list --global
        aiskills list --json
    """
    paths = get_path_resolver()
    loader = get_loader()

    # Collect skills from all locations
    skills: list[tuple[SkillIndex, str]] = []  # (index, location_display)
    seen_names: set[str] = set()

    search_dirs = paths.get_search_dirs()

    for skills_dir, location_type in search_dirs:
        # Determine if this is project or global
        is_global = str(skills_dir).startswith(str(paths.global_base))

        if global_only and not is_global:
            continue
        if project_only and is_global:
            continue

        # Find skills in this directory
        skill_dirs = loader.list_skill_dirs(skills_dir)

        for skill_dir in skill_dirs:
            try:
                skill = loader.load(
                    skill_dir,
                    source="global" if is_global else "project",
                    location_type=location_type,
                )

                # Skip duplicates (first one wins due to priority order)
                if skill.manifest.name in seen_names:
                    continue
                seen_names.add(skill.manifest.name)

                # Create display location
                if is_global:
                    loc_display = f"~/.aiskills"
                else:
                    loc_display = f"./{location_type}"

                skills.append((skill.to_index(), loc_display))

            except Exception as e:
                if verbose:
                    console.print(f"[dim]Skipping {skill_dir}: {e}[/dim]")

    # Sort by name
    skills.sort(key=lambda x: x[0].name)

    # Output
    if json_output:
        import json

        output = [
            {
                "name": s.name,
                "version": s.version,
                "description": s.description,
                "tags": s.tags,
                "location": loc,
                "path": s.path,
            }
            for s, loc in skills
        ]
        console.print(json.dumps(output, indent=2))
        return

    if not skills:
        console.print("[dim]No skills installed[/dim]")
        console.print("\n[bold]To get started:[/bold]")
        console.print("  aiskills init my-skill      # Create a new skill")
        console.print("  aiskills install owner/repo # Install from GitHub")
        return

    # Create table
    table = Table(
        title=f"Installed Skills ({len(skills)})",
        show_header=True,
        header_style="bold",
    )

    table.add_column("Name", style="cyan")
    table.add_column("Version", style="dim")
    table.add_column("Description")
    table.add_column("Location", style="dim")

    if verbose:
        table.add_column("Tags", style="dim")

    for skill, location in skills:
        # Truncate description
        desc = skill.description
        if len(desc) > 50:
            desc = desc[:47] + "..."

        row = [
            skill.name,
            skill.version,
            desc,
            location,
        ]

        if verbose:
            row.append(", ".join(skill.tags) if skill.tags else "-")

        table.add_row(*row)

    console.print(table)

    # Summary
    project_count = sum(1 for _, loc in skills if not loc.startswith("~"))
    global_count = len(skills) - project_count

    console.print()
    console.print(
        f"[dim]Project: {project_count} | Global: {global_count}[/dim]"
    )
