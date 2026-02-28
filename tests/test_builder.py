"""Tests for the skill builder."""

import hashlib
import tarfile
import zipfile
from pathlib import Path

import pytest

from skillforge.builder import Builder, BuildError


class TestBuilder:
    def test_build_tar_gz(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        artifact = b.build(valid_skill_dir, output, fmt="tar.gz")
        assert artifact.archive_path.exists()
        assert artifact.archive_path.name.endswith(".tar.gz")
        assert "valid-skill" in artifact.archive_path.name

    def test_build_zip(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        artifact = b.build(valid_skill_dir, output, fmt="zip")
        assert artifact.archive_path.exists()
        assert artifact.archive_path.suffix == ".zip"

    def test_build_fails_on_invalid_skill(self, invalid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        with pytest.raises(BuildError, match="Validation failed"):
            b.build(invalid_skill_dir, output)

    def test_tar_contains_expected_files(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        artifact = b.build(valid_skill_dir, output, fmt="tar.gz")

        with tarfile.open(artifact.archive_path, "r:gz") as tar:
            names = sorted(tar.getnames())
            prefix = "valid-skill/"
            assert f"{prefix}SKILL.md" in names
            assert f"{prefix}scripts/helper.py" in names
            assert f"{prefix}templates/example.py.j2" in names

    def test_zip_contains_expected_files(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        artifact = b.build(valid_skill_dir, output, fmt="zip")

        with zipfile.ZipFile(artifact.archive_path, "r") as zf:
            names = sorted(zf.namelist())
            prefix = "valid-skill/"
            assert f"{prefix}SKILL.md" in names
            assert f"{prefix}scripts/helper.py" in names

    def test_checksum_valid(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        artifact = b.build(valid_skill_dir, output, fmt="tar.gz")
        actual = hashlib.sha256(artifact.archive_path.read_bytes()).hexdigest()
        assert artifact.checksum == actual

    def test_deterministic_build(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        a1 = b.build(valid_skill_dir, output, fmt="tar.gz")
        a2 = b.build(valid_skill_dir, output / "dist2", fmt="tar.gz")
        assert a1.checksum == a2.checksum
        assert a1.size_bytes == a2.size_bytes

    def test_unsupported_format_raises(self, valid_skill_dir: Path, tmp_path: Path) -> None:
        output = tmp_path / "dist"
        b = Builder()
        with pytest.raises(BuildError, match="Unsupported format"):
            b.build(valid_skill_dir, output, fmt="rar")
