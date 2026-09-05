"""Comprehensive unit and adversarial tests for data-driven PromotionJudge."""

import pytest
from nsb.auditor.judge import (
    BaselineObservation,
    CriterionStatus,
    PromotionJudge,
    TrackAObservation,
    TrackBObservation,
    TrackCObservation,
    TrackDObservation,
    TrackVerdict,
)
from nsb.director.engine import ResearchDirector


def test_promotion_judge_empty_data():
    """Adversarial check: Empty input data MUST yield NOT_ENOUGH_DATA, never pass."""
    judge = PromotionJudge()
    judgments = judge.evaluate_all(track_data={})

    for trk in ["A", "B", "C", "D"]:
        ev = judgments[trk]
        assert ev.verdict == TrackVerdict.NOT_ENOUGH_DATA
        assert ev.criteria[0].status == CriterionStatus.NOT_ENOUGH_DATA
        assert "no data" in ev.primary_metric_value


def test_track_a_empirical_and_adversarial():
    judge = PromotionJudge()

    # 1. Measured empirical data: collapse to 0 at 32b
    empirical_obs = [
        TrackAObservation(bits=16, candidate_rate=10.6, baseline_rate=10.7, candidate_relations=35, baseline_relations=32),
        TrackAObservation(bits=20, candidate_rate=1.0, baseline_rate=2.8, candidate_relations=4, baseline_relations=10),
        TrackAObservation(bits=32, candidate_rate=0.0, baseline_rate=0.0, candidate_relations=0, baseline_relations=0),
    ]
    res = judge.evaluate_track_a(empirical_obs)
    assert res.verdict == TrackVerdict.INCONCLUSIVE
    assert any(c.name == "relation_rate_gain" and c.status == CriterionStatus.FAIL for c in res.criteria)
    assert any(c.name == "scaling_persistence" and c.status == CriterionStatus.FAIL for c in res.criteria)
    assert "0.99x at 16b" in res.criteria[0].observed_value or "10.6 vs 10.7" in res.criteria[0].observed_value

    # 2. Adversarial winning run: >= 1.5x across 3 adjacent sizes, no zero collapse
    winning_obs = [
        TrackAObservation(bits=16, candidate_rate=30.0, baseline_rate=15.0, candidate_relations=50, baseline_relations=25),
        TrackAObservation(bits=20, candidate_rate=20.0, baseline_rate=10.0, candidate_relations=40, baseline_relations=20),
        TrackAObservation(bits=24, candidate_rate=10.0, baseline_rate=5.0, candidate_relations=30, baseline_relations=15),
    ]
    res_win = judge.evaluate_track_a(winning_obs)
    assert res_win.verdict == TrackVerdict.PROMOTED
    assert all(c.status == CriterionStatus.PASS for c in res_win.criteria)

    # 3. Missing one size: only 2 sizes >= 1.5x
    short_obs = winning_obs[:2]
    res_short = judge.evaluate_track_a(short_obs)
    assert res_short.verdict == TrackVerdict.INCONCLUSIVE

    # 4. Permutation invariance: reordered input must produce identical verdict
    reordered_obs = [winning_obs[2], winning_obs[0], winning_obs[1]]
    res_reordered = judge.evaluate_track_a(reordered_obs)
    assert res_reordered.verdict == res_win.verdict
    assert res_reordered.bit_range == res_win.bit_range


