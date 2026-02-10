"""Filesystem scanner that discovers skill directories."""

from pathlib import Path

import yaml

from skillforge.models import SkillManifest, ValidationResult
from skillforge.validator import Validator


class Scanner:
    """Scans a directory tree for skill directories (folders containing SKILL.md)."""

    def __init__(self, validator: Validator | None = None) -> None:
        self._validator = validator or Validator()

    def scan(
        self, root: Path
    ) -> list[tuple[Path, SkillManifest | None, ValidationResult | None]]:
        """Return every discovered skill directory with its parsed manifest and validation result."""
        results: list[tuple[Path, SkillManifest | None, ValidationResult | None]] = []
        for skill_file in sorted(root.rglob("SKILL.md")):
            skill_dir = skill_file.parent
            validation = self._validator.validate(skill_dir)
            manifest = self._try_parse_manifest(skill_dir)
            results.append((skill_dir, manifest, validation))
        return results

    @staticmethod
    def _try_parse_manifest(skill_dir: Path) -> SkillManifest | None:
        """Best-effort manifest extraction for display purposes."""
        content = (skill_dir / "SKILL.md").read_text()
        if not content.startswith("---"):
            return None
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        front = yaml.safe_load(parts[1])
        if not isinstance(front, dict):
            return None
        try:
            return SkillManifest(**front)
        except Exception:
            return None
