# skillforge Documentation

## Quickstart

```bash
# Install
pip install skillforge

# Create a new skill
skillforge init my-skill

# Validate
skillforge validate .skills/my-skill

# Build
skillforge build .skills/my-skill

# Publish (dry-run)
skillforge publish .skills/my-skill --dry-run
```

## CLI Reference

### `skillforge scan [PATH]`

Scans a directory tree for skill directories. Outputs a table with name, version, and validation status.

Options:
- `--json` — machine-readable JSON output

### `skillforge init NAME`

Creates a new skill directory with a scaffolded `SKILL.md`.

Options:
- `--path DIR` — base directory for skills (default: `.skills`)
- `--template TYPE` — template to use (default: `default`)

### `skillforge validate PATH`

Validates skill manifests. Reports errors and warnings.

Options:
- `--strict` — treat warnings as errors
- `--json` — machine-readable JSON output

Exit codes:
- `0` — all valid
- `1` — errors found
- `2` — warnings only (non-strict mode)

### `skillforge build PATH`

Builds a distributable archive from a skill directory.

Options:
- `--format tar.gz|zip` — archive format (default: `tar.gz`)
- `--output DIR` — output directory (default: `dist`)

### `skillforge publish PATH`

Publishes a skill to a registry.

Options:
- `--registry URL` — registry endpoint
- `--dry-run` — simulate without publishing

## Skill Format

Every skill is a directory containing a `SKILL.md` file with YAML front matter:

```yaml
---
name: "my-skill"
description: "What this skill does."
version: "1.0.0"
allowed_tools:
  - read
  - write
asset_paths:
  - templates/
  - scripts/helper.py
---

# Instructions

The body of SKILL.md contains the skill instructions.
```

## Directory Convention

```
.skills/
  my-skill/
    SKILL.md
    templates/
      example.py.j2
    scripts/
      helper.py
```
