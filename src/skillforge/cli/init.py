"""`skillforge init` command."""

from pathlib import Path

import typer
from rich.console import Console

from skillforge.manager import SkillManager

console = Console()


def init(
    name: str = typer.Argument(..., help="Skill name (lowercase, hyphens)"),
    path: str = typer.Option(".skills", "--path", help="Base directory for skills"),
    template: str = typer.Option("default", "--template", help="Template to use"),
) -> None:
    """Create a new skill directory with a scaffolded SKILL.md."""
    manager = SkillManager()
    try:
        created = manager.init_skill(name, Path(path), template)
        console.print(f"[green]Created skill at[/green] {created}")
    except FileExistsError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)
