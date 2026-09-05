"""Authoritative supervisor and monitored sandbox runner for NFS candidate selection."""

import hashlib
import inspect
import json
import multiprocessing as mp
import os
import pickle
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import psutil

from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector
from nsb.baselines.cado_nfs.profiles import CadoParameterProfile
from nsb.baselines.cado_nfs.verifier import verify_nfs_polynomial_pair
from nsb.candidates.models import (
    CandidateExecutionRecord,
    CandidateInterventionLevel,
    CandidateOutput,
    NfsCandidateSelector,
    RunnerExecutionEvidence,
    SearchBudget,
)
from nsb.candidates.sandbox import CgroupV2Sandbox, build_isolated_env
from nsb.core.hashing import hash_file, hash_string


class MonitoredCandidateRunner:
    """Supervisor executing candidate and baseline selectors through unified sandboxing."""

    def __init__(
        self,
        artifact_dir: Optional[Path] = None,
        cgroup_root: Optional[Path] = None,
        require_containment: bool = False,
    ):
        self.artifact_dir = Path(artifact_dir or "reports/candidates").resolve()
        self.cgroup_root = Path(cgroup_root or "/sys/fs/cgroup/nsb")
        self.require_containment = require_containment
        self.selector = CadoPolynomialSelector()

    def resolve_paired_budget(
        self,
        N: int,
        profile: CadoParameterProfile,
        baseline_selector_cpu: Optional[float] = None,
        baseline_records: Optional[List[Dict[str, Any]]] = None,
        budget_multiplier: float = 1.0,
    ) -> SearchBudget:
        """Derive search budget strictly paired to the 1.00x baseline CADO selector CPU."""
        paired_cpu = baseline_selector_cpu

        if paired_cpu is None and baseline_records:
            for rec in baseline_records:
                if str(rec.get("modulus_n", "")) == str(N) or rec.get("N") == N:
                    poly_block = rec.get("polyselect", {})
                    if "cpu_seconds" in poly_block:
                        paired_cpu = float(poly_block["cpu_seconds"])
                        break

        if paired_cpu is None or paired_cpu <= 0:
            # Fallback estimation for public development / smoke tests
            paired_cpu = max(1.0, float(profile.target_digits) * 0.2)

        max_cpu = float(paired_cpu * budget_multiplier)
        return SearchBudget(
            max_cpu_seconds=max_cpu,
            max_wall_seconds=600.0,
            max_peak_rss_mb=4096.0,
            threads=1,
            allow_gpu=False,
            allow_network=False,
        )

    def _run_monitored_stage(
        self,
        fn: Callable,
        args: Tuple,
        kwargs: Dict[str, Any],
        stage_name: str,
        budget: SearchBudget,
        accumulated_cpu: float,
        t_start_wall: float,
        sandbox: Optional[CgroupV2Sandbox],
        has_cgroup: bool,
        run_dir: Path,
    ) -> Tuple[bool, Any, float, float, str, str]:
        """Execute a helper stage under process containment with active supervisor watchdog.

        Returns:
            (success, result, stage_cpu, stage_wall, termination_status, termination_reason)
        """
        elapsed_so_far = max(0.0, time.monotonic() - t_start_wall)
        if elapsed_so_far > budget.max_wall_seconds:
            msg = f"{stage_name} exceeded wall timeout before start: {elapsed_so_far:.2f}s > {budget.max_wall_seconds:.2f}s"
            return False, None, 0.0, elapsed_so_far, "TIMEOUT", msg

        initial_cgroup_cpu = 0.0
        if has_cgroup and sandbox:
            try:
                initial_cgroup_cpu = sandbox.read_cpu_seconds()
            except RuntimeError as e:
                return False, None, 0.0, elapsed_so_far, "ERROR", f"Authoritative cgroup CPU unreadable: {e}"

        current_total = initial_cgroup_cpu if has_cgroup else accumulated_cpu
        if current_total > budget.max_cpu_seconds:
            overshoot = current_total - budget.max_cpu_seconds
            msg = (
                f"{stage_name} exceeded CPU budget before start: {current_total:.4f}s > {budget.max_cpu_seconds:.4f}s "
                f"(overshoot: {overshoot:.4f}s)"
            )
            return False, None, 0.0, elapsed_so_far, "BUDGET_EXCEEDED_REJECTED", msg

        fork_ctx = None
        if hasattr(mp, "get_context") and sys.platform != "win32":
            try:
                fork_ctx = mp.get_context("fork")
            except ValueError:
                fork_ctx = None

        result_file = run_dir / f"stage_{uuid.uuid4().hex[:8]}_result.pkl"

        if fork_ctx is not None:
            ready_r, ready_w = os.pipe()
            go_r, go_w = os.pipe()

            def _worker_entry():
                os.close(ready_r)
                os.close(go_w)
                try:
                    # 1. Environment isolation: strip sensitive variables, enforce thread caps
                    isolated_env = build_isolated_env(
                        allow_gpu=budget.allow_gpu,
                        allow_network=budget.allow_network,
                    )
                    src_path = str(Path(__file__).resolve().parents[2])
                    existing_pp = isolated_env.get("PYTHONPATH", "")
                    isolated_env["PYTHONPATH"] = f"{src_path}:{existing_pp}" if existing_pp else src_path
                    os.environ.clear()
                    os.environ.update(isolated_env)

                    # 2. Namespace, session, and core affinity restrictions
                    if sys.platform != "win32":
                        try:
                            os.setpgrp()
                        except Exception:
                            pass
                        if hasattr(os, "sched_setaffinity"):
                            try:
                                os.sched_setaffinity(0, {0})
                            except Exception:
                                pass

                        # Network namespace isolation
                        if sys.platform.startswith("linux") and not budget.allow_network:
                            import ctypes
                            libc = ctypes.CDLL(None, use_errno=True)
                            CLONE_NEWUSER = 0x10000000
                            CLONE_NEWNET = 0x40000000
                            res = libc.unshare(CLONE_NEWNET)
                            if res != 0:
                                res = libc.unshare(CLONE_NEWUSER | CLONE_NEWNET)
                            if res != 0:
                                err = ctypes.get_errno()
                                raise RuntimeError(f"Failed to isolate network namespace: unshare returned errno {err}")

                    # 3. Synchronization handshake: signal READY to supervisor
                    os.write(ready_w, f"READY {os.getpid()}\n".encode())
                    os.close(ready_w)

                    # 4. Block until supervisor attaches PID to cgroup and sends GO
                    signal_bytes = os.read(go_r, 1024)
                    os.close(go_r)
                    signal = signal_bytes.decode().strip()
                    if signal != "GO":
                        sys.exit(2)

                    # 5. Now inside containment: execute helper code
                    t0_c = time.process_time()
                    t0_w = time.monotonic()
                    r = fn(*args, **kwargs)
                    c_time = time.process_time() - t0_c
                    w_time = max(0.0, time.monotonic() - t0_w)

                    # 6. File-backed result serialization prevents IPC queue/pipe deadlock
                    payload = {"status": "SUCCESS", "result": r, "cpu_time": c_time, "wall_time": w_time}
                    with open(result_file, "wb") as f:
                        pickle.dump(payload, f)
                    sys.exit(0)
                except Exception as e:
                    try:
                        os.write(ready_w, f"SETUP_ERROR {e}\n".encode())
                        os.close(ready_w)
                    except Exception:
                        pass
                    payload = {"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}
                    try:
                        with open(result_file, "wb") as f:
                            pickle.dump(payload, f)
                    except Exception:
                        pass
                    sys.exit(1)

            proc = fork_ctx.Process(target=_worker_entry)
            proc.start()
            os.close(ready_w)
            os.close(go_r)

            # Wait for child READY handshake
            handshake_timeout = min(10.0, max(0.1, budget.max_wall_seconds - (time.monotonic() - t_start_wall)))
            rlist, _, _ = select.select([ready_r], [], [], handshake_timeout)
            if not rlist:
                os.close(ready_r)
                os.close(go_w)
                try:
                    proc.kill()
                except Exception:
                    pass
                proc.join(timeout=0.2)
                return False, None, 0.0, max(0.0, time.monotonic() - t_start_wall), "TIMEOUT", f"{stage_name} failed to signal READY within {handshake_timeout:.2f}s"

            ready_line = os.read(ready_r, 1024).decode().strip()
            os.close(ready_r)

            if not ready_line.startswith("READY"):
                os.close(go_w)
                try:
                    proc.kill()
                except Exception:
                    pass
                proc.join(timeout=0.2)
                err_msg = f"{stage_name} failed containment setup: '{ready_line}'"
                if self.require_containment:
                    raise RuntimeError(f"Canonical execution rejected: {err_msg}")
                return False, None, 0.0, max(0.0, time.monotonic() - t_start_wall), "ERROR", err_msg

            pid = proc.pid
            attached = False
            if has_cgroup and sandbox:
                attached = sandbox.attach_pid(pid)

            if has_cgroup and not attached:
                # Attachment failed: abort child before it ever executes helper code
                try:
                    os.write(go_w, b"ABORT\n")
                except Exception:
                    pass
                os.close(go_w)
                try:
                    proc.kill()
                except Exception:
                    pass
                proc.join(timeout=0.2)
                if self.require_containment:
                    raise RuntimeError(f"Canonical execution rejected: failed to attach helper PID {pid} to cgroup at {sandbox.cgroup_path}.")
                return False, None, 0.0, max(0.0, time.monotonic() - t_start_wall), "ERROR", f"Failed to attach helper PID {pid} to cgroup at {sandbox.cgroup_path}"

            # Successfully attached: signal GO to unblock worker
            try:
                os.write(go_w, b"GO\n")
            except Exception:
                pass
            os.close(go_w)

            ps_p = None
            try:
                ps_p = psutil.Process(pid)
            except Exception:
                pass

            t_stage_start = time.monotonic()
            stage_cpu = 0.0
            status = "COMPLETED"
            reason = "Normal completion"

            while proc.is_alive():
                time.sleep(0.005)
                wall_elapsed = max(0.0, time.monotonic() - t_start_wall)
                if wall_elapsed > budget.max_wall_seconds:
                    if has_cgroup and sandbox:
                        sandbox.kill_all()
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    proc.join(timeout=0.2)
                    status = "TIMEOUT"
                    reason = f"{stage_name} exceeded wall timeout: {wall_elapsed:.2f}s > {budget.max_wall_seconds:.2f}s"
                    break

                if has_cgroup and sandbox and attached:
                    try:
                        total_cgroup_cpu = sandbox.read_cpu_seconds()
                    except RuntimeError as e:
                        status = "ERROR"
                        reason = f"Authoritative cgroup CPU unreadable: {e}"
                        sandbox.kill_all()
                        try:
                            proc.kill()
                        except Exception:
                            pass
                        proc.join(timeout=0.2)
                        break
                    stage_cpu = max(0.0, total_cgroup_cpu - initial_cgroup_cpu)
                else:
                    current_cpu = 0.0
                    if ps_p is not None:
                        try:
                            ct = ps_p.cpu_times()
                            current_cpu = ct.user + ct.system
                            for ch in ps_p.children(recursive=True):
                                c_ct = ch.cpu_times()
                                current_cpu += c_ct.user + c_ct.system
                        except Exception:
                            pass
                    stage_cpu = max(stage_cpu, current_cpu)
                    total_cgroup_cpu = accumulated_cpu + stage_cpu

                if total_cgroup_cpu > budget.max_cpu_seconds:
                    if has_cgroup and sandbox:
                        sandbox.kill_all()
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    proc.join(timeout=0.2)
                    status = "BUDGET_EXCEEDED_REJECTED"
                    overshoot = total_cgroup_cpu - budget.max_cpu_seconds
                    reason = (
                        f"{stage_name} exceeded CPU budget: {total_cgroup_cpu:.4f}s > {budget.max_cpu_seconds:.4f}s "
                        f"(overshoot: {overshoot:.4f}s)"
                    )
                    break

            proc.join(timeout=0.5)
            stage_wall = max(0.0, time.monotonic() - t_stage_start)

            if status != "COMPLETED":
                return False, None, stage_cpu, stage_wall, status, reason

            if result_file.is_file():
                try:
                    with open(result_file, "rb") as f:
                        payload = pickle.load(f)
                    if payload.get("status") == "SUCCESS":
                        res = payload["result"]
                        if has_cgroup and sandbox and attached:
                            try:
                                stage_cpu = max(0.0, sandbox.read_cpu_seconds() - initial_cgroup_cpu)
                            except RuntimeError as e:
                                return False, None, 0.0, stage_wall, "ERROR", f"Authoritative cgroup CPU unreadable: {e}"
                        else:
                            stage_cpu = payload.get("cpu_time", stage_cpu)
                            if hasattr(res, "cpu_seconds"):
                                stage_cpu = max(stage_cpu, float(res.cpu_seconds))
                            elif isinstance(res, tuple) and len(res) >= 2 and isinstance(res[1], (int, float)):
                                stage_cpu = max(stage_cpu, float(res[1]))
                        return True, res, stage_cpu, stage_wall, "COMPLETED", "Normal completion"
                    else:
                        err = payload.get("error", "Unknown error")
                        return False, None, stage_cpu, stage_wall, "ERROR", f"{stage_name} raised exception: {err}"
                except Exception as e:
                    return False, None, stage_cpu, stage_wall, "ERROR", f"Failed to load {stage_name} result file: {e}"
            else:
                if proc.exitcode != 0:
                    return False, None, stage_cpu, stage_wall, "ERROR", f"{stage_name} worker process exited with code {proc.exitcode}"
                return False, None, stage_cpu, stage_wall, "ERROR", f"{stage_name} worker exited without returning a result"

        else:
            # Fallback for environments without fork (e.g. Windows)
            t_stage_start = time.monotonic()
            t0_cpu = time.process_time()
            try:
                res = fn(*args, **kwargs)
                stage_wall = max(0.0, time.monotonic() - t_stage_start)
                stage_cpu = time.process_time() - t0_cpu
                total_cpu = accumulated_cpu + stage_cpu
                total_wall = max(0.0, time.monotonic() - t_start_wall)
                if total_wall > budget.max_wall_seconds:
                    msg = f"{stage_name} exceeded wall timeout: {total_wall:.2f}s > {budget.max_wall_seconds:.2f}s"
                    return False, None, stage_cpu, stage_wall, "TIMEOUT", msg
                if total_cpu > budget.max_cpu_seconds:
                    overshoot = total_cpu - budget.max_cpu_seconds
                    msg = f"{stage_name} exceeded CPU budget: {total_cpu:.4f}s > {budget.max_cpu_seconds:.4f}s (overshoot: {overshoot:.4f}s)"
                    return False, None, stage_cpu, stage_wall, "BUDGET_EXCEEDED_REJECTED", msg
                return True, res, stage_cpu, stage_wall, "COMPLETED", "Normal completion"
            except Exception as e:
                stage_wall = max(0.0, time.monotonic() - t_stage_start)
                stage_cpu = time.process_time() - t0_cpu
                return False, None, stage_cpu, stage_wall, "ERROR", f"{stage_name} raised exception: {e}"

    def run_candidate(
        self,
        candidate: NfsCandidateSelector,
        N: int,
        profile: CadoParameterProfile,
        budget: SearchBudget,
        seed: int,
        instance_id: Optional[str] = None,
    ) -> CandidateExecutionRecord:
        """Execute candidate selector under process containment and verify against protocol constraints."""
        # Validate budget constraints upfront
        if budget.threads != 1 or budget.allow_gpu or budget.allow_network:
            raise ValueError(
                f"Invalid candidate search budget: threads={budget.threads}, "
                f"allow_gpu={budget.allow_gpu}, allow_network={budget.allow_network}"
            )

        # Unique, collision-free run directory per execution
        unique_run_id = f"{candidate.method_id}_{instance_id or 'instance'}_{uuid.uuid4().hex[:8]}_{int(time.time() * 1000)}"
        run_dir = self.artifact_dir / unique_run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        task_file = run_dir / "task.json"
        stdout_path = run_dir / "stdout.log"
        stderr_path = run_dir / "stderr.log"
        output_file = run_dir / "candidate_output.json"
        poly_path = run_dir / "selected.poly"

        # Initialize sandbox
        sandbox = CgroupV2Sandbox(
            cgroup_root=self.cgroup_root,
            sandbox_id=unique_run_id,
        )
        has_cgroup = sandbox.setup_cgroup(budget)

        if self.require_containment and not has_cgroup:
            raise RuntimeError(
                f"Canonical execution rejected: cgroup v2 containment unavailable at {self.cgroup_root}. "
                "Canonical evaluation strictly requires kernel-level cgroup v2 process containment."
            )

        # Prepare candidate serialization for isolated worker
        candidate_cls = type(candidate)
        candidate_module = candidate_cls.__module__
        candidate_name = candidate_cls.__name__
        candidate_code = None

        # If candidate class was defined dynamically (e.g. inside a test script), extract source
        if candidate_module in ("__main__", None) or candidate_module.startswith("test_") or "pytest" in candidate_module:
            try:
                candidate_code = inspect.getsource(candidate_cls)
            except Exception:
                pass

        t_start_wall = time.monotonic()
        pool_effective_cpu = 0.0
        worker_effective_cpu = 0.0
        ropt_effective_cpu = 0.0
        cgroup_t0 = 0.0
        pool_wall = 0.0
        actual_cpu = 0.0
        peak_rss = 0.0
        total_selector_cpu = 0.0
        overshoot = 0.0
        worker_pid: Optional[int] = None
        attached = False
        termination_status = "COMPLETED"
        termination_reason = "Normal completion"
        rejection_reason = ""
        passed = False
        candidate_out: Optional[CandidateOutput] = None
        candidate_pool_dicts: Optional[List[Dict[str, Any]]] = None
        candidate_pool_pairs: Optional[List[NfsPolynomialPair]] = None
        pair_hash = ""
        trace_hash = ""

        try:
            # 0. Initial authoritative CPU counter reading inside protected execution block
            if has_cgroup and sandbox:
                try:
                    cgroup_t0 = sandbox.read_cpu_seconds()
                except RuntimeError as e:
                    termination_status = "ERROR"
                    termination_reason = f"Authoritative cgroup CPU unreadable at start: {e}"
                    rejection_reason = termination_reason

            # 1. Helper Stage: Pool generation for POST_ROPT_RANKER under monitored containment
            if (
                candidate.intervention_level == CandidateInterventionLevel.POST_ROPT_RANKER
                and termination_status == "COMPLETED"
            ):
                pool_ok, pool_res, p_cpu, p_wall, p_status, p_reason = self._run_monitored_stage(
                    fn=self.selector.generate_stage1_pool,
                    args=(N, profile),
                    kwargs={"timeout_seconds": budget.max_wall_seconds, "run_ropt_on_candidates": True},
                    stage_name="Candidate pool generation",
                    budget=budget,
                    accumulated_cpu=0.0,
                    t_start_wall=t_start_wall,
                    sandbox=sandbox,
                    has_cgroup=has_cgroup,
                    run_dir=run_dir,
                )
                pool_wall = p_wall
                pool_cgroup_end = cgroup_t0
                if has_cgroup and sandbox:
                    try:
                        pool_cgroup_end = sandbox.read_cpu_seconds()
                    except RuntimeError as e:
                        termination_status = "ERROR"
                        termination_reason = f"Authoritative cgroup CPU unreadable: {e}"
                        rejection_reason = termination_reason
                pool_cgroup_cpu = max(0.0, pool_cgroup_end - cgroup_t0)
                pool_declared_cpu = 0.0
                if isinstance(pool_res, tuple) and len(pool_res) >= 2 and isinstance(pool_res[1], (int, float)):
                    pool_declared_cpu = float(pool_res[1])
                pool_effective_cpu = max(pool_cgroup_cpu, p_cpu, pool_declared_cpu)
                total_selector_cpu = max(pool_cgroup_end if (has_cgroup and sandbox) else 0.0, pool_effective_cpu)

                if not pool_ok:
                    termination_status = p_status
                    termination_reason = p_reason
                    rejection_reason = p_reason
                else:
                    if isinstance(pool_res, tuple) and len(pool_res) >= 1:
                        candidate_pool_pairs = pool_res[0]
                    else:
                        candidate_pool_pairs = pool_res
                    if candidate_pool_pairs is not None:
                        candidate_pool_dicts = [p.model_dump() for p in candidate_pool_pairs]

            # 2. Worker Subprocess Execution (only if still COMPLETED)
            if termination_status == "COMPLETED":
                task_payload = {
                    "candidate_module": candidate_module,
                    "candidate_class": candidate_name,
                    "candidate_kwargs": {},
                    "candidate_code": candidate_code,
                    "N": N,
                    "profile_name": profile.name,
                    "budget": budget.model_dump(),
                    "seed": seed,
                    "output_file": str(output_file),
                    "stdout_file": str(stdout_path),
                    "stderr_file": str(stderr_path),
                    "sync_handshake": has_cgroup,
                    "candidate_pool": candidate_pool_dicts,
                }
                task_file.write_text(json.dumps(task_payload, indent=2), encoding="utf-8")

                isolated_env = build_isolated_env(
                    allow_gpu=budget.allow_gpu,
                    allow_network=budget.allow_network,
                )
                src_path = str(Path(__file__).resolve().parents[2])
                existing_pp = isolated_env.get("PYTHONPATH", "")
                isolated_env["PYTHONPATH"] = f"{src_path}:{existing_pp}" if existing_pp else src_path

                cmd = [sys.executable, "-m", "nsb.candidates.worker", "--task-file", str(task_file)]
                if sys.platform.startswith("linux"):
                    if not budget.allow_network and shutil.which("unshare"):
                        cmd = ["unshare", "-rn"] + cmd
                    if shutil.which("taskset"):
                        cmd = ["taskset", "-c", "0"] + cmd

                start_new_session = sys.platform != "win32"
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=isolated_env,
                    text=True,
                    start_new_session=start_new_session,
                )
                worker_pid = proc.pid

                def _kill_worker():
                    if sys.platform != "win32":
                        try:
                            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                        except Exception:
                            try:
                                proc.kill()
                            except Exception:
                                pass
                    else:
                        try:
                            proc.kill()
                        except Exception:
                            pass

                if has_cgroup:
                    handshake_timeout = min(10.0, budget.max_wall_seconds)
                    ready_line = ""
                    try:
                        if sys.platform != "win32":
                            import select
                            rlist, _, _ = select.select([proc.stdout], [], [], handshake_timeout)
                            if rlist and proc.stdout:
                                ready_line = proc.stdout.readline()
                            else:
                                termination_status = "TIMEOUT"
                                termination_reason = f"Worker failed to signal READY within {handshake_timeout}s startup timeout"
                                _kill_worker()
                        else:
                            ready_line = proc.stdout.readline() if proc.stdout else ""

                        if "READY" in ready_line:
                            attached = sandbox.attach_pid(proc.pid)
                            if attached:
                                if proc.stdin:
                                    proc.stdin.write("GO\n")
                                    proc.stdin.flush()
                            else:
                                termination_status = "ERROR"
                                termination_reason = f"Failed to attach worker PID {proc.pid} to cgroup at {sandbox.cgroup_path}"
                                if proc.stdin:
                                    try:
                                        proc.stdin.write("ABORT\n")
                                        proc.stdin.flush()
                                    except Exception:
                                        pass
                                _kill_worker()
                        elif termination_status != "TIMEOUT":
                            err_msg = proc.stderr.read() if proc.stderr else ""
                            termination_status = "ERROR"
                            termination_reason = (
                                f"Worker failed containment handshake: '{ready_line.strip()}' "
                                f"(stderr: '{err_msg.strip()}')"
                            )
                            _kill_worker()
                    except Exception as e:
                        termination_status = "ERROR"
                        termination_reason = f"Failed during cgroup attachment: {e}"
                        _kill_worker()

                    if not attached or termination_status in ("ERROR", "TIMEOUT"):
                        if self.require_containment and not attached:
                            raise RuntimeError(f"Canonical execution rejected: {termination_reason}")

                cgroup_worker_start = cgroup_t0
                if has_cgroup and sandbox and attached:
                    try:
                        cgroup_worker_start = sandbox.read_cpu_seconds()
                    except RuntimeError as e:
                        if termination_status == "COMPLETED":
                            termination_status = "ERROR"
                            termination_reason = f"Authoritative cgroup CPU unreadable: {e}"

                if termination_status == "COMPLETED":
                    while proc.poll() is None:
                        time.sleep(0.01)
                        wall_elapsed = max(0.0, time.monotonic() - t_start_wall)

                        if has_cgroup and attached:
                            try:
                                current_cgroup = sandbox.read_cpu_seconds()
                            except RuntimeError as e:
                                termination_status = "ERROR"
                                termination_reason = f"Authoritative cgroup CPU unreadable: {e}"
                                sandbox.kill_all()
                                _kill_worker()
                                break
                            peak_rss = max(peak_rss, sandbox.read_peak_memory_mb())
                            worker_cgroup_cpu = max(0.0, current_cgroup - cgroup_worker_start)
                            worker_effective_cpu = max(worker_effective_cpu, worker_cgroup_cpu)
                            total_selector_cpu = max(current_cgroup, pool_effective_cpu + worker_effective_cpu)
                        else:
                            try:
                                p = psutil.Process(proc.pid)
                                ct = p.cpu_times()
                                current_cpu = ct.user + ct.system
                                for ch in p.children(recursive=True):
                                    c_ct = ch.cpu_times()
                                    current_cpu += c_ct.user + c_ct.system
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                current_cpu = 0.0
                            worker_effective_cpu = max(worker_effective_cpu, current_cpu)
                            total_selector_cpu = pool_effective_cpu + worker_effective_cpu

                        if wall_elapsed > budget.max_wall_seconds:
                            termination_status = "TIMEOUT"
                            termination_reason = f"Candidate exceeded wall timeout: {wall_elapsed:.2f}s > {budget.max_wall_seconds:.2f}s"
                            if has_cgroup:
                                sandbox.kill_all()
                            _kill_worker()
                            break

                        if total_selector_cpu > budget.max_cpu_seconds:
                            termination_status = "BUDGET_EXCEEDED_REJECTED"
                            overshoot = total_selector_cpu - budget.max_cpu_seconds
                            termination_reason = (
                                f"Total selector CPU exceeded budget: {total_selector_cpu:.4f}s > {budget.max_cpu_seconds:.4f}s "
                                f"(overshoot: {overshoot:.4f}s)"
                            )
                            if has_cgroup:
                                sandbox.kill_all()
                            _kill_worker()
                            break

                    try:
                        proc.wait(timeout=2.0)
                    except Exception:
                        if has_cgroup:
                            sandbox.kill_all()
                        _kill_worker()

                    if proc.returncode != 0 and termination_status == "COMPLETED":
                        termination_status = "ERROR"
                        err_text = stderr_path.read_text(encoding="utf-8") if stderr_path.exists() else ""
                        termination_reason = f"Worker exited with code {proc.returncode}: {err_text.strip()}"

                    if has_cgroup and attached:
                        try:
                            current_cgroup = sandbox.read_cpu_seconds()
                            peak_rss = max(peak_rss, sandbox.read_peak_memory_mb())
                            worker_cgroup_cpu = max(0.0, current_cgroup - cgroup_worker_start)
                            worker_effective_cpu = max(worker_effective_cpu, worker_cgroup_cpu)
                            total_selector_cpu = max(current_cgroup, pool_effective_cpu + worker_effective_cpu)
                        except RuntimeError as e:
                            if termination_status == "COMPLETED":
                                termination_status = "ERROR"
                                termination_reason = f"Authoritative cgroup CPU unreadable: {e}"
                    else:
                        total_selector_cpu = pool_effective_cpu + worker_effective_cpu

                    if output_file.is_file() and termination_status == "COMPLETED":
                        try:
                            candidate_out = CandidateOutput.model_validate_json(
                                output_file.read_text(encoding="utf-8")
                            )
                        except Exception as e:
                            termination_status = "ERROR"
                            termination_reason = f"Failed to parse candidate output JSON: {e}"

            # 3. Helper Stage: Stage-one Root Optimization for STAGE1_GENERATOR under monitored containment
            if (
                candidate.intervention_level == CandidateInterventionLevel.STAGE1_GENERATOR
                and termination_status == "COMPLETED"
                and candidate_out is not None
                and candidate_out.selected_pair is not None
            ):
                stage1_pair = candidate_out.selected_pair
                elapsed_so_far = max(0.0, time.monotonic() - t_start_wall)
                remaining_wall = max(0.01, budget.max_wall_seconds - elapsed_so_far)
                cgroup_ropt_start = 0.0
                if has_cgroup and sandbox and attached:
                    try:
                        cgroup_ropt_start = sandbox.read_cpu_seconds()
                    except RuntimeError as e:
                        termination_status = "ERROR"
                        termination_reason = f"Authoritative cgroup CPU unreadable: {e}"
                        rejection_reason = termination_reason

                ropt_ok, ropt_res, ropt_cpu, ropt_wall, r_status, r_reason = self._run_monitored_stage(
                    fn=self.selector.run_ropt,
                    args=(stage1_pair, profile),
                    kwargs={"timeout_seconds": remaining_wall, "tmp_dir": run_dir},
                    stage_name="Stage-one root optimization",
                    budget=budget,
                    accumulated_cpu=total_selector_cpu,
                    t_start_wall=t_start_wall,
                    sandbox=sandbox,
                    has_cgroup=has_cgroup,
                    run_dir=run_dir,
                )
                ropt_cgroup_end = cgroup_ropt_start
                if has_cgroup and sandbox and attached:
                    try:
                        ropt_cgroup_end = sandbox.read_cpu_seconds()
                    except RuntimeError as e:
                        termination_status = "ERROR"
                        termination_reason = f"Authoritative cgroup CPU unreadable: {e}"
                        rejection_reason = termination_reason
                ropt_cgroup_cpu = max(0.0, ropt_cgroup_end - cgroup_ropt_start)
                ropt_declared_cpu = float(ropt_res.cpu_seconds) if hasattr(ropt_res, "cpu_seconds") else 0.0
                ropt_effective_cpu = max(ropt_cgroup_cpu, ropt_cpu, ropt_declared_cpu)
                total_selector_cpu = max(ropt_cgroup_end if (has_cgroup and sandbox and attached) else 0.0, pool_effective_cpu + worker_effective_cpu + ropt_effective_cpu)

                if not ropt_ok:
                    termination_status = r_status
                    termination_reason = r_reason
                    rejection_reason = r_reason
                else:
                    if hasattr(ropt_res, "pair"):
                        candidate_out.selected_pair = ropt_res.pair

        except RuntimeError as e:
            if "Canonical execution rejected" in str(e):
                raise
            termination_status = "ERROR"
            termination_reason = f"Candidate execution raised unexpected exception: {e}"
        except Exception as e:
            termination_status = "ERROR"
            termination_reason = f"Candidate execution raised unexpected exception: {e}"
            rejection_reason = termination_reason
        finally:
            if has_cgroup and sandbox:
                if attached:
                    try:
                        total_selector_cpu = max(total_selector_cpu, sandbox.read_cpu_seconds())
                        peak_rss = max(peak_rss, sandbox.read_peak_memory_mb())
                    except RuntimeError as e:
                        if termination_status == "COMPLETED":
                            termination_status = "ERROR"
                            termination_reason = f"Authoritative cgroup CPU unreadable: {e}"
                sandbox.cleanup()

        # Authoritative wall clock time across the entire pipeline
        actual_wall = max(0.0, time.monotonic() - t_start_wall)

        if actual_wall > budget.max_wall_seconds and termination_status == "COMPLETED":
            termination_status = "TIMEOUT"
            termination_reason = f"Candidate exceeded wall timeout: {actual_wall:.2f}s > {budget.max_wall_seconds:.2f}s"
            rejection_reason = termination_reason

        if total_selector_cpu > budget.max_cpu_seconds and termination_status == "COMPLETED":
            termination_status = "BUDGET_EXCEEDED_REJECTED"
            overshoot = total_selector_cpu - budget.max_cpu_seconds
            termination_reason = (
                f"Total selector CPU exceeded budget: {total_selector_cpu:.4f}s > {budget.max_cpu_seconds:.4f}s "
                f"(overshoot: {overshoot:.4f}s)"
            )
            rejection_reason = termination_reason

        # Unconditional Failure Gate:
        # Polynomial validation can NEVER override an execution failure, timeout, or budget exhaustion
        if termination_status != "COMPLETED":
            passed = False
            rejection_reason = rejection_reason or termination_reason or f"Execution failed with status {termination_status}"
            if total_selector_cpu > budget.max_cpu_seconds:
                overshoot = max(overshoot, total_selector_cpu - budget.max_cpu_seconds)
        elif rejection_reason:
            passed = False
        elif candidate_out is None or candidate_out.selected_pair is None:
            passed = False
            rejection_reason = "Candidate did not return a selected polynomial pair"
        else:
            pair = candidate_out.selected_pair

            def _matches_pool(target: NfsPolynomialPair, p_list: List[NfsPolynomialPair]) -> bool:
                for p in p_list:
                    if (
                        target.f1_coeffs == p.f1_coeffs
                        and target.f2_coeffs == p.f2_coeffs
                        and target.m == p.m
                        and target.N == p.N
                    ):
                        return True
                return False

            if (
                candidate.intervention_level == CandidateInterventionLevel.POST_ROPT_RANKER
                and candidate_pool_pairs is not None
                and not _matches_pool(pair, candidate_pool_pairs)
            ):
                passed = False
                rejection_reason = "Selected polynomial pair is not a member of the generated candidate pool"
            elif pair.N != N:
                passed = False
                rejection_reason = f"Returned pair N ({pair.N}) does not match requested N ({N})"
            elif pair.degree1 != profile.degree:
                passed = False
                rejection_reason = f"Returned algebraic degree ({pair.degree1}) does not match profile degree ({profile.degree})"
            elif pair.degree2 != 1:
                passed = False
                rejection_reason = f"Returned rational degree ({pair.degree2}) must be exactly 1"
            else:
                is_valid, v_msg = verify_nfs_polynomial_pair(pair)
                if not is_valid:
                    passed = False
                    rejection_reason = f"Polynomial mathematical verification failed: {v_msg}"
                else:
                    passed = True
                    pair.save_cado_poly_file(poly_path)
                    pair_hash = hash_file(poly_path)

        passed = bool(passed and termination_status == "COMPLETED" and not rejection_reason)

        trace_log = candidate_out.search_trace_log if candidate_out else ""
        trace_path = run_dir / "search_trace.log"
        trace_path.write_text(trace_log, encoding="utf-8")
        trace_hash = hash_file(trace_path)

        stdout_hash = hash_file(stdout_path) if stdout_path.exists() else ""
        stderr_hash = hash_file(stderr_path) if stderr_path.exists() else ""

        evidence = RunnerExecutionEvidence(
            actual_cpu_seconds=round(total_selector_cpu, 4),
            actual_wall_seconds=round(max(0.0, actual_wall), 4),
            peak_rss_mb=round(peak_rss, 2),
            termination_status=termination_status,
            termination_reason=termination_reason,
            cgroup_path=str(sandbox.cgroup_path) if has_cgroup else None,
            contained=bool(has_cgroup and attached),
            worker_pid=worker_pid,
            overshoot_cpu_seconds=round(overshoot, 4),
            search_trace_hash=trace_hash,
            selected_pair_hash=pair_hash,
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            stdout_hash=stdout_hash,
            stderr_hash=stderr_hash,
        )

        return CandidateExecutionRecord(
            instance_id=instance_id,
            modulus_n=str(N),
            digits=len(str(N)),
            profile_name=profile.name,
            profile=profile.to_full_dict(),
            budget=budget,
            candidate_output=candidate_out,
            evidence=evidence,
            passed=passed,
            rejection_reason=rejection_reason,
        )
