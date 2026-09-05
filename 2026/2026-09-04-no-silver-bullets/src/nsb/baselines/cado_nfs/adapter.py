"""Execution adapter for discrete CADO-NFS binaries with high-resolution CPU accounting.

Eliminates the sequential-controller CPU undercounting bug by executing and
measuring each binary independently:
    polyselect -> polyselect_ropt -> score -> makefb -> las
and recording process CPU (user + system) and wall-clock times per stage.
"""

import os
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List, Optional, Union
import psutil
from pydantic import BaseModel, Field

from nsb.baselines.cado_nfs.environment import CadoEnvironment


class CommandExecutionResult(BaseModel):
    """Result of an individual discrete binary execution."""

    command: List[str]
    binary_name: str
    returncode: int
    stdout: str
    stderr: str
    wall_seconds: float
    cpu_seconds: float
    max_rss_mb: float
    children_detected: bool = False


class CadoSubprocessAdapter:
    """Manages discrete invocations of CADO-NFS executables."""

    def __init__(
        self,
        environment: Optional[CadoEnvironment] = None,
        use_wsl_bridge: bool = False,
        wsl_distro: Optional[str] = None,
    ):
        self.env = environment or CadoEnvironment()
        self.use_wsl_bridge = use_wsl_bridge
        self.wsl_distro = wsl_distro

    def build_command(self, binary_name: str, args: List[str]) -> List[str]:
        """Construct command line arguments for binary execution."""
        b_path = self.env.get_binary_path(binary_name)
        b_str = str(b_path) if b_path else binary_name

        if self.use_wsl_bridge:
            wsl_cmd = ["wsl.exe"]
            if self.wsl_distro:
                wsl_cmd.extend(["-d", self.wsl_distro])
            return wsl_cmd + [b_str] + [str(a) for a in args]

        return [b_str] + [str(a) for a in args]

    def run_binary(
        self,
        binary_name: str,
        args: List[str],
        timeout_seconds: float = 300.0,
        cwd: Optional[Union[str, Path]] = None,
    ) -> CommandExecutionResult:
        """Execute a discrete CADO binary with file-backed stream capture and CPU accounting."""
        cmd = self.build_command(binary_name, args)
        work_dir = Path(cwd) if cwd else Path.cwd()
        work_dir.mkdir(parents=True, exist_ok=True)

        t_wall_start = time.time()
        t_cpu_start = time.process_time()
        timestamp_ms = int(t_wall_start * 1000)

        stdout_file_path = work_dir / f"{binary_name}_{timestamp_ms}.stdout.log"
        stderr_file_path = work_dir / f"{binary_name}_{timestamp_ms}.stderr.log"

        max_rss_bytes = 0
        seen_pids_cpu: Dict[int, float] = {}
        children_detected = False

        with open(stdout_file_path, "w", encoding="utf-8", errors="replace") as f_out, \
             open(stderr_file_path, "w", encoding="utf-8", errors="replace") as f_err:

            proc = subprocess.Popen(
                cmd,
                stdout=f_out,
                stderr=f_err,
                cwd=str(work_dir),
            )

            try:
                ps_proc = psutil.Process(proc.pid)
            except Exception:
                ps_proc = None

            try:
                while proc.poll() is None:
                    if ps_proc is not None:
                        try:
                            # Main process memory & CPU
                            current_mem = ps_proc.memory_info().rss
                            ct = ps_proc.cpu_times()
                            seen_pids_cpu[proc.pid] = max(
                                seen_pids_cpu.get(proc.pid, 0.0),
                                ct.user + ct.system,
                            )

                            # Descendant processes
                            children = ps_proc.children(recursive=True)
                            if children:
                                children_detected = True
                                for ch in children:
                                    try:
                                        current_mem += ch.memory_info().rss
                                        ch_ct = ch.cpu_times()
                                        seen_pids_cpu[ch.pid] = max(
                                            seen_pids_cpu.get(ch.pid, 0.0),
                                            ch_ct.user + ch_ct.system,
                                        )
                                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                                        pass

                            if current_mem > max_rss_bytes:
                                max_rss_bytes = current_mem
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                    elapsed_wall = time.time() - t_wall_start
                    if elapsed_wall > timeout_seconds:
                        proc.kill()
                        raise TimeoutError(
                            f"Binary '{binary_name}' exceeded timeout of {timeout_seconds}s "
                            f"(wall: {elapsed_wall:.1f}s)"
                        )
                    time.sleep(0.05)

                proc.wait()
            except TimeoutError:
                proc.kill()
                proc.wait()
                raise
            except Exception as exc:
                proc.kill()
                proc.wait()
                raise RuntimeError(f"Error running binary '{binary_name}': {exc}")

        # Final capture on main process
        if ps_proc is not None:
            try:
                ct = ps_proc.cpu_times()
                seen_pids_cpu[proc.pid] = max(seen_pids_cpu.get(proc.pid, 0.0), ct.user + ct.system)
            except Exception:
                pass

        t_wall_elapsed = time.time() - t_wall_start

        # Read back complete stdout / stderr from disk
        stdout = stdout_file_path.read_text(encoding="utf-8", errors="replace") if stdout_file_path.exists() else ""
        stderr = stderr_file_path.read_text(encoding="utf-8", errors="replace") if stderr_file_path.exists() else ""

        # Cumulative CPU time across all observed PIDs (main process + any descendants)
        total_tracked_cpu = sum(seen_pids_cpu.values())
        cpu_sec = total_tracked_cpu if total_tracked_cpu > 0 else max(0.001, time.process_time() - t_cpu_start)
        max_rss_mb = max_rss_bytes / (1024 * 1024)

        return CommandExecutionResult(
            command=cmd,
            binary_name=binary_name,
            returncode=proc.returncode,
            stdout=stdout,
            stderr=stderr,
            wall_seconds=round(t_wall_elapsed, 4),
            cpu_seconds=round(cpu_sec, 4),
            max_rss_mb=round(max_rss_mb, 2),
            children_detected=children_detected,
        )
