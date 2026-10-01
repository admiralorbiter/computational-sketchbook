"""Unit tests for the Observatory Schema and Clock-Collision Detector."""

import pytest
import sys
import os

# Add src to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import observatory_schema as obs
except ImportError:
    import src.observatory_schema as obs


def test_clock_types_and_statuses():
    """Verify enum members and values."""
    assert len(obs.ClockType) == 4
    assert obs.ClockType.PHYSICAL == "PHYSICAL"
    assert obs.ClockType.CONTRACT == "CONTRACT"
    assert obs.ClockType.FINANCIAL == "FINANCIAL"
    assert obs.ClockType.SUPPORT == "SUPPORT"

    assert len(obs.LeadTimeStatus) == 4
    assert obs.LeadTimeStatus.OBSERVED == "OBSERVED"
    assert obs.LeadTimeStatus.RIGHT_CENSORED_OBSERVED == "RIGHT_CENSORED_OBSERVED"
    assert obs.LeadTimeStatus.MONITORING_WINDOW == "MONITORING_WINDOW"
    assert obs.LeadTimeStatus.HYPOTHESIZED_WINDOW == "HYPOTHESIZED_WINDOW"


def test_default_scenario_library():
    """Verify the 6 certified reusable failure archetypes."""
    scenarios = obs.get_default_scenario_library()
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
    
    df = obs.export_scenarios_to_df(scenarios)
    assert len(df) == 6
    assert "reconverging_entity" in df.columns
    assert "subordinate_boundary_mechanic" in df.columns


def test_default_indicator_catalog_epistemic_rigor():
    """Verify that observed lead times are strictly separated from monitoring windows."""
    indicators = obs.get_default_indicator_catalog()
    assert len(indicators) >= 7

    df = obs.export_indicators_to_df(indicators)
    assert len(df) >= 7

    # Jupiter checks: must be OBSERVED or RIGHT_CENSORED_OBSERVED
    jup_perm = df[df["indicator_id"] == "IND-JUP-001"].iloc[0]
    assert jup_perm["lead_time_status"] == obs.LeadTimeStatus.OBSERVED.value
    assert jup_perm["lead_time_days_min"] == 65.0

    jup_fm = df[df["indicator_id"] == "IND-JUP-002"].iloc[0]
    assert jup_fm["lead_time_status"] == obs.LeadTimeStatus.OBSERVED.value
    assert jup_fm["lead_time_days_min"] == 71.0

    jup_sec = df[df["indicator_id"] == "IND-JUP-003"].iloc[0]
    assert jup_sec["lead_time_status"] == obs.LeadTimeStatus.RIGHT_CENSORED_OBSERVED.value
    assert jup_sec["lead_time_days_min"] == 77.0

    # PF1 checks: must NOT be OBSERVED (interconnection is MONITORING_WINDOW; sponsor reconvergence is HYPOTHESIZED_WINDOW)
    pf1_docket = df[df["indicator_id"] == "IND-PF1-001"].iloc[0]
    assert pf1_docket["lead_time_status"] == obs.LeadTimeStatus.MONITORING_WINDOW.value

    pf1_sponsor = df[df["indicator_id"] == "IND-PF1-002"].iloc[0]
    assert pf1_sponsor["lead_time_status"] == obs.LeadTimeStatus.HYPOTHESIZED_WINDOW.value

    # Mackenzie checks: must be MONITORING_WINDOW
    mac_equip = df[df["indicator_id"] == "IND-MAC-001"].iloc[0]
    assert mac_equip["lead_time_status"] == obs.LeadTimeStatus.MONITORING_WINDOW.value


def test_mackenzie_boundary_collision_evaluation():
    """Verify deterministic boundary calculation for Mackenzie availability cliff."""
    # Scenario A: On-time delivery within the 128-day window (~4.2 months)
    res_ontime = obs.evaluate_mackenzie_availability_collision(
        current_month=0.0,
        expected_acceptance_month=3.0,
        total_committed_capex_usd=2_400_000_000.0,
        capex_per_month_usd=600_000_000.0,
    )
    assert res_ontime.binding_clock == obs.ClockType.PHYSICAL
    assert res_ontime.margin_months > 0.0
    assert "on track" in res_ontime.interpretation

    # Scenario B: Delayed acceptance past Dec 31, 2026 cliff
    res_delayed = obs.evaluate_mackenzie_availability_collision(
        current_month=0.0,
        expected_acceptance_month=6.0,
        total_committed_capex_usd=2_400_000_000.0,
        capex_per_month_usd=600_000_000.0,
    )
    assert res_delayed.binding_clock == obs.ClockType.FINANCIAL
    assert res_delayed.secondary_clock == obs.ClockType.PHYSICAL
    assert "CLOCK COLLISION" in res_delayed.interpretation
    assert "unfinanced capex calls on IREN Limited equity" in res_delayed.interpretation