def test_track_b_empirical_and_adversarial():
    judge = PromotionJudge()

    # 1. Measured empirical data: cubic passed B1 across 32, 48, 64b, B3 not evaluated
    empirical_obs = [
        TrackBObservation(bits=32, deg2_log_norm=30.68, deg3_log_norm=23.80, b3_pairs=141),
        TrackBObservation(bits=48, deg2_log_norm=46.79, deg3_log_norm=34.99, b3_pairs=141),
        TrackBObservation(bits=64, deg2_log_norm=61.97, deg3_log_norm=46.06, b3_pairs=141),
    ]
    res = judge.evaluate_track_b(empirical_obs)
    assert res.verdict == TrackVerdict.CANDIDATE
    assert res.bit_range == "32-64"
    assert any(c.name == "b1_log_norm_advantage" and c.status == CriterionStatus.PASS for c in res.criteria)
    assert any(c.name == "b3_downstream_yield_promotion" and c.status == CriterionStatus.NOT_ENOUGH_DATA for c in res.criteria)
    assert "46.06 (64b)" in res.primary_metric_value

    # 2. Adversarial winning run: B1 pass AND B3 smooth relations evaluated
    winning_obs = [
        TrackBObservation(bits=32, deg2_log_norm=30.68, deg3_log_norm=23.80, b3_pairs=141, b3_smooth_relations=15),
        TrackBObservation(bits=48, deg2_log_norm=46.79, deg3_log_norm=34.99, b3_pairs=141, b3_smooth_relations=10),
        TrackBObservation(bits=64, deg2_log_norm=61.97, deg3_log_norm=46.06, b3_pairs=141, b3_smooth_relations=5),
    ]
    res_win = judge.evaluate_track_b(winning_obs)
    assert res_win.verdict == TrackVerdict.PROMOTED
    assert all(c.status == CriterionStatus.PASS for c in res_win.criteria)

    # 3. Adversarial inverted scores: deg3 has higher log norm (fails B1)
    inverted_obs = [
        TrackBObservation(bits=32, deg2_log_norm=20.0, deg3_log_norm=30.0),
        TrackBObservation(bits=48, deg2_log_norm=30.0, deg3_log_norm=45.0),
    ]
    res_inv = judge.evaluate_track_b(inverted_obs)
    assert res_inv.verdict == TrackVerdict.REJECTED
    assert res_inv.criteria[0].status == CriterionStatus.FAIL

    # 4. Permutation invariance
    reordered_b = [empirical_obs[2], empirical_obs[0], empirical_obs[1]]
    res_reordered = judge.evaluate_track_b(reordered_b)
    assert res_reordered.verdict == res.verdict
    assert res_reordered.bit_range == "32-64"


def test_track_c_empirical_and_adversarial():
    judge = PromotionJudge()

    # 1. Measured empirical data: 1/3 recovered at 50%, synthetic at 25%
    empirical_obs = [
        TrackCObservation(bits=32, fraction=0.50, success=True, wall_seconds=0.13, is_synthetic=False),
        TrackCObservation(bits=40, fraction=0.50, success=False, wall_seconds=0.21, is_synthetic=False),
        TrackCObservation(bits=48, fraction=0.50, success=False, wall_seconds=0.42, is_synthetic=False),
        TrackCObservation(bits=32, fraction=0.25, success=False, wall_seconds=0.01, is_synthetic=True),
    ]
    res = judge.evaluate_track_c(empirical_obs)
    assert res.verdict == TrackVerdict.CALIBRATION_INCOMPLETE
    assert any(c.name == "50pct_msb_recovery_rate" and c.status == CriterionStatus.FAIL for c in res.criteria)
    assert any(c.name == "calibration_ladder_completeness" and c.status == CriterionStatus.NOT_ENOUGH_DATA for c in res.criteria)
    assert "1/3 recovered" in res.criteria[0].observed_value

    # 2. Adversarial winning run: 100% at 50% across ladder + genuine fractions (no synthetic)
    winning_obs = [
        TrackCObservation(bits=32, fraction=0.50, success=True, wall_seconds=0.10, is_synthetic=False),
        TrackCObservation(bits=40, fraction=0.50, success=True, wall_seconds=0.15, is_synthetic=False),
        TrackCObservation(bits=48, fraction=0.50, success=True, wall_seconds=0.25, is_synthetic=False),
        TrackCObservation(bits=32, fraction=0.25, success=False, wall_seconds=0.05, is_synthetic=False),
        TrackCObservation(bits=32, fraction=0.35, success=False, wall_seconds=0.05, is_synthetic=False),
        TrackCObservation(bits=32, fraction=0.45, success=True, wall_seconds=0.08, is_synthetic=False),
    ]
    res_win = judge.evaluate_track_c(winning_obs)
    assert res_win.verdict == TrackVerdict.PROMOTED
    assert all(c.status == CriterionStatus.PASS for c in res_win.criteria)

    # 3. Complete failure at 50%
    fail_obs = [
        TrackCObservation(bits=32, fraction=0.50, success=False, wall_seconds=0.10, is_synthetic=False),
        TrackCObservation(bits=40, fraction=0.50, success=False, wall_seconds=0.15, is_synthetic=False),
    ]
    res_fail = judge.evaluate_track_c(fail_obs)
    assert res_fail.verdict == TrackVerdict.REJECTED


