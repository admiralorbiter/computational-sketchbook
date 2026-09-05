"""Unit tests for R3-G4 candidate interface, cgroup v2 sandbox, runner, and promotion judge."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import pytest
import numpy as np

from nsb.candidates.models import (
    CandidateInterventionLevel,
    SearchBudget,
    CandidateOutput,
    RunnerExecutionEvidence,
    CandidateExecutionRecord,
    NfsCandidateSelector,
)
from nsb.candidates.sandbox import CgroupV2Sandbox, build_isolated_env
from nsb.candidates.runner import MonitoredCandidateRunner
from nsb.candidates.judge import PromotionJudge, PairedEvaluationRecord, PromotionVerdict
from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.profiles import CADO_PARAMS_C60


def test_candidate_models_serialization_and_validation():
    budget = SearchBudget(
        max_cpu_seconds=120.0,
        max_wall_seconds=300.0,
        max_peak_rss_mb=2048.0,
        threads=1,
    )
    assert budget.threads == 1
    assert not budget.allow_gpu
    assert not budget.allow_network

    # Rejection of invalid configurations
    with pytest.raises(ValueError, match="threads=1"):
        SearchBudget(max_cpu_seconds=120.0, threads=2)

    with pytest.raises(ValueError, match="forbids GPU"):
        SearchBudget(max_cpu_seconds=120.0, allow_gpu=True)

    with pytest.raises(ValueError, match="forbids network"):
        SearchBudget(max_cpu_seconds=120.0, allow_network=True)

    with pytest.raises(ValueError, match="finite and positive"):
        SearchBudget(max_cpu_seconds=-1.0)

    with pytest.raises(ValueError, match="finite and positive"):
        SearchBudget(max_cpu_seconds=float("nan"))

    with pytest.raises(ValueError, match="finite and positive"):
        SearchBudget(max_cpu_seconds=float("inf"))

    with pytest.raises(ValueError, match="finite and positive"):
        SearchBudget(max_cpu_seconds=10.0, max_wall_seconds=-5.0)

    with pytest.raises(ValueError, match="finite and positive"):
        SearchBudget(max_cpu_seconds=10.0, max_peak_rss_mb=0.0)

    out = CandidateOutput(
        method_id="test_candidate",
        version="1.0.0",
        intervention_level=CandidateInterventionLevel.FULL_SELECTOR,
        seed=12345,
        metadata={"generator": "test"},
        search_trace_log="trace line 1\ntrace line 2\n",
    )
    assert out.method_id == "test_candidate"
    assert out.intervention_level == CandidateInterventionLevel.FULL_SELECTOR

    evidence = RunnerExecutionEvidence(
        actual_cpu_seconds=12.34,
        actual_wall_seconds=13.0,
        peak_rss_mb=45.2,
        termination_status="COMPLETED",
        termination_reason="Normal completion",
        cgroup_path="/sys/fs/cgroup/nsb/test",
        contained=True,
        worker_pid=1234,
        overshoot_cpu_seconds=0.0,
        search_trace_hash="abcdef0123456789",
        stdout_hash="1" * 64,
        stderr_hash="2" * 64,
    )
    assert evidence.actual_cpu_seconds == 12.34
    assert evidence.contained is True


def test_build_isolated_env():
    env = build_isolated_env()
    assert "PATH" in env
    # Sensitive tokens and cloud vars must be stripped
    assert "AWS_SECRET_ACCESS_KEY" not in env
    assert "GITHUB_TOKEN" not in env
    assert "OPENAI_API_KEY" not in env
    assert "GEMINI_API_KEY" not in env
    # Threading caps enforced
    assert env["OMP_NUM_THREADS"] == "1"
    assert env["OPENBLAS_NUM_THREADS"] == "1"
    assert env["MKL_NUM_THREADS"] == "1"
    assert env["VECLIB_MAXIMUM_THREADS"] == "1"
    assert env["NUMEXPR_NUM_THREADS"] == "1"
    # Network blocking proxy
    assert env["http_proxy"] == "http://127.0.0.1:0"
    assert env["https_proxy"] == "http://127.0.0.1:0"


def test_cgroup_v2_sandbox_basic():
    """Test cgroup v2 sandbox creation, containment, CPU accounting, and cleanup."""
    sandbox = CgroupV2Sandbox(
        cgroup_root=Path("/sys/fs/cgroup/nsb"),
        sandbox_id="test_unit_basic",
    )
    if not sandbox.is_cgroup_available():
        pytest.skip("Cgroup v2 /sys/fs/cgroup/nsb not configured or not available")

    budget = SearchBudget(max_cpu_seconds=60.0, max_peak_rss_mb=512.0)
    try:
        active = sandbox.setup_cgroup(budget)
        assert active
        assert sandbox.cgroup_path.exists()

        # Run child process
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; [x**2 for x in range(500000)]; time.sleep(0.05)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        sandbox.attach_pid(proc.pid)
        proc.wait(timeout=5)

        cpu_usage = sandbox.read_cpu_seconds()
        assert cpu_usage > 0.0, "Cgroup cpu.stat usage_usec must record strictly positive CPU"
    finally:
        sandbox.cleanup()
        assert not sandbox.cgroup_path.exists()


def test_cgroup_v2_sandbox_runaway_kill():
    """Test that cgroup.kill terminates runaway child and descendant processes."""
    sandbox = CgroupV2Sandbox(
        cgroup_root=Path("/sys/fs/cgroup/nsb"),
        sandbox_id="test_unit_runaway",
    )
    if not sandbox.is_cgroup_available():
        pytest.skip("Cgroup v2 /sys/fs/cgroup/nsb not configured or not available")

    budget = SearchBudget(max_cpu_seconds=60.0, max_peak_rss_mb=256.0)
    try:
        active = sandbox.setup_cgroup(budget)
        assert active
        proc = subprocess.Popen(
            [sys.executable, "-c", "while True: pass"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        sandbox.attach_pid(proc.pid)

        # Kill sandbox
        killed = sandbox.kill_all()
        assert killed
        proc.wait(timeout=2)
        assert proc.poll() is not None
    finally:
        sandbox.cleanup()


class RunawayInfiniteCandidate(NfsCandidateSelector):
    method_id = "runaway_infinite_candidate"
    version = "0.1.0"
    intervention_level = CandidateInterventionLevel.FULL_SELECTOR

    def select(self, N: int, profile, budget: SearchBudget, seed: int) -> CandidateOutput:
        # Deliberately infinite loop burning CPU
        while True:
            pass


def test_monitored_candidate_runner_watchdog_terminates_overbudget(tmp_path):
    """Test that the supervisor watchdog terminates an over-budget infinite-loop candidate."""
    runner = MonitoredCandidateRunner(
        artifact_dir=tmp_path / "runs",
    )

    budget = SearchBudget(max_cpu_seconds=0.10, max_wall_seconds=2.0, max_peak_rss_mb=256.0)
    t0 = time.time()
    record = runner.run_candidate(
        candidate=RunawayInfiniteCandidate(),
        N=5893,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="watchdog_cpu_test",
    )
    elapsed_wall = time.time() - t0

    assert not record.passed
    assert record.evidence.termination_status in ("BUDGET_EXCEEDED_REJECTED", "TIMEOUT")
    # Must have been terminated quickly by watchdog, not hang
    assert elapsed_wall < 3.0


class ChildSpawningCandidate(NfsCandidateSelector):
    method_id = "child_spawning_candidate"
    version = "0.1.0"
    intervention_level = CandidateInterventionLevel.FULL_SELECTOR

    def select(self, N: int, profile, budget: SearchBudget, seed: int) -> CandidateOutput:
        # Spawn child process that consumes CPU
        p = subprocess.Popen(
            [sys.executable, "-c", "import time; [x**2 for x in range(3000000)]; time.sleep(0.05)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.wait()

        from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
        return CandidateOutput(
            selected_pair=VERIFIED_C60_POLY,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            search_trace_log="child process spawned and waited",
        )


def test_monitored_candidate_runner_charges_child_process(tmp_path):
    """Test that runner accounting captures CPU consumed by candidate child processes."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(
        artifact_dir=tmp_path / "runs",
    )

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=10.0, max_peak_rss_mb=512.0)
    record = runner.run_candidate(
        candidate=ChildSpawningCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="child_accounting_test",
    )

    assert record.passed
    assert record.evidence.actual_cpu_seconds > 0.0, "Runner must record strictly positive CPU for child process"
    assert record.evidence.contained is True


