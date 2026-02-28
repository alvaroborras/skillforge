"""Tests for SkillManager orchestrator."""

from pathlib import Path

import pytest

from skillforge.manager import SkillManager


class TestManagerInit:
    def test_init_creates_skill_directory(self, tmp_path: Path) -> None:
        mgr = SkillManager()
        base = tmp_path / ".skills"
        created = mgr.init_skill("my-skill", base)
        assert created.exists()
        assert (created / "SKILL.md").exists()

    def test_init_skill_md_has_front_matter(self, tmp_path: Path) -> None:
        mgr = SkillManager()
        base = tmp_path / ".skills"
        created = mgr.init_skill("test-skill", base)
        content = (created / "SKILL.md").read_text()
        assert content.startswith("---")

    def test_init_raises_on_existing_dir(self, tmp_path: Path) -> None:
        mgr = SkillManager()
        base = tmp_path / ".skills"
        mgr.init_skill("dup", base)
        with pytest.raises(FileExistsError):
            mgr.init_skill("dup", base)


class TestManagerValidate:
    def test_validate_single_skill(self, valid_skill_dir: Path) -> None:
        mgr = SkillManager()
        results = mgr.validate(valid_skill_dir)
        assert len(results) == 1
        _, _, validation = results[0]
        assert validation.valid

    def test_validate_tree(self, multi_skill_dir: Path) -> None:
        mgr = SkillManager()
        results = mgr.validate(multi_skill_dir)
        assert len(results) == 2


class TestManagerPublish:
    def test_publish_dry_run(self, valid_skill_dir: Path) -> None:
        mgr = SkillManager()
        result = mgr.publish(valid_skill_dir, "https://example.com", dry_run=True)
        assert result["dry_run"] is True
        assert "DRY RUN" in result["message"]