def test_track_d_empirical_and_adversarial():
    judge = PromotionJudge()

    # 1. Measured empirical data: 5 bit sizes characterized for Schoolbook SAT, no candidate
    empirical_obs = [
        TrackDObservation(bits=16, baseline_solve_time=0.0011, sat_vars=200, sat_clauses=978),
        TrackDObservation(bits=20, baseline_solve_time=0.0033, sat_vars=310, sat_clauses=1562),
        TrackDObservation(bits=24, baseline_solve_time=0.0145, sat_vars=444, sat_clauses=2282),
        TrackDObservation(bits=28, baseline_solve_time=0.0409, sat_vars=602, sat_clauses=3138),
        TrackDObservation(bits=32, baseline_solve_time=0.2237, sat_vars=784, sat_clauses=4130),
    ]
    res = judge.evaluate_track_d(empirical_obs)
    assert res.verdict == TrackVerdict.BASELINE_ESTABLISHED
    assert any(c.name == "baseline_characterization" and c.status == CriterionStatus.PASS for c in res.criteria)
    assert any(c.name == "comparative_encoding_advantage" and c.status == CriterionStatus.NOT_ENOUGH_DATA for c in res.criteria)
    assert "0.0011s (16b)" in res.primary_metric_value
    assert "0.2237s (32b)" in res.primary_metric_value

    # 2. Adversarial winning run: candidate encoding achieves >= 2x speedup on >= 3 sizes
    winning_obs = [
        TrackDObservation(bits=16, baseline_solve_time=0.010, candidate_solve_time=0.003),
        TrackDObservation(bits=20, baseline_solve_time=0.030, candidate_solve_time=0.008),
        TrackDObservation(bits=24, baseline_solve_time=0.100, candidate_solve_time=0.020),
    ]
    res_win = judge.evaluate_track_d(winning_obs)
    assert res_win.verdict == TrackVerdict.PROMOTED
    assert all(c.status == CriterionStatus.PASS for c in res_win.criteria)


def test_director_responsive_proposals():
    judge = PromotionJudge()
    empirical_data = {
        "A": [
            TrackAObservation(bits=16, candidate_rate=10.6, baseline_rate=10.7, candidate_relations=35, baseline_relations=32),
            TrackAObservation(bits=32, candidate_rate=0.0, baseline_rate=0.0, candidate_relations=0, baseline_relations=0),
        ],
        "B": [
            TrackBObservation(bits=32, deg2_log_norm=30.68, deg3_log_norm=23.80),
        ],
        "C": [
            TrackCObservation(bits=32, fraction=0.50, success=True, wall_seconds=0.13),
            TrackCObservation(bits=40, fraction=0.50, success=False, wall_seconds=0.21),
        ],
        "D": [
            TrackDObservation(bits=16, baseline_solve_time=0.0011),
            TrackDObservation(bits=20, baseline_solve_time=0.0033),
            TrackDObservation(bits=24, baseline_solve_time=0.0145),
        ],
    }
    judgments = judge.evaluate_all(track_data=empirical_data)

    director = ResearchDirector(mode="proposal_only")
    proposals = director.propose_next_experiments(latest_metrics=judgments)

    assert len(proposals) == 4
    prop_by_track = {p.track: p for p in proposals}

    assert "A" in prop_by_track
    assert "collapse" in prop_by_track["A"].mechanism or "grid" in prop_by_track["A"].hypothesis

    assert "B" in prop_by_track
    assert "B3" in prop_by_track["B"].hypothesis or "sieve" in prop_by_track["B"].mechanism

    assert "C" in prop_by_track
    assert "calibration" in prop_by_track["C"].hypothesis.lower()

    assert "D" in prop_by_track
    assert "carry-save" in prop_by_track["D"].hypothesis.lower()


