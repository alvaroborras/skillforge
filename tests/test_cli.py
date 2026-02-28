"""Integration tests for skillforge CLI commands."""

import json
from pathlib import Path

from typer.testing import CliRunner

from skillforge.cli.main import app

runner = CliRunner()


class TestScan:
    def test_scan_json(self, multi_skill_dir: Path) -> None:
        result = runner.invoke(app, ["scan", str(multi_skill_dir), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 2

    def test_scan_table(self, multi_skill_dir: Path) -> None:
        result = runner.invoke(app, ["scan", str(multi_skill_dir)])
        assert result.exit_code == 0
        assert "skill-a" in result.stdout
        assert "skill-b" in result.stdout

    def test_scan_empty(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["scan", str(tmp_path)])
        assert result.exit_code == 0
        assert "No skills found" in result.stdout


class TestInit:
    def test_init_creates_skill(self, tmp_path: Path) -> None:
        base = tmp_path / ".skills"
        result = runner.invoke(app, ["init", "my-skill", "--path", str(base)])
        assert result.exit_code == 0
        assert (base / "my-skill" / "SKILL.md").exists()

    def test_init_skill_has_front_matter(self, tmp_path: Path) -> None:
        base = tmp_path / ".skills"
        runner.invoke(app, ["init", "test-skill", "--path", str(base)])
        content = (base / "test-skill" / "SKILL.md").read_text()
        assert content.startswith("---")

    def test_init_fails_on_existing(self, tmp_path: Path) -> None:
        base = tmp_path / ".skills"
        runner.invoke(app, ["init", "dup", "--path", str(base)])
        result = runner.invoke(app, ["init", "dup", "--path", str(base)])
        assert result.exit_code == 1
        assert "already exists" in result.stdout


class TestValidate:
    def test_validate_valid_skill(self, valid_skill_dir: Path) -> None:
        result = runner.invoke(app, ["validate", str(valid_skill_dir)])
        assert result.exit_code == 0
        assert "PASS" in result.stdout

    def test_validate_invalid_skill(self, invalid_skill_dir: Path) -> None:
        result = runner.invoke(app, ["validate", str(invalid_skill_dir)])
        assert result.exit_code == 1

    def test_validate_strict(self, invalid_skill_dir: Path) -> None:
        result = runner.invoke(app, ["validate", str(invalid_skill_dir), "--strict"])
        assert result.exit_code == 1

    def test_validate_json(self, valid_skill_dir: Path) -> None:
        result = runner.invoke(app, ["validate", str(valid_skill_dir), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data[0]["valid"] is True

    def test_validate_not_a_skill_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["validate", str(tmp_path)])
        assert result.exit_code == 1
        assert "not a skill directory" in result.stdout


class TestBuild:
    def test_build_creates_archive(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        result = runner.invoke(
            app, ["build", str(valid_skill_dir), "--output", str(output)]
        )
        assert result.exit_code == 0
        archives = list(output.glob("*.tar.gz"))
        assert len(archives) == 1

    def test_build_fails_invalid(self, invalid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        result = runner.invoke(
            app, ["build", str(invalid_skill_dir), "--output", str(output)]
        )
        assert result.exit_code == 2

    def test_build_zip_format(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        result = runner.invoke(
            app, ["build", str(valid_skill_dir), "--format", "zip", "--output", str(output)]
        )
        assert result.exit_code == 0
        assert list(output.glob("*.zip"))


class TestPublish:
    def test_publish_dry_run_dir(self, valid_skill_dir: Path) -> None:
        result = runner.invoke(app, ["publish", str(valid_skill_dir), "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "valid-skill" in result.stdout

    def test_publish_missing_skill(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["publish", str(tmp_path), "--dry-run"])
        assert result.exit_code == 1


class TestEndToEnd:
    def test_init_validate_build_publish_pipeline(self, tmp_path: Path) -> None:
        base = tmp_path / ".skills"
        dist = tmp_path / "dist"

        # Init
        r = runner.invoke(app, ["init", "e2e-skill", "--path", str(base)])
        assert r.exit_code == 0

        skill_dir = base / "e2e-skill"
        assert skill_dir.is_dir()

        # Validate
        r = runner.invoke(app, ["validate", str(skill_dir)])
        assert r.exit_code == 0

        # Build
        r = runner.invoke(app, ["build", str(skill_dir), "--output", str(dist)])
        assert r.exit_code == 0
        archives = list(dist.glob("*.tar.gz"))
        assert len(archives) == 1

        # Publish --dry-run
        r = runner.invoke(app, ["publish", str(skill_dir), "--dry-run"])
        assert r.exit_code == 0
        assert "DRY RUN" in r.stdout
