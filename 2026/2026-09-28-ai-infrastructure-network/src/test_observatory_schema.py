"""Unit tests for the Observatory Schema, Canonical Tables, and Monitoring Pipeline."""

from datetime import date
import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import observatory_schema as obs
    import observatory_monitor as mon
except ImportError:
    from src import observatory_schema as obs
    from src import observatory_monitor as mon


def test_clock_types_roles_and_observability():
    """Verify enums including SignalRole and Observability."""
    assert len(obs.ClockType) == 4
    assert obs.ClockType.PHYSICAL == "PHYSICAL"
    assert obs.ClockType.CONTRACT == "CONTRACT"
    assert obs.ClockType.FINANCIAL == "FINANCIAL"
    assert obs.ClockType.SUPPORT == "SUPPORT"

    assert len(obs.SignalRole) == 4
    assert obs.SignalRole.EARLY_WARNING == "EARLY_WARNING"
    assert obs.SignalRole.CONFIRMATION == "CONFIRMATION"
    assert obs.SignalRole.FINANCIAL_RECOGNITION == "FINANCIAL_RECOGNITION"
    assert obs.SignalRole.OUTCOME == "OUTCOME"

    assert len(obs.Observability) == 3
    assert obs.Observability.PUBLIC == "PUBLIC"
    assert obs.Observability.COMMERCIAL_DATA == "COMMERCIAL_DATA"
    assert obs.Observability.PRIVATE_OR_UNAVAILABLE == "PRIVATE_OR_UNAVAILABLE"


def test_load_canonical_scenarios():
    """Verify loading the 6 certified failure archetypes from Parquet."""
    scenarios = obs.load_canonical_scenarios()
    assert len(scenarios) == 6
    ids = [s.scenario_id for s in scenarios]
    assert ids == [
        "SCN-ARCH-001",
        "SCN-ARCH-002",
        "SCN-ARCH-003",
        "SCN-ARCH-004",
        "SCN-ARCH-005",
        "SCN-ARCH-006",
    ]

    # Verify PF1 Scenario 3 workout boundary (not equity cure)
    scn3 = next(s for s in scenarios if s.scenario_id == "SCN-ARCH-003")
    assert "Bondholder Workout / Debt Acceleration Boundary" in scn3.reconverging_entity
    assert "post-shortfall continuation unmodeled" in scn3.reconverging_entity

    # Verify Mackenzie Scenario 4 replacement-funding requirement (not pure equity call)
    scn4 = next(s for s in scenarios if s.scenario_id == "SCN-ARCH-004")
    assert "Borrower Capital Gap" in scn4.reconverging_entity
    assert "replacement-funding requirement" in scn4.reconverging_entity


