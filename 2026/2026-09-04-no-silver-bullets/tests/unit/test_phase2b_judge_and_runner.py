"""Adversarial and anti-inflation unit tests for Wave 2 Phase 2B judge and runner."""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch
import pytest

from nsb.auditor.judge import PromotionJudge, Wave2Phase2BCohortObservation
from nsb.benchmarks.corpus import (
    derive_phase2b_seed,
    derive_phase2b_seed_v4,
    generate_wave2_phase2b_holdout,
    generate_wave2_phase2b_holdout_v4,
    load_public_instances,
)
from nsb.tracks.algebraic_evolution.evaluator import (
    AlgebraicEvaluator,
    TimingInvalidError,
)
from nsb.tracks.algebraic_evolution.murphy import select_in_house_murphy_e_baseline
from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
    generate_systematic_representation_grid,
)
from nsb.tracks.algebraic_evolution.search import FrozenSearchOptimizer
from nsb.experiments.wave2_phase2b_runner import Wave2Phase2BRunner


def make_passing_phase2b_cohort(
    bits: int,
    n_moduli: int = 30,
    relation_floor_count: int = 25,
    paired_t_p: float = 1e-5,
    wilcoxon_p: float = 1e-5,
    murphy_e_ratio: float = 1.10,
    throughput_ratio: float = 1.20,
    proxy_wilcoxon_p: float = 1e-4,
    mean_cand_yield: float = 0.05,
    mean_base_yield: float = 0.01,
    mean_paired_diff: float = 0.04,
    candidate_wins: int = 25,
    yield_gain: Optional[float] = 5.0,
    mean_log_norm_ratio: float = 0.85,
    proxy_yield_diff: float = 0.01,
    raw_cand_e: Optional[float] = None,
    raw_proxy_e: Optional[float] = None,
    raw_cand_th: Optional[float] = None,
    raw_proxy_th: Optional[float] = None,
    raw_cand_yield: Optional[float] = None,
    raw_base_yield: Optional[float] = None,
    raw_log_norm_ratio: Optional[float] = None,
) -> Wave2Phase2BCohortObservation:
    floor_ratio = relation_floor_count / n_moduli if n_moduli > 0 else 0.0
    return Wave2Phase2BCohortObservation(
        bits=bits,
        n_moduli=n_moduli,
        mean_cand_yield=mean_cand_yield,
        mean_base_yield=mean_base_yield,
        mean_paired_diff=mean_paired_diff,
        candidate_wins=candidate_wins,
        win_rate=candidate_wins / n_moduli if n_moduli > 0 else 0.0,
        wilcoxon_pvalue=wilcoxon_p,
        paired_t_pvalue=paired_t_p,
        yield_gain=yield_gain,
        moduli_with_relations_cand=relation_floor_count,
        relation_floor_ratio=floor_ratio,
        mean_log_norm_ratio=mean_log_norm_ratio,
        ci_95=(0.03, 0.05),
        mean_cand_murphy_e=1.5e-4,
        mean_proxy_murphy_e=1.3e-4,
        murphy_e_ratio=murphy_e_ratio,
        cumulative_cand_throughput=5000.0,
        cumulative_proxy_throughput=4000.0,
        throughput_ratio=throughput_ratio,
        proxy_yield_diff=proxy_yield_diff,
        proxy_wilcoxon_pvalue=proxy_wilcoxon_p,
        proxy_paired_t_pvalue=1e-4,
        proxy_win_rate=0.80,
        raw_mean_cand_yield=raw_cand_yield if raw_cand_yield is not None else mean_cand_yield,
        raw_mean_base_yield=raw_base_yield if raw_base_yield is not None else mean_base_yield,
        raw_mean_cand_murphy_e=raw_cand_e,
        raw_mean_proxy_murphy_e=raw_proxy_e,
        raw_cum_cand_throughput=raw_cand_th,
        raw_cum_proxy_throughput=raw_proxy_th,
        raw_mean_log_norm_ratio=raw_log_norm_ratio if raw_log_norm_ratio is not None else mean_log_norm_ratio,
    )


