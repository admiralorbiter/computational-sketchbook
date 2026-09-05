"""Tests for modulus-level paired statistical evaluation and 4-tier anti-inflation promotion logic."""

import pytest
from nsb.auditor.judge import PromotionJudge, Wave2CohortObservation
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator


def test_evaluator_evaluate_modulus_cohort():
    evaluator = AlgebraicEvaluator(small_primes_bound=50)
    # Small test moduli
    moduli = [10403, 11849, 13189]
    res = evaluator.evaluate_modulus_cohort(moduli, bound_a=20, bound_b=5)

    assert res["n_moduli"] == 3
    assert "mean_paired_diff" in res
    assert "candidate_wins" in res
    assert "win_rate" in res
    assert "wilcoxon_pvalue" in res
    assert "paired_t_pvalue" in res
    assert "diagnostic_intra_mcnemar_pooled" in res
    assert len(res["per_modulus"]) == 3


def _make_zero_yield_cohort(bits: int, n_moduli: int = 30) -> Wave2CohortObservation:
    return Wave2CohortObservation(
        bits=bits,
        n_moduli=n_moduli,
        mean_cand_yield=0.0,
        mean_base_yield=0.0,
        mean_paired_diff=0.0,
        candidate_wins=0,
        win_rate=0.0,
        wilcoxon_pvalue=1.0,
        paired_t_pvalue=1.0,
        mean_cand_throughput=0.0,
        mean_base_throughput=0.0,
    )


def test_judge_wave2_anti_inflation_tier1_only():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # Synthetic cohorts across all 5 sizes where cubic replication passes on 32b
    # and zero yield floor is reached on larger sizes
    cohorts = {
        32: Wave2CohortObservation(
            bits=32,
            n_moduli=30,
            mean_cand_yield=0.15,
            mean_base_yield=0.01,
            mean_paired_diff=0.14,
            candidate_wins=27,
            win_rate=27 / 30,  # 90% >= 70% threshold
            wilcoxon_pvalue=1e-5,
            paired_t_pvalue=1e-6,
            mean_cand_throughput=50000.0,
            mean_base_throughput=3500.0,
            throughput_ratio=14.2,
        ),
        48: _make_zero_yield_cohort(48),
        64: _make_zero_yield_cohort(64),
        80: _make_zero_yield_cohort(80),
        96: _make_zero_yield_cohort(96),
    }

    # Partial run rejection test
    partial_res = judge.evaluate_wave2_b_confirmatory({32: cohorts[32]})
    assert partial_res["verdict"] == "PARTIAL_RUN_DIAGNOSTIC_ONLY"

    eval_result = judge.evaluate_wave2_b_confirmatory(cohorts)

    # ANTI-INFLATION ASSERTION:
    # Strong replication evidence MUST NOT promote to SOTA or scaling certification!
    assert eval_result["verdict"] == "REPLICATION_CERTIFIED"
    assert eval_result["claims"]["tier1_replication"]["status"] == "PASS"
    assert eval_result["claims"]["tier2_search"]["status"] == "NOT_ENOUGH_DATA"
    assert eval_result["claims"]["tier3_sota_proxy"]["status"] == "NOT_ENOUGH_DATA"
    assert eval_result["claims"]["tier4_scaling"]["status"] == "NOT_ENOUGH_DATA"


def test_judge_wave2_enforces_paired_t_test():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # Cohort where Wilcoxon passes (p=1e-5), but paired t-test fails (p=0.03 > 0.01)
    cohorts = {
        32: Wave2CohortObservation(
            bits=32,
            n_moduli=30,
            mean_cand_yield=0.15,
            mean_base_yield=0.01,
            mean_paired_diff=0.14,
            candidate_wins=25,
            win_rate=25 / 30,
            wilcoxon_pvalue=1e-5,  # Passes
            paired_t_pvalue=0.03,  # FAILS (threshold 0.01)
            mean_cand_throughput=50000.0,
            mean_base_throughput=3500.0,
        ),
        48: _make_zero_yield_cohort(48),
        64: _make_zero_yield_cohort(64),
        80: _make_zero_yield_cohort(80),
        96: _make_zero_yield_cohort(96),
    }

    eval_result = judge.evaluate_wave2_b_confirmatory(cohorts)
    # Must fail because paired t-test gate is mechanically enforced
    assert eval_result["verdict"] == "REPLICATION_FAILED"
    assert eval_result["claims"]["tier1_replication"]["status"] == "FAIL"
    assert eval_result["claims"]["tier1_replication"]["per_size_verdicts"][32] == "FAIL"


