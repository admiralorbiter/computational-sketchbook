"""Shared test fixtures."""

from pathlib import Path

import pytest

from observatory.config import Settings
from observatory.store.corpus import CorpusStore


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Provide a temporary data directory."""
    return tmp_path / "data"


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """Provide settings pointing to temporary directories."""
    return Settings(
        data_dir=tmp_path / "data",
        runs_dir=tmp_path / "runs",
    )


@pytest.fixture
def test_corpus(test_settings: Settings) -> CorpusStore:
    """Provide a corpus store with temporary storage."""
    return CorpusStore(settings=test_settings)
