"""Unit tests for NSB core utilities: hashing, identity, config, and database ledger."""

import tempfile
from pathlib import Path
import pytest
from nsb.core.hashing import hash_bytes, hash_file, hash_object
from nsb.core.identity import generate_experiment_id, parse_experiment_id
from nsb.core.config import load_config
from nsb.core.db import LedgerDB


def test_hashing_primitives():
    # Byte hashing
    h1 = hash_bytes(b"hello world")
    assert len(h1) == 64
    assert h1 == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    # Object hashing (deterministic key ordering)
    obj1 = {"b": 2, "a": 1}
    obj2 = {"a": 1, "b": 2}
    assert hash_object(obj1) == hash_object(obj2)

    # File hashing
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("hello world")
        tmp_path = f.name
    try:
        assert hash_file(tmp_path) == h1
    finally:
        Path(tmp_path).unlink()


def test_experiment_id_generation():
    exp_id = generate_experiment_id(track="B", suffix="ABC123")
    assert exp_id.startswith("NSB-B-")
    assert exp_id.endswith("-ABC123")

    parsed = parse_experiment_id(exp_id)
    assert parsed["track"] == "B"
    assert parsed["suffix"] == "ABC123"

    with pytest.raises(ValueError):
        generate_experiment_id(track="INVALID")

    with pytest.raises(ValueError):
        parse_experiment_id("INVALID-ID")


def test_config_loading():
    config_path = Path("config/defaults.yaml")
    config, chash = load_config(config_path)
    assert config.contract_id == "NSB-R0-FOUNDATION"
    assert len(chash) == 64


def test_ledger_database():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_ledger.sqlite"
        ledger = LedgerDB(db_path)

        # Initial hash should be all zeros
        assert ledger.get_latest_event_hash() == "0" * 64

        # Record events and check chaining
        h1 = ledger.record_event(actor="runner", event_type="INIT", payload={"status": "ready"})
        assert len(h1) == 64
        assert ledger.get_latest_event_hash() == h1

        h2 = ledger.record_event(actor="verifier", event_type="VERIFY", payload={"passed": True})
        assert len(h2) == 64
        assert h2 != h1
        assert ledger.get_latest_event_hash() == h2

        # Record experiment
        exp_id = generate_experiment_id(track="A", suffix="112233")
        ledger.insert_experiment(
            exp_id=exp_id,
            track="A",
            contract_id="NSB-R0-FOUNDATION",
            commit_sha="c981a21",
            config_sha256="abc1234",
            benchmark_version="v001",
        )
        ledger.update_experiment_status(exp_id=exp_id, status="COMPLETE", verdict="PROMOTED")

        ledger.close()
