"""Resource-governed execution engine tracking child CPU time, wall time, peak memory, and timeouts."""

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import psutil
from pydantic import BaseModel, Field

from nsb.core.hashing import hash_file
from nsb.verifier.factor import FactorVerificationResult


class ExecutionResult(BaseModel):
    run_id: str
    experiment_id: str
    instance_id: str
    bit_length: int
    seed: int
    exit_code: int
    wall_seconds: float
    cpu_seconds: float
    peak_rss_mb: float
    timeout: bool
    resource_killed: bool = False
    kill_reason: Optional[str] = None
    metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    verification: Dict[str, Any]
    artifacts: Dict[str, str] = Field(default_factory=dict)


def kill_process_tree(parent_pid: int, timeout: float = 2.0) -> None:
    """Recursively kill parent process and all of its spawned children."""
    try:
        parent = psutil.Process(parent_pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        gone, alive = psutil.wait_procs(children, timeout=timeout)
        for proc in alive:
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        try:
            parent.kill()
            parent.wait(timeout=timeout)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass


class SubprocessRunner:
    """Executes commands under strict wall-time, CPU, and memory budgets, capturing output artifacts."""

    def __init__(self, artifacts_base_dir: Union[str, Path] = "experiments/artifacts"):
        self.artifacts_base_dir = Path(artifacts_base_dir)

    def run_command(
        self,
        command: List[str],
        experiment_id: str,
        run_id: str,
        max_wall_seconds: float = 60.0,
        max_cpu_seconds: Optional[float] = None,
        max_rss_mb: Optional[float] = None,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, float, float, float, bool, bool, Optional[str], Path, Path]:
        """Execute command line and measure real child process wall time, CPU time, and peak memory.

        Measures total CPU and RSS across the entire process tree (parent and all spawned children).

        Returns:
            Tuple[exit_code, wall_seconds, child_cpu_seconds, peak_rss_mb, timeout_occurred, resource_killed, kill_reason, stdout_path, stderr_path]
        """
        run_artifact_dir = self.artifacts_base_dir / experiment_id / run_id
        run_artifact_dir.mkdir(parents=True, exist_ok=True)

        stdout_path = run_artifact_dir / "stdout.log"
        stderr_path = run_artifact_dir / "stderr.log"

        start_wall = time.perf_counter()
        timeout_occurred = False
        resource_killed = False
        kill_reason = None
        exit_code = 0
        child_cpu_sec = 0.0
        peak_rss_mb = 0.0

        with open(stdout_path, "wb") as f_out, open(stderr_path, "wb") as f_err:
            proc = subprocess.Popen(
                command,
                cwd=cwd,
                env=env or os.environ.copy(),
                stdout=f_out,
                stderr=f_err,
            )

            try:
                ps_proc = psutil.Process(proc.pid)
            except psutil.NoSuchProcess:
                ps_proc = None

            # Monitor loop
            poll_interval = 0.05
            while proc.poll() is None:
                elapsed_wall = time.perf_counter() - start_wall
                if elapsed_wall >= max_wall_seconds:
                    timeout_occurred = True
                    kill_reason = f"Wall-clock timeout ({elapsed_wall:.2f}s >= {max_wall_seconds:.2f}s)"
                    break

                if ps_proc:
                    try:
                        procs = [ps_proc]
                        try:
                            procs.extend(ps_proc.children(recursive=True))
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                        curr_cpu = 0.0
                        curr_rss = 0.0
                        for p in procs:
                            try:
                                t = p.cpu_times()
                                curr_cpu += (t.user + t.system)
                                curr_rss += p.memory_info().rss / (1024.0 * 1024.0)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass

                        child_cpu_sec = max(child_cpu_sec, curr_cpu)
                        peak_rss_mb = max(peak_rss_mb, curr_rss)

                        if max_cpu_seconds is not None and child_cpu_sec >= max_cpu_seconds:
                            resource_killed = True
                            kill_reason = f"CPU budget exceeded ({child_cpu_sec:.2f}s >= {max_cpu_seconds:.2f}s)"
                            break

                        if max_rss_mb is not None and peak_rss_mb >= max_rss_mb:
                            resource_killed = True
                            kill_reason = f"Memory budget exceeded ({peak_rss_mb:.2f}MB >= {max_rss_mb:.2f}MB)"
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                time.sleep(poll_interval)

            if timeout_occurred or resource_killed:
                kill_process_tree(proc.pid)
                exit_code = -1
            else:
                exit_code = proc.returncode

        elapsed_wall = time.perf_counter() - start_wall

        return (
            exit_code,
            round(elapsed_wall, 4),
            round(child_cpu_sec, 4),
            round(peak_rss_mb, 2),
            timeout_occurred,
            resource_killed,
            kill_reason,
            stdout_path,
            stderr_path,
        )
