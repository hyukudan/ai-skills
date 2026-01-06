"""API server command."""

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8420, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
) -> None:
    """Start the REST API server.

    The server provides HTTP endpoints for skill operations,
    compatible with any HTTP client including ChatGPT Custom GPTs,
    Gemini, and other LLM integrations.

    Examples:
        aiskills api serve
        aiskills api serve --port 3000
        aiskills api serve --host 127.0.0.1 --port 8080
    """
    try:
        from ..api.server import run_server
    except ImportError:
        console.print("[red]Error:[/red] API support not installed.")
        console.print("Install with: [cyan]pip install aiskills[api][/cyan]")
        raise typer.Exit(1)

    console.print(f"[bold]Starting aiskills API server[/bold]")
    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")
    console.print(f"  Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    console.print(f"  OpenAI tools: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/openai/tools")
    console.print()

    run_server(host=host, port=port, reload=reload)


@app.command()
def info() -> None:
    """Show API server information and endpoints."""
    console.print("[bold]aiskills REST API[/bold]\n")

    console.print("[bold]Endpoints:[/bold]")
    endpoints = [
        ("GET", "/", "API info"),
        ("GET", "/health", "Health check"),
        ("GET", "/skills", "List all skills"),
        ("GET", "/skills/{name}", "Get skill by name"),
        ("POST", "/skills/read", "Read skill with variables"),
        ("POST", "/skills/search", "Search skills"),
        ("POST", "/skills/suggest", "Suggest skills"),
        ("GET", "/openai/tools", "OpenAI-compatible tool definitions"),
        ("POST", "/openai/call", "Execute OpenAI function call"),
    ]

    for method, path, desc in endpoints:
        console.print(f"  [cyan]{method:6}[/cyan] {path:25} {desc}")

    console.print("\n[bold]Usage with ChatGPT Custom GPTs:[/bold]")
    console.print("1. Start the server: [cyan]aiskills api serve[/cyan]")
    console.print("2. Expose via ngrok or deploy to cloud")
    console.print("3. Get tool definitions from [cyan]/openai/tools[/cyan]")
    console.print("4. Configure Custom GPT with the tools")

    console.print("\n[bold]Usage with curl:[/bold]")
    console.print('[dim]curl http://localhost:8420/skills[/dim]')
    console.print('[dim]curl -X POST http://localhost:8420/skills/search -H "Content-Type: application/json" -d \'{"query": "debugging"}\'[/dim]')


# Main entry point for direct command
def main() -> None:
    """Start the API server."""
    serve()