class FraudulentCandidate(NfsCandidateSelector):
    method_id = "fraudulent_candidate"
    version = "0.1.0"
    intervention_level = CandidateInterventionLevel.FULL_SELECTOR

    def select(self, N: int, profile, budget: SearchBudget, seed: int) -> CandidateOutput:
        pair = NfsPolynomialPair(
            f1_coeffs=[-5832, 0, 0, 1],
            f2_coeffs=[-18, 1],
            N=N - 2,  # Wrong N
            m=18,
        )
        return CandidateOutput(
            selected_pair=pair,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            search_trace_log="fraudulent trace",
        )


def test_monitored_candidate_runner_wrong_n_rejection(tmp_path):
    """Test that the runner rejects a candidate polynomial that matches a different N."""
    runner = MonitoredCandidateRunner(
        artifact_dir=tmp_path / "runs",
    )

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0, max_peak_rss_mb=256.0)
    record = runner.run_candidate(
        candidate=FraudulentCandidate(),
        N=5893,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="wrong_n_test",
    )

    assert not record.passed
    assert "does not match requested N" in record.rejection_reason


class InvalidDegreeCandidate(NfsCandidateSelector):
    method_id = "invalid_degree_candidate"
    version = "0.1.0"
    intervention_level = CandidateInterventionLevel.FULL_SELECTOR

    def select(self, N: int, profile, budget: SearchBudget, seed: int) -> CandidateOutput:
        pair = NfsPolynomialPair(
            f1_coeffs=[-5832, 0, 0, 0, 0, 1],  # Degree 5 when c60 expects 4
            f2_coeffs=[-18, 1],
            N=N,
            m=18,
        )
        return CandidateOutput(
            selected_pair=pair,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            search_trace_log="invalid degree trace",
        )


