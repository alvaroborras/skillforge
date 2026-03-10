"""`skillforge build` command."""

from pathlib import Path

import typer
from rich.console import Console

from skillforge.builder import BuildError
from skillforge.manager import SkillManager

console = Console()


def build(
    path: str = typer.Argument(..., help="Path to skill directory"),
    fmt: str = typer.Option("tar.gz", "--format", help="Archive format: tar.gz or zip"),
    output: str = typer.Option("dist", "--output", help="Output directory"),
) -> None:
    """Build a distributable archive from a skill directory."""
    manager = SkillManager()
    try:
        artifact = manager.build(Path(path), Path(output), fmt)
    except BuildError as exc:
        console.print(f"[red]Build failed:[/red] {exc}")
        raise typer.Exit(2)

    console.print(f"[green]Built[/green] {artifact.archive_path}")
    console.print(f"  Size:  {artifact.size_bytes:,} bytes")
    console.print(f"  SHA256: {artifact.checksum}")
