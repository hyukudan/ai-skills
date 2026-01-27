"""Publish skills to a remote registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from ..core.loader import get_loader
from ..sources.registry import RegistryClient, get_registry_client

console = Console()


def publish(
    path: str = typer.Argument(
        ".",
        help="Path to skill directory (default: current directory)",
    ),
    registry_url: Optional[str] = typer.Option(
        None,
        "--registry",
        "-r",
        help="Registry URL (default: from AISKILLS_REGISTRY_URL or built-in)",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--key",
        "-k",
        help="API key for authentication (or set AISKILLS_REGISTRY_KEY)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Validate but don't actually publish",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts",
    ),
) -> None:
    """Publish a skill to a remote registry.

    The skill must have a valid SKILL.md with complete metadata.
    You'll need an API key to publish (set via --key or AISKILLS_REGISTRY_KEY).

    Before publishing:
    1. Ensure SKILL.md has all required fields (name, version, description)
    2. Validate with 'aiskills validate'
    3. Test locally with 'aiskills use'

    Examples:
        aiskills publish ./my-skill
        aiskills publish . --dry-run
        aiskills publish --registry https://my-registry.com
    """
    loader = get_loader()

    # Resolve path
    skill_path = Path(path).resolve()

    if not skill_path.exists():
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    # Load and validate skill
    with console.status("[bold]Validating skill...[/bold]"):
        try:
            skill = loader.load(skill_path, source="local")
        except Exception as e:
            console.print(f"[red]Failed to load skill: {e}[/red]")
            raise typer.Exit(1)

    manifest = skill.manifest

    # Check required fields
    errors = []
    if not manifest.name:
        errors.append("Missing required field: name")
    if not manifest.version:
        errors.append("Missing required field: version")
    if not manifest.description:
        errors.append("Missing required field: description")

    if errors:
        console.print("[red]Validation errors:[/red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)

    # Show what will be published
    console.print()
    console.print("[bold]Skill to publish:[/bold]")
    console.print()

    info_lines = [
        f"[bold cyan]Name:[/bold cyan] {manifest.name}",
        f"[bold cyan]Version:[/bold cyan] {manifest.version}",
        f"[bold cyan]Description:[/bold cyan] {manifest.description[:100]}{'...' if len(manifest.description) > 100 else ''}",
    ]

    if manifest.author:
        info_lines.append(f"[bold cyan]Author:[/bold cyan] {manifest.author}")
    if manifest.category:
        info_lines.append(f"[bold cyan]Category:[/bold cyan] {manifest.category}")
    if manifest.tags:
        info_lines.append(f"[bold cyan]Tags:[/bold cyan] {', '.join(manifest.tags)}")

    info_lines.append(f"[bold cyan]Path:[/bold cyan] {skill_path}")
    info_lines.append(f"[bold cyan]Content Hash:[/bold cyan] {skill.content_hash[:16]}...")
    info_lines.append(f"[bold cyan]Est. Tokens:[/bold cyan] {skill.tokens_est}")

    console.print(Panel(
        "\n".join(info_lines),
        title="[bold]Skill Metadata[/bold]",
        border_style="cyan",
    ))

    if dry_run:
        console.print("\n[yellow]Dry run - skill not published[/yellow]")
        console.print("[green]✓ Skill is valid and ready to publish[/green]")
        raise typer.Exit(0)

    # Confirm publication
    if not yes:
        console.print()
        if not Confirm.ask("Publish this skill to the registry?"):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # Initialize registry client
    try:
        client = RegistryClient(
            base_url=registry_url,
            api_key=api_key,
        )
    except Exception as e:
        console.print(f"[red]Failed to connect to registry: {e}[/red]")
        raise typer.Exit(1)

    # Publish
    console.print()
    with console.status("[bold]Publishing skill...[/bold]"):
        try:
            # Package skill for upload
            import io
            import zipfile

            # Create zip in memory
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add SKILL.md
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    zf.write(skill_md, "SKILL.md")

                # Add any other files (resources, scripts, etc.)
                for item in skill_path.rglob("*"):
                    if item.is_file() and item.name != "SKILL.md":
                        # Exclude hidden files and __pycache__
                        if not any(p.startswith(".") for p in item.parts) and "__pycache__" not in item.parts:
                            arcname = item.relative_to(skill_path)
                            zf.write(item, arcname)

            buffer.seek(0)
            zip_data = buffer.getvalue()

            # Upload to registry
            http_client = client._get_client()
            response = http_client.post(
                f"{client.base_url}/api/skills/publish",
                headers=client._headers(),
                files={"file": (f"{manifest.name}.zip", zip_data, "application/zip")},
                data={
                    "name": manifest.name,
                    "version": manifest.version,
                    "description": manifest.description,
                    "category": manifest.category or "",
                    "tags": json.dumps(manifest.tags or []),
                    "author": manifest.author or "",
                },
            )

            response.raise_for_status()
            result = response.json()

        except Exception as e:
            console.print(f"[red]Failed to publish: {e}[/red]")
            client.close()
            raise typer.Exit(1)

    client.close()

    # Success
    console.print(Panel(
        f"[green]✓ Published {manifest.name} v{manifest.version}[/green]\n\n"
        f"Install with: [bold]aiskills install {manifest.name}[/bold]",
        title="[bold green]Success[/bold green]",
        border_style="green",
    ))


def unpublish(
    name: str = typer.Argument(
        ...,
        help="Skill name to unpublish",
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="Specific version to unpublish (default: all versions)",
    ),
    registry_url: Optional[str] = typer.Option(
        None,
        "--registry",
        "-r",
        help="Registry URL",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--key",
        "-k",
        help="API key for authentication",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts",
    ),
) -> None:
    """Unpublish a skill from the registry.

    This removes the skill from the public registry.
    Requires authentication as the skill owner.

    Examples:
        aiskills unpublish my-skill
        aiskills unpublish my-skill --version 1.0.0
    """
    # Confirm
    if not yes:
        msg = f"Unpublish {name}"
        if version:
            msg += f" v{version}"
        msg += " from the registry?"

        if not Confirm.ask(msg):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # Initialize client
    try:
        client = RegistryClient(
            base_url=registry_url,
            api_key=api_key,
        )
    except Exception as e:
        console.print(f"[red]Failed to connect to registry: {e}[/red]")
        raise typer.Exit(1)

    # Unpublish
    with console.status(f"[bold]Unpublishing {name}...[/bold]"):
        try:
            http_client = client._get_client()
            endpoint = f"/api/skills/{name}"
            if version:
                endpoint += f"/versions/{version}"

            response = http_client.delete(
                f"{client.base_url}{endpoint}",
                headers=client._headers(),
            )
            response.raise_for_status()

        except Exception as e:
            console.print(f"[red]Failed to unpublish: {e}[/red]")
            client.close()
            raise typer.Exit(1)

    client.close()

    if version:
        console.print(f"[green]✓ Unpublished {name} v{version}[/green]")
    else:
        console.print(f"[green]✓ Unpublished {name} (all versions)[/green]")
