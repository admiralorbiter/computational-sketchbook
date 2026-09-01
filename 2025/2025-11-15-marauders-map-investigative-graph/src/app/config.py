from __future__ import annotations

import os
from pathlib import Path


def get_config() -> dict:
    """Return base configuration dict for the app.

    This keeps things simple for Slice 0 while matching the architecture docs:
    - SQLite for data
    - workspace-scoped data directory
    """
    base_dir = Path(os.getenv("MM_BASE_DIR", Path.cwd()))
    data_dir = base_dir / "data"

    return {
        "ENV": os.getenv("FLASK_ENV", "development"),
        "DEBUG": os.getenv("FLASK_DEBUG", "1") == "1",
        "DATA_DIR": str(data_dir),
        "DATABASE_PATH": str(data_dir / "marauders_map.db"),
    }


