"""MCP server command."""

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def serve() -> None:
    """Start the MCP server (stdio mode).

    The server communicates via stdin/stdout using the MCP protocol.
    This is typically used by MCP clients like Claude Desktop.

    Example claude_desktop_config.json:

        {
            "mcpServers": {
                "aiskills": {
                    "command": "aiskills",
                    "args": ["mcp", "serve"]
                }
            }
        }
    """
    try:
        from ..mcp.server import main as mcp_main
    except ImportError:
        console.print("[red]Error:[/red] MCP support not installed.")
        console.print("Install with: [cyan]pip install aiskills[mcp][/cyan]")
        raise typer.Exit(1)

    # Run the MCP server
    mcp_main()


@app.command()
def info() -> None:
    """Show MCP server information and configuration."""
    try:
        from ..mcp.tools import TOOL_DEFINITIONS
    except ImportError:
        console.print("[red]Error:[/red] MCP support not installed.")
        console.print("Install with: [cyan]pip install aiskills[mcp][/cyan]")
        raise typer.Exit(1)

    console.print("[bold]aiskills MCP Server[/bold]\n")

    console.print("[bold]Available Tools:[/bold]")
    for tool in TOOL_DEFINITIONS:
        console.print(f"\n  [cyan]{tool['name']}[/cyan]")
        console.print(f"    {tool['description'][:80]}...")

    console.print("\n[bold]Usage with Claude Desktop:[/bold]")
    console.print("Add to ~/Library/Application Support/Claude/claude_desktop_config.json:\n")

    config = '''{
    "mcpServers": {
        "aiskills": {
            "command": "aiskills",
            "args": ["mcp", "serve"]
        }
    }
}'''
    console.print(f"[dim]{config}[/dim]")


# Main entry point for direct command
def main() -> None:
    """Start the MCP server."""
    serve()
