"""`skillforge scan` command."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from skillforge.manager import SkillManager

console = Console()


def scan(
    path: str = typer.Argument(".", help="Directory to scan for skills"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Scan a directory tree for skill directories."""
    manager = SkillManager()
    results = manager.scan(Path(path))

    if json_output:
        payload = []
        for skill_dir, manifest, validation in results:
            entry: dict = {"path": str(skill_dir)}
            if manifest:
                entry["name"] = manifest.name
                entry["version"] = manifest.version
            if validation:
                entry["valid"] = validation.valid
                entry["errors"] = [e.message for e in validation.errors]
                entry["warnings"] = [w.message for w in validation.warnings]
            payload.append(entry)
        console.print(json.dumps(payload, indent=2))
        return

    if not results:
        console.print("[dim]No skills found.[/dim]")
        return

    table = Table(title="Discovered Skills")
    table.add_column("Path", style="cyan")
    table.add_column("Name")
    table.add_column("Version")
    table.add_column("Status")

    for skill_dir, manifest, validation in results:
        name = manifest.name if manifest else "—"
        version = manifest.version if manifest else "—"
        if validation is None:
            status = "[dim]unparseable[/dim]"
        elif validation.valid and not validation.warnings:
            status = "[green]valid[/green]"
        elif validation.valid:
            status = "[yellow]valid (warnings)[/yellow]"
        else:
            status = "[red]invalid[/red]"

        table.add_row(str(skill_dir), name, version, status)

    console.print(table)
