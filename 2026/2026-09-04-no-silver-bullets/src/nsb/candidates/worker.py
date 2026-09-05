"""Isolated worker process for running candidate NFS polynomial selectors under containment."""

import argparse
import importlib
import inspect
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import List, Optional

from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.profiles import get_cado_profile
from nsb.candidates.models import (
    CandidateInterventionLevel,
    CandidateOutput,
    NfsCandidateSelector,
    SearchBudget,
)


def run_worker(task_file: Path) -> int:
    """Read task specification from disk, synchronize containment with supervisor, and run candidate."""
    if not task_file.is_file():
        sys.stderr.write(f"Worker task file not found: {task_file}\n")
        return 1

    try:
        task_data = json.loads(task_file.read_text(encoding="utf-8"))
    except Exception as e:
        sys.stderr.write(f"Worker failed to parse task JSON: {e}\n")
        return 1

    candidate_module = task_data.get("candidate_module")
    candidate_class_name = task_data["candidate_class"]
    candidate_kwargs = task_data.get("candidate_kwargs", {})
    candidate_code = task_data.get("candidate_code")
    N = int(task_data["N"])
    profile_name = task_data["profile_name"]
    budget_dict = task_data["budget"]
    seed = int(task_data["seed"])
    output_file = Path(task_data["output_file"])
    stdout_file = Path(task_data["stdout_file"])
    stderr_file = Path(task_data["stderr_file"])
    sync_handshake = task_data.get("sync_handshake", False)
    candidate_pool_data = task_data.get("candidate_pool")

    # 1. Synchronization handshake: notify supervisor of readiness, wait for cgroup attachment
    if sync_handshake:
        sys.stdout.write(f"READY {os.getpid()}\n")
        sys.stdout.flush()
        supervisor_signal = sys.stdin.readline().strip()
        if supervisor_signal != "GO":
            sys.stderr.write(f"Worker received abort or unexpected supervisor signal: '{supervisor_signal}'\n")
            return 2

    # 2. Redirect stdout and stderr to disk files for authoritative evidence capture
    stdout_file.parent.mkdir(parents=True, exist_ok=True)
    stderr_file.parent.mkdir(parents=True, exist_ok=True)
    out_fd = os.open(str(stdout_file), os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    err_fd = os.open(str(stderr_file), os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    os.dup2(out_fd, 1)
    os.dup2(err_fd, 2)
    os.close(out_fd)
    os.close(err_fd)

    # 3. Import and instantiate candidate
    try:
        if candidate_code:
            ns = {
                "__builtins__": __builtins__,
                "NfsCandidateSelector": NfsCandidateSelector,
                "CandidateInterventionLevel": CandidateInterventionLevel,
                "CandidateOutput": CandidateOutput,
                "SearchBudget": SearchBudget,
                "NfsPolynomialPair": NfsPolynomialPair,
                "subprocess": subprocess,
                "time": time,
                "sys": sys,
                "os": os,
                "Path": Path,
            }
            exec(candidate_code, ns)
            candidate_cls = ns[candidate_class_name]
            candidate = candidate_cls(**candidate_kwargs)
        else:
            mod = importlib.import_module(candidate_module)
            candidate_cls = getattr(mod, candidate_class_name)
            candidate = candidate_cls(**candidate_kwargs)
    except Exception as e:
        sys.stderr.write(f"Failed to load candidate class {candidate_class_name}: {e}\n")
        traceback.print_exc(file=sys.stderr)
        return 3

    # 4. Retrieve profile and budget
    profile = get_cado_profile(profile_name)
    budget = SearchBudget.model_validate(budget_dict)

    # Parse candidate pool if provided
    candidate_pool: Optional[List[NfsPolynomialPair]] = None
    if candidate_pool_data:
        candidate_pool = [NfsPolynomialPair.model_validate(p) for p in candidate_pool_data]

    # 5. Execute candidate search
    try:
        select_kwargs = {
            "N": N,
            "profile": profile,
            "budget": budget,
            "seed": seed,
        }
        sig = inspect.signature(candidate.select)
        if "candidate_pool" in sig.parameters and candidate_pool is not None:
            select_kwargs["candidate_pool"] = candidate_pool
        elif candidate_pool is not None and hasattr(candidate, "set_candidate_pool"):
            candidate.set_candidate_pool(candidate_pool)

        candidate_output = candidate.select(**select_kwargs)
    except Exception as e:
        sys.stderr.write(f"Candidate execution raised exception: {e}\n")
        traceback.print_exc(file=sys.stderr)
        return 4

    # 6. Serialize output to disk
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(candidate_output.model_dump_json(indent=2), encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"Failed to write candidate output: {e}\n")
        return 5

    return 0


def main():
    parser = argparse.ArgumentParser(description="NSB Candidate Worker Process")
    parser.add_argument("--task-file", required=True, type=Path, help="Path to JSON task configuration file")
    args = parser.parse_args()

    exit_code = run_worker(args.task_file)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
