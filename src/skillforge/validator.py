"""Structural and semantic validation of skill directories."""

from pathlib import Path

import yaml
from pydantic import ValidationError as PydanticValidationError

from skillforge.models import (
    KNOWN_TOOLS,
    SkillManifest,
    ValidationError,
    ValidationResult,
    ValidationWarning,
)

MANIFEST_FIELDS = {
    "name",
    "description",
    "version",
    "allowed_tools",
    "asset_paths",
    "skill_file",
}


class Validator:
    """Validates a skill directory against the canonical schema."""

    def validate(
        self, skill_dir: Path, manifest: SkillManifest | None = None
    ) -> ValidationResult:
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(ValidationError(message="SKILL.md not found", path=skill_dir))
            return ValidationResult(valid=False, errors=errors)

        raw = skill_file.read_text()
        data = self._parse_yaml(raw, errors)
        if data is None:
            return ValidationResult(valid=False, errors=errors)

        # Try to build the Pydantic model; collect errors.
        _manifest = self._build_manifest(data, errors)

        # Check assets and tools from raw data so these checks run
        # even when model fields (e.g. version) fail validation.
        self._check_assets_from_data(skill_dir, data, errors)
        self._check_tools_from_data(data, warnings)
        self._check_unknown_fields(data, warnings)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _parse_yaml(
        content: str, errors: list[ValidationError]
    ) -> dict | None:
        if not content.startswith("---"):
            errors.append(
                ValidationError(
                    field="front_matter",
                    message="SKILL.md must start with YAML front matter (---)",
                )
            )
            return None
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(
                ValidationError(
                    field="front_matter",
                    message="Unclosed YAML front matter in SKILL.md",
                )
            )
            return None
        try:
            data = yaml.safe_load(parts[1])
        except yaml.YAMLError as exc:
            errors.append(
                ValidationError(
                    field="front_matter",
                    message=f"Invalid YAML: {exc}",
                )
            )
            return None
        if not isinstance(data, dict):
            errors.append(
                ValidationError(
                    field="front_matter",
                    message="Front matter must be a YAML mapping",
                )
            )
            return None
        return dict(data)

    @staticmethod
    def _build_manifest(
        data: dict, errors: list[ValidationError]
    ) -> SkillManifest | None:
        try:
            return SkillManifest(**data)
        except PydanticValidationError as exc:
            for e in exc.errors():
                field = ".".join(str(loc) for loc in e["loc"])
                errors.append(
                    ValidationError(field=field, message=e["msg"])
                )
            return None

    @staticmethod
    def _check_assets_from_data(
        skill_dir: Path, data: dict, errors: list[ValidationError]
    ) -> None:
        for asset in data.get("asset_paths", []):
            full = skill_dir / asset
            if not full.exists():
                errors.append(
                    ValidationError(
                        field="asset_paths",
                        message=f"Referenced asset not found: {asset}",
                        path=full,
                    )
                )

    @staticmethod
    def _check_tools_from_data(
        data: dict, warnings: list[ValidationWarning]
    ) -> None:
        for tool in data.get("allowed_tools", []):
            if tool not in KNOWN_TOOLS:
                warnings.append(
                    ValidationWarning(
                        field="allowed_tools",
                        message=f"Tool '{tool}' is not in the known tools registry",
                    )
                )

    @staticmethod
    def _check_unknown_fields(
        data: dict, warnings: list[ValidationWarning]
    ) -> None:
        for key in data:
            if key not in MANIFEST_FIELDS:
                warnings.append(
                    ValidationWarning(
                        field=key,
                        message=f"Unknown manifest field: {key}",
                    )
                )