def test_monitored_candidate_runner_degree_rejection(tmp_path):
    """Test that the runner rejects a candidate polynomial with degree exceeding profile degree."""
    runner = MonitoredCandidateRunner(
        artifact_dir=tmp_path / "runs",
    )

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0, max_peak_rss_mb=256.0)
    record = runner.run_candidate(
        candidate=InvalidDegreeCandidate(),
        N=5893,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="deg_mismatch_test",
    )

    assert not record.passed
    assert "does not match profile degree" in record.rejection_reason


def test_monitored_candidate_runner_evidence_files_and_unique_dirs(tmp_path):
    """Test that stdout.log and stderr.log are written to disk with hashes, and run dirs are unique."""
    runner = MonitoredCandidateRunner(
        artifact_dir=tmp_path / "runs",
    )

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0, max_peak_rss_mb=256.0)
    rec1 = runner.run_candidate(
        candidate=ChildSpawningCandidate(),
        N=5893,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="shared_instance",
    )
    rec2 = runner.run_candidate(
        candidate=ChildSpawningCandidate(),
        N=5893,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=43,
        instance_id="shared_instance",
    )

    # Reusing instance_id must not collide or overwrite run directories
    assert rec1.evidence.stdout_path != rec2.evidence.stdout_path
    assert Path(rec1.evidence.stdout_path).exists()
    assert Path(rec1.evidence.stderr_path).exists()
    assert len(rec1.evidence.stdout_hash) == 64
    assert len(rec1.evidence.stderr_hash) == 64


def test_promotion_judge_adjudication_valid():
    """Test PromotionJudge with valid synthetic paired records across 95d and 100d."""
    judge = PromotionJudge(
        n_resamples=2000,
        random_seed=42,
        quality_ratio_threshold=1.10,
        system_reduction_threshold=0.05,
        require_manifest=False,
    )

    # 1. Clear Tier 1 Winner
    records_t1 = []
    for i in range(10):
        records_t1.append(
            PairedEvaluationRecord(
                instance_id=f"95d_{i}",
                digits=95,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=1000,
                candidate_yield=1200,
                baseline_total_cpu=100.0,
                candidate_total_cpu=98.0,
            )
        )
        records_t1.append(
            PairedEvaluationRecord(
                instance_id=f"100d_{i}",
                digits=100,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=2000,
                candidate_yield=2400,
                baseline_total_cpu=200.0,
                candidate_total_cpu=195.0,
            )
        )

    verdict_t1 = judge.judge(records_t1)
    assert verdict_t1.tier1_quality.passed
    assert verdict_t1.verdict in ("R3_CANDIDATE_PROMOTED", "QUALITY_ADVANTAGE_ONLY")

    # 2. Tier 2 Winner (System Cost Reduction >= 5% with iso-quality / equal yield)
    records_t2 = []
    for i in range(10):
        records_t2.append(
            PairedEvaluationRecord(
                instance_id=f"95d_{i}",
                digits=95,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=1000,
                candidate_yield=1000,
                baseline_total_cpu=100.0,
                candidate_total_cpu=85.0,  # 15% cheaper
            )
        )
        records_t2.append(
            PairedEvaluationRecord(
                instance_id=f"100d_{i}",
                digits=100,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=2000,
                candidate_yield=2000,
                baseline_total_cpu=200.0,
                candidate_total_cpu=170.0,  # 15% cheaper
            )
        )

    verdict_t2 = judge.judge(records_t2)
    assert not verdict_t2.tier1_quality.passed
    assert verdict_t2.tier2_system.passed
    assert verdict_t2.verdict == "SYSTEM_ADVANTAGE_ONLY"


def test_promotion_judge_rejection_on_invalid_manifest():
    """Verify PromotionJudge strictly rejects invalid comparisons (duplicates, wrong digits, failed baselines)."""
    judge = PromotionJudge(
        n_resamples=1000,
        random_seed=42,
        require_manifest=False,
    )

    # 1. Reject duplicate instance IDs
    records_dup = [
        PairedEvaluationRecord(
            instance_id="same_id",
            digits=95,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=1000,
            candidate_yield=1200,
            baseline_total_cpu=100.0,
            candidate_total_cpu=90.0,
        )
        for _ in range(20)
    ]
    with pytest.raises(ValueError, match="duplicate instance IDs detected"):
        judge.judge(records_dup)

    # 2. Reject incomplete instance count
    records_short = [
        PairedEvaluationRecord(
            instance_id=f"inst_{i}",
            digits=95,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=1000,
            candidate_yield=1200,
            baseline_total_cpu=100.0,
            candidate_total_cpu=90.0,
        )
        for i in range(2)
    ]
    with pytest.raises(ValueError, match="do not match required promotion cohorts"):
        judge.judge(records_short)

    # 3. Reject wrong cohorts (60d/70d instead of 95d/100d)
    records_wrong_digits = []
    for i in range(10):
        records_wrong_digits.append(
            PairedEvaluationRecord(
                instance_id=f"60d_{i}",
                digits=60,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=1000,
                candidate_yield=1200,
                baseline_total_cpu=100.0,
                candidate_total_cpu=90.0,
            )
        )
        records_wrong_digits.append(
            PairedEvaluationRecord(
                instance_id=f"70d_{i}",
                digits=70,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=2000,
                candidate_yield=2400,
                baseline_total_cpu=200.0,
                candidate_total_cpu=180.0,
            )
        )
    with pytest.raises(ValueError, match="do not match required promotion cohorts"):
        judge.judge(records_wrong_digits)

    # 4. Reject if any baseline failed
    records_failed_base = []
    for i in range(10):
        records_failed_base.append(
            PairedEvaluationRecord(
                instance_id=f"95d_{i}",
                digits=95,
                baseline_passed=False,  # Baseline failed!
                candidate_passed=True,
                baseline_yield=0,
                candidate_yield=1200,
                baseline_total_cpu=100.0,
                candidate_total_cpu=90.0,
            )
        )
        records_failed_base.append(
            PairedEvaluationRecord(
                instance_id=f"100d_{i}",
                digits=100,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=2000,
                candidate_yield=2400,
                baseline_total_cpu=200.0,
                candidate_total_cpu=180.0,
            )
        )
    with pytest.raises(ValueError, match="baseline failed"):
        judge.judge(records_failed_base)


