"""Canary test for full smoke suite S0-S5 execution."""

import pytest
from nsb.smoke import run_smoke_suite


def test_smoke_suite_execution():
    """Run full smoke suite S0-S5 end-to-end and assert success."""
    success = run_smoke_suite("config/smoke.yaml", allow_dirty=True)
    assert success is True


def test_smoke_suite_rejects_dirty_when_uncommitted():
    """Verify that canonical run rejects dirty working tree."""
    from nsb.auditor.engine import Auditor
    auditor = Auditor()
    _, git_dirty, _ = auditor.check_git_status()
    if git_dirty:
        success = run_smoke_suite("config/smoke.yaml", allow_dirty=False)
        assert success is False

