"""Unit tests for environment fingerprinting and SubprocessRunner."""

import sys
import tempfile
from pathlib import Path
import pytest
from nsb.core.fingerprint import capture_environment_fingerprint
from nsb.core.runner import SubprocessRunner


def test_capture_environment_fingerprint():
    fp = capture_environment_fingerprint()
    assert fp.os_name != ""
    assert fp.python_version != ""
    assert fp.cpu_model != ""
    assert "gmpy2" in fp.packages
    assert fp.packages["gmpy2"] != "unknown"


def test_subprocess_runner_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = SubprocessRunner(artifacts_base_dir=tmpdir)
        cmd = [sys.executable, "-c", "print('NSB_TEST_OK')"]

        (
            exit_code,
            wall_sec,
            cpu_sec,
            peak_rss,
            timeout,
            killed,
            reason,
            stdout_path,
            stderr_path,
        ) = runner.run_command(
            command=cmd,
            experiment_id="EXP_TEST",
            run_id="RUN_001",
            max_wall_seconds=5.0,
        )

        assert exit_code == 0
        assert timeout is False
        assert killed is False
        assert wall_sec > 0.0
        assert stdout_path.is_file()
        assert "NSB_TEST_OK" in stdout_path.read_text()


def test_subprocess_runner_timeout():
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = SubprocessRunner(artifacts_base_dir=tmpdir)
        cmd = [sys.executable, "-c", "import time; time.sleep(10)"]

        (
            exit_code,
            wall_sec,
            cpu_sec,
            peak_rss,
            timeout,
            killed,
            reason,
            stdout_path,
            stderr_path,
        ) = runner.run_command(
            command=cmd,
            experiment_id="EXP_TEST",
            run_id="RUN_TIMEOUT",
            max_wall_seconds=0.2,
        )

        assert timeout is True
        assert exit_code == -1
        assert wall_sec >= 0.2
        assert "Wall-clock timeout" in reason


def test_subprocess_runner_child_process_tree_killed():
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = SubprocessRunner(artifacts_base_dir=tmpdir)
        # Parent spawns child and writes child PID to a file, then sleeps
        child_pid_file = Path(tmpdir) / "child_pid.txt"
        script = (
            "import subprocess, sys, time, pathlib\n"
            "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
            f"pathlib.Path(r'{child_pid_file}').write_text(str(p.pid))\n"
            "p.wait()\n"
        )
        cmd = [sys.executable, "-c", script]

        (
            exit_code,
            wall_sec,
            cpu_sec,
            peak_rss,
            timeout,
            killed,
            reason,
            stdout_path,
            stderr_path,
        ) = runner.run_command(
            command=cmd,
            experiment_id="EXP_TEST",
            run_id="RUN_TREE_KILL",
            max_wall_seconds=0.5,
        )

        assert timeout is True
        assert exit_code == -1
        assert child_pid_file.is_file()
        child_pid = int(child_pid_file.read_text().strip())
        import psutil
        assert not psutil.pid_exists(child_pid) or psutil.Process(child_pid).status() == psutil.STATUS_ZOMBIE
