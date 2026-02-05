"""Pydantic data models for skillforge."""

import re
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

ALLOWED_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_RE = re.compile(
    r"^\d+\.\d+\.\d+(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$"
)

KNOWN_TOOLS: frozenset[str] = frozenset(
    {
        "read",
        "write",
        "bash",
        "search",
        "find",
        "lsp",
        "edit",
        "ast_grep",
        "ast_edit",
        "browser",
        "task",
        "job",
        "irc",
        "eval",
    }
)


class SkillManifest(BaseModel):
    """A skill manifest parsed from SKILL.md YAML front matter."""

    name: str
    description: str
    version: str
    allowed_tools: list[str] = Field(default_factory=list)
    asset_paths: list[Path] = Field(default_factory=list)
    skill_file: Path = Field(default=Path("SKILL.md"))

    @field_validator("name")
    @classmethod
    def _check_name(cls, v: str) -> str:
        if not ALLOWED_NAME_RE.match(v):
            raise ValueError(
                f"Invalid skill name '{v}'. Must be lowercase alphanumeric with hyphens, "
                "starting with a letter or digit."
            )
        return v

    @field_validator("version")
    @classmethod
    def _check_semver(cls, v: str) -> str:
        if not SEMVER_RE.match(v):
            raise ValueError(f"Invalid semver '{v}'. Expected format: MAJOR.MINOR.PATCH.")
        return v


class ValidationError(BaseModel):
    """A validation error for a specific field or asset."""

    field: str | None = None
    message: str
    path: Path | None = None


class ValidationWarning(BaseModel):
    """A non-fatal validation warning."""

    field: str | None = None
    message: str
    path: Path | None = None


class ValidationResult(BaseModel):
    """Result of validating a skill directory."""

    valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)


class BuildArtifact(BaseModel):
    """Result of building a skill package."""

    manifest: SkillManifest
    archive_path: Path
    checksum: str
    size_bytes: int
