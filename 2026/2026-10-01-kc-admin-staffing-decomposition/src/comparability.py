"""
Machine-Enforced Longitudinal Comparability Registry & Gate.

Guarantees that Phase 2 econometric models and Phase 1 descriptive pipelines
cannot accidentally execute on broken or non-comparable outcome series.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
import pandas as pd


class ComparabilityStatus(str, Enum):
    GREEN = "PASS (GREEN)"               # Fully continuous, comparable across period
    AMBER = "CONDITIONAL (AMBER)"       # Requires aggregate pairing or sensitivity testing
    RED = "DISCONTINUITY (RED)"         # Severe reporting break; requires exclusion
    FAIL = "FAIL (STOPPING RULE)"       # Unviable; modeling prohibited


@dataclass(frozen=True)
class OutcomeComparabilityRule:
    outcome_variable: str
    valid_period: Tuple[str, str]
    valid_states: Set[str]
    status: ComparabilityStatus
    allow_isolated_modeling: bool
    requires_state_year_fe: bool
    excluded_state_years: Set[Tuple[str, str]]
    analytical_rationale: str


# Machine-readable registry of comparability rules
COMPARABILITY_REGISTRY: Dict[str, OutcomeComparabilityRule] = {
    # 1. Instructional Coordinators (Modern Era)
    "corsup_modern": OutcomeComparabilityRule(
        outcome_variable="instructional_coordinators_fte",
        valid_period=("2014-2015", "2024-2025"),
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.GREEN,
        allow_isolated_modeling=True,
        requires_state_year_fe=True,
        excluded_state_years=set(),
        analytical_rationale="Continuous reporting across all 55 regular districts; primary outcome."
    ),
    # 2. Instructional Coordinators (20-Year Horizon)
    "corsup_historical_20yr": OutcomeComparabilityRule(
        outcome_variable="instructional_coordinators_fte",
        valid_period=("2004-2005", "2024-2025"),
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.AMBER,
        allow_isolated_modeling=False,  # STOPPING RULE: Cannot model isolated CORSUP over 20 years
        requires_state_year_fe=True,
        excluded_state_years={("KS", "2004-2005"), ("KS", "2005-2006"), ("KS", "2006-2007"), ("KS", "2007-2008"), ("KS", "2008-2009")},
        analytical_rationale="Kansas did not report CORSUP pre-2009; model only in paired central aggregate."
    ),
    # 3. District Administrators (Modern Era)
    "leaadm_modern": OutcomeComparabilityRule(
        outcome_variable="lea_administrators_fte",
        valid_period=("2014-2015", "2023-2024"),  # Excludes KS 2024-25 from primary primary window
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.GREEN,
        allow_isolated_modeling=True,
        requires_state_year_fe=True,
        excluded_state_years={("KS", "2024-2025")},
        analytical_rationale="Clean central line management; Kansas 2024-25 break excluded from primary model."
    ),
    # 4. School Building Administrators (Primary Window)
    "schadm_primary": OutcomeComparabilityRule(
        outcome_variable="school_administrators_fte",
        valid_period=("2014-2015", "2023-2024"),  # Excludes KS 2024-25 from primary primary window
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.GREEN,
        allow_isolated_modeling=True,
        requires_state_year_fe=True,
        excluded_state_years={("KS", "2024-2025")},
        analytical_rationale="Primary building leadership model; pairs with school counts; Kansas 2024-25 break excluded."
    ),
    # 5. Kansas 2024-25 Break Indicator
    "schadm_leaadm_ks24": OutcomeComparabilityRule(
        outcome_variable="school_administrators_fte",
        valid_period=("2024-2025", "2024-2025"),
        valid_states={"KS"},
        status=ComparabilityStatus.RED,
        allow_isolated_modeling=False,
        requires_state_year_fe=True,
        excluded_state_years={("KS", "2024-2025")},
        analytical_rationale="Kansas omitted assistant principals (SCHADM -36.8%) and central directors (LEAADM -32.0%)."
    ),
    # 6a. Combined Central Management + Coordinators (Modern Era: 2014-15 to 2023-24)
    "central_mgmt_and_coordinators_modern": OutcomeComparabilityRule(
        outcome_variable="central_mgmt_and_coordinators_fte",
        valid_period=("2014-2015", "2023-2024"),
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.GREEN,
        allow_isolated_modeling=True,
        requires_state_year_fe=True,
        excluded_state_years={("KS", "2024-2025")},
        analytical_rationale="Clean modern supervisory footprint; safe against title substitutions between LEAADM and CORSUP."
    ),
    # 6b. Combined Central Management + Coordinators (20-Year Horizon)
    "central_mgmt_and_coordinators_20yr": OutcomeComparabilityRule(
        outcome_variable="central_mgmt_and_coordinators_fte",
        valid_period=("2004-2005", "2024-2025"),
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.AMBER,  # DOWNGRADED FROM GREEN: Kansas 2006-09 reporting hole
        allow_isolated_modeling=False,     # Requires reconciliation before 20-year regressions
        requires_state_year_fe=True,
        excluded_state_years={("KS", "2006-2007"), ("KS", "2007-2008"), ("KS", "2008-2009"), ("KS", "2024-2025")},
        analytical_rationale="Reclassification-resistant for MO 2014, but KS 2006-09 experienced unmodeled reporting void."
    ),
    # 7. Guidance Counselors (GUI)
    "counselors_20yr": OutcomeComparabilityRule(
        outcome_variable="counselors_fte",
        valid_period=("2004-2005", "2024-2025"),
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.GREEN,
        allow_isolated_modeling=True,
        requires_state_year_fe=True,
        excluded_state_years=set(),
        analytical_rationale="Continuous, clean 21-year series for student counseling capacity."
    ),
    # 8. Broad Student Support Staff (STUSUP)
    "student_support_broad": OutcomeComparabilityRule(
        outcome_variable="student_support_staff_fte",
        valid_period=("2004-2005", "2024-2025"),
        valid_states={"KS", "MO"},
        status=ComparabilityStatus.FAIL,
        allow_isolated_modeling=False,  # HARD STOPPING RULE
        requires_state_year_fe=True,
        excluded_state_years={("KS", "2016-2017"), ("KS", "2017-2018"), ("KS", "2018-2019"),
                              ("MO", "2016-2017"), ("MO", "2017-2018"), ("MO", "2018-2019")},
        analytical_rationale="STOPPING RULE: Unviable for 20-year modeling due to 2016-18 zero reporting void."
    ),
}


def assert_outcome_eligible(
    outcome_var: str,
    start_year: str,
    end_year: str,
    state: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Enforcement gate. Returns (is_eligible, reason).
    Raises ValueError if a model is invoked on a disallowed outcome series.
    Matches the most specific valid rule for the specified period.
    """
    candidates = []
    for rule in COMPARABILITY_REGISTRY.values():
        if rule.outcome_variable == outcome_var:
            r_start, r_end = rule.valid_period
            if start_year >= r_start and end_year <= r_end:
                span = int(r_end[:4]) - int(r_start[:4])
                candidates.append((span, rule))

    matched_rule = None
    if candidates:
        candidates.sort(key=lambda x: x[0])
        matched_rule = candidates[0][1]

    if not matched_rule:
        msg = f"STOPPING RULE: No certified comparability rule found for outcome '{outcome_var}' from {start_year} to {end_year}."
        return False, msg

    if matched_rule.status == ComparabilityStatus.FAIL:
        msg = f"HARD STOPPING RULE TRIGGERED: '{outcome_var}' is flagged as FAIL. Rationale: {matched_rule.analytical_rationale}"
        return False, msg

    if not matched_rule.allow_isolated_modeling:
        msg = f"CONDITIONAL RULE TRIGGERED: '{outcome_var}' ({matched_rule.status.value}) cannot be modeled in isolation over {start_year}–{end_year}. Rationale: {matched_rule.analytical_rationale}"
        return False, msg

    if state and state not in matched_rule.valid_states:
        msg = f"STATE RULE TRIGGERED: State '{state}' is invalid for '{outcome_var}'."
        return False, msg

    return True, f"Outcome '{outcome_var}' is certified for modeling ({matched_rule.status.value})."


def filter_eligible_observations(df: pd.DataFrame, outcome_var: str) -> pd.DataFrame:
    """
    Filters a dataframe to remove state-years tagged as invalid/discontinuous
    for the specific outcome variable.
    """
    df = df.copy()
    for rule in COMPARABILITY_REGISTRY.values():
        if rule.outcome_variable == outcome_var:
            for st, sy in rule.excluded_state_years:
                mask = (df["state"] == st) & (df["school_year"] == sy)
                if mask.any():
                    df.loc[mask, outcome_var] = pd.NA
    return df
