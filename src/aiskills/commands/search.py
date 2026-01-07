"""Search command - find skills semantically or by text."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ..core.registry import get_registry
from ..storage.paths import get_path_resolver

app = typer.Typer()
console = Console()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    text: bool = typer.Option(
        False, "--text", "-t", help="Use text search instead of semantic"
    ),
    hybrid: bool = typer.Option(
        False, "--hybrid", "-H", help="Use hybrid search (semantic + BM25)"
    ),
    tags: list[str] = typer.Option(
        None, "--tag", "-T", help="Filter by tags (can specify multiple)"
    ),
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum results"),
    min_score: float = typer.Option(
        0.0, "--min-score", help="Minimum similarity score (0-1)"
    ),
    sync: bool = typer.Option(
        False, "--sync", "-s", help="Sync registry before searching"
    ),
) -> None:
    """Search for skills by query.

    By default uses semantic search (requires search extras).
    Use --text for simple text matching.
    Use --hybrid for best accuracy (combines semantic + keyword matching).

    Examples:
        aiskills search "debug python"
        aiskills search "api testing" --tag testing
        aiskills search debug --text
        aiskills search "memory leak" --hybrid
        aiskills search "performance" --sync
    """
    registry = get_registry()

    # Sync registry if requested
    if sync:
        console.print("[dim]Syncing registry...[/dim]")
        try:
            from ..core.manager import get_manager

            manager = get_manager()
            count = registry.sync_from_manager(manager)
            console.print(f"[green]✓[/green] Indexed {count} skills")
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Sync failed: {e}")

    if text:
        # Text-based search
        results = registry.search_text(query, limit=limit)

        if not results:
            console.print(f"[yellow]No skills found matching '{query}'[/yellow]")
            return

        table = Table(title=f"Text Search: '{query}'")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="dim")
        table.add_column("Description")
        table.add_column("Tags", style="green")
        table.add_column("Source", style="dim")

        for skill_idx in results:
            tags_str = ", ".join(skill_idx.tags[:3])
            if len(skill_idx.tags) > 3:
                tags_str += f" (+{len(skill_idx.tags) - 3})"

            desc = skill_idx.description
            if len(desc) > 50:
                desc = desc[:47] + "..."

            table.add_row(
                skill_idx.name,
                skill_idx.version,
                desc,
                tags_str,
                skill_idx.source,
            )

        console.print(table)

    elif hybrid:
        # Hybrid search (semantic + BM25)
        try:
            results = registry.search_hybrid(
                query=query,
                limit=limit,
                tags=tags,
                category=category,
                min_score=min_score,
            )
        except Exception as e:
            error_msg = str(e)
            if "not installed" in error_msg.lower():
                console.print(
                    "[red]Error:[/red] Hybrid search requires search extras."
                )
                console.print("Install with: [cyan]pip install aiskills[search][/cyan]")
                console.print(
                    "\nAlternatively, use [cyan]--text[/cyan] for simple text search."
                )
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

        if not results:
            console.print(f"[yellow]No skills found matching '{query}'[/yellow]")
            if registry.count() == 0:
                console.print(
                    "[dim]Registry is empty. Run with --sync to index installed skills.[/dim]"
                )
            return

        table = Table(title=f"Hybrid Search: '{query}'")
        table.add_column("Score", style="yellow", width=6)
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="dim")
        table.add_column("Description")
        table.add_column("Tags", style="green")

        for skill_idx, score in results:
            tags_str = ", ".join(skill_idx.tags[:3])
            if len(skill_idx.tags) > 3:
                tags_str += f" (+{len(skill_idx.tags) - 3})"

            desc = skill_idx.description
            if len(desc) > 50:
                desc = desc[:47] + "..."

            score_str = f"{score:.0%}"

            table.add_row(
                score_str,
                skill_idx.name,
                skill_idx.version,
                desc,
                tags_str,
            )

        console.print(table)
        console.print(f"\n[dim]Found {len(results)} results (semantic + BM25)[/dim]")

    else:
        # Semantic search
        try:
            results = registry.search(
                query=query,
                limit=limit,
                tags=tags,
                category=category,
                min_score=min_score,
            )
        except Exception as e:
            error_msg = str(e)
            if "not installed" in error_msg.lower():
                console.print(
                    "[red]Error:[/red] Semantic search requires search extras."
                )
                console.print("Install with: [cyan]pip install aiskills[search][/cyan]")
                console.print(
                    "\nAlternatively, use [cyan]--text[/cyan] for simple text search."
                )
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

        if not results:
            console.print(f"[yellow]No skills found matching '{query}'[/yellow]")
            if registry.count() == 0:
                console.print(
                    "[dim]Registry is empty. Run with --sync to index installed skills.[/dim]"
                )
            return

        table = Table(title=f"Semantic Search: '{query}'")
        table.add_column("Score", style="yellow", width=6)
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="dim")
        table.add_column("Description")
        table.add_column("Tags", style="green")

        for skill_idx, score in results:
            tags_str = ", ".join(skill_idx.tags[:3])
            if len(skill_idx.tags) > 3:
                tags_str += f" (+{len(skill_idx.tags) - 3})"

            desc = skill_idx.description
            if len(desc) > 50:
                desc = desc[:47] + "..."

            # Format score as percentage
            score_str = f"{score:.0%}"

            table.add_row(
                score_str,
                skill_idx.name,
                skill_idx.version,
                desc,
                tags_str,
            )

        console.print(table)
        console.print(f"\n[dim]Found {len(results)} results[/dim]")


@app.command()
def index(
    rebuild: bool = typer.Option(
        False, "--rebuild", "-r", help="Rebuild entire index from scratch"
    ),
) -> None:
    """Index installed skills for semantic search.

    This command must be run before semantic search will work.
    It scans all installed skills and creates embeddings.

    Examples:
        aiskills search index
        aiskills search index --rebuild
    """
    from ..core.manager import get_manager

    console.print("[dim]Indexing skills for semantic search...[/dim]")

    try:
        registry = get_registry()
        manager = get_manager()

        if rebuild:
            console.print("[dim]Rebuilding index from scratch...[/dim]")

        count = registry.sync_from_manager(manager)
        console.print(f"[green]✓[/green] Indexed {count} skills")

        if count == 0:
            console.print(
                "[dim]No skills installed. Use 'aiskills install' to add skills.[/dim]"
            )
    except Exception as e:
        error_msg = str(e)
        if "not installed" in error_msg.lower():
            console.print("[red]Error:[/red] Indexing requires search extras.")
            console.print("Install with: [cyan]pip install aiskills[search][/cyan]")
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def stats() -> None:
    """Show search index statistics."""
    registry = get_registry()
    paths = get_path_resolver()

    console.print("[bold]Search Index Stats[/bold]\n")

    # Basic stats
    skill_count = registry.count()
    console.print(f"Indexed skills: [cyan]{skill_count}[/cyan]")

    # Registry location
    registry_dir = paths.get_registry_dir()
    console.print(f"Index location: [dim]{registry_dir}[/dim]")

    # Vector store stats (if available)
    try:
        store = registry._get_vector_store()
        vector_count = store.count()
        console.print(f"Vector count: [cyan]{vector_count}[/cyan]")
    except Exception:
        console.print("Vector store: [dim]not initialized[/dim]")

    # List indexed skills
    if skill_count > 0:
        console.print("\n[bold]Indexed Skills:[/bold]")
        for idx in registry.list_all():
            console.print(f"  • {idx.name} [dim]v{idx.version}[/dim]")


# Main entry point for direct command
def main(
    query: str = typer.Argument(..., help="Search query"),
    text: bool = typer.Option(
        False, "--text", "-t", help="Use text search instead of semantic"
    ),
    hybrid: bool = typer.Option(
        False, "--hybrid", "-H", help="Use hybrid search (semantic + BM25)"
    ),
    tags: list[str] = typer.Option(
        None, "--tag", "-T", help="Filter by tags (can specify multiple)"
    ),
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum results"),
    min_score: float = typer.Option(
        0.0, "--min-score", help="Minimum similarity score (0-1)"
    ),
    sync: bool = typer.Option(
        False, "--sync", "-s", help="Sync registry before searching"
    ),
) -> None:
    """Search for skills."""
    search(
        query=query,
        text=text,
        hybrid=hybrid,
        tags=tags,
        category=category,
        limit=limit,
        min_score=min_score,
        sync=sync,
    )
