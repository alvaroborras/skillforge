"""`skillforge publish` command."""

from pathlib import Path

import typer
from rich.console import Console

from skillforge.manager import SkillManager
from skillforge.publisher import PublishError

console = Console()


def publish(
    path: str = typer.Argument(..., help="Path to skill directory or archive"),
    registry: str = typer.Option(
        "https://registry.dotskills.dev", "--registry", help="Registry URL"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate publication"),
) -> None:
    """Publish a skill to a registry."""
    manager = SkillManager()
    try:
        result = manager.publish(Path(path), registry, dry_run)
    except PublishError as exc:
        console.print(f"[red]Publish failed:[/red] {exc}")
        raise typer.Exit(1)

    console.print(result["message"])
    if "url" in result:
        console.print(f"  URL: {result['url']}")
