"""CLI entry point for skillforge."""

import typer

from skillforge.cli.build import build
from skillforge.cli.init import init
from skillforge.cli.publish import publish
from skillforge.cli.scan import scan
from skillforge.cli.validate import validate_cmd as validate

app = typer.Typer(help="skillforge — author, validate, build, and publish agent skills.")
app.command(name="scan")(scan)
app.command(name="init")(init)
app.command(name="validate")(validate)
app.command(name="build")(build)
app.command(name="publish")(publish)


def main() -> None:
    app()