def test_phase2b_judge_rejects_missing_cohorts():
    """Judge mechanically rejects partial runs missing required cohorts."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    # Only 32-bit cohort provided
    cohorts = {32: make_passing_phase2b_cohort(32)}
    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)

    assert res["verdict"] == "PARTIAL_RUN_DIAGNOSTIC_ONLY"
    assert "Missing cohorts" in res["claims"]["tier2_search"]["findings"][-1]


def test_phase2b_judge_rejects_non_canonical():
    """Judge mechanically rejects non-canonical flag even if all cohorts present."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 64, 80, 96]}
    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=False)

    assert res["verdict"] == "PARTIAL_RUN_DIAGNOSTIC_ONLY"


def test_phase2b_judge_enforces_relation_floor():
    """Candidate must produce relations on >= 50% of cohort moduli (15/30)."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    # 14 out of 30 produces relations: floor ratio = 0.467 < 0.50 -> FAILS Tier 2
    failing_cohort = make_passing_phase2b_cohort(64, relation_floor_count=14)
    cohorts_fail = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 80, 96]}
    cohorts_fail[64] = failing_cohort

    res_fail = judge.evaluate_wave2_b_phase2b(cohorts_fail, is_canonical=True)
    assert res_fail["claims"]["tier2_search"]["per_size_verdicts"][64] == "FAIL"
    assert "relation floor failed" in res_fail["claims"]["tier2_search"]["findings"][2]

    # 15 out of 30 produces relations: floor ratio = 0.50 >= 0.50 -> PASSES Tier 2
    passing_cohort = make_passing_phase2b_cohort(64, relation_floor_count=15)
    cohorts_pass = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 80, 96]}
    cohorts_pass[64] = passing_cohort

    res_pass = judge.evaluate_wave2_b_phase2b(cohorts_pass, is_canonical=True)
    assert res_pass["claims"]["tier2_search"]["per_size_verdicts"][64] == "PASS"


def test_phase2b_judge_enforces_paired_t_gate():
    """Failing paired t-test blocks Tier 2 certification even if Wilcoxon passes."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    # Wilcoxon passes (1e-5), but paired t-test fails (0.05 > 0.01)
    failing_cohort = make_passing_phase2b_cohort(64, paired_t_p=0.05, wilcoxon_p=1e-5)
    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 80, 96]}
    cohorts[64] = failing_cohort

    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier2_search"]["per_size_verdicts"][64] == "FAIL"
    assert "stats failed" in res["claims"]["tier2_search"]["findings"][2]


def test_phase2b_judge_zero_denominator_no_sentinel():
    """Baseline yield or throughput of zero produces None, avoiding 999.0 sentinels."""
    evaluator = AlgebraicEvaluator()
    pair1 = create_base_m_representation(10403, degree=3)
    pair2 = create_base_m_representation(10403, degree=2)

    # In evaluate_paired_throughput_benchmark, mock benchmark_relation_throughput to return base=0
    with patch.object(evaluator, "benchmark_relation_throughput") as mock_bm:
        mock_bm.side_effect = [
            {"throughput_relations_per_core_sec": 100.0, "cumulative_cpu_seconds": 0.26, "batches_executed": 10},
            {"throughput_relations_per_core_sec": 0.0, "cumulative_cpu_seconds": 0.26, "batches_executed": 10},
        ]
        res = evaluator.evaluate_paired_throughput_benchmark(10403, pair1, pair2)
        assert res["throughput_ratio"] is None
        assert res["throughput_ratio"] != 999.0


def test_proxy_baseline_symmetry():
    """Verify select_in_house_murphy_e_baseline() and FrozenSearchOptimizer evaluate identical 35 candidates."""
    N = 10403
    grid = generate_systematic_representation_grid(N, degree=3, translation_radius=5, rotation_u_bound=2, rotation_v_bound=2)
    assert len(grid) == 35

    # Check that canonical is candidate 0
    assert grid[0][1] == "canonical_base_m"

    # Check 10 translations
    trans_ops = [op for _, op in grid if op.startswith("translation_")]
    assert len(trans_ops) == 10

    # Check 24 rotations
    rot_ops = [op for _, op in grid if op.startswith("rotation_")]
    assert len(rot_ops) == 24

    # Run optimizer and baseline; ensure both run without error on identical grid
    opt = FrozenSearchOptimizer(budget=50)
    cand = opt.optimize(N, degree=3)
    base_pair, base_stats = select_in_house_murphy_e_baseline(N, degree=3, budget=50)

    assert cand.evaluations_run <= 35
    assert base_stats["evaluations_run"] <= 35
    assert cand.pair.degree == 3
    assert base_pair.degree == 3
    assert cand.evaluated_operations == base_stats["evaluated_operations"]


