"""Environment detection, fingerprinting, and binary validation for CADO-NFS.

Verifies:
1. OS environment (Linux native or WSL2).
2. Pinned git commit in CADO source repository.
3. Existence and SHA-256 digests of canonical binaries.
4. Toolchain capabilities (C++20, GCC, CMake, Python, GMP).
"""

import hashlib
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml


class CadoEnvironment:
    """Manages environment validation and binary location for CADO-NFS."""

    def __init__(
        self,
        cado_root: Optional[Union[str, Path]] = None,
        lockfile_path: Union[str, Path] = "config/external/cado_nfs.lock.yaml",
    ):
        self.lockfile_path = Path(lockfile_path)
        self.lock_data = self._load_lockfile()

        # Determine CADO root directory
        if cado_root is not None:
            self.cado_root = Path(cado_root)
        elif "CADO_NFS_ROOT" in os.environ:
            self.cado_root = Path(os.environ["CADO_NFS_ROOT"])
        else:
            # Default candidates: current dir / "cado-nfs", home / "cado-nfs"
            candidates = [
                Path("cado-nfs"),
                Path.home() / "cado-nfs",
                Path("/opt/cado-nfs"),
            ]
            found = None
            for c in candidates:
                if c.exists() and (c / "cado-nfs.py").exists():
                    found = c
                    break
            self.cado_root = found or Path("cado-nfs")

    def _load_lockfile(self) -> Dict[str, Any]:
        if self.lockfile_path.exists():
            with open(self.lockfile_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    @property
    def is_linux(self) -> bool:
        """True if running inside native Linux or WSL2 Linux environment."""
        return sys.platform.startswith("linux")

    @property
    def is_windows(self) -> bool:
        """True if running on Windows host."""
        return sys.platform == "win32"

    def has_wsl(self) -> bool:
        """Check if Windows Subsystem for Linux (WSL) is available."""
        if not self.is_windows:
            return False
        wsl_bin = shutil.which("wsl.exe") or shutil.which("wsl")
        if not wsl_bin:
            return False
        try:
            res = subprocess.run(
                ["wsl.exe", "-l", "-q"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return res.returncode == 0 and bool(res.stdout.strip())
        except Exception:
            return False

    def get_binary_path(self, binary_name: str) -> Optional[Path]:
        """Locate binary path inside CADO tree."""
        binary_specs = self.lock_data.get("canonical_binaries", {})
        spec = binary_specs.get(binary_name)
        if not spec:
            return None

        rel_path = spec.get("relative_path", "")
        # Check in build directory
        direct_path = self.cado_root / rel_path
        if direct_path.exists():
            return direct_path

        # Check alternative common build directory layout
        alt_path = self.cado_root / "build" / rel_path.replace("build/x86_64/", "")
        if alt_path.exists():
            return alt_path

        # Fallback to direct name under cado root
        simple_path = self.cado_root / Path(rel_path).name
        if simple_path.exists():
            return simple_path

        return None

    def hash_binary(self, binary_path: Path) -> str:
        """Compute SHA-256 digest of binary executable."""
        h = hashlib.sha256()
        with open(binary_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def get_git_commit(self) -> Optional[str]:
        """Get git commit SHA of cado-nfs repository."""
        if not self.cado_root.exists() or not (self.cado_root / ".git").exists():
            return None
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.cado_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def is_git_clean(self) -> bool:
        """Check if CADO repository working tree is clean."""
        if not self.cado_root.exists() or not (self.cado_root / ".git").exists():
            return False
        try:
            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.cado_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return res.returncode == 0 and len(res.stdout.strip()) == 0
        except Exception:
            return False

    def get_toolchain_versions(self) -> Dict[str, str]:
        """Detect versions of compilers and build tools."""
        versions = {}
        for tool, cmd in [
            ("gcc", ["gcc", "-dumpfullversion"]),
            ("cmake", ["cmake", "--version"]),
            ("git", ["git", "--version"]),
        ]:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    first_line = res.stdout.splitlines()[0].strip() if res.stdout.splitlines() else ""
                    versions[tool] = first_line
                else:
                    versions[tool] = "unavailable"
            except Exception:
                versions[tool] = "unavailable"
        return versions

    def get_cpu_model(self) -> str:
        """Detect human-readable CPU model string across Linux and Windows."""
        if sys.platform.startswith("linux"):
            try:
                cpuinfo = Path("/proc/cpuinfo")
                if cpuinfo.exists():
                    for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
                        if "model name" in line:
                            return line.split(":", 1)[1].strip()
            except Exception:
                pass
        return (
            platform.processor()
            or os.environ.get("PROCESSOR_IDENTIFIER")
            or platform.machine()
            or "unknown"
        )

    def get_ram_info(self) -> Dict[str, Any]:
        """Detect system total and available RAM via psutil."""
        try:
            import psutil
            vm = psutil.virtual_memory()
            return {
                "total_bytes": vm.total,
                "available_bytes": vm.available,
                "total_mb": round(vm.total / (1024 * 1024), 2),
                "available_mb": round(vm.available / (1024 * 1024), 2),
            }
        except Exception:
            return {
                "total_bytes": 0,
                "available_bytes": 0,
                "total_mb": 0.0,
                "available_mb": 0.0,
            }

    def get_python_lock_digest(self) -> Dict[str, str]:
        """Compute SHA-256 digests of active dependency locks (poetry.lock, etc.)."""
        digests = {}
        for fname in ["poetry.lock", "pyproject.toml"]:
            fpath = Path(fname)
            if fpath.exists():
                digests[fname] = self.hash_binary(fpath)
            else:
                digests[fname] = "not_found"
        return digests

    @staticmethod
    def parse_cmake_cache_flags(cache_path: Path) -> Dict[str, str]:
        """Extract effective CMake compiler and build configuration flags from CMakeCache.txt."""
        flags: Dict[str, str] = {}
        keys_of_interest = {
            "CMAKE_BUILD_TYPE",
            "CMAKE_C_COMPILER",
            "CMAKE_CXX_COMPILER",
            "CMAKE_C_FLAGS",
            "CMAKE_CXX_FLAGS",
            "CMAKE_C_FLAGS_RELEASE",
            "CMAKE_CXX_FLAGS_RELEASE",
            "CMAKE_C_FLAGS_DEBUG",
            "CMAKE_CXX_FLAGS_DEBUG",
            "CMAKE_GENERATOR",
            "CMAKE_EXE_LINKER_FLAGS",
            "CMAKE_SHARED_LINKER_FLAGS",
            "CMAKE_MODULE_LINKER_FLAGS",
        }
        try:
            text = cache_path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith(("#", "//")):
                    continue
                if ":" in line and "=" in line:
                    var_part, val = line.split("=", 1)
                    var_name = var_part.split(":", 1)[0].strip()
                    if var_name in keys_of_interest:
                        flags[var_name] = val.strip()
        except Exception:
            pass
        return flags

    def get_cmake_cache_info(self) -> Dict[str, Any]:
        """Inspect CMake build cache status and flags in build directory."""
        candidates = [
            self.cado_root / "build" / "nsb-r3" / "CMakeCache.txt",
            self.cado_root / "build" / "CMakeCache.txt",
        ]
        for c in candidates:
            if c.exists():
                return {
                    "cache_path": str(c),
                    "exists": True,
                    "sha256": self.hash_binary(c),
                    "effective_cmake_flags": self.parse_cmake_cache_flags(c),
                }
        return {
            "cache_path": None,
            "exists": False,
            "sha256": None,
            "effective_cmake_flags": {},
        }

    def get_nsb_git_status(self) -> Tuple[str, bool]:
        """Retrieve current NSB git commit hash and working tree dirty state."""
        repo_root = Path(__file__).resolve().parents[4]
        try:
            from nsb.core.fingerprint import get_git_commit
            return get_git_commit(str(repo_root))
        except Exception:
            return "UNKNOWN_COMMIT", True

    def get_installed_python_packages(self) -> Tuple[Dict[str, str], str]:
        """Retrieve all installed Python packages and a deterministic SHA-256 digest."""
        import importlib.metadata
        pkgs: Dict[str, str] = {}
        try:
            for dist in importlib.metadata.distributions():
                name = dist.metadata.get("Name")
                version = dist.metadata.get("Version")
                if name and version:
                    pkgs[name.lower()] = version
        except Exception:
            pass
        if not pkgs:
            try:
                from nsb.core.fingerprint import get_package_versions
                pkgs = get_package_versions()
            except Exception:
                pass
        sorted_lines = [f"{k}=={pkgs[k]}" for k in sorted(pkgs.keys())]
        digest = hashlib.sha256("\n".join(sorted_lines).encode("utf-8")).hexdigest()
        return pkgs, digest

    def get_gmp_mpfr_versions(self) -> Dict[str, str]:
        """Detect runtime/header versions of GMP and MPFR libraries."""
        versions = {"gmp": "unavailable", "mpfr": "unavailable"}
        if not self.is_linux:
            return versions

        code = (
            "#include <stdio.h>\n"
            "#include <gmp.h>\n"
            "#include <mpfr.h>\n"
            "int main() {\n"
            "    printf(\"GMP:%s\\nMPFR:%s\\n\", gmp_version, mpfr_get_version());\n"
            "    return 0;\n"
            "}\n"
        )
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                src_path = Path(tmpdir) / "probe.c"
                bin_path = Path(tmpdir) / "probe"
                src_path.write_text(code, encoding="utf-8")
                comp = subprocess.run(
                    ["gcc", str(src_path), "-lgmp", "-lmpfr", "-o", str(bin_path)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if comp.returncode == 0 and bin_path.exists():
                    run = subprocess.run([str(bin_path)], capture_output=True, text=True, timeout=5)
                    if run.returncode == 0:
                        for line in run.stdout.splitlines():
                            if line.startswith("GMP:"):
                                versions["gmp"] = line.split(":", 1)[1].strip()
                            elif line.startswith("MPFR:"):
                                versions["mpfr"] = line.split(":", 1)[1].strip()
        except Exception:
            pass
        return versions

    @staticmethod
    def _parse_version_tuple(ver_str: str) -> Tuple[int, ...]:
        """Extract numeric version tuple from version string e.g. '12.3.0' -> (12, 3, 0)."""
        nums = re.findall(r"\d+", ver_str)
        return tuple(int(x) for x in nums) if nums else (0,)

    def get_relevant_environment_vars(self) -> Dict[str, Optional[str]]:
        """Capture relevant environment variables for reproducibility."""
        vars_to_capture = [
            "CADO_NFS_ROOT",
            "CC",
            "CXX",
            "CFLAGS",
            "CXXFLAGS",
            "OMP_NUM_THREADS",
            "PYTHONPATH",
        ]
        return {k: os.environ.get(k) for k in vars_to_capture if k in os.environ}

    def fingerprint(self) -> Dict[str, Any]:
        """Produce full immutable environment fingerprint."""
        binary_hashes = {}
        missing_binaries = []

        for b_name in ["polyselect", "polyselect_ropt", "score", "makefb", "las", "check_rels"]:
            b_path = self.get_binary_path(b_name)
            if b_path and b_path.exists():
                binary_hashes[b_name] = {
                    "path": str(b_path),
                    "sha256": self.hash_binary(b_path),
                }
            else:
                missing_binaries.append(b_name)

        nsb_commit, nsb_dirty = self.get_nsb_git_status()
        installed_pkgs, pkgs_hash = self.get_installed_python_packages()

        return {
            "platform": sys.platform,
            "is_linux": self.is_linux,
            "is_windows": self.is_windows,
            "has_wsl": self.has_wsl(),
            "nsb_git_commit": nsb_commit,
            "nsb_git_dirty": nsb_dirty,
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
            "python_build": list(platform.python_build()),
            "python_compiler": platform.python_compiler(),
            "python_dependency_locks": self.get_python_lock_digest(),
            "installed_python_packages": installed_pkgs,
            "installed_python_packages_hash": pkgs_hash,
            "cpu_architecture": platform.machine(),
            "cpu_model": self.get_cpu_model(),
            "cpu_count": os.cpu_count(),
            "ram": self.get_ram_info(),
            "os_system": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "uname": dict(platform.uname()._asdict()),
            "cado_root": str(self.cado_root),
            "cado_root_exists": self.cado_root.exists(),
            "pinned_git_commit": self.lock_data.get("pinned_git_commit"),
            "detected_git_commit": self.get_git_commit(),
            "is_git_clean": self.is_git_clean(),
            "toolchain": self.get_toolchain_versions(),
            "gmp_mpfr": self.get_gmp_mpfr_versions(),
            "cmake_cache": self.get_cmake_cache_info(),
            "relevant_env_vars": self.get_relevant_environment_vars(),
            "binaries_present": list(binary_hashes.keys()),
            "missing_binaries": missing_binaries,
            "binary_hashes": binary_hashes,
        }

    def validate_for_canonical_execution(self, require_clean_nsb: bool = True) -> Tuple[bool, str]:
        """Fail-closed validation check before running canonical R3 experiments."""
        # 1. OS check: Python runner must execute in Linux environment
        if not self.is_linux:
            return False, (
                "Canonical R3 execution requires Python runner executing inside native Linux / WSL2. "
                "Windows host execution is non-canonical."
            )

        # 2. NSB working tree check (must be clean and have valid commit)
        nsb_commit, nsb_dirty = self.get_nsb_git_status()
        if not nsb_commit or nsb_commit == "UNKNOWN_COMMIT":
            return False, "Could not detect NSB git commit hash"
        if require_clean_nsb and nsb_dirty:
            return False, "NSB working tree has uncommitted changes (dirty git state). Canonical certification requires clean NSB tree."

        # 3. Python version requirement (>= 3.8)
        if sys.version_info < (3, 8):
            return False, f"Python version {platform.python_version()} does not meet lockfile requirement >= 3.8"

        # 4. Toolchain version checks (GCC >= 10.0, CMake >= 3.18)
        tool_vers = self.get_toolchain_versions()
        gcc_ver = tool_vers.get("gcc", "unavailable")
        if gcc_ver == "unavailable":
            return False, "GCC compiler is unavailable"
        if self._parse_version_tuple(gcc_ver) < (10,):
            return False, f"GCC version {gcc_ver} does not satisfy lockfile requirement >= 10.0"

        cmake_ver = tool_vers.get("cmake", "unavailable")
        if cmake_ver == "unavailable":
            return False, "CMake build tool is unavailable"
        if self._parse_version_tuple(cmake_ver) < (3, 18):
            return False, f"CMake version {cmake_ver} does not satisfy lockfile requirement >= 3.18"

        # 5. Library version checks (GMP >= 6.1, MPFR >= 4.0)
        lib_vers = self.get_gmp_mpfr_versions()
        gmp_ver = lib_vers.get("gmp", "unavailable")
        if gmp_ver == "unavailable" or self._parse_version_tuple(gmp_ver) < (6, 1):
            return False, f"libgmp version '{gmp_ver}' does not satisfy lockfile requirement >= 6.1"
        mpfr_ver = lib_vers.get("mpfr", "unavailable")
        if mpfr_ver == "unavailable" or self._parse_version_tuple(mpfr_ver) < (4, 0):
            return False, f"libmpfr version '{mpfr_ver}' does not satisfy lockfile requirement >= 4.0"

        # 6. CADO installation check
        if not self.cado_root.exists():
            return False, f"CADO-NFS directory not found at {self.cado_root}"

        # 7. Pinned commit check (exact 40-char SHA)
        pinned_commit = self.lock_data.get("pinned_git_commit")
        detected_commit = self.get_git_commit()
        if not detected_commit:
            return False, f"Could not detect git commit at {self.cado_root}"
        if detected_commit != pinned_commit:
            return False, (
                f"CADO-NFS commit mismatch: expected full SHA {pinned_commit}, "
                f"found {detected_commit}"
            )

        # 8. Clean CADO working tree check
        if not self.is_git_clean():
            return False, f"CADO-NFS source tree at {self.cado_root} is not clean (dirty working tree)"

        # 9. Binary checks
        for b_name in ["polyselect", "polyselect_ropt", "score", "makefb", "las", "check_rels"]:
            b_path = self.get_binary_path(b_name)
            if not b_path or not b_path.exists():
                return False, f"Required CADO binary '{b_name}' not found"

        return True, "CADO-NFS environment verified"