def test_promotion_judge_true_zero_geometric_mean():
    """Verify that a single candidate failure or zero-yield produces strictly 0.0 geometric mean."""
    judge = PromotionJudge(
        n_resamples=1000,
        random_seed=42,
        require_manifest=False,
    )

    records = []
    for i in range(10):
        records.append(
            PairedEvaluationRecord(
                instance_id=f"95d_{i}",
                digits=95,
                baseline_passed=True,
                candidate_passed=(i != 0),  # Instance 0 failed!
                baseline_yield=1000,
                candidate_yield=1500 if i != 0 else 0,
                baseline_total_cpu=100.0,
                candidate_total_cpu=80.0,
            )
        )
        records.append(
            PairedEvaluationRecord(
                instance_id=f"100d_{i}",
                digits=100,
                baseline_passed=True,
                candidate_passed=True,
                baseline_yield=2000,
                candidate_yield=3000,
                baseline_total_cpu=200.0,
                candidate_total_cpu=160.0,
            )
        )

    verdict = judge.judge(records)
    assert not verdict.tier1_quality.passed
    assert verdict.tier1_quality.sample_geometric_mean_ratio == 0.0, "True zero geometric mean must be strictly 0.0"
    assert verdict.verdict == "PROMOTION_REJECTED"


def test_failed_cgroup_attachment_aborts_execution(tmp_path, monkeypatch):
    """Verify that failed cgroup attachment immediately aborts execution and reports contained=False."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(
        artifact_dir=tmp_path / "runs",
        require_containment=False,
    )

    # Simulate cgroup setup succeeding but attach_pid failing (e.g. permission or race condition)
    def mock_setup_cgroup(self, budget):
        self._cgroup_active = True
        return True

    monkeypatch.setattr(CgroupV2Sandbox, "setup_cgroup", mock_setup_cgroup)
    monkeypatch.setattr(CgroupV2Sandbox, "read_cpu_seconds", lambda self: 0.0)
    monkeypatch.setattr(CgroupV2Sandbox, "attach_pid", lambda self, pid: False)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=ChildSpawningCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="attachment_failure_test",
    )

    assert not record.passed
    assert record.evidence.contained is False, "Failed attachment must report contained=False"
    assert record.evidence.actual_cpu_seconds == 0.0
    assert record.evidence.termination_status == "ERROR"
    assert "Failed to attach worker" in record.rejection_reason

    # With require_containment=True, attachment failure must raise RuntimeError
    runner_strict = MonitoredCandidateRunner(
        artifact_dir=tmp_path / "runs_strict",
        require_containment=True,
    )
    with pytest.raises(RuntimeError, match="Canonical execution rejected"):
        runner_strict.run_candidate(
            candidate=ChildSpawningCandidate(),
            N=VERIFIED_C60_POLY.N,
            profile=CADO_PARAMS_C60,
            budget=budget,
            seed=42,
            instance_id="attachment_failure_strict",
        )


class Stage1Candidate(NfsCandidateSelector):
    method_id = "stage1_candidate"
    version = "1.0.0"
    intervention_level = CandidateInterventionLevel.STAGE1_GENERATOR

    def select(self, N: int, profile, budget: SearchBudget, seed: int) -> CandidateOutput:
        from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
        return CandidateOutput(
            selected_pair=VERIFIED_C60_POLY,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            search_trace_log="stage 1 unoptimized pair generated",
        )


def test_stage1_generator_pipeline_execution(tmp_path, monkeypatch):
    """Verify that STAGE1_GENERATOR runs real run_ropt method and charges candidate + ropt CPU."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
    from nsb.baselines.cado_nfs.adapter import CommandExecutionResult

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    # Mock ONLY adapter.run_binary so the real CadoPolynomialSelector.run_ropt method is exercised
    mock_stdout = VERIFIED_C60_POLY.to_cado_poly_string()
    def mock_run_binary(bin_name, args, timeout_seconds=300.0, cwd=None):
        return CommandExecutionResult(
            command=[bin_name] + args,
            binary_name=bin_name,
            returncode=0,
            stdout=mock_stdout,
            stderr="",
            wall_seconds=1.30,
            cpu_seconds=1.25,
            max_rss_mb=50.0,
        )

    monkeypatch.setattr(runner.selector.adapter, "run_binary", mock_run_binary)

    budget = SearchBudget(max_cpu_seconds=10.0, max_wall_seconds=10.0)
    record = runner.run_candidate(
        candidate=Stage1Candidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="stage1_pipeline_test",
    )

    assert record.passed
    # Total CPU must include ropt CPU (1.25s)
    assert record.evidence.actual_cpu_seconds >= 1.25
    assert record.candidate_output.selected_pair is not None