def test_load_canonical_indicators():
    """Verify loading certified indicators with SignalRole and Observability."""
    indicators = obs.load_canonical_indicators()
    assert len(indicators) == 13

    # Verify NMSLO pipeline denial: EARLY_WARNING, PUBLIC, OBSERVED 65d
    jup_permit = next(i for i in indicators if i.indicator_id == "IND-JUP-001")
    assert jup_permit.signal_role == obs.SignalRole.EARLY_WARNING
    assert jup_permit.observability == obs.Observability.PUBLIC
    assert jup_permit.lead_time_status == obs.LeadTimeStatus.OBSERVED
    assert jup_permit.lead_time_days_min == 65.0

    # Verify secondary debt mark: FINANCIAL_RECOGNITION, COMMERCIAL_DATA, 0d
    jup_loan = next(i for i in indicators if i.indicator_id == "IND-JUP-004")
    assert jup_loan.signal_role == obs.SignalRole.FINANCIAL_RECOGNITION
    assert jup_loan.observability == obs.Observability.COMMERCIAL_DATA

    # Verify Mackenzie testing logs: PRIVATE_OR_UNAVAILABLE
    mac_logs = next(i for i in indicators if i.indicator_id == "IND-MAC-001")
    assert mac_logs.signal_role == obs.SignalRole.EARLY_WARNING
    assert mac_logs.observability == obs.Observability.PRIVATE_OR_UNAVAILABLE

    # Verify Mackenzie 10-Q draws: FINANCIAL_RECOGNITION, PUBLIC
    mac_10q = next(i for i in indicators if i.indicator_id == "IND-MAC-002")
    assert mac_10q.signal_role == obs.SignalRole.FINANCIAL_RECOGNITION
    assert mac_10q.observability == obs.Observability.PUBLIC

    # Verify IND-JUP-003 right-censored interval representation (min=77, max=unbounded/None)
    jup_censor = next(i for i in indicators if i.indicator_id == "IND-JUP-003")
    assert jup_censor.signal_role == obs.SignalRole.CONFIRMATION
    assert jup_censor.lead_time_status == obs.LeadTimeStatus.RIGHT_CENSORED_OBSERVED
    assert jup_censor.lead_time_days_min == 77.0
    assert jup_censor.lead_time_days_max is None

    # Verify TeraWulf Lake Mariner & Core Scientific Denton indicators loaded
    wulf_ind = next(i for i in indicators if i.indicator_id == "IND-WULF-001")
    assert wulf_ind.project_id == "TERAWULF_LAKE_MARINER"
    corz_ind = next(i for i in indicators if i.indicator_id == "IND-CORZ-002")
    assert corz_ind.project_id == "CORE_SCIENTIFIC_DENTON"
    assert corz_ind.layer == "UTILITY_DOCKET"


def test_evaluate_mackenzie_date_boundary():
    """Verify minimal, assumption-free date boundary calculator for Mackenzie."""
    # Case 1: Expected acceptance Dec 18, 2026 -> 13 days of slack
    res_ontime = obs.evaluate_mackenzie_date_boundary(
        expected_acceptance_date=date(2026, 12, 18),
        cliff_date=date(2026, 12, 31),
    )
    assert not res_ontime.is_collision
    assert res_ontime.acceptance_slack_days == 13
    assert "13 days of slack" in res_ontime.interpretation

    # Case 2: Expected acceptance Jan 20, 2027 -> 20 days late collision
    res_late = obs.evaluate_mackenzie_date_boundary(
        expected_acceptance_date=date(2027, 1, 20),
        cliff_date=date(2026, 12, 31),
        eligible_financing_capacity_usd=500_000_000.0,
    )
    assert res_late.is_collision
    assert res_late.acceptance_slack_days == -20
    assert "precedes equipment acceptance by 20 days" in res_late.interpretation
    assert "Unfinanced capacity at risk: $500.0M (replacement-funding requirement)" in res_late.interpretation


def test_observatory_monitor_and_scoreboard():
    """Verify the prospective monitoring pipeline and empirical scoreboard."""
    monitor = mon.ObservatoryMonitor()
    assert len(monitor.observations) >= 5

    scorecard = monitor.compute_empirical_scoreboard()
    assert scorecard["total_observations_logged"] >= 5
    assert "PROJECT_JUPITER" in scorecard["projects_monitored"]
    assert "IREN_MACKENZIE" in scorecard["projects_monitored"]
    assert scorecard["observed_early_warning_sample_count"] == 1
    assert scorecard["exact_early_warning_lead_days"] == 65.0
    assert scorecard["observed_propagation_lag_days"] == 71.0
    assert scorecard["right_censored_disclosure_lag_days"] == 77.0
    assert scorecard["observed_public_early_warning_episodes"] == 1
    assert scorecard["sec_disclosure_lag_display"] == ">=77 days (right-censored)"

    # Verify save_observations() raises RuntimeError (direct mutation prohibited)
    with pytest.raises(RuntimeError, match="Direct mutation of derived Parquet/CSV is prohibited"):
        monitor.save_observations()


