"""Browse skills with metadata only (Progressive Disclosure Phase 1)."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def browse(
    context: Optional[str] = typer.Argument(
        None,
        help="Optional query for semantic filtering",
    ),
    paths: Optional[str] = typer.Option(
        None,
        "--paths",
        "-p",
        help="Comma-separated file paths for scope matching",
    ),
    languages: Optional[str] = typer.Option(
        None,
        "--lang",
        "-l",
        help="Comma-separated languages for scope matching",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Maximum number of results",
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
        help="Show more details (scope, priority)",
    ),
) -> None:
    """Browse skills with metadata only (Phase 1 of Progressive Disclosure).

    Returns lightweight metadata without loading full content.
    Use this to discover relevant skills before loading them.

    Examples:
        aiskills browse                       # List all skills
        aiskills browse "debug python"        # Semantic search
        aiskills browse --paths "src/**/*.py" # Scope by paths
        aiskills browse --lang python,rust    # Scope by language
        aiskills browse --json                # JSON output
    """
    from ..core.router import get_router

    router = get_router()

    # Parse comma-separated values
    active_paths = paths.split(",") if paths else None
    lang_list = languages.split(",") if languages else None

    # Get browse results
    try:
        results = router.browse(
            context=context,
            active_paths=active_paths,
            languages=lang_list,
            limit=limit,
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    if json_output:
        import json

        output = [
            {
                "name": r.name,
                "description": r.description,
                "version": r.version,
                "tags": r.tags,
                "category": r.category,
                "tokens_est": r.tokens_est,
                "priority": r.priority,
                "precedence": r.precedence,
                "source": r.source,
                "scope": {
                    "paths": r.scope_paths,
                    "languages": r.scope_languages,
                    "triggers": r.scope_triggers,
                },
                "has_variables": r.has_variables,
                "has_dependencies": r.has_dependencies,
            }
            for r in results
        ]
        console.print(json.dumps(output, indent=2))
        return

    if not results:
        console.print("[dim]No skills found[/dim]")
        if context:
            console.print(f"[dim]Query: {context}[/dim]")
        return

    # Create table
    title = f"Skills ({len(results)})"
    if context:
        title += f" matching '{context}'"

    table = Table(title=title, show_header=True, header_style="bold")

    table.add_column("Name", style="cyan")
    table.add_column("Version", style="dim")
    table.add_column("Description")
    table.add_column("Tokens", style="dim", justify="right")

    if verbose:
        table.add_column("Priority", style="dim", justify="right")
        table.add_column("Scope", style="dim")

    for skill in results:
        # Truncate description
        desc = skill.description
        if len(desc) > 40:
            desc = desc[:37] + "..."

        tokens = str(skill.tokens_est) if skill.tokens_est else "-"

        row = [skill.name, skill.version, desc, tokens]

        if verbose:
            row.append(str(skill.priority))

            # Build scope summary
            scope_parts = []
            if skill.scope_languages:
                scope_parts.append(f"lang:{','.join(skill.scope_languages[:2])}")
            if skill.scope_paths:
                scope_parts.append(f"paths:{len(skill.scope_paths)}")
            if skill.scope_triggers:
                scope_parts.append(f"triggers:{len(skill.scope_triggers)}")

            row.append(" ".join(scope_parts) if scope_parts else "-")

        table.add_row(*row)

    console.print(table)

    # Summary
    total_tokens = sum(r.tokens_est or 0 for r in results)
    console.print()
    console.print(f"[dim]Total estimated tokens: {total_tokens}[/dim]")
    console.print("[dim]Use 'aiskills use <name>' to load full content[/dim]")