def test_judge_wave2_replication_inconclusive_under_replicated():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # Under-replicated across cohorts (only 10 moduli instead of 30): should be INCONCLUSIVE
    cohorts = {
        b: Wave2CohortObservation(
            bits=b,
            n_moduli=10,
            mean_cand_yield=0.15 if b == 32 else 0.0,
            mean_base_yield=0.01 if b == 32 else 0.0,
            mean_paired_diff=0.14 if b == 32 else 0.0,
            candidate_wins=9 if b == 32 else 0,
            win_rate=0.9 if b == 32 else 0.0,
            wilcoxon_pvalue=1e-4 if b == 32 else 1.0,
            paired_t_pvalue=1e-4 if b == 32 else 1.0,
            mean_cand_throughput=50000.0 if b == 32 else 0.0,
            mean_base_throughput=3500.0 if b == 32 else 0.0,
        )
        for b in [32, 48, 64, 80, 96]
    }

    eval_result = judge.evaluate_wave2_b_confirmatory(cohorts)
    assert eval_result["verdict"] == "INCONCLUSIVE"
    assert eval_result["claims"]["tier1_replication"]["status"] == "NOT_ENOUGH_DATA"
    assert eval_result["claims"]["tier1_replication"]["per_size_verdicts"][32] == "UNDER_REPLICATED"


def test_judge_wave2_replication_failed_adequately_replicated():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # Adequately replicated (30 moduli), but candidate loses or fails win rate threshold
    cohorts = {
        32: Wave2CohortObservation(
            bits=32,
            n_moduli=30,
            mean_cand_yield=0.02,
            mean_base_yield=0.05,
            mean_paired_diff=-0.03,
            candidate_wins=10,
            win_rate=10 / 30,  # 33% < 70% threshold
            wilcoxon_pvalue=0.85,
            paired_t_pvalue=0.90,
            mean_cand_throughput=2000.0,
            mean_base_throughput=5000.0,
        ),
        48: _make_zero_yield_cohort(48),
        64: _make_zero_yield_cohort(64),
        80: _make_zero_yield_cohort(80),
        96: _make_zero_yield_cohort(96),
    }

    eval_result = judge.evaluate_wave2_b_confirmatory(cohorts)
    assert eval_result["verdict"] == "REPLICATION_FAILED"
    assert eval_result["claims"]["tier1_replication"]["status"] == "FAIL"
    assert eval_result["claims"]["tier1_replication"]["per_size_verdicts"][32] == "FAIL"


def test_judge_wave2_sota_passed():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # 5 sizes satisfying canonical 5-cohort requirement and scaling persistence requirement
    cohorts = {
        32: Wave2CohortObservation(
            bits=32,
            n_moduli=30,
            mean_cand_yield=0.15,
            mean_base_yield=0.01,
            mean_paired_diff=0.14,
            candidate_wins=28,
            win_rate=28 / 30,
            wilcoxon_pvalue=1e-5,
            paired_t_pvalue=1e-6,
            mean_cand_throughput=50000.0,
            mean_base_throughput=3500.0,
            throughput_ratio=14.2,
        ),
        48: Wave2CohortObservation(
            bits=48,
            n_moduli=30,
            mean_cand_yield=0.015,
            mean_base_yield=0.001,
            mean_paired_diff=0.014,
            candidate_wins=25,
            win_rate=25 / 30,
            wilcoxon_pvalue=0.002,
            paired_t_pvalue=0.001,
            mean_cand_throughput=1000.0,
            mean_base_throughput=50.0,
            throughput_ratio=20.0,
        ),
        64: Wave2CohortObservation(
            bits=64,
            n_moduli=30,
            mean_cand_yield=0.002,
            mean_base_yield=0.0001,
            mean_paired_diff=0.0019,
            candidate_wins=24,
            win_rate=24 / 30,
            wilcoxon_pvalue=0.003,
            paired_t_pvalue=0.002,
            mean_cand_throughput=200.0,
            mean_base_throughput=10.0,
            throughput_ratio=20.0,
        ),
        80: Wave2CohortObservation(
            bits=80,
            n_moduli=30,
            mean_cand_yield=0.0003,
            mean_base_yield=0.00001,
            mean_paired_diff=0.00029,
            candidate_wins=22,
            win_rate=22 / 30,
            wilcoxon_pvalue=0.004,
            paired_t_pvalue=0.003,
            mean_cand_throughput=50.0,
            mean_base_throughput=2.0,
            throughput_ratio=25.0,
        ),
        96: Wave2CohortObservation(
            bits=96,
            n_moduli=30,
            mean_cand_yield=0.00005,
            mean_base_yield=0.000001,
            mean_paired_diff=0.000049,
            candidate_wins=21,
            win_rate=21 / 30,
            wilcoxon_pvalue=0.005,
            paired_t_pvalue=0.004,
            mean_cand_throughput=10.0,
            mean_base_throughput=0.4,
            throughput_ratio=25.0,
        ),
    }

    search_comp = {"yield_gain": 1.25, "wilcoxon_pvalue": 0.001, "log_norm_ratio": 0.90}
    sota_comp = {"murphy_e_ratio": 1.15, "throughput_ratio": 1.10, "wilcoxon_pvalue": 0.001}

    eval_result = judge.evaluate_wave2_b_confirmatory(
        cohorts,
        search_comparison=search_comp,
        sota_comparison=sota_comp,
    )

    assert eval_result["claims"]["tier1_replication"]["status"] == "PASS"
    assert eval_result["claims"]["tier2_search"]["status"] == "PASS"
    assert eval_result["claims"]["tier3_sota_proxy"]["status"] == "PASS"
    assert eval_result["claims"]["tier4_scaling"]["status"] == "PASS"
    assert eval_result["verdict"] == "SCALING_PERSISTENCE_CERTIFIED"
