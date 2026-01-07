"""CLI commands for testing LLM integrations."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="Test LLM integrations")
console = Console()


@app.command(name="status")
def status() -> None:
    """Check which LLM integrations are available."""
    table = Table(title="LLM Integration Status")
    table.add_column("Provider", style="cyan")
    table.add_column("Package", style="dim")
    table.add_column("Status", style="green")

    # Check OpenAI
    try:
        import openai
        table.add_row("OpenAI", "openai", "✅ Installed")
    except ImportError:
        table.add_row("OpenAI", "openai", "❌ Not installed")

    # Check Gemini
    try:
        import google.generativeai
        table.add_row("Gemini", "google-generativeai", "✅ Installed")
    except ImportError:
        table.add_row("Gemini", "google-generativeai", "❌ Not installed")

    # Check Anthropic
    try:
        import anthropic
        table.add_row("Anthropic", "anthropic", "✅ Installed")
    except ImportError:
        table.add_row("Anthropic", "anthropic", "❌ Not installed")

    # Check Ollama
    try:
        import ollama
        table.add_row("Ollama", "ollama", "✅ Installed")
    except ImportError:
        table.add_row("Ollama", "ollama", "❌ Not installed")

    console.print(table)
    console.print("\n[dim]Install with: pip install aiskills[openai|anthropic|gemini|ollama|llms][/dim]")


@app.command(name="openai")
def test_openai(
    message: str = typer.Argument(
        "What skills do you have?",
        help="Message to send"
    ),
    model: str = typer.Option("gpt-3.5-turbo", "--model", "-m", help="Model to use"),
) -> None:
    """Test OpenAI integration."""
    try:
        from ..integrations.openai import create_openai_client
    except ImportError:
        console.print("[red]OpenAI not installed. Run: pip install aiskills[openai][/red]")
        raise typer.Exit(1)

    import os
    if "OPENAI_API_KEY" not in os.environ:
        console.print("[red]OPENAI_API_KEY not set[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Testing OpenAI ({model})...[/cyan]\n")

    with console.status("Sending message..."):
        try:
            client = create_openai_client(model=model)
            response = client.chat(message)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    console.print(Panel(response, title="Response", border_style="green"))


@app.command(name="gemini")
def test_gemini(
    message: str = typer.Argument(
        "What skills do you have?",
        help="Message to send"
    ),
    model: str = typer.Option("gemini-1.5-flash", "--model", "-m", help="Model to use"),
) -> None:
    """Test Gemini integration."""
    try:
        from ..integrations.gemini import create_gemini_client
    except ImportError:
        console.print("[red]Gemini not installed. Run: pip install aiskills[gemini][/red]")
        raise typer.Exit(1)

    import os
    if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in os.environ:
        console.print("[red]GEMINI_API_KEY or GOOGLE_API_KEY not set[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Testing Gemini ({model})...[/cyan]\n")

    with console.status("Sending message..."):
        try:
            client = create_gemini_client(model_name=model)
            response = client.chat(message)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    console.print(Panel(response, title="Response", border_style="green"))


@app.command(name="anthropic")
def test_anthropic(
    message: str = typer.Argument(
        "What skills do you have?",
        help="Message to send"
    ),
    model: str = typer.Option("claude-sonnet-4-20250514", "--model", "-m", help="Model to use"),
) -> None:
    """Test Anthropic Claude integration."""
    try:
        from ..integrations.anthropic import create_anthropic_client
    except ImportError:
        console.print("[red]Anthropic not installed. Run: pip install aiskills[anthropic][/red]")
        raise typer.Exit(1)

    import os
    if "ANTHROPIC_API_KEY" not in os.environ:
        console.print("[red]ANTHROPIC_API_KEY not set[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Testing Anthropic Claude ({model})...[/cyan]\n")

    with console.status("Sending message..."):
        try:
            client = create_anthropic_client(model=model)
            response = client.chat(message)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    console.print(Panel(response, title="Response", border_style="green"))


@app.command(name="ollama")
def test_ollama(
    message: str = typer.Argument(
        "What skills do you have?",
        help="Message to send"
    ),
    model: str = typer.Option("llama3.1", "--model", "-m", help="Model to use"),
    no_tools: bool = typer.Option(False, "--no-tools", help="Disable tool calling"),
) -> None:
    """Test Ollama integration."""
    try:
        from ..integrations.ollama import create_ollama_client
    except ImportError:
        console.print("[red]Ollama not installed. Run: pip install aiskills[ollama][/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Testing Ollama ({model})...[/cyan]\n")

    with console.status("Connecting to Ollama..."):
        try:
            client = create_ollama_client(model=model, use_tools=not no_tools)

            if not client.is_model_available():
                console.print(f"[yellow]Model '{model}' not found locally.[/yellow]")
                console.print(f"[dim]Run: ollama pull {model}[/dim]")
                raise typer.Exit(1)

        except Exception as e:
            if "connection" in str(e).lower():
                console.print("[red]Cannot connect to Ollama. Is it running?[/red]")
                console.print("[dim]Run: ollama serve[/dim]")
            else:
                console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    with console.status("Sending message..."):
        try:
            response = client.chat(message)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    console.print(Panel(response, title="Response", border_style="green"))


@app.command(name="list-models")
def list_ollama_models() -> None:
    """List available Ollama models."""
    try:
        from ..integrations.ollama import create_ollama_client
    except ImportError:
        console.print("[red]Ollama not installed. Run: pip install aiskills[ollama][/red]")
        raise typer.Exit(1)

    try:
        client = create_ollama_client()
        models = client.list_local_models()
    except Exception as e:
        if "connection" in str(e).lower():
            console.print("[red]Cannot connect to Ollama. Is it running?[/red]")
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    if not models:
        console.print("[yellow]No models installed.[/yellow]")
        console.print("[dim]Run: ollama pull llama3.1[/dim]")
        return

    table = Table(title="Ollama Models")
    table.add_column("Name", style="cyan")
    table.add_column("Size", style="dim")
    table.add_column("Modified", style="dim")

    for model in models:
        name = model.get("name", "unknown")
        size = model.get("size", 0)
        size_str = f"{size / 1e9:.1f}GB" if size > 1e9 else f"{size / 1e6:.0f}MB"
        modified = model.get("modified_at", "")[:10] if model.get("modified_at") else ""
        table.add_row(name, size_str, modified)

    console.print(table)


@app.command(name="tools")
def show_tools(
    provider: str = typer.Argument(
        "openai",
        help="Provider format: openai, anthropic, gemini, ollama"
    ),
) -> None:
    """Show tool definitions for a provider."""
    if provider == "openai":
        from ..integrations.openai import get_openai_tools
        tools = get_openai_tools()
    elif provider == "anthropic":
        from ..integrations.anthropic import get_anthropic_tools
        tools = get_anthropic_tools()
    elif provider == "ollama":
        from ..integrations.ollama import get_ollama_tools
        tools = get_ollama_tools()
    elif provider == "gemini":
        from ..integrations.gemini import get_gemini_tools
        tools = get_gemini_tools()
        # Gemini tools are functions, show their names
        console.print("[cyan]Gemini Tools (Python functions):[/cyan]\n")
        for tool in tools:
            console.print(f"  • [green]{tool.__name__}[/green]")
            doc = tool.__doc__ or ""
            first_line = doc.split("\n")[0].strip()
            console.print(f"    {first_line}\n")
        return
    else:
        console.print(f"[red]Unknown provider: {provider}[/red]")
        console.print("[dim]Options: openai, anthropic, gemini, ollama[/dim]")
        raise typer.Exit(1)

    # Show tool definitions
    console.print(f"[cyan]{provider.title()} Tools:[/cyan]\n")
    for tool in tools:
        # Handle both OpenAI format (nested under "function") and Anthropic format (flat)
        if "function" in tool:
            func = tool.get("function", {})
            name = func.get("name", "unknown")
            desc = func.get("description", "")[:80]
            params = list(func.get("parameters", {}).get("properties", {}).keys())
        else:
            name = tool.get("name", "unknown")
            desc = tool.get("description", "")[:80]
            params = list(tool.get("input_schema", {}).get("properties", {}).keys())

        console.print(f"  • [green]{name}[/green]")
        console.print(f"    {desc}...")
        console.print(f"    Parameters: {params}\n")
