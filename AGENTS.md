# Agent Instructions — skillforge

## Project overview

`skillforge` is a CLI for creating, managing, and publishing reusable agent skills tied to the `dotskills` ecosystem. It provides the tooling to author, validate, build, and distribute skills in a canonical format.

**Tech stack:** Python 3.12+, uv, Typer, Rich, Pydantic, PyYAML, Jinja2, pytest.

## Common commands

- Install dependencies: `uv sync`
- Run tests: `uv run pytest`
- Run linting: `uv run ruff check .`
- Run formatting: `uv run ruff format .`
- Run type checking: `uv run mypy src`
- Build package: `uv build`
- Run the CLI locally: `uv run skillforge --help`

## Development rules

- Keep changes small and test-driven. Add or update tests for behavior changes.
- Data models live in `src/skillforge/models.py`. CLI commands live in `src/skillforge/cli/`.
- Prefer editing existing modules over introducing new abstractions unless the change clearly reduces complexity.
- All skill operations read/write through the `SkillManager` class in `src/skillforge/manager.py`.
- Do not read `.env`, `.env.*`, `secrets/`, or credential files.
- Commit messages should be concise and describe the "what" and "why", not the "how".

## Repository map

- `src/skillforge/` — package source
  - `cli/` — Typer CLI commands (`scan.py`, `init.py`, `build.py`, `validate.py`, `publish.py`)
  - `models.py` — Pydantic data models (SkillManifest, ValidationResult, BuildArtifact)
  - `manager.py` — `SkillManager` orchestrator
  - `scanner.py` — filesystem scanner for existing skills
  - `validator.py` — structural and semantic validation
  - `builder.py` — package builder
  - `publisher.py` — publishing to registries
  - `templates/` — Jinja2 templates for `init` scaffolding
- `tests/` — pytest suite
- `docs/` — user-facing documentation