class RankerCandidate(NfsCandidateSelector):
    method_id = "ranker_candidate"
    version = "1.0.0"
    intervention_level = CandidateInterventionLevel.POST_ROPT_RANKER

    def select(self, N: int, profile, budget: SearchBudget, seed: int, candidate_pool=None) -> CandidateOutput:
        from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
        selected = candidate_pool[0] if candidate_pool else VERIFIED_C60_POLY
        return CandidateOutput(
            selected_pair=selected,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            search_trace_log=f"selected from pool of size {len(candidate_pool) if candidate_pool else 0}",
        )


class FraudulentRanker(NfsCandidateSelector):
    method_id = "fraudulent_ranker"
    version = "1.0.0"
    intervention_level = CandidateInterventionLevel.POST_ROPT_RANKER

    def select(self, N: int, profile, budget: SearchBudget, seed: int, candidate_pool=None) -> CandidateOutput:
        from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
        from nsb.baselines.cado_nfs.models import NfsPolynomialPair
        valid_unpooled_pair = NfsPolynomialPair(
            f1_coeffs=[VERIFIED_C60_POLY.f1_coeffs[0] + VERIFIED_C60_POLY.N] + VERIFIED_C60_POLY.f1_coeffs[1:],
            f2_coeffs=VERIFIED_C60_POLY.f2_coeffs,
            m=VERIFIED_C60_POLY.m,
            N=VERIFIED_C60_POLY.N,
            skew=VERIFIED_C60_POLY.skew,
        )
        return CandidateOutput(
            selected_pair=valid_unpooled_pair,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            search_trace_log="chose valid pair outside pool",
        )


class CrashingRanker(NfsCandidateSelector):
    method_id = "crashing_ranker"
    version = "1.0.0"
    intervention_level = CandidateInterventionLevel.POST_ROPT_RANKER

    def select(self, N: int, profile, budget: SearchBudget, seed: int, candidate_pool=None) -> CandidateOutput:
        raise RuntimeError("Candidate deliberate crash")


def test_post_ropt_ranker_pipeline_execution(tmp_path, monkeypatch):
    """Verify that POST_ROPT_RANKER generates pool, supplies pool to candidate, and charges total CPU."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    # Mock selector.generate_stage1_pool
    def mock_generate_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        return [VERIFIED_C60_POLY], 2.50, 2.55

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_generate_pool)

    budget = SearchBudget(max_cpu_seconds=10.0, max_wall_seconds=10.0)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="ranker_pipeline_test",
    )

    assert record.passed
    # Total CPU must include pool generation CPU (2.50s)
    assert record.evidence.actual_cpu_seconds >= 2.50
    assert "selected from pool of size 1" in record.candidate_output.search_trace_log


def test_post_ropt_ranker_pool_membership_rejection(tmp_path, monkeypatch):
    """Verify that POST_ROPT_RANKER rejects output if selected_pair is not in candidate_pool."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    # Pool contains only VERIFIED_C60_POLY
    def mock_generate_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        return [VERIFIED_C60_POLY], 0.10, 0.10

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_generate_pool)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=FraudulentRanker(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="pool_membership_rejection_test",
    )

    assert not record.passed
    assert "not a member of the generated candidate pool" in record.rejection_reason


