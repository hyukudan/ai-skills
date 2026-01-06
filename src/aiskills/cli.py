"""CLI entry point for aiskills."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__

# Create main app
app = typer.Typer(
    name="aiskills",
    help="Universal LLM-agnostic skills system",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Console for rich output
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"aiskills version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """aiskills - Universal AI Skills System.

    Manage, discover, and use skills across any LLM agent.
    """
    pass


# Import and register commands
from .commands import init as init_cmd
from .commands import install as install_cmd
from .commands import list as list_cmd
from .commands import read as read_cmd
from .commands import remove as remove_cmd
from .commands import search as search_cmd
from .commands import sync as sync_cmd
from .commands import use as use_cmd
from .commands import validate as validate_cmd

app.command(name="init")(init_cmd.init)
app.command(name="install")(install_cmd.install)
app.command(name="list")(list_cmd.list_skills)
app.command(name="read")(read_cmd.read)
app.command(name="remove")(remove_cmd.remove)
app.command(name="use")(use_cmd.main)
app.command(name="validate")(validate_cmd.validate)
app.command(name="search")(search_cmd.main)
app.command(name="sync")(sync_cmd.sync)

# Search subcommands (index, stats)
app.add_typer(search_cmd.app, name="search-index", help="Manage search index")

# MCP server commands
from .commands import mcp as mcp_cmd
app.add_typer(mcp_cmd.app, name="mcp", help="MCP server commands")

# API server commands
from .commands import api as api_cmd
app.add_typer(api_cmd.app, name="api", help="REST API server commands")


# Quick aliases for common operations
@app.command(name="ls")
def ls(
    global_only: bool = typer.Option(False, "--global", "-g", help="Only show global skills"),
) -> None:
    """Alias for 'list' command."""
    list_cmd.list_skills(global_only=global_only)


if __name__ == "__main__":
    app()
