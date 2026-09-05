"""Cryptographic hashing utilities ensuring deterministic artifact provenance."""

import hashlib
import json
from pathlib import Path
from typing import Any, Union


def hash_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_string(s: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hash_bytes(s.encode("utf-8"))


def hash_file(path: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file on disk."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found for hashing: {p}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def hash_object(obj: Any) -> str:
    """Compute deterministic SHA-256 hash of a JSON-serializable Python object."""
    encoded = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hash_bytes(encoded)