def test_pool_generation_wall_timeout(tmp_path, monkeypatch):
    """Verify that pool generation exceeding wall budget immediately aborts with TIMEOUT."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    def mock_slow_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        time.sleep(0.15)
        return [VERIFIED_C60_POLY], 0.15, 0.15

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_slow_pool)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=0.05)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="pool_timeout_test",
    )

    assert not record.passed
    assert record.evidence.termination_status == "TIMEOUT"
    assert "exceeded wall timeout" in record.rejection_reason


def test_retained_costs_on_worker_failure(tmp_path, monkeypatch):
    """Verify that pool generation CPU is retained in evidence when worker fails."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    def mock_generate_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        return [VERIFIED_C60_POLY], 2.50, 2.55

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_generate_pool)

    budget = SearchBudget(max_cpu_seconds=10.0, max_wall_seconds=10.0)
    record = runner.run_candidate(
        candidate=CrashingRanker(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="retained_costs_crash_test",
    )

    assert not record.passed
    assert record.evidence.termination_status == "ERROR"
    assert record.evidence.actual_cpu_seconds >= 2.50


def test_promotion_judge_numerical_and_manifest_validation():
    """Verify PromotionJudge strictly rejects invalid costs, zero baseline yields, and missing manifest."""
    # 1. Reject negative candidate CPU
    judge = PromotionJudge(n_resamples=500, random_seed=42, require_manifest=False)
    records_neg_cpu = [
        PairedEvaluationRecord(
            instance_id=f"95d_{i}",
            digits=95,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=1000,
            candidate_yield=1200,
            baseline_total_cpu=100.0,
            candidate_total_cpu=-50.0 if i == 0 else 90.0,
        )
        for i in range(10)
    ] + [
        PairedEvaluationRecord(
            instance_id=f"100d_{i}",
            digits=100,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=2000,
            candidate_yield=2400,
            baseline_total_cpu=200.0,
            candidate_total_cpu=180.0,
        )
        for i in range(10)
    ]
    with pytest.raises(ValueError, match="candidate_total_cpu must be finite and non-negative"):
        judge.judge(records_neg_cpu)

    # 2. Reject passed baseline with zero yield
    records_zero_base_yield = [
        PairedEvaluationRecord(
            instance_id=f"95d_{i}",
            digits=95,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=0 if i == 0 else 1000,  # Zero yield on passed baseline!
            candidate_yield=1200,
            baseline_total_cpu=100.0,
            candidate_total_cpu=90.0,
        )
        for i in range(10)
    ] + [
        PairedEvaluationRecord(
            instance_id=f"100d_{i}",
            digits=100,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=2000,
            candidate_yield=2400,
            baseline_total_cpu=200.0,
            candidate_total_cpu=180.0,
        )
        for i in range(10)
    ]
    with pytest.raises(ValueError, match="passed baseline must have strictly positive yield"):
        judge.judge(records_zero_base_yield)

    # 3. Reject when formal promotion requires manifest and none is provided (and verify default is True)
    records_valid = [
        PairedEvaluationRecord(
            instance_id=f"95d_{i}",
            digits=95,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=1000,
            candidate_yield=1200,
            baseline_total_cpu=100.0,
            candidate_total_cpu=90.0,
        )
        for i in range(10)
    ] + [
        PairedEvaluationRecord(
            instance_id=f"100d_{i}",
            digits=100,
            baseline_passed=True,
            candidate_passed=True,
            baseline_yield=2000,
            candidate_yield=2400,
            baseline_total_cpu=200.0,
            candidate_total_cpu=180.0,
        )
        for i in range(10)
    ]

    judge_default = PromotionJudge()
    assert judge_default.require_manifest is True
    with pytest.raises(ValueError, match="formal promotion requires expected_instance_ids or a frozen manifest"):
        judge_default.judge(records_valid)

    judge_formal = PromotionJudge(require_manifest=True)
    with pytest.raises(ValueError, match="formal promotion requires expected_instance_ids or a frozen manifest"):
        judge_formal.judge(records_valid)


def test_reference_candidate_selector_through_worker(tmp_path):
    """Verify that an ordinary candidate module imported by worker executes cleanly without UnboundLocalError."""
    from nsb.candidates.reference import ReferenceDummyCandidateSelector
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")
    candidate = ReferenceDummyCandidateSelector()

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=candidate,
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="reference_worker_import_test",
    )

    assert record.passed
    assert record.candidate_output is not None
    assert record.candidate_output.method_id == "reference_dummy_selector"
    assert record.evidence.actual_cpu_seconds >= 0.0
    assert record.evidence.termination_status == "COMPLETED"


def test_stage1_ropt_timeout_unconditional_failure_gate(tmp_path, monkeypatch):
    """Verify that timed-out stage-one ropt unconditionally results in passed=False even if poly is valid."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
    import time

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    def mock_run_ropt_timeout(poly, profile, timeout_seconds=300.0, extra_ropt_flags=None, tmp_dir=None):
        time.sleep(0.15)
        from nsb.baselines.cado_nfs.models import CadoPolyselectResult
        return CadoPolyselectResult(
            pair=poly,
            modulus_n=poly.N,
            degree=profile.degree,
            cpu_seconds=0.05,
            wall_seconds=0.15,
            raw_output="mock ropt output",
            command=["mock_polyselect_ropt"],
        )

    monkeypatch.setattr(runner.selector, "run_ropt", mock_run_ropt_timeout)

    # Budget max_wall_seconds=0.08 will cause ropt helper stage to timeout at ~0.08s
    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=0.08)
    record = runner.run_candidate(
        candidate=Stage1Candidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="stage1_timeout_gate_test",
    )

    assert record.passed is False, "Timed out stage-1 execution must NEVER return passed=True"
    assert record.evidence.termination_status in ("TIMEOUT", "BUDGET_EXCEEDED_REJECTED")
    assert len(record.rejection_reason) > 0


def test_pool_generation_active_cpu_containment_termination(tmp_path, monkeypatch):
    """Verify that pool generation exceeding CPU budget is actively terminated by supervisor watchdog."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
    import time

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    def mock_burn_cpu(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        # Burn CPU for 1.0s
        t_end = time.time() + 1.0
        while time.time() < t_end:
            _ = [x * x for x in range(1000)]
        return [VERIFIED_C60_POLY], 1.0, 1.0

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_burn_cpu)

    # Small CPU allowance of 0.05s, wall allowance of 1.5s
    budget = SearchBudget(max_cpu_seconds=0.05, max_wall_seconds=1.5)
    t0 = time.time()
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="pool_containment_active_kill_test",
    )
    elapsed_wall = time.time() - t0

    assert record.passed is False
    assert record.evidence.termination_status == "BUDGET_EXCEEDED_REJECTED"
    assert "exceeded CPU budget" in record.rejection_reason
    # Active watchdog must terminate helper long before full 1.0s burn completes
    assert elapsed_wall < 0.6, f"Helper should have been terminated early, took {elapsed_wall:.2f}s"


