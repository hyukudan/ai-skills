"""Read skill content for agent consumption."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..core.loader import LoadError
from ..core.manager import get_manager

console = Console()


def parse_variables(var_list: list[str] | None) -> dict:
    """Parse variable assignments from command line.

    Accepts formats:
    - key=value
    - key:value
    """
    if not var_list:
        return {}

    variables = {}
    for item in var_list:
        if "=" in item:
            key, value = item.split("=", 1)
        elif ":" in item:
            key, value = item.split(":", 1)
        else:
            continue

        # Try to parse as JSON for complex types
        key = key.strip()
        value = value.strip()

        # Simple type coercion
        if value.lower() == "true":
            variables[key] = True
        elif value.lower() == "false":
            variables[key] = False
        elif value.isdigit():
            variables[key] = int(value)
        else:
            try:
                variables[key] = float(value)
            except ValueError:
                variables[key] = value

    return variables


def read(
    name: str = typer.Argument(
        ...,
        help="Name of skill to read",
    ),
    var: Optional[list[str]] = typer.Option(
        None,
        "--var",
        "-V",
        help="Variable assignment (key=value). Can be repeated.",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Output raw SKILL.md content without formatting",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Minimal output (just content, no headers)",
    ),
    no_compose: bool = typer.Option(
        False,
        "--no-compose",
        help="Don't resolve extends/includes",
    ),
    show_vars: bool = typer.Option(
        False,
        "--show-vars",
        help="Show skill's variable definitions and exit",
    ),
) -> None:
    """Read a skill's content for agent consumption.

    Outputs the skill content in a format suitable for AI agents.
    Use this command in agent prompts to load skill instructions.

    Variables can be passed to customize the skill output:
        aiskills read my-skill --var language=python --var debug=true

    Examples:
        aiskills read python-debugging
        aiskills read my-skill --var language=rust
        aiskills read my-skill --raw
        $(aiskills read my-skill -q)  # In shell scripts
    """
    manager = get_manager()

    # Get skill first
    try:
        skill = manager.get(name)
    except LoadError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        raise typer.Exit(1)

    if skill is None:
        console.print(f"[red]Error:[/red] Skill '{name}' not found", stderr=True)
        raise typer.Exit(1)

    # Show variables mode
    if show_vars:
        var_defs = manager.get_skill_variables(name)
        if not var_defs:
            console.print(f"[dim]Skill '{name}' has no variables defined[/dim]")
            return

        table = Table(title=f"Variables for {name}")
        table.add_column("Name", style="cyan")
        table.add_column("Type")
        table.add_column("Default")
        table.add_column("Required")
        table.add_column("Description")

        for var_name, meta in var_defs.items():
            default = str(meta.get("default", "-"))
            if len(default) > 20:
                default = default[:17] + "..."

            table.add_row(
                var_name,
                meta.get("type", "string"),
                default,
                "✓" if meta.get("required") else "",
                meta.get("description") or "-",
            )

        console.print(table)
        return

    # Parse variables
    variables = parse_variables(var)

    if raw:
        # Output raw SKILL.md content
        print(skill.raw_content)
    elif quiet:
        # Just the content, rendered if variables provided
        if variables or skill.manifest.has_variables:
            output = manager.read(name, variables=variables, resolve_composition=not no_compose)
            # Strip the header lines
            lines = output.split("\n")
            # Skip first 3 lines (header, base dir, empty line)
            print("\n".join(lines[3:]))
        else:
            print(skill.content)
    else:
        # Formatted output for agents
        output = manager.read(name, variables=variables, resolve_composition=not no_compose)
        print(output)
