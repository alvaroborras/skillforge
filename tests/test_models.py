"""Unit tests for skillforge.models."""

from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError

from skillforge.models import SkillManifest, ValidationError, ValidationResult, ValidationWarning


class TestSkillManifest:
    def test_valid_manifest(self) -> None:
        m = SkillManifest(name="my-skill", description="A skill", version="1.0.0")
        assert m.name == "my-skill"
        assert m.version == "1.0.0"
        assert m.allowed_tools == []
        assert m.asset_paths == []
        assert m.skill_file == Path("SKILL.md")

    def test_defaults(self) -> None:
        m = SkillManifest(name="test", description="desc", version="0.1.0")
        assert m.allowed_tools == []
        assert m.asset_paths == []
        assert m.skill_file == Path("SKILL.md")

    def test_name_must_be_lowercase_hyphenated(self) -> None:
        with pytest.raises(PydanticValidationError):
            SkillManifest(name="Invalid_Name", description="desc", version="1.0.0")

    def test_name_cannot_start_with_hyphen(self) -> None:
        with pytest.raises(PydanticValidationError):
            SkillManifest(name="-bad", description="desc", version="1.0.0")

    def test_version_must_be_semver(self) -> None:
        with pytest.raises(PydanticValidationError):
            SkillManifest(name="test", description="desc", version="not-semver")

    def test_version_accepts_prerelease(self) -> None:
        m = SkillManifest(name="test", description="desc", version="1.0.0-alpha.1")
        assert m.version == "1.0.0-alpha.1"

    def test_asset_paths_accept_path_objects(self) -> None:
        m = SkillManifest(
            name="test",
            description="desc",
            version="1.0.0",
            asset_paths=[Path("scripts/helper.py")],
        )
        assert len(m.asset_paths) == 1
        assert m.asset_paths[0] == Path("scripts/helper.py")


class TestValidationResult:
    def test_valid_result(self) -> None:
        r = ValidationResult(valid=True)
        assert r.valid
        assert r.errors == []
        assert r.warnings == []

    def test_invalid_result_with_errors(self) -> None:
        e = ValidationError(field="name", message="bad name")
        r = ValidationResult(valid=False, errors=[e])
        assert not r.valid
        assert len(r.errors) == 1

    def test_result_with_warnings(self) -> None:
        w = ValidationWarning(field="allowed_tools", message="unknown tool")
        r = ValidationResult(valid=True, warnings=[w])
        assert r.valid
        assert len(r.warnings) == 1