def test_evaluator_fail_closed_timing():
    """Verify TimingInvalidError is raised when cumulative CPU time < min_cpu_seconds."""
    evaluator = AlgebraicEvaluator()
    pair = create_base_m_representation(10403, degree=3)

    # Set min_cpu_seconds to 10.0 and max_repeats to 1 so underflow is guaranteed
    with pytest.raises(TimingInvalidError) as exc_info:
        evaluator.benchmark_relation_throughput(pair, bound_a=10, bound_b=2, min_cpu_seconds=10.0, max_repeats=1)

    assert "Cumulative CPU time" in str(exc_info.value)


def test_runner_enforces_whole_modulus_cpu_budget():
    """Verify Wave2Phase2BRunner aborts with TimeoutError if modulus CPU time exceeds limit."""
    runner = Wave2Phase2BRunner(allow_dirty=True)

    # Set per_modulus_cpu_limit to 0.05s while the cumulative benchmarks take >= 0.25s each
    with pytest.raises(TimeoutError) as exc_info:
        runner.evaluate_cohort([10403], bound_a=100, bound_b=20, per_modulus_cpu_limit=0.05)

    assert "exceeded whole-pipeline CPU ceiling" in str(exc_info.value)


def test_phase2b_judge_low_bits_alone_cannot_promote():
    """Passing 32b and 48b controls provides baseline calibration but zero promotion credit toward search claim."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    cohorts = {}
    for b in [32, 48]:
        cohorts[b] = make_passing_phase2b_cohort(b)
    for b in [64, 80, 96]:
        cohorts[b] = make_passing_phase2b_cohort(b, paired_t_p=0.5, wilcoxon_p=0.5)

    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier2_search"]["per_size_verdicts"][32] == "PASS"
    assert res["claims"]["tier2_search"]["per_size_verdicts"][48] == "PASS"
    assert res["claims"]["tier2_search"]["per_size_verdicts"][64] == "FAIL"
    assert res["claims"]["tier2_search"]["status"] == "FAIL"
    assert res["verdict"] == "SEARCH_ADVANTAGE_FAILED"


def test_phase2b_judge_incomplete_target_sizes_cannot_promote():
    """If 64b and 80b pass but 96b fails, global certification is denied."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 64, 80]}
    cohorts[96] = make_passing_phase2b_cohort(96, paired_t_p=0.05, wilcoxon_p=0.05)

    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier2_search"]["per_size_verdicts"][64] == "PASS"
    assert res["claims"]["tier2_search"]["per_size_verdicts"][80] == "PASS"
    assert res["claims"]["tier2_search"]["per_size_verdicts"][96] == "FAIL"
    assert res["claims"]["tier2_search"]["status"] == "FAIL"
    assert res["verdict"] == "SEARCH_ADVANTAGE_FAILED"