def test_helper_exception_guarantees_cleanup_and_record(tmp_path, monkeypatch):
    """Verify that exceptions in helper stages return a valid CandidateExecutionRecord and clean up sandboxes."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    cleanup_called = False
    original_cleanup = CgroupV2Sandbox.cleanup

    def tracking_cleanup(self):
        nonlocal cleanup_called
        cleanup_called = True
        return original_cleanup(self)

    monkeypatch.setattr(CgroupV2Sandbox, "cleanup", tracking_cleanup)

    def mock_failing_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        raise RuntimeError("Simulated internal pool generator crash")

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_failing_pool)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="pool_exception_cleanup_test",
    )

    assert record is not None
    assert record.passed is False
    assert record.evidence.termination_status == "ERROR"
    assert "Simulated internal pool generator crash" in record.rejection_reason
    assert cleanup_called is True, "Sandbox cleanup must be guaranteed on helper exception"


def test_helper_attachment_barrier_prevents_pre_containment_execution(tmp_path, monkeypatch):
    """Verify that helper NEVER executes before cgroup attachment barrier completes."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
    import time

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs", require_containment=False)

    marker_file = tmp_path / "helper_started.txt"
    attach_times = []
    helper_start_time = None

    def delayed_attach(self, pid):
        time.sleep(0.08)  # Controlled attachment delay
        attach_times.append(time.monotonic())
        return True

    monkeypatch.setattr(CgroupV2Sandbox, "setup_cgroup", lambda self, budget: True)
    monkeypatch.setattr(CgroupV2Sandbox, "attach_pid", delayed_attach)
    monkeypatch.setattr(CgroupV2Sandbox, "read_cpu_seconds", lambda self: 0.05)
    monkeypatch.setattr(CgroupV2Sandbox, "read_peak_memory_mb", lambda self: 10.0)

    def monitored_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        marker_file.write_text(f"{time.monotonic()}")
        return [VERIFIED_C60_POLY], 0.05, 0.05

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", monitored_pool)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="barrier_test",
    )

    assert record.passed
    assert len(attach_times) >= 1
    assert marker_file.is_file()
    helper_start_time = float(marker_file.read_text().strip())
    assert attach_times[0] <= helper_start_time, "Attachment MUST occur before helper begins execution"

    # Now verify failed attachment: helper must NEVER execute
    marker_failed = tmp_path / "never_run.txt"
    helper_executed = False

    def uninvoked_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        nonlocal helper_executed
        helper_executed = True
        marker_failed.write_text("should_not_run")
        return [VERIFIED_C60_POLY], 0.05, 0.05

    monkeypatch.setattr(CgroupV2Sandbox, "attach_pid", lambda self, pid: False)
    monkeypatch.setattr(runner.selector, "generate_stage1_pool", uninvoked_pool)

    record_fail = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="barrier_fail_test",
    )

    assert not record_fail.passed
    assert record_fail.evidence.termination_status == "ERROR"
    assert "Failed to attach helper" in record_fail.rejection_reason
    assert helper_executed is False, "Helper code must NEVER execute if cgroup attachment fails"
    assert not marker_failed.exists()


def test_cgroup_cumulative_counter_no_double_counting(tmp_path, monkeypatch):
    """Verify that cumulative cgroup counter is not added to itself across pipeline stages."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs", require_containment=False)

    call_count = 0
    # Simulate cgroup cumulative counter:
    # 0.0 at start, 0.60 after pool generation, 0.70 during/after worker
    def mock_read_cpu(self):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return 0.60
        return 0.70

    monkeypatch.setattr(CgroupV2Sandbox, "setup_cgroup", lambda self, budget: True)
    monkeypatch.setattr(CgroupV2Sandbox, "attach_pid", lambda self, pid: True)
    monkeypatch.setattr(CgroupV2Sandbox, "read_cpu_seconds", mock_read_cpu)

    def mock_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        return [VERIFIED_C60_POLY], 0.60, 0.60

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_pool)

    # Budget allowance: 1.00s.
    # If 0.60 pool was added to 0.70 cgroup, total would be 1.30s -> incorrect rejection!
    # With single cumulative counter, total is 0.70s -> accepted!
    budget = SearchBudget(max_cpu_seconds=1.00, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="cumulative_counter_test",
    )

    assert record.passed, f"Should pass within 1.00s budget, rejected with: {record.rejection_reason}"
    assert record.evidence.actual_cpu_seconds == 0.70
    assert record.evidence.termination_status == "COMPLETED"


def test_unreadable_cgroup_cpu_triggers_error_status(tmp_path, monkeypatch):
    """Verify that unreadable cgroup cpu.stat immediately terminates execution with ERROR."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs", require_containment=False)

    def unreadable_cpu(self):
        raise RuntimeError("Permission denied reading cpu.stat")

    monkeypatch.setattr(CgroupV2Sandbox, "setup_cgroup", lambda self, budget: True)
    monkeypatch.setattr(CgroupV2Sandbox, "attach_pid", lambda self, pid: True)
    monkeypatch.setattr(CgroupV2Sandbox, "read_cpu_seconds", unreadable_cpu)

    def mock_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        return [VERIFIED_C60_POLY], 0.10, 0.10

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_pool)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="unreadable_cpu_test",
    )

    assert not record.passed
    assert record.evidence.termination_status == "ERROR"
    assert "Authoritative cgroup CPU unreadable" in record.rejection_reason