def test_authored_claims_epistemic_validation(tmp_path):
    """Verify that newly authored claims must satisfy rigorous validation before admission."""
    from curate_observatory import validate_authored_claims
    import yaml

    # Case 1: Valid claim format
    valid_yaml = tmp_path / "valid_claims.yaml"
    with open(valid_yaml, "w", encoding="utf-8") as f:
        yaml.dump([{
            "claim_id": "CLM-TEST-001",
            "entity_id": "WULF",
            "source_type": "CORPORATE_EARNINGS_RELEASE",
            "filing_date": "2026-08-10",
            "document_url": "https://investors.terawulf.com/test",
            "section_locator": "Note 8",
            "quote_type": "source_excerpt",
            "exact_quote": "Operational capacity update text",
            "verified_by": "HUMAN_AUDITOR",
            "verification_status": "VERIFIED_AUDITED",
            "verifier_notes": "Cross-verified against Form 10-Q disclosures and investor relations reports.",
        }], f)

    admitted = validate_authored_claims(valid_yaml)
    assert "CLM-TEST-001" in admitted

    # Case 2: Claim without quote_type fails validation
    invalid_yaml = tmp_path / "invalid_claims.yaml"
    with open(invalid_yaml, "w", encoding="utf-8") as f:
        yaml.dump([{
            "claim_id": "CLM-BAD-001",
            "entity_id": "WULF",
            "source_type": "CORPORATE_EARNINGS_RELEASE",
            "filing_date": "2026-08-10",
            "document_url": "https://investors.terawulf.com/test",
            "section_locator": "Note 8",
            "exact_quote": "Missing quote_type",
            "verified_by": "HUMAN_AUDITOR",
            "verification_status": "VERIFIED_AUDITED",
            "verifier_notes": "Some notes here that meet the length check.",
        }], f)

    with pytest.raises(ValueError, match="missing required verification fields"):
        validate_authored_claims(invalid_yaml)


def test_observatory_monitor_add_observation_hermetic(tmp_path):
    """Verify that add_observation updates observations.yaml and syncs observations."""
    import yaml
    import pandas as pd
    from observatory_schema import ClockType, SignalRole, Observability, LeadTimeStatus

    tmp_yaml = tmp_path / "obs.yaml"
    with open(tmp_yaml, "w", encoding="utf-8") as f:
        yaml.dump([], f)
    tmp_pq = tmp_path / "obs.parquet"
    pd.DataFrame(columns=[
        "observation_id", "indicator_id", "project_id", "source_event_date",
        "first_publicly_observable_date", "ingestion_date", "clock_affected",
        "threatened_boundary", "signal_role", "observability", "headline_text",
        "raw_source_uri", "evidence_claim_id", "lead_time_days_to_financial_recognition",
        "propagation_lag_days_from_upstream_signal", "reference_event_date",
        "censor_date", "censored_lead_days", "lead_time_status"
    ]).to_parquet(tmp_pq)

    monitor = mon.ObservatoryMonitor(parquet_path=str(tmp_pq), authored_obs_yaml=str(tmp_yaml))
    assert len(monitor.observations) == 0

    obs_res = monitor.add_observation(
        observation_id="OBS-TEST-001",
        indicator_id="IND-JUP-001",
        project_id="PROJECT_JUPITER",
        source_event_date=date(2026, 7, 15),
        first_publicly_observable_date=date(2026, 7, 15),
        ingestion_date=date(2026, 9, 30),
        clock_affected=ClockType.PHYSICAL,
        threatened_boundary="Fuel supply boundary",
        signal_role=SignalRole.EARLY_WARNING,
        observability=Observability.PUBLIC,
        headline_text="NMSLO test observation",
        raw_source_uri="https://nmstatelands.org/test",
        evidence_claim_id="CLM-PRE-NMSLO-DENIAL-JUL15",
        lead_time_days_to_financial_recognition=65.0,
        lead_time_status=LeadTimeStatus.OBSERVED,
    )

    assert obs_res.observation_id == "OBS-TEST-001"
    assert len(monitor.observations) == 1
    # Check that YAML on disk was updated
    with open(tmp_yaml, "r", encoding="utf-8") as f:
        loaded_yaml = yaml.safe_load(f)
    assert len(loaded_yaml) == 1
    assert loaded_yaml[0]["observation_id"] == "OBS-TEST-001"