def test_promotion_judge_custom_criteria_contract():
    """Verify that PromotionJudge dynamically adapts evaluations when provided custom criteria config."""
    custom_criteria = {
        "track_a": {
            "min_advantage_ratio": 2.5,  # Stricter than standard 1.5
            "min_consecutive_sizes": 2,
        },
        "track_b": {
            "require_b3_for_promotion": False,  # Relaxed: promotes on B1 alone
            "b1_norm_ratio_threshold": 0.90,
        },
        "track_c": {
            "required_recovery_rate": 0.30,  # Relaxed: 30% recovery rate accepted
        },
        "track_d": {
            "require_paired_encoding": False,  # Relaxed: baseline alone promoted
            "min_baseline_sizes": 3,
        },
    }

    judge_default = PromotionJudge()
    judge_custom = PromotionJudge(criteria_config=custom_criteria)

    # Track A test: ratio is 2.0x across sizes
    obs_a = [
        TrackAObservation(bits=16, candidate_rate=20.0, baseline_rate=10.0, candidate_relations=20, baseline_relations=10),
        TrackAObservation(bits=20, candidate_rate=20.0, baseline_rate=10.0, candidate_relations=20, baseline_relations=10),
        TrackAObservation(bits=24, candidate_rate=20.0, baseline_rate=10.0, candidate_relations=20, baseline_relations=10),
    ]
    # Under default (1.5x), 2.0x passes -> PROMOTED
    assert judge_default.evaluate_track_a(obs_a).verdict == TrackVerdict.PROMOTED
    # Under custom (2.5x), 2.0x fails -> INCONCLUSIVE
    assert judge_custom.evaluate_track_a(obs_a).verdict == TrackVerdict.INCONCLUSIVE

    # Track B test: B1 pass, B3 missing
    obs_b = [
        TrackBObservation(bits=32, deg2_log_norm=30.0, deg3_log_norm=20.0),
        TrackBObservation(bits=48, deg2_log_norm=45.0, deg3_log_norm=30.0),
        TrackBObservation(bits=64, deg2_log_norm=60.0, deg3_log_norm=40.0),
    ]
    # Under default, require_b3=True -> CANDIDATE
    assert judge_default.evaluate_track_b(obs_b).verdict == TrackVerdict.CANDIDATE
    # Under custom, require_b3=False -> PROMOTED
    assert judge_custom.evaluate_track_b(obs_b).verdict == TrackVerdict.PROMOTED

    # Track C test: 1/3 recovered at 50%
    obs_c = [
        TrackCObservation(bits=32, fraction=0.50, success=True),
        TrackCObservation(bits=40, fraction=0.50, success=False),
        TrackCObservation(bits=48, fraction=0.50, success=False),
    ]
    # Under default, required_recovery_rate=1.0 -> FAIL on crit1
    eval_c_default = judge_default.evaluate_track_c(obs_c)
    assert eval_c_default.criteria[0].status == CriterionStatus.FAIL
    # Under custom, required_recovery_rate=0.30 -> PASS on crit1 (1/3 = 33.3% >= 30%)
    eval_c_custom = judge_custom.evaluate_track_c(obs_c)
    assert eval_c_custom.criteria[0].status == CriterionStatus.PASS

    # Track D test: 3 baseline sizes characterized, candidate missing
    obs_d = [
        TrackDObservation(bits=16, baseline_solve_time=0.01),
        TrackDObservation(bits=20, baseline_solve_time=0.03),
        TrackDObservation(bits=24, baseline_solve_time=0.09),
    ]
    # Under default, require_paired=True -> BASELINE_ESTABLISHED
    assert judge_default.evaluate_track_d(obs_d).verdict == TrackVerdict.BASELINE_ESTABLISHED
    # Under custom, require_paired=False -> PROMOTED
    assert judge_custom.evaluate_track_d(obs_d).verdict == TrackVerdict.PROMOTED


