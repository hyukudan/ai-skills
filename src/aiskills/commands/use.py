"""Use command - find and use skills by natural language."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

app = typer.Typer()
console = Console()


@app.command()
def use(
    context: str = typer.Argument(
        ...,
        help="Natural language description of what you need",
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", help="Show raw output without formatting"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output as JSON"
    ),
) -> None:
    """Find and use the best matching skill for your task.

    Describe what you need in natural language, and this command will
    find and display the most relevant skill.

    Examples:
        aiskills use "debug python memory leak"
        aiskills use "write unit tests for flask"
        aiskills use "optimize SQL queries"
    """
    from ..core.router import get_router

    router = get_router()

    try:
        result = router.use(context=context)
    except Exception as e:
        error_msg = str(e)
        if "not installed" in error_msg.lower():
            console.print("[red]Error:[/red] Search requires extras.")
            console.print("Install with: [cyan]pip install aiskills[search][/cyan]")
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if not result.skill_name:
        console.print(f"[yellow]No matching skill found for:[/yellow] {context}")
        console.print("\n[dim]Try a different query or check installed skills with 'aiskills list'[/dim]")
        raise typer.Exit(1)

    if json_output:
        import json
        output = {
            "skill_name": result.skill_name,
            "score": result.score,
            "matched_query": result.matched_query,
            "content": result.content,
        }
        console.print(json.dumps(output, indent=2))
        return

    if raw:
        console.print(result.content)
        return

    # Rich formatted output
    score_str = f"{result.score:.0%}" if result.score else "N/A"
    
    console.print(f"\n[bold cyan]✓ Found:[/bold cyan] {result.skill_name} [dim](score: {score_str})[/dim]\n")
    
    # Render markdown content
    md = Markdown(result.content)
    console.print(md)


# Main entry point for direct command
def main(
    context: str = typer.Argument(
        ...,
        help="Natural language description of what you need",
    ),
    raw: bool = typer.Option(
        False, "--raw", "-r", help="Show raw output without formatting"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output as JSON"
    ),
) -> None:
    """Find and use the best matching skill."""
    use(context=context, raw=raw, json_output=json_output)