def test_phase2b_judge_all_target_sizes_pass_promotes():
    """When all target cohorts [64, 80, 96] pass, global certification succeeds."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 64, 80, 96]}
    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier2_search"]["status"] == "PASS"
    assert res["claims"]["tier3_proxy"]["status"] == "PASS"
    assert res["verdict"] == "IN_HOUSE_POLYSELECT_PROXY_BEATEN"

    # If Tier 3 fails on target sizes, Tier 2 still confers SEARCH_ADVANTAGE_CERTIFIED
    cohorts_t3_fail = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 64, 80, 96]}
    cohorts_t3_fail[64] = make_passing_phase2b_cohort(64, proxy_yield_diff=0.0)
    res_t2_only = judge.evaluate_wave2_b_phase2b(cohorts_t3_fail, is_canonical=True)
    assert res_t2_only["claims"]["tier2_search"]["status"] == "PASS"
    assert res_t2_only["claims"]["tier3_proxy"]["status"] == "FAIL"
    assert res_t2_only["verdict"] == "SEARCH_ADVANTAGE_CERTIFIED"


def test_phase2b_judge_target_cohort_zero_yield_is_fail():
    """Remaining at zero yield on target sizes is FAIL (relation floor), not exempt ZERO_YIELD_FLOOR."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    # Zero yield on 64b target size
    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 80, 96]}
    cohorts[64] = make_passing_phase2b_cohort(
        64,
        relation_floor_count=0,
        mean_cand_yield=0.0,
        mean_base_yield=0.0,
        mean_paired_diff=0.0,
        candidate_wins=0,
        yield_gain=None,
    )
    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier2_search"]["per_size_verdicts"][64] == "FAIL"
    assert "zero-yield floor reached on primary target size" in res["claims"]["tier2_search"]["findings"][2]

    # Zero yield on 32b supporting size is ZERO_YIELD_FLOOR (exempt)
    cohorts_supp = {b: make_passing_phase2b_cohort(b) for b in [48, 64, 80, 96]}
    cohorts_supp[32] = make_passing_phase2b_cohort(
        32,
        relation_floor_count=0,
        mean_cand_yield=0.0,
        mean_base_yield=0.0,
        mean_paired_diff=0.0,
        candidate_wins=0,
        yield_gain=None,
    )
    res_supp = judge.evaluate_wave2_b_phase2b(cohorts_supp, is_canonical=True)
    assert res_supp["claims"]["tier2_search"]["per_size_verdicts"][32] == "ZERO_YIELD_FLOOR"


def test_phase2b_judge_log_norm_ratio_gate():
    """Mean log norm ratio > 0.95 blocks Tier 2 certification."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    # 64b has mean_log_norm_ratio = 0.96 > 0.95
    failing_cohort = make_passing_phase2b_cohort(64, mean_log_norm_ratio=0.96)
    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 80, 96]}
    cohorts[64] = failing_cohort

    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier2_search"]["per_size_verdicts"][64] == "FAIL"
    assert "log-norm ratio failed" in res["claims"]["tier2_search"]["findings"][2]


def test_phase2b_judge_tier3_strict_positive_yield_diff():
    """Tier 3 requires strict proxy_yield_diff > 0.0; exactly 0.0 fails."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    # 64b has proxy_yield_diff = 0.0
    failing_cohort = make_passing_phase2b_cohort(64, proxy_yield_diff=0.0)
    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 80, 96]}
    cohorts[64] = failing_cohort

    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier3_proxy"]["per_size_verdicts"][64] == "FAIL"
    assert "empirical yield test failed" in res["claims"]["tier3_proxy"]["findings"][2]


def test_phase2b_judge_unrounded_comparison_guards():
    """Unrounded float comparisons prevent rounding-inflated gate passes."""
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_phase2b_criteria.yaml")

    # Raw Murphy E: candidate is 0.99996 of proxy, below min ratio 1.0
    cohorts = {b: make_passing_phase2b_cohort(b) for b in [32, 48, 80, 96]}
    cohorts[64] = make_passing_phase2b_cohort(
        64,
        murphy_e_ratio=1.0,
        raw_cand_e=0.99996e-4,
        raw_proxy_e=1.00000e-4,
    )
    res = judge.evaluate_wave2_b_phase2b(cohorts, is_canonical=True)
    assert res["claims"]["tier3_proxy"]["per_size_verdicts"][64] == "FAIL"
    assert "Murphy-E raw gate failed" in res["claims"]["tier3_proxy"]["findings"][2]