def test_track_b_mcnemar_and_replication_criteria():
    """Verify Track B paired B3 evaluation with McNemar statistics and sample replication constraint."""
    judge = PromotionJudge(criteria_path="config/contracts/r1_wave1_criteria.yaml")

    # Single instance per size (32b, 48b, 64b) with strong B3 yield
    obs = [
        TrackBObservation(
            bits=32,
            deg2_log_norm=30.0,
            deg3_log_norm=20.0,
            deg2_b3_pairs=100,
            deg2_b3_smooth=2,
            deg3_b3_pairs=100,
            deg3_b3_smooth=30,
            n11_both=2,
            n10_deg3_only=28,
            n01_deg2_only=0,
            n00_neither=70,
            yield_gain=15.0,
        ),
        TrackBObservation(
            bits=48,
            deg2_log_norm=45.0,
            deg3_log_norm=32.0,
            deg2_b3_pairs=100,
            deg2_b3_smooth=0,
            deg3_b3_smooth=10,
            deg3_b3_pairs=100,
            n11_both=0,
            n10_deg3_only=10,
            n01_deg2_only=0,
            n00_neither=90,
            yield_gain=1.0,  # No 999.0 sentinel!
        ),
        TrackBObservation(
            bits=64,
            deg2_log_norm=60.0,
            deg3_log_norm=44.0,
            deg2_b3_pairs=100,
            deg2_b3_smooth=0,
            deg3_b3_smooth=5,
            deg3_b3_pairs=100,
            n11_both=0,
            n10_deg3_only=5,
            n01_deg2_only=0,
            n00_neither=95,
            yield_gain=1.0,
        ),
    ]

    res = judge.evaluate_track_b(obs)
    # Must be CANDIDATE due to single instance per size (requires 5)
    assert res.verdict == TrackVerdict.CANDIDATE
    assert "confirmatory replication on 20-50 instances warranted" in res.delta_description
    assert any(c.name == "confirmatory_sample_replication" and c.status == CriterionStatus.FAIL for c in res.criteria)
    assert any(c.name == "b3_downstream_yield_promotion" and c.status == CriterionStatus.PASS for c in res.criteria)
    # Check that 999.0 is nowhere in the observed value or justification
    for c in res.criteria:
        assert "999" not in c.observed_value
        assert "999" not in c.justification


def test_replication_minimum_distribution():
    """Verify that sample replication gate uses the minimum count among bit sizes, not the average."""
    judge = PromotionJudge(criteria_path="config/contracts/r1_wave1_criteria.yaml")

    # Unbalanced distribution: 10 at 32b, 10 at 48b, but only 1 at 64b (average = 7, min = 1, threshold = 5)
    obs = []
    for _ in range(10):
        obs.append(TrackBObservation(bits=32, deg2_log_norm=30.0, deg3_log_norm=20.0, deg2_b3_pairs=100, deg2_b3_smooth=1, deg3_b3_pairs=100, deg3_b3_smooth=10, n10_deg3_only=9, yield_gain=10.0))
    for _ in range(10):
        obs.append(TrackBObservation(bits=48, deg2_log_norm=45.0, deg3_log_norm=30.0, deg2_b3_pairs=100, deg2_b3_smooth=1, deg3_b3_pairs=100, deg3_b3_smooth=10, n10_deg3_only=9, yield_gain=10.0))
    obs.append(TrackBObservation(bits=64, deg2_log_norm=60.0, deg3_log_norm=40.0, deg2_b3_pairs=100, deg2_b3_smooth=1, deg3_b3_pairs=100, deg3_b3_smooth=10, n10_deg3_only=9, yield_gain=10.0))

    res = judge.evaluate_track_b(obs)
    # Average is 21 // 3 = 7 >= 5, but MINIMUM is 1 < 5, so it MUST fail replication and be CANDIDATE
    rep_crit = next(c for c in res.criteria if c.name == "confirmatory_sample_replication")
    assert rep_crit.status == CriterionStatus.FAIL
    assert "min 1 instance(s)" in rep_crit.observed_value
    assert res.verdict == TrackVerdict.CANDIDATE