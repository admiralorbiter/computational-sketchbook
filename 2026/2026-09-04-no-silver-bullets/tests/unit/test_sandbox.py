"""Unit tests for WorkerSandbox isolation."""

import tempfile
from pathlib import Path
import pytest

from nsb.core.sandbox import IsolationViolationError, WorkerSandbox
from nsb.benchmarks.corpus import TRIPWIRE_FILENAME


def test_worker_sandbox_clean_setup():
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        pub = base / "benchmarks" / "public" / "v1" / "smoke"
        pub.mkdir(parents=True)
        (pub / "instances.jsonl").write_text('{"instance_id": "R-032-00001"}\n')

        sealed = base / "benchmarks" / "sealed" / "v1" / "smoke"
        sealed.mkdir(parents=True)
        (sealed / "truth.jsonl").write_text('{"p": "2", "q": "3"}\n')
        (sealed / TRIPWIRE_FILENAME).write_text("TRIPWIRE")

        sandbox = WorkerSandbox(base_dir=base, cleanup_on_exit=True)
        sb_dir = sandbox.setup("exp1", "run1")

        assert (sb_dir / "benchmarks" / "public" / "v1" / "smoke" / "instances.jsonl").exists()
        assert not (sb_dir / "benchmarks" / "sealed").exists()
        assert not (sb_dir / TRIPWIRE_FILENAME).exists()

        # Check violation detection
        bad_dir = base / "bad_dir"
        bad_dir.mkdir()
        (bad_dir / TRIPWIRE_FILENAME).write_text("leak")
        with pytest.raises(IsolationViolationError):
            WorkerSandbox.verify_no_sealed_leakage(bad_dir)
