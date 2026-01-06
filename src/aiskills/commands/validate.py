"""Validate skill structure and content."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core.loader import LoadError, SkillLoader, get_loader
from ..core.parser import ParseError

console = Console()


def validate(
    path: Path = typer.Argument(
        Path("."),
        help="Path to skill directory to validate",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        "-s",
        help="Enable strict validation (warnings become errors)",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Only output errors, no success message",
    ),
) -> None:
    """Validate a skill's structure and SKILL.md content.

    Checks:
    - SKILL.md exists and has valid frontmatter
    - Required fields are present (name, description)
    - Optional directories are valid
    - No potentially sensitive files

    Examples:
        aiskills validate ./my-skill
        aiskills validate --strict ./my-skill
    """
    path = path.resolve()
    loader = get_loader()

    errors: list[str] = []
    warnings: list[str] = []

    # Check directory exists
    if not path.exists():
        console.print(f"[red]Error:[/red] Path does not exist: {path}")
        raise typer.Exit(1)

    if not path.is_dir():
        console.print(f"[red]Error:[/red] Path is not a directory: {path}")
        raise typer.Exit(1)

    # Structural validation
    structure_errors = loader.validate_structure(path)
    for err in structure_errors:
        if "Potentially sensitive" in err:
            warnings.append(err)
        else:
            errors.append(err)

    # Try to load the skill for deeper validation
    skill = None
    if not any("Missing SKILL.md" in e or "Invalid SKILL.md" in e for e in errors):
        try:
            skill = loader.load(path)
        except (LoadError, ParseError) as e:
            errors.append(str(e))

    # Validate skill content if loaded
    if skill:
        manifest = skill.manifest

        # Check description quality
        if len(manifest.description) < 20:
            warnings.append("Description is very short (< 20 chars)")

        if len(manifest.description) > 1000:
            warnings.append("Description is very long (> 1000 chars)")

        # Check for empty content
        if len(skill.content.strip()) < 50:
            warnings.append("Skill content is very short (< 50 chars)")

        # Check tags
        if not manifest.tags:
            warnings.append("No tags defined (helps with discovery)")

        # Check version format
        version_parts = manifest.version.split(".")
        if len(version_parts) != 3:
            warnings.append(f"Version '{manifest.version}' is not semantic (x.y.z)")

        # Check for composition without dependencies
        if manifest.extends and not manifest.dependencies:
            warnings.append(
                f"Skill extends '{manifest.extends}' but doesn't list it as dependency"
            )

        for include in manifest.includes:
            dep_names = [d.name for d in manifest.dependencies]
            if include not in dep_names:
                warnings.append(
                    f"Skill includes '{include}' but doesn't list it as dependency"
                )

        # Check variables have defaults
        for var_name, var in manifest.variables.items():
            if var.required and var.default is None:
                warnings.append(f"Variable '{var_name}' is required but has no default")

    # Output results
    if strict:
        errors.extend(warnings)
        warnings = []

    # Create result table
    has_issues = bool(errors) or bool(warnings)

    if has_issues:
        table = Table(title=f"Validation: {path.name}", show_header=True)
        table.add_column("Type", style="bold")
        table.add_column("Issue")

        for err in errors:
            table.add_row("[red]ERROR[/red]", err)
        for warn in warnings:
            table.add_row("[yellow]WARNING[/yellow]", warn)

        console.print(table)
        console.print()

    if errors:
        console.print(
            f"[red]Validation failed:[/red] {len(errors)} error(s)"
            + (f", {len(warnings)} warning(s)" if warnings else "")
        )
        raise typer.Exit(1)
    elif warnings:
        console.print(
            f"[yellow]Validation passed with {len(warnings)} warning(s)[/yellow]"
        )
    elif not quiet:
        console.print(
            Panel(
                f"[bold green]✓[/bold green] Skill [cyan]{path.name}[/cyan] is valid",
                border_style="green",
            )
        )

        if skill:
            console.print(f"\n[dim]Name:[/dim] {skill.manifest.name}")
            console.print(f"[dim]Version:[/dim] {skill.manifest.version}")
            console.print(f"[dim]Tags:[/dim] {', '.join(skill.manifest.tags) or 'none'}")
