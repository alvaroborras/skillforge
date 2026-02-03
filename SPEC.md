# skillforge — Product Specification

## 1. Product Overview

`skillforge` is a CLI tool for authoring, validating, building, and publishing reusable agent skills. It provides a canonical format for skills (manifest + instructions), enforces structural integrity, and enables distribution to registries.

**Target users:** AI tooling developers, open-source maintainers, and teams building agent workflows who need consistent, versioned, testable skill artifacts.

## 2. Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      skillforge CLI                       │
│  scan │ init │ validate │ build │ publish                 │
├──────────────────────────────────────────────────────────┤
│                    SkillManager                          │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Scanner  │Validator │ Builder  │Publisher │ Templates    │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│                    Models (Pydantic)                      │
│  SkillManifest │ ValidationResult │ BuildArtifact        │
└──────────────────────────────────────────────────────────┘
```

### Design principles

- **Stateless CLI**: each command is self-contained; no daemon, no server.
- **Canonical format first**: every skill is a directory containing `SKILL.md` (markdown with YAML front matter) plus optional assets.
- **Validation is strict**: unknown fields, unreferenced assets, invalid tool names all produce errors.
- **Build is deterministic**: same input → same output archive.

## 3. Data Models

### SkillManifest (YAML front matter in SKILL.md)

```yaml
name: "my-skill"
description: "A brief description of what this skill does."
version: "1.0.0"
allowed_tools:
  - read
  - write
  - bash
asset_paths:
  - templates/
  - scripts/helper.py
skill_file: "SKILL.md"
```

### Pydantic models

```python
class SkillManifest(BaseModel):
    name: str
    description: str
    version: str  # semver
    allowed_tools: list[str] = []
    asset_paths: list[Path] = []
    skill_file: Path = Path("SKILL.md")


class ValidationResult(BaseModel):
    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]


class ValidationError(BaseModel):
    field: str | None
    message: str
    path: Path | None


class BuildArtifact(BaseModel):
    manifest: SkillManifest
    archive_path: Path
    checksum: str
    size_bytes: int
```

## 4. CLI Contract

### `skillforge scan [PATH]`

Scans a directory tree for skill directories (any folder containing a `SKILL.md` file). Outputs a table of discovered skills with their name, version, and validation status.

- **Input**: optional path (defaults to `.`)
- **Output**: Rich table to stdout
- **Exit code**: 0 (always, even if no skills found)
- **Options**: `--json` for machine-readable output

### `skillforge init [NAME]`

Creates a new skill directory with a scaffolded `SKILL.md` and optional asset structure.

- **Input**: skill name (required)
- **Output**: created directory with `SKILL.md`
- **Exit code**: 0 on success, 1 if the directory already exists
- **Options**: `--path DIR` (defaults to `.skills/`), `--template TYPE`

### `skillforge validate [PATH]`

Validates one or more skill manifests against the canonical schema and checks that referenced assets and tools exist.

- **Input**: path to a skill directory or a directory containing skills
- **Output**: validation report (errors and warnings) to stdout
- **Exit code**: 0 if valid, 1 if errors found, 2 if warnings only
- **Options**: `--strict` (treat warnings as errors), `--json`

### `skillforge build [PATH]`

Builds a distributable package (`.tar.gz` or `.zip`) from a skill directory.

- **Input**: path to a skill directory
- **Output**: archive at `dist/<name>-<version>.tar.gz`
- **Exit code**: 0 on success, 1 on validation failure, 2 on build failure
- **Options**: `--format tar.gz|zip` (default `tar.gz`), `--output DIR`

### `skillforge publish [PATH]`

Publishes a built skill package to a registry.

- **Input**: path to a skill directory or built archive
- **Output**: confirmation message with registry URL
- **Exit code**: 0 on success, 1 on failure
- **Options**: `--registry URL`, `--dry-run`

## 5. Directory Convention

Skills live in a `.skills/` directory at the repo root (configurable). Each skill is a subdirectory:

```
.skills/
  my-skill/
    SKILL.md          # Manifest (YAML front matter) + instructions (markdown body)
    templates/
      example.py.j2
    scripts/
      helper.py
  another-skill/
    SKILL.md
```

## 6. Acceptance Criteria

### Phase 1: Core CLI (scan, init, validate)

- [ ] `skillforge scan .` discovers all skill directories and prints a table
- [ ] `skillforge init my-skill` creates `.skills/my-skill/SKILL.md` with valid YAML front matter
- [ ] `skillforge validate .skills/my-skill` reports errors for missing name, invalid version, unreferenced assets
- [ ] `skillforge validate .skills/my-skill` reports warnings for unknown YAML keys (non-strict mode)
- [ ] Exit codes are correct: 0=valid, 1=errors, 2=warnings only
- [ ] `--json` flag produces valid JSON output for scan and validate

### Phase 2: Build and publish

- [ ] `skillforge build .skills/my-skill` creates `dist/my-skill-1.0.0.tar.gz`
- [ ] Build fails with clear error if validation fails
- [ ] Built archive contains `SKILL.md` and all declared assets
- [ ] Archive is bit-for-bit deterministic for same input
- [ ] `skillforge publish .skills/my-skill --dry-run` prints what would be published

### Phase 3: CI integration

- [ ] GitHub Action template checks skill drift on PR
- [ ] `skillforge validate --strict` is suitable for CI gates
- [ ] Documentation covers CI setup

## 7. Error Handling

| Scenario | Behavior |
|----------|----------|
| No `SKILL.md` found | `scan` shows empty table; `validate` errors with "not a skill directory" |
| Invalid YAML front matter | `validate` reports parse error with line number |
| Asset path references non-existent file | `validate` error |
| Tool name not in known registry | `validate` warning (non-strict), error (strict) |
| Version not valid semver | `validate` error |
| `init` target already exists | Error exit code 1, message to stderr |
| Build archive fails (disk full, permissions) | Exit code 2, message to stderr |

## 8. Testing Strategy

- **Unit tests**: each Pydantic model, validator rule, scanner logic
- **Integration tests**: CLI commands run against fixture `.skills/` directories (valid skills, invalid skills, edge cases)
- **End-to-end**: `init` → `validate` → `build` → `publish --dry-run` pipeline
- Fixture directories: `tests/fixtures/valid-skill/`, `tests/fixtures/invalid-skill/`, `tests/fixtures/multi-skill-repo/`

## 9. Phased Task Breakdown

| Phase | Tasks | Deliverable |
|-------|-------|-------------|
| 1 | `models.py`, `scanner.py`, `cli/scan.py`, `cli/init.py`, `cli/validate.py`, `templates/init/`, `tests/` | `scan`, `init`, `validate` work end-to-end |
| 2 | `builder.py`, `cli/build.py`, `publisher.py`, `cli/publish.py` | `build` and `publish` work |
| 3 | `.github/workflows/skill-check.yml`, `docs/` | CI template and documentation |
