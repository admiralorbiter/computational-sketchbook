"""Adversarial test verifying mechanical enforcement of per_modulus_timeout_cpu_seconds."""

from unittest.mock import MagicMock
import pytest
from nsb.experiments.wave2_runner import Wave2ConfirmatoryRunner
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator


def test_evaluator_aborts_on_per_modulus_cpu_ceiling():
    """Verify AlgebraicEvaluator.evaluate_modulus_cohort raises TimeoutError when a modulus exceeds CPU limit."""
    evaluator = AlgebraicEvaluator()
    # Mock evaluate_paired_b3 to simulate an expensive modulus taking 5.5s CPU (e.g. 2.5s d=2, 3.0s d=3)
    evaluator.evaluate_paired_b3 = MagicMock(return_value={
        "deg3": {"yield_rate": 0.05, "relation_rate": 100.0},
        "deg2": {"yield_rate": 0.01, "relation_rate": 50.0},
        "yield_diff": 0.04,
        "yield_gain": 5.0,
        "deg2_cpu_sec": 2.5,
        "deg3_cpu_sec": 3.0,  # Combined 5.5s > 5.0s ceiling
        "n11_both": 0,
        "n10_deg3_only": 5,
        "n01_deg2_only": 1,
        "n00_neither": 94,
        "mcnemar_pvalue": 0.01,
    })

    with pytest.raises(TimeoutError, match="exceeded CPU budget ceiling"):
        evaluator.evaluate_modulus_cohort(
            moduli=[10403],
            max_cpu_seconds_per_modulus=5.0,
        )


def test_runner_aborts_and_refuses_certification_on_cpu_budget_exceeded():
    """Verify Wave2ConfirmatoryRunner refuses certification and aborts when evaluate_paired_b3 exceeds 5.0s CPU."""
    runner = Wave2ConfirmatoryRunner(allow_dirty=True)

    # Mock evaluate_paired_b3 to return 6.0 CPU seconds
    runner.evaluator.evaluate_paired_b3 = MagicMock(return_value={
        "deg3": {"yield_rate": 0.05, "relation_rate": 100.0},
        "deg2": {"yield_rate": 0.01, "relation_rate": 50.0},
        "yield_diff": 0.04,
        "yield_gain": 5.0,
        "deg2_cpu_sec": 3.0,
        "deg3_cpu_sec": 3.0,  # Combined 6.0s > 5.0s ceiling
        "n11_both": 0,
        "n10_deg3_only": 5,
        "n01_deg2_only": 1,
        "n00_neither": 94,
        "mcnemar_pvalue": 0.01,
    })

    with pytest.raises(TimeoutError, match="exceeded CPU budget ceiling"):
        runner.run(max_sizes=1)


def test_runner_retrospective_check_aborts_on_cpu_budget_exceeded():
    """Verify Wave2ConfirmatoryRunner retrospective check catches any modulus reporting >5.0s CPU."""
    runner = Wave2ConfirmatoryRunner(allow_dirty=True)

    fake_cohort_data = {
        "n_moduli": 1,
        "mean_cand_yield": 0.05,
        "mean_base_yield": 0.01,
        "mean_paired_diff": 0.04,
        "candidate_wins": 1,
        "win_rate": 1.0,
        "wilcoxon_pvalue": 0.001,
        "paired_t_pvalue": 0.001,
        "mean_cand_throughput": 1000.0,
        "mean_base_throughput": 500.0,
        "throughput_ratio": 2.0,
        "ci_95": (0.01, 0.07),
        "per_modulus": [
            {
                "N": 99999999,
                "cand_yield": 0.05,
                "base_yield": 0.01,
                "yield_diff": 0.04,
                "yield_gain": 5.0,
                "cand_throughput": 1000.0,
                "base_throughput": 500.0,
                "deg2_cpu_sec": 2.5,
                "deg3_cpu_sec": 3.5,
                "cpu_seconds": 6.0,  # Exceeds 5.0s ceiling
                "mcnemar_pvalue": 0.01,
            }
        ],
    }

    runner.evaluator.evaluate_modulus_cohort = MagicMock(return_value=fake_cohort_data)

    with pytest.raises(TimeoutError, match="exceeded CPU budget ceiling"):
        runner.run(max_sizes=1)
