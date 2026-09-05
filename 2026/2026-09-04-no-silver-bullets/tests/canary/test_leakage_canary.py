"""Canary test for leakage detection and tripwire audit checks."""

import os
import tempfile
from pathlib import Path
import pytest
from nsb.verifier.leakage import audit_environment_leakage, audit_path_access
from nsb.benchmarks.corpus import TRIPWIRE_FILENAME, create_corpus_split


def test_audit_environment_leakage_clean():
    res = audit_environment_leakage()
    assert res.passed is True
    assert len(res.violations) == 0


def test_audit_environment_leakage_detected(monkeypatch):
    monkeypatch.setenv("NSB_SEALED_TRUTH", "forbidden_leak")
    res = audit_environment_leakage()
    assert res.passed is False
    assert any("NSB_SEALED_TRUTH" in v for v in res.violations)


def test_audit_path_access_violation():
    with tempfile.TemporaryDirectory() as tmpdir:
        sealed_dir = Path(tmpdir) / "sealed"
        sealed_dir.mkdir()
        secret_file = sealed_dir / "truth.jsonl"
        secret_file.touch()

        allowed_dir = Path(tmpdir) / "public"
        allowed_dir.mkdir()
        public_file = allowed_dir / "instances.jsonl"
        public_file.touch()

        # Clean access
        clean_res = audit_path_access([public_file], sealed_dir)
        assert clean_res.passed is True

        # Leaked access
        leak_res = audit_path_access([public_file, secret_file], sealed_dir)
        assert leak_res.passed is False
        assert any("truth.jsonl" in v for v in leak_res.violations)


def test_tripwire_created_in_sealed_corpus():
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = [{"family": "R", "bit_sizes": [32], "count_per_size": 1}]
        create_corpus_split(tmpdir, "v001_test", "smoke", spec, 42)

        tripwire_path = Path(tmpdir) / "benchmarks" / "sealed" / "v001_test" / "smoke" / TRIPWIRE_FILENAME
        assert tripwire_path.is_file()
        content = tripwire_path.read_text(encoding="utf-8")
        assert "SECURITY WARNING" in content