def test_runner_abba_timing_counterbalance():
    """Wave2Phase2BRunner alternates candidate-first and proxy-first across moduli."""
    runner = Wave2Phase2BRunner(allow_dirty=True)

    dummy_pair = create_base_m_representation(10403, degree=3)
    dummy_cand = MagicMock(pair=dummy_pair, log_norm=5.0)
    dummy_proxy_stats = {"murphy_e": 1.0e-4, "evaluations_run": 35}

    with patch.object(runner.search_optimizer, "optimize", return_value=dummy_cand), \
         patch("nsb.experiments.wave2_phase2b_runner.select_in_house_murphy_e_baseline", return_value=(dummy_pair, dummy_proxy_stats)), \
         patch("nsb.experiments.wave2_phase2b_runner.compute_murphy_e", return_value={"murphy_e": 1.0e-4}), \
         patch.object(runner.evaluator, "benchmark_relation_throughput") as mock_bm, \
         patch.object(runner.evaluator, "homogeneous_sieve_b3") as mock_sieve:
        mock_bm.return_value = {
            "throughput_relations_per_core_sec": 100.0,
            "cumulative_cpu_seconds": 0.25,
            "batches_executed": 10,
        }
        mock_sieve.return_value = {"yield_rate": 0.05, "smooth_relations": 10, "evaluated_pairs": 200}

        cohort = runner.evaluate_cohort(
            moduli=[10403, 10403, 10403, 10403],
            bound_a=100,
            bound_b=20,
            per_modulus_cpu_limit=10.0,
        )

        per_mod = cohort["per_modulus"]
        assert len(per_mod) == 4
        # Even indices: candidate first (timing_order == "cand_then_proxy")
        assert per_mod[0]["timing_order"] == "cand_then_proxy"
        assert per_mod[2]["timing_order"] == "cand_then_proxy"
        # Odd indices: proxy first (timing_order == "proxy_then_cand")
        assert per_mod[1]["timing_order"] == "proxy_then_cand"
        assert per_mod[3]["timing_order"] == "proxy_then_cand"


def test_phase2b_seed_derivation_and_holdout_generator(tmp_path):
    """Verify deterministic seed derivation and holdout generation into tmp_path."""
    freeze_sha = "8d49b15f4ec7e7bbc9e07b552644c0b7b111d647"
    seed = derive_phase2b_seed(freeze_sha)
    assert seed == 70017527946254476

    # Test generation in temporary directory (zero contamination of real benchmarks)
    manifest = generate_wave2_phase2b_holdout(tmp_path, freeze_sha)
    assert manifest["total_instances"] == 150
    assert manifest["master_seed"] == seed

    # Verify instances
    instances = load_public_instances(tmp_path, "v003_wave2", "search_holdout")
    assert len(instances) == 150
    counts: Dict[int, int] = {}
    for inst in instances:
        counts[inst.bits] = counts.get(inst.bits, 0) + 1
    assert counts == {32: 30, 48: 30, 64: 30, 80: 30, 96: 30}

    # Verify calling again without force=True raises FileExistsError
    with pytest.raises(FileExistsError):
        generate_wave2_phase2b_holdout(tmp_path, freeze_sha, force=False)


def test_phase2b_v004_seed_derivation_and_holdout_generator(tmp_path):
    """Verify deterministic v004 seed derivation and holdout generation into tmp_path."""
    freeze_sha = "0e84f80c55fd8c4bf760769ebff4d6af609ad5f1"
    seed = derive_phase2b_seed_v4(freeze_sha)
    assert isinstance(seed, int)
    assert seed > 0

    # Test generation in temporary directory (zero contamination of real benchmarks)
    manifest = generate_wave2_phase2b_holdout_v4(tmp_path, freeze_sha)
    assert manifest["total_instances"] == 150
    assert manifest["master_seed"] == seed
    assert manifest["benchmark_version"] == "v004_wave2"

    # Verify instances
    instances = load_public_instances(tmp_path, "v004_wave2", "search_holdout")
    assert len(instances) == 150
    counts: Dict[int, int] = {}
    for inst in instances:
        counts[inst.bits] = counts.get(inst.bits, 0) + 1
    assert counts == {32: 30, 48: 30, 64: 30, 80: 30, 96: 30}

    # Verify calling again without force=True raises FileExistsError
    with pytest.raises(FileExistsError):
        generate_wave2_phase2b_holdout_v4(tmp_path, freeze_sha, force=False)