def test_helper_large_payload_no_deadlock(tmp_path, monkeypatch):
    """Verify that large helper return payloads (>128 KiB) complete cleanly without queue/join deadlock."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
    import time

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs")

    # Generate a payload with 256 KiB of data
    large_payload_string = "A" * (256 * 1024)

    def mock_large_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        # Return pool with large metadata
        poly_copy = VERIFIED_C60_POLY.model_copy()
        return ([poly_copy], 0.05, 0.05, large_payload_string)

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_large_pool)

    # Wall allowance of 2.0s: queue deadlock would produce TIMEOUT
    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=2.0)
    t0 = time.monotonic()
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="large_payload_test",
    )
    elapsed = time.monotonic() - t0

    assert record.passed
    assert record.evidence.termination_status == "COMPLETED"
    assert elapsed < 1.5, f"Execution took {elapsed:.2f}s, indicating potential IPC stall"


def test_helper_environment_and_network_namespace_isolation(tmp_path, monkeypatch):
    """Verify that helper receives isolated environment (no credentials, thread caps) and separate network namespace."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
    import os

    monkeypatch.setenv("SYNTHETIC_CREDENTIAL", "synthetic_test_secret_123")
    monkeypatch.setenv("OMP_NUM_THREADS", "17")

    supervisor_net_ns = os.readlink("/proc/self/ns/net") if os.path.exists("/proc/self/ns/net") else None

    probe_file = tmp_path / "probe_result.json"

    def probe_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        import json
        helper_net_ns = os.readlink("/proc/self/ns/net") if os.path.exists("/proc/self/ns/net") else None
        same_ns = (helper_net_ns == supervisor_net_ns) if supervisor_net_ns else False
        cred_inherited = ("SYNTHETIC_CREDENTIAL" in os.environ)
        omp_threads = os.environ.get("OMP_NUM_THREADS")
        probe_file.write_text(json.dumps({
            "same_ns": same_ns,
            "cred_inherited": cred_inherited,
            "omp_threads": omp_threads,
        }))
        return [VERIFIED_C60_POLY], 0.05, 0.05

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs", require_containment=False)
    monkeypatch.setattr(CgroupV2Sandbox, "setup_cgroup", lambda self, budget: True)
    monkeypatch.setattr(CgroupV2Sandbox, "attach_pid", lambda self, pid: True)
    monkeypatch.setattr(CgroupV2Sandbox, "read_cpu_seconds", lambda self: 0.05)
    monkeypatch.setattr(CgroupV2Sandbox, "read_peak_memory_mb", lambda self: 10.0)
    monkeypatch.setattr(runner.selector, "generate_stage1_pool", probe_pool)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="helper_isolation_test",
    )

    assert record.passed
    assert probe_file.exists(), "Helper must have executed and written probe result"
    probe_result = json.loads(probe_file.read_text())
    assert probe_result.get("cred_inherited") is False, "Synthetic credentials must not be inherited"
    assert probe_result.get("omp_threads") == "1", f"OMP_NUM_THREADS must be capped to 1, got {probe_result.get('omp_threads')}"
    if os.path.exists("/proc/self/ns/net") and sys.platform.startswith("linux"):
        assert probe_result.get("same_ns") is False, "Helper must not share network namespace with supervisor"


def test_initial_authoritative_cpu_read_failure_fails_closed(tmp_path, monkeypatch):
    """Verify that a failure on the initial cgroup CPU read immediately returns ERROR with cleanup."""
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    runner = MonitoredCandidateRunner(artifact_dir=tmp_path / "runs", require_containment=True)

    read_count = 0
    def mock_read_cpu(self):
        nonlocal read_count
        read_count += 1
        if read_count == 1:
            raise RuntimeError("Initial cgroup cpu.stat read failed")
        return 0.05

    cleanup_called = False
    def mock_cleanup(self):
        nonlocal cleanup_called
        cleanup_called = True

    monkeypatch.setattr(CgroupV2Sandbox, "setup_cgroup", lambda self, budget: True)
    monkeypatch.setattr(CgroupV2Sandbox, "attach_pid", lambda self, pid: True)
    monkeypatch.setattr(CgroupV2Sandbox, "read_cpu_seconds", mock_read_cpu)
    monkeypatch.setattr(CgroupV2Sandbox, "cleanup", mock_cleanup)

    def mock_pool(n, profile, timeout_seconds=300.0, run_ropt_on_candidates=True):
        return [VERIFIED_C60_POLY], 0.05, 0.05

    monkeypatch.setattr(runner.selector, "generate_stage1_pool", mock_pool)

    budget = SearchBudget(max_cpu_seconds=5.0, max_wall_seconds=5.0)
    record = runner.run_candidate(
        candidate=RankerCandidate(),
        N=VERIFIED_C60_POLY.N,
        profile=CADO_PARAMS_C60,
        budget=budget,
        seed=42,
        instance_id="initial_read_fail_test",
    )

    assert not record.passed
    assert record.evidence.termination_status == "ERROR"
    assert "Authoritative cgroup CPU unreadable at start" in record.rejection_reason
    assert cleanup_called is True, "Sandbox cleanup must be guaranteed on initial read failure"



