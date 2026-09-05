"""Tests for Amendment v2.1.1 judge execution guardrails and partial run rejection."""

from nsb.auditor.judge import PromotionJudge, Wave2CohortObservation


def make_passing_cohort(bits: int, n_moduli: int = 30) -> Wave2CohortObservation:
    return Wave2CohortObservation(
        bits=bits,
        n_moduli=n_moduli,
        mean_cand_yield=0.10 / (bits // 16),
        mean_base_yield=0.005 / (bits // 16),
        mean_paired_diff=0.095 / (bits // 16),
        candidate_wins=27,
        win_rate=27 / 30,
        wilcoxon_pvalue=1e-5,
        paired_t_pvalue=1e-5,
        mean_cand_throughput=10000.0,
        mean_base_throughput=500.0,
        throughput_ratio=20.0,
    )


def test_judge_rejects_partial_run_missing_cohorts():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # Only 32-bit cohort provided (missing 48, 64, 80, 96)
    cohorts = {32: make_passing_cohort(32)}

    res = judge.evaluate_wave2_b_confirmatory(cohorts, is_canonical=True)
    assert res["verdict"] == "PARTIAL_RUN_DIAGNOSTIC_ONLY"
    assert "missing" in res["claims"]["tier1_replication"]["findings"][-1].lower()


def test_judge_rejects_non_canonical_flag():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # All 5 cohorts provided, but marked non-canonical (e.g. diagnostic run)
    cohorts = {b: make_passing_cohort(b) for b in [32, 48, 64, 80, 96]}

    res = judge.evaluate_wave2_b_confirmatory(cohorts, is_canonical=False)
    assert res["verdict"] == "PARTIAL_RUN_DIAGNOSTIC_ONLY"


def test_judge_certifies_full_canonical_five_cohorts():
    judge = PromotionJudge(criteria_path="config/contracts/r2_wave2_criteria.yaml")

    # All 5 cohorts provided and is_canonical=True
    cohorts = {b: make_passing_cohort(b) for b in [32, 48, 64, 80, 96]}

    res = judge.evaluate_wave2_b_confirmatory(cohorts, is_canonical=True)
    assert res["verdict"] in ("REPLICATION_CERTIFIED", "SCALING_PERSISTENCE_CERTIFIED")
    assert res["claims"]["tier1_replication"]["status"] == "PASS"
