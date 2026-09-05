"""Unit tests for Gate 1 Pilot harness and review packet generation."""

from pathlib import Path
from nsb.auditor.engine import Auditor
from nsb.auditor.judge import (
    BaselineObservation,
    PromotionJudge,
    TrackAObservation,
    TrackBObservation,
    TrackCObservation,
    TrackDObservation,
)
from nsb.pilots.engine import PilotRunner
from nsb.pilots.packet import generate_pilot_review_packet


def test_pilot_runner_initialization():
    runner = PilotRunner(config_path="config/pilot.yaml", allow_dirty=True)
    assert runner.cfg.contract_id == "NSB-R0-GATE1-PILOTS"
    assert runner.cfg.benchmark_version == "v001_pilot"
    assert runner.ledger is not None


def test_generate_pilot_review_packet(tmp_path):
    auditor = Auditor()
    report = auditor.audit(require_clean_git=False)
    judge = PromotionJudge()
    
    # Structured empirical observations
    data = {
        "A": [TrackAObservation(bits=16, candidate_rate=10.6, baseline_rate=10.7, candidate_relations=35, baseline_relations=32)],
        "B": [TrackBObservation(bits=32, deg2_log_norm=30.68, deg3_log_norm=23.80)],
        "C": [TrackCObservation(bits=32, fraction=0.50, success=True, wall_seconds=0.13)],
        "D": [TrackDObservation(bits=16, baseline_solve_time=0.0011)],
    }
    judgments = judge.evaluate_all(track_data=data)
    baseline_obs = [
        BaselineObservation(family="F", method="fermat", bits=48, wall_seconds=0.0001, steps=1, success=True),
        BaselineObservation(family="P1", method="pollard_pm1", bits=48, wall_seconds=0.0002, steps=None, success=True),
        BaselineObservation(family="R", method="pollard_rho", bits=32, wall_seconds=0.0001, steps=255, success=True),
    ]

    pkt_path = generate_pilot_review_packet(
        contract_id="NSB-R0-GATE1-PILOTS",
        audit_report=report,
        benchmark_version="v001_pilot",
        wave_name="Gate 1A — Feasibility & Calibration",
        track_summaries=[
            {
                "track": "A",
                "champion_id": "TEST-A-01",
                "evidence_tier": "E1",
                "bit_range": "16-32",
                "primary_metric": "10.5 rel/cpu_s",
                "baseline": "5.0 rel/cpu_s",
                "delta": "+10%",
                "validation_status": "VALIDATED",
                "verdict": "INCONCLUSIVE",
            }
        ],
        scaling_data={"A": [{"label": "test", "bits": 32, "metric_str": "ok"}]},
        rejected_branches=[],
        director_proposals=[],
        total_compute_seconds=12.34,
        attestation_commit="abcdef1234",
        output_dir=str(tmp_path),
        judgments=judgments,
        baseline_observations=baseline_obs,
    )

    assert pkt_path.is_file()
    content = pkt_path.read_text(encoding="utf-8")
    assert "# No Silver Bullet — Gate 1 Pilot Review Packet" in content
    assert f"**Evaluated Commit**: `{report.git_sha}`" in content
    assert "**Attestation Commit**: `abcdef1234`" in content
    assert "GATE_1A_FEASIBILITY_PASSED" in content
    assert "Promotion Criteria Breakdown" in content
    assert "Track A" in content
    assert "Track B" in content
    assert "Track C" in content
    assert "Track D" in content
    assert "Fermat cleanly factored" in content