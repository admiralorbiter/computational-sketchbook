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
