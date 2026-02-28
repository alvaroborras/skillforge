"""Tests for the skill scanner."""

from pathlib import Path

from skillforge.scanner import Scanner


class TestScanner:
    def test_scan_finds_valid_skill(self, valid_skill_dir: Path) -> None:
        scanner = Scanner()
        results = scanner.scan(valid_skill_dir)
        assert len(results) == 1
        _, manifest, validation = results[0]
        assert manifest is not None
        assert manifest.name == "valid-skill"
        assert validation is not None
        assert validation.valid

    def test_scan_finds_invalid_skill(self, invalid_skill_dir: Path) -> None:
        scanner = Scanner()
        results = scanner.scan(invalid_skill_dir)
        assert len(results) == 1
        _, manifest, validation = results[0]
        # Invalid manifest fields mean the parse may fail for display,
        # but validation always runs.
        assert validation is not None
        assert not validation.valid

    def test_scan_multi_skill_repo(self, multi_skill_dir: Path) -> None:
        scanner = Scanner()
        results = scanner.scan(multi_skill_dir)
        assert len(results) == 2
        names = {m.name for _, m, _ in results if m}
        assert names == {"skill-a", "skill-b"}

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        scanner = Scanner()
        results = scanner.scan(tmp_path)
        assert results == []

    def test_scan_ignores_non_skill_dirs(self, tmp_path: Path) -> None:
        (tmp_path / "README.md").write_text("hello")
        scanner = Scanner()
        results = scanner.scan(tmp_path)
        assert results == []
