"""Kernel-level cgroup v2 sandbox and process-tree accounting for candidate execution."""

import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

from nsb.candidates.models import SearchBudget


DEFAULT_CGROUP_ROOT = Path("/sys/fs/cgroup/nsb")


class CgroupV2Sandbox:
    """Manages process containment, cumulative CPU accounting, and atomic kill via cgroup v2."""

    def __init__(
        self,
        cgroup_root: Path = DEFAULT_CGROUP_ROOT,
        sandbox_id: Optional[str] = None,
    ):
        self.sandbox_id = sandbox_id or f"run_{uuid.uuid4().hex[:12]}"
        self.cgroup_root = cgroup_root
        self.cgroup_path = self.cgroup_root / self.sandbox_id
        self._cgroup_active = False

    def is_cgroup_available(self) -> bool:
        """Check if Linux cgroup v2 root is mounted and writable."""
        if not sys.platform.startswith("linux"):
            return False
        if not Path("/sys/fs/cgroup").is_dir():
            return False
        # Verify cgroup2 mount
        try:
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                content = f.read()
                if "cgroup2" not in content:
                    return False
        except Exception:
            return False

        # Verify delegation root
        try:
            self.cgroup_root.mkdir(parents=True, exist_ok=True)
            test_dir = self.cgroup_root / f".probe_{uuid.uuid4().hex[:6]}"
            test_dir.mkdir(parents=True, exist_ok=False)
            test_dir.rmdir()
            return True
        except Exception:
            return False

    def setup_cgroup(self, budget: SearchBudget) -> bool:
        """Create isolated cgroup and apply resource limits."""
        if not self.is_cgroup_available():
            self._cgroup_active = False
            return False

        try:
            self.cgroup_path.mkdir(parents=True, exist_ok=False)

            # Set memory ceiling
            mem_max_file = self.cgroup_path / "memory.max"
            if mem_max_file.exists():
                mem_bytes = int(budget.max_peak_rss_mb * 1024 * 1024)
                mem_max_file.write_text(str(mem_bytes), encoding="utf-8")

            self._cgroup_active = True
            return True
        except Exception:
            self._cgroup_active = False
            return False

    def attach_pid(self, pid: int) -> bool:
        """Add PID to cgroup.procs and verify attachment."""
        if not self._cgroup_active:
            return False
        try:
            procs_file = self.cgroup_path / "cgroup.procs"
            procs_file.write_text(str(pid), encoding="utf-8")
            # Verify PID is attached
            if procs_file.is_file():
                attached_pids = [p.strip() for p in procs_file.read_text(encoding="utf-8").splitlines()]
                return str(pid) in attached_pids
            return True
        except Exception:
            return False

    def read_cpu_seconds(self) -> float:
        """Read authoritative cumulative CPU usage from cpu.stat."""
        if not self._cgroup_active:
            raise RuntimeError(f"Cgroup accounting query rejected: cgroup is not active ({self.cgroup_path})")
        stat_file = self.cgroup_path / "cpu.stat"
        if not stat_file.is_file():
            raise RuntimeError(f"Cgroup accounting failure: missing cpu.stat at {stat_file}")
        try:
            for line in stat_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("usage_usec"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return float(parts[1]) / 1_000_000.0
            raise RuntimeError(f"Cgroup accounting failure: usage_usec not found in {stat_file}")
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Cgroup accounting failure reading {stat_file}: {e}")

    def read_peak_memory_mb(self) -> float:
        """Read peak memory usage in MB from memory.peak."""
        if not self._cgroup_active:
            return 0.0
        try:
            peak_file = self.cgroup_path / "memory.peak"
            if peak_file.is_file():
                val = peak_file.read_text(encoding="utf-8").strip()
                return float(val) / (1024.0 * 1024.0)
        except Exception:
            pass
        return 0.0

    def kill_all(self) -> bool:
        """Atomically terminate all processes in the cgroup."""
        if not self._cgroup_active:
            return False
        terminated = False
        try:
            kill_file = self.cgroup_path / "cgroup.kill"
            if kill_file.exists():
                kill_file.write_text("1", encoding="utf-8")
                terminated = True
        except Exception:
            pass

        # Defense-in-depth: terminate any remaining PIDs recorded in cgroup.procs
        try:
            import signal
            procs_file = self.cgroup_path / "cgroup.procs"
            if procs_file.is_file():
                for line in procs_file.read_text(encoding="utf-8").splitlines():
                    p_str = line.strip()
                    if p_str:
                        try:
                            os.kill(int(p_str), signal.SIGKILL)
                            terminated = True
                        except Exception:
                            pass
        except Exception:
            pass

        return terminated

    def cleanup(self) -> None:
        """Remove cgroup directory after processes have exited."""
        if not self._cgroup_active:
            return
        # Ensure killed
        self.kill_all()
        # Brief retry loop for processes to exit
        for _ in range(10):
            try:
                if self.cgroup_path.exists():
                    self.cgroup_path.rmdir()
                self._cgroup_active = False
                return
            except Exception:
                time.sleep(0.05)
        self._cgroup_active = False


def build_isolated_env(allow_gpu: bool = False, allow_network: bool = False) -> Dict[str, str]:
    """Build environment dictionary with network and GPU access stripped, and single-thread caps."""
    env = dict(os.environ)

    # Disable GPU access
    if not allow_gpu:
        env["CUDA_VISIBLE_DEVICES"] = ""
        env["ROCR_VISIBLE_DEVICES"] = ""
        env["NVIDIA_VISIBLE_DEVICES"] = ""
        env["USE_GPU"] = "0"

    # Disable network proxy
    if not allow_network:
        env["http_proxy"] = "http://127.0.0.1:0"
        env["https_proxy"] = "http://127.0.0.1:0"
        env["all_proxy"] = "http://127.0.0.1:0"
        env["NO_PROXY"] = ""

    # Enforce single-thread caps
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["VECLIB_MAXIMUM_THREADS"] = "1"
    env["NUMEXPR_NUM_THREADS"] = "1"

    # Strip sensitive credentials, tokens, secrets, passwords, and synthetic test credentials
    sensitive_keys = {
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
        "GITHUB_TOKEN", "GH_TOKEN", "GITLAB_TOKEN", "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY",
    }
    for k in list(env.keys()):
        ku = k.upper()
        if (
            k in sensitive_keys
            or "CREDENTIAL" in ku
            or "SECRET" in ku
            or "TOKEN" in ku
            or "API_KEY" in ku
            or "PASSWORD" in ku
            or "PASSWD" in ku
            or "SYNTHETIC" in ku
            or ("AUTH" in ku and k != "SSH_AUTH_SOCK")
        ):
            env.pop(k, None)

    return env

