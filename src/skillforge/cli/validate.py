"""`skillforge validate` command."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from skillforge.manager import SkillManager

console = Console()


def validate_cmd(
    path: str = typer.Argument(..., help="Path to a skill directory or repo root"),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Validate one or more skill manifests."""
    manager = SkillManager()
    target = Path(path)
    results = manager.validate(target)

    # If no results or SKILL.md doesn't exist, it's not a skill directory.
    if not results or not (target / "SKILL.md").exists():
        console.print(f"[red]Error:[/red] '{target}' is not a skill directory")
        raise typer.Exit(1)

    # If the only result has no validation (no SKILL.md parsed), report error.
    if len(results) == 1 and results[0][2] is None:
        console.print(f"[red]Error:[/red] '{target}' is not a skill directory")
        raise typer.Exit(1)

    if json_output:
        payload = _build_json(results, strict)
        console.print(json.dumps(payload, indent=2))
        raise typer.Exit(_exit_code(results, strict))

    table = Table(title="Validation Results")
    table.add_column("Skill")
    table.add_column("Errors")
    table.add_column("Warnings")
    table.add_column("Verdict")

    for skill_dir, manifest, validation in results:
        name = manifest.name if manifest else skill_dir.name
        errs = validation.errors if validation else []
        warns = validation.warnings if validation else []
        err_str = _fmt_items([e.message for e in errs])
        warn_str = _fmt_items([w.message for w in warns])

        if strict and warns:
            verdict = "[red]FAIL[/red]"
        elif errs:
            verdict = "[red]FAIL[/red]"
        elif warns:
            verdict = "[yellow]WARNINGS[/yellow]"
        else:
            verdict = "[green]PASS[/green]"

        table.add_row(name, err_str, warn_str, verdict)

    console.print(table)

    # Print details
    for _, _, validation in results:
        if validation is None:
            continue
        for e in validation.errors:
            console.print(f"  [red]ERROR[/red] [{e.field or '-'}] {e.message}")
        for w in validation.warnings:
            console.print(f"  [yellow]WARNING[/yellow] [{w.field or '-'}] {w.message}")

    raise typer.Exit(_exit_code(results, strict))


def _exit_code(results, strict: bool) -> int:
    for _, _, v in results:
        if v is None:
            continue
        if v.errors or (strict and v.warnings):
            return 1
        if v.warnings:
            return 2
    return 0


def _build_json(results, strict: bool) -> list:
    payload = []
    for skill_dir, manifest, validation in results:
        entry: dict = {"path": str(skill_dir)}
        if manifest:
            entry["name"] = manifest.name
            entry["version"] = manifest.version
        if validation:
            entry["valid"] = validation.valid and not (strict and validation.warnings)
            entry["errors"] = [
                {"field": e.field, "message": e.message} for e in validation.errors
            ]
            entry["warnings"] = [
                {"field": w.field, "message": w.message} for w in validation.warnings
            ]
        payload.append(entry)
    return payload


def _fmt_items(items: list[str]) -> str:
    if not items:
        return "[dim]—[/dim]"
    return "\n".join(items[:3]) + ("\n…" if len(items) > 3 else "")
