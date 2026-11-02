"""Application configuration loaded from environment variables and .env files."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Observatory configuration.

    Values are loaded from environment variables, with fallback to a .env file
    in the project root.
    """

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # Paths
    data_dir: Path = Path("./data")
    runs_dir: Path = Path("./runs")
    media_dir_override: Path | None = Field(
        default=None,
        validation_alias="OBSERVATORY_MEDIA_DIR",
    )

    # Scraping behavior
    user_agent: str = "signal-observatory/0.1.0 (research)"
    request_delay_seconds: float = 1.0

    @property
    def raw_dir(self) -> Path:
        """Immutable raw API responses."""
        return self.data_dir / "raw"

    @property
    def media_dir(self) -> Path:
        """Downloaded media files directory (customizable via OBSERVATORY_MEDIA_DIR)."""
        if self.media_dir_override:
            return Path(self.media_dir_override)
        return self.data_dir / "media"

    @property
    def normalized_dir(self) -> Path:
        """Parquet tables of normalized artifacts."""
        return self.data_dir / "normalized"

    @property
    def derived_dir(self) -> Path:
        """Model-derived annotations, clusters, transcripts."""
        return self.data_dir / "derived"

    @property
    def indexes_dir(self) -> Path:
        """Lookup indexes (media hashes, etc.)."""
        return self.data_dir / "indexes"

    def ensure_directories(self) -> None:
        """Create all data directories if they don't exist."""
        for d in [
            self.raw_dir,
            self.media_dir,
            self.normalized_dir,
            self.derived_dir,
            self.indexes_dir,
            self.runs_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
