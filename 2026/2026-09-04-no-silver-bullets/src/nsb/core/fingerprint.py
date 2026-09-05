"""Hardware, environment, and dependency fingerprinting for scientific reproducibility."""

import os
import platform
import subprocess
import sys
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EnvironmentFingerprint(BaseModel):
    os_name: str
    os_release: str
    os_version: str
    architecture: str
    python_version: str
    python_compiler: str
    cpu_model: str
    cpu_count_logical: Optional[int]
    memory_total_mb: Optional[int]
    git_commit: str
    git_dirty: bool
    packages: Dict[str, str] = Field(default_factory=dict)


def get_git_commit(repo_dir: Optional[str] = None) -> tuple[str, bool]:
    """Retrieve current Git commit hash and whether the working directory has uncommitted changes."""
    try:
        cmd = ["git", "rev-parse", "HEAD"]
        res = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True, check=True)
        commit = res.stdout.strip()

        status_cmd = ["git", "status", "--porcelain"]
        status_res = subprocess.run(status_cmd, cwd=repo_dir, capture_output=True, text=True, check=True)
        dirty_lines = [
            line
            for line in status_res.stdout.splitlines()
            if line.strip()
            and not line.endswith(".log")
            and not line.endswith(".sqlite")
            and not line.endswith(".sqlite-journal")
            and not line.endswith(".sqlite-wal")
            and not line.endswith(".sqlite-shm")
            and not line.endswith("SMOKE_REVIEW_PACKET.md")
            and not line.endswith("SMOKE_REVIEW_PACKET.json")
            and not line.endswith("PILOT_REVIEW_PACKET.md")
            and not line.endswith("PILOT_REVIEW_PACKET.json")
        ]
        dirty = len(dirty_lines) > 0
        return commit, dirty
    except Exception:
        return "UNKNOWN_COMMIT", True



def get_cpu_model() -> str:
    """Detect CPU model across platforms."""
    model = platform.processor()
    if not model and platform.system() == "Windows":
        model = os.environ.get("PROCESSOR_IDENTIFIER", "Unknown Windows CPU")
    return model or "Unknown CPU"


def get_total_ram_mb() -> Optional[int]:
    """Detect total system physical RAM in megabytes."""
    try:
        if platform.system() == "Windows":
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                return int(stat.ullTotalPhys // (1024 * 1024))
        else:
            # Unix sysconf
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            return int((pages * page_size) // (1024 * 1024))
    except Exception:
        pass
    return None


def get_package_versions() -> Dict[str, str]:
    """Query versions of key scientific libraries."""
    pkgs = {}
    for mod_name in ["gmpy2", "pysat", "z3", "numpy", "scipy", "pydantic", "yaml", "pytest"]:
        try:
            m = __import__(mod_name)
            pkgs[mod_name] = getattr(m, "__version__", "unknown")
        except ImportError:
            pass
    return pkgs


def capture_environment_fingerprint(repo_dir: Optional[str] = None) -> EnvironmentFingerprint:
    """Capture full environment fingerprint."""
    commit, dirty = get_git_commit(repo_dir)
    return EnvironmentFingerprint(
        os_name=platform.system(),
        os_release=platform.release(),
        os_version=platform.version(),
        architecture=platform.machine(),
        python_version=platform.python_version(),
        python_compiler=platform.python_compiler(),
        cpu_model=get_cpu_model(),
        cpu_count_logical=os.cpu_count(),
        memory_total_mb=get_total_ram_mb(),
        git_commit=commit,
        git_dirty=dirty,
        packages=get_package_versions(),
    )
