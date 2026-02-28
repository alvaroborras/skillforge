"""Shared test fixtures."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_skill_dir() -> Path:
    return FIXTURES / "valid-skill"


@pytest.fixture
def invalid_skill_dir() -> Path:
    return FIXTURES / "invalid-skill"


@pytest.fixture
def multi_skill_dir() -> Path:
    return FIXTURES / "multi-skill-repo"


@pytest.fixture
def tmp_skill_dir(tmp_path: Path) -> Path:
    """A temporary directory to init skills into (simulates .skills/ base)."""
    return tmp_path / ".skills"
