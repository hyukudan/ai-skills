"""Show skill variables command."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ..core.loader import LoadError
from ..core.manager import get_manager

console = Console()


def vars(
    name: str = typer.Argument(
        ...,
        help="Name of skill to show variables for",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output as JSON",
    ),
) -> None:
    """Show a skill's available variables and their options.

    Displays all variables defined by a skill, including:
    - Variable name and type
    - Allowed values (enum) if restricted
    - Default value
    - Description

    This helps you understand what customization options are available
    when using a skill with the --var flag.

    Examples:
        aiskills vars python-debugging
        aiskills vars code-review --json
    """
    manager = get_manager()

    # Get skill
    try:
        skill = manager.get(name)
    except LoadError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        raise typer.Exit(1)

    if skill is None:
        console.print(f"[red]Error:[/red] Skill '{name}' not found", stderr=True)
        raise typer.Exit(1)

    var_defs = skill.manifest.variables

    if not var_defs:
        console.print(f"[dim]Skill '{name}' has no variables defined[/dim]")
        return

    if json_output:
        import json

        output = {}
        for var_name, var_meta in var_defs.items():
            output[var_name] = {
                "type": var_meta.type,
                "description": var_meta.description,
                "default": var_meta.default,
                "required": var_meta.required,
            }
            if var_meta.enum:
                output[var_name]["enum"] = var_meta.enum
            if var_meta.min is not None:
                output[var_name]["min"] = var_meta.min
            if var_meta.max is not None:
                output[var_name]["max"] = var_meta.max
        print(json.dumps(output, indent=2))
        return

    # Rich table output
    table = Table(
        title=f"Variables for [cyan]{name}[/cyan]",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Variable", style="cyan", no_wrap=True)
    table.add_column("Type", style="dim")
    table.add_column("Options / Range", style="green")
    table.add_column("Default", style="yellow")
    table.add_column("Description")

    for var_name, var_meta in var_defs.items():
        # Format options/range
        options = ""
        if var_meta.enum:
            options = " | ".join(str(v) for v in var_meta.enum)
        elif var_meta.min is not None or var_meta.max is not None:
            min_val = var_meta.min if var_meta.min is not None else "∞"
            max_val = var_meta.max if var_meta.max is not None else "∞"
            options = f"{min_val} → {max_val}"

        # Format default
        default = str(var_meta.default) if var_meta.default is not None else "-"
        if len(default) > 20:
            default = default[:17] + "..."

        # Required marker
        var_display = var_name
        if var_meta.required:
            var_display = f"{var_name} [red]*[/red]"

        table.add_row(
            var_display,
            var_meta.type,
            options or "-",
            default,
            var_meta.description or "-",
        )

    console.print(table)

    # Usage hint
    console.print()
    console.print("[dim]Usage: aiskills read", name, "--var", "variable=value[/dim]")
