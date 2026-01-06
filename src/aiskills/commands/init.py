"""Initialize a new skill."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from ..constants import ASSETS_DIR, REFERENCES_DIR, SCRIPTS_DIR, SKILL_FILE

console = Console()

# Default SKILL.md template
SKILL_TEMPLATE = '''---
name: {name}
description: |
  {description}
version: 1.0.0
tags: [{tags}]
category: {category}

# Uncomment to add dependencies
# dependencies:
#   - name: base-skill
#     version: ">=1.0.0"

# Uncomment to add variables
# variables:
#   language:
#     type: string
#     default: python
#     enum: [python, javascript, rust]
---

# {title}

## When to Use

Load this skill when:
- [Describe primary use case]
- [Describe secondary use case]

## Instructions

[Write clear, imperative instructions for the AI agent]

1. First, [do something]
2. Then, [do something else]
3. Finally, [complete the task]

## Best Practices

- [Best practice 1]
- [Best practice 2]

## References

See `references/` for detailed documentation.

## Scripts

Run scripts in `scripts/` for automation.
'''


def init(
    name: Optional[str] = typer.Argument(
        None,
        help="Skill name (will create directory with this name)",
    ),
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help="Parent directory to create skill in",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        "-i/-I",
        help="Interactive mode with prompts",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Skill description",
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        "-t",
        help="Comma-separated tags",
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        "-c",
        help="Skill category (e.g., development/debugging)",
    ),
    with_refs: bool = typer.Option(
        True,
        "--refs/--no-refs",
        help="Create references/ directory",
    ),
    with_scripts: bool = typer.Option(
        True,
        "--scripts/--no-scripts",
        help="Create scripts/ directory",
    ),
    with_assets: bool = typer.Option(
        False,
        "--assets/--no-assets",
        help="Create assets/ directory",
    ),
) -> None:
    """Initialize a new skill with template files.

    Creates a new skill directory with SKILL.md and optional subdirectories.

    Examples:
        aiskills init my-skill
        aiskills init debugging-python --tags "python,debugging"
        aiskills init -p ./skills my-custom-skill
    """
    # Interactive prompts if not provided
    if interactive:
        if not name:
            name = Prompt.ask(
                "[bold]Skill name[/bold]",
                default="my-skill",
            )

        if not description:
            description = Prompt.ask(
                "[bold]Description[/bold]",
                default="A useful skill for AI agents",
            )

        if not tags:
            tags = Prompt.ask(
                "[bold]Tags[/bold] (comma-separated)",
                default="",
            )

        if not category:
            category = Prompt.ask(
                "[bold]Category[/bold] (e.g., development/debugging)",
                default="general",
            )
    else:
        # Use defaults for non-interactive
        name = name or "my-skill"
        description = description or "A useful skill for AI agents"
        tags = tags or ""
        category = category or "general"

    # Validate name
    if not name:
        console.print("[red]Error:[/red] Skill name is required")
        raise typer.Exit(1)

    # Clean up name (lowercase, hyphenated)
    clean_name = name.lower().replace(" ", "-").replace("_", "-")
    if clean_name != name:
        console.print(f"[dim]Using normalized name: {clean_name}[/dim]")
        name = clean_name

    # Create skill directory
    skill_dir = path / name
    if skill_dir.exists():
        if interactive and not Confirm.ask(
            f"[yellow]Directory '{skill_dir}' exists. Overwrite?[/yellow]"
        ):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    skill_dir.mkdir(parents=True, exist_ok=True)

    # Create SKILL.md
    title = name.replace("-", " ").title()
    content = SKILL_TEMPLATE.format(
        name=name,
        description=description,
        tags=tags,
        category=category,
        title=title,
    )

    skill_file = skill_dir / SKILL_FILE
    skill_file.write_text(content)

    # Create optional directories
    created_dirs = []
    if with_refs:
        refs_dir = skill_dir / REFERENCES_DIR
        refs_dir.mkdir(exist_ok=True)
        (refs_dir / ".gitkeep").touch()
        created_dirs.append(REFERENCES_DIR)

    if with_scripts:
        scripts_dir = skill_dir / SCRIPTS_DIR
        scripts_dir.mkdir(exist_ok=True)
        (scripts_dir / ".gitkeep").touch()
        created_dirs.append(SCRIPTS_DIR)

    if with_assets:
        assets_dir = skill_dir / ASSETS_DIR
        assets_dir.mkdir(exist_ok=True)
        (assets_dir / ".gitkeep").touch()
        created_dirs.append(ASSETS_DIR)

    # Success output
    console.print()
    console.print(
        Panel(
            f"[bold green]Created skill:[/bold green] {name}\n\n"
            f"[dim]Location:[/dim] {skill_dir.absolute()}\n"
            f"[dim]Files:[/dim] {SKILL_FILE}"
            + (f", {', '.join(created_dirs)}/" if created_dirs else ""),
            title="[bold]Skill Created[/bold]",
            border_style="green",
        )
    )

    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  1. Edit [cyan]{skill_dir / SKILL_FILE}[/cyan]")
    console.print(f"  2. Add references to [cyan]{skill_dir / REFERENCES_DIR}/[/cyan]")
    console.print(f"  3. Validate with [cyan]aiskills validate {skill_dir}[/cyan]")
