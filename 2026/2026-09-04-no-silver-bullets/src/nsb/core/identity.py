"""Experiment and run identity generation conforming to NSB standards."""

import datetime
import os
import re
from typing import Optional

EXPERIMENT_ID_PATTERN = re.compile(r"^NSB-(A|B|C|D|BASE)-(\d{8})-([0-9A-F]{6})$")
VALID_TRACKS = {"A", "B", "C", "D", "BASE"}


def generate_experiment_id(track: str, date: Optional[datetime.date] = None, suffix: Optional[str] = None) -> str:
    """Generate a canonical experiment ID: NSB-<TRACK>-<YYYYMMDD>-<6HEX>.

    Args:
        track: One of 'A', 'B', 'C', 'D', 'BASE'.
        date: Specific date or None for UTC today.
        suffix: Specific 6-character hex string or None for random.
    """
    track_upper = track.upper()
    if track_upper not in VALID_TRACKS:
        raise ValueError(f"Invalid track '{track}'. Must be one of {VALID_TRACKS}")

    d = date or datetime.datetime.now(datetime.timezone.utc).date()
    date_str = d.strftime("%Y%m%d")

    if suffix is None:
        suffix_str = os.urandom(3).hex().upper()
    else:
        suffix_str = suffix.upper()
        if len(suffix_str) != 6 or not all(c in "0123456789ABCDEF" for c in suffix_str):
            raise ValueError(f"Suffix must be 6 hex characters, got '{suffix}'")

    return f"NSB-{track_upper}-{date_str}-{suffix_str}"


def parse_experiment_id(exp_id: str) -> dict:
    """Parse and validate an experiment ID."""
    m = EXPERIMENT_ID_PATTERN.match(exp_id)
    if not m:
        raise ValueError(f"Malformed experiment ID: '{exp_id}'")
    track, date_str, suffix = m.groups()
    return {
        "track": track,
        "date": datetime.datetime.strptime(date_str, "%Y%m%d").date(),
        "suffix": suffix,
    }
