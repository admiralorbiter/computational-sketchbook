"""Observatory Schema & Canonical Table Loader.

This module provides the formal typing, data structures, and loader
for the Infrastructure Stress Observatory. It operationalizes the paradigm pivot
from speculative scalar default predictions to deterministic clock-collision detection
across the four fundamental infrastructure-financing clocks:
    1. Physical Clocks (permits, grid interconnections, civil works, hardware delivery, acceptance)
    2. Contract Clocks (lease commencement, rent step-up, development carry, force majeure, acceptance windows)
    3. Financial Clocks (coupon dates, reserve exhaustion, facility availability expiration, debt maturity)
    4. Support Clocks (completion guarantee cash calls, parent corporate liquidity, capital raises)

Epistemic Standards & Taxonomy:
    - signal_role: EARLY_WARNING | CONFIRMATION | FINANCIAL_RECOGNITION | OUTCOME
    - observability: PUBLIC | COMMERCIAL_DATA | PRIVATE_OR_UNAVAILABLE
    - lead_time_status: OBSERVED | RIGHT_CENSORED_OBSERVED | MONITORING_WINDOW | HYPOTHESIZED_WINDOW
    - Zero hidden priors: separates committed facility capacity from drawn debt.
    - Minimal assumption-free date boundary calculation: evaluates calendar slack without synthetic dollar calls.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
import os
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

DATA_PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
SCENARIOS_PARQUET = os.path.join(DATA_PROCESSED_DIR, "observatory_scenarios.parquet")
INDICATORS_PARQUET = os.path.join(DATA_PROCESSED_DIR, "observatory_indicators.parquet")
OBSERVATIONS_PARQUET = os.path.join(DATA_PROCESSED_DIR, "observatory_observations.parquet")


class ClockType(str, Enum):
    """The four fundamental clocks operating in infrastructure project financings."""
    PHYSICAL = "PHYSICAL"
    CONTRACT = "CONTRACT"
    FINANCIAL = "FINANCIAL"
    SUPPORT = "SUPPORT"


class SignalRole(str, Enum):
    """Functional role of an observable signal in the early-warning timeline."""
    EARLY_WARNING = "EARLY_WARNING"
    CONFIRMATION = "CONFIRMATION"
    FINANCIAL_RECOGNITION = "FINANCIAL_RECOGNITION"
    OUTCOME = "OUTCOME"


class Observability(str, Enum):
    """Degree of public accessibility of an indicator signal."""
    PUBLIC = "PUBLIC"
    COMMERCIAL_DATA = "COMMERCIAL_DATA"
    PRIVATE_OR_UNAVAILABLE = "PRIVATE_OR_UNAVAILABLE"


class LeadTimeStatus(str, Enum):
    """Epistemic classification of indicator lead times."""
    OBSERVED = "OBSERVED"
    RIGHT_CENSORED_OBSERVED = "RIGHT_CENSORED_OBSERVED"
    MONITORING_WINDOW = "MONITORING_WINDOW"
    HYPOTHESIZED_WINDOW = "HYPOTHESIZED_WINDOW"


class ProjectArchetype(str, Enum):
    """The structural archetypes in the observatory corpus."""
    BINARY_RENT_STEPUP = "BINARY_RENT_STEPUP"                     # Polaris Forge 1
    MULTI_STATE_OFFTAKE_CARRY = "MULTI_STATE_OFFTAKE_CARRY"       # Project Jupiter
    STAGED_EQUIPMENT_ACCEPTANCE_CLIFF = "STAGED_EQUIPMENT_ACCEPTANCE_CLIFF"  # IREN Mackenzie
    SHARED_SPONSOR_RECONVERGENCE = "SHARED_SPONSOR_RECONVERGENCE" # Dual-Silo Sponsor Overlay


@dataclass(frozen=True)
class ObservableIndicator:
    """An observable public or regulatory signal preceding financial distress."""
    indicator_id: str
    project_id: str
    archetype: ProjectArchetype
    name: str
    layer: str
    signal_role: SignalRole
    observability: Observability
    source_description: str
    trigger_event: str
    affected_clock: ClockType
    threatened_boundary: str
    lead_time_status: LeadTimeStatus
    lead_time_days_min: float
    lead_time_days_max: float
    lead_time_notes: str
    source_status: str
    model_treatment: str
    valid_from: str
    known_from: str
    expected_observation_date: str
    evidence_claim_ids: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "project_id": self.project_id,
            "archetype": self.archetype.value,
            "name": self.name,
            "layer": self.layer,
            "signal_role": self.signal_role.value,
            "observability": self.observability.value,
            "source_description": self.source_description,
            "trigger_event": self.trigger_event,
            "affected_clock": self.affected_clock.value,
            "threatened_boundary": self.threatened_boundary,
            "lead_time_status": self.lead_time_status.value,
            "lead_time_days_min": self.lead_time_days_min,
            "lead_time_days_max": self.lead_time_days_max,
            "lead_time_notes": self.lead_time_notes,
            "source_status": self.source_status,
            "model_treatment": self.model_treatment,
            "valid_from": self.valid_from,
            "known_from": self.known_from,
            "expected_observation_date": self.expected_observation_date,
            "evidence_claim_ids": self.evidence_claim_ids,
        }


@dataclass(frozen=True)
class ClockCollisionScenario:
    """A failure archetype where physical, contract, financial, and support clocks collide."""
    scenario_id: str
    title: str
    archetype_exemplar: str
    project_exemplar: str
    physical_clock_event: str
    contract_clock_event: str
    financial_clock_event: str
    support_clock_event: str
    binding_collision_condition: str
    reconverging_entity: str
    subordinate_boundary_mechanic: str
    source_status: str
    model_treatment: str
    valid_from: str
    known_from: str
    evidence_claim_ids: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "title": self.title,
            "archetype_exemplar": self.archetype_exemplar,
            "project_exemplar": self.project_exemplar,
            "physical_clock_event": self.physical_clock_event,
            "contract_clock_event": self.contract_clock_event,
            "financial_clock_event": self.financial_clock_event,
            "support_clock_event": self.support_clock_event,
            "binding_collision_condition": self.binding_collision_condition,
            "reconverging_entity": self.reconverging_entity,
            "subordinate_boundary_mechanic": self.subordinate_boundary_mechanic,
            "source_status": self.source_status,
            "model_treatment": self.model_treatment,
            "valid_from": self.valid_from,
            "known_from": self.known_from,
            "evidence_claim_ids": self.evidence_claim_ids,
        }


def load_canonical_scenarios(parquet_path: str = SCENARIOS_PARQUET) -> List[ClockCollisionScenario]:
    """Loads scenarios directly from the canonical Parquet table."""
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Canonical scenarios table not found: {parquet_path}. Run curate_observatory.py first.")
    df = pd.read_parquet(parquet_path)
    scenarios = []
    for _, row in df.iterrows():
        scenarios.append(ClockCollisionScenario(
            scenario_id=str(row["scenario_id"]),
            title=str(row["title"]),
            archetype_exemplar=str(row["archetype_exemplar"]),
            project_exemplar=str(row["project_exemplar"]),
            physical_clock_event=str(row["physical_clock_event"]),
            contract_clock_event=str(row["contract_clock_event"]),
            financial_clock_event=str(row["financial_clock_event"]),
            support_clock_event=str(row["support_clock_event"]),
            binding_collision_condition=str(row["binding_collision_condition"]),
            reconverging_entity=str(row["reconverging_entity"]),
            subordinate_boundary_mechanic=str(row["subordinate_boundary_mechanic"]),
            source_status=str(row["source_status"]),
            model_treatment=str(row["model_treatment"]),
            valid_from=str(row["valid_from"]),
            known_from=str(row["known_from"]),
            evidence_claim_ids=str(row["evidence_claim_ids"]),
        ))
    return scenarios


def load_canonical_indicators(parquet_path: str = INDICATORS_PARQUET) -> List[ObservableIndicator]:
    """Loads indicators directly from the canonical Parquet table."""
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Canonical indicators table not found: {parquet_path}. Run curate_observatory.py first.")
    df = pd.read_parquet(parquet_path)
    indicators = []
    for _, row in df.iterrows():
        indicators.append(ObservableIndicator(
            indicator_id=str(row["indicator_id"]),
            project_id=str(row["project_id"]),
            archetype=ProjectArchetype(str(row["archetype"])),
            name=str(row["name"]),
            layer=str(row["layer"]),
            signal_role=SignalRole(str(row["signal_role"])),
            observability=Observability(str(row["observability"])),
            source_description=str(row["source_description"]),
            trigger_event=str(row["trigger_event"]),
            affected_clock=ClockType(str(row["affected_clock"])),
            threatened_boundary=str(row["threatened_boundary"]),
            lead_time_status=LeadTimeStatus(str(row["lead_time_status"])),
            lead_time_days_min=float(row["lead_time_days_min"]),
            lead_time_days_max=float(row["lead_time_days_max"]),
            lead_time_notes=str(row["lead_time_notes"]),
            source_status=str(row["source_status"]),
            model_treatment=str(row["model_treatment"]),
            valid_from=str(row["valid_from"]),
            known_from=str(row["known_from"]),
            expected_observation_date=str(row["expected_observation_date"]),
            evidence_claim_ids=str(row["evidence_claim_ids"]),
        ))
    return indicators


@dataclass
class MackenzieDateBoundaryResult:
    """Minimal, assumption-free date boundary calculation for Mackenzie."""
    expected_acceptance_date: date
    cliff_date: date
    acceptance_slack_days: int
    is_collision: bool
    binding_boundary: str
    interpretation: str
    financing_capacity_at_risk_usd: Optional[float] = None


def evaluate_mackenzie_date_boundary(
    expected_acceptance_date: date,
    cliff_date: date = date(2026, 12, 31),
    eligible_financing_capacity_usd: Optional[float] = None,
) -> MackenzieDateBoundaryResult:
    """Calculates date slack against the December 31, 2026 facility availability deadline.
    
    Operates without synthetic capex burn or parent equity cash-call assumptions:
        - If expected_acceptance <= cliff_date: acceptance occurs before cliff (positive slack).
        - If expected_acceptance > cliff_date: financial availability precedes acceptance (collision).
        - If eligible_financing_capacity_usd is explicitly known, calculates capacity at risk.
    """
    slack_days = (cliff_date - expected_acceptance_date).days
    
    if slack_days >= 0:
        interp = f"Acceptance on track: {slack_days} days of slack prior to {cliff_date.isoformat()} availability cliff."
        return MackenzieDateBoundaryResult(
            expected_acceptance_date=expected_acceptance_date,
            cliff_date=cliff_date,
            acceptance_slack_days=slack_days,
            is_collision=False,
            binding_boundary="Equipment Acceptance Qualified",
            interpretation=interp,
            financing_capacity_at_risk_usd=0.0,
        )
    else:
        collision_days = abs(slack_days)
        interp = (
            f"CLOCK COLLISION: Financial availability boundary ({cliff_date.isoformat()}) "
            f"precedes equipment acceptance by {collision_days} days. Facility expires prior to draw."
        )
        if eligible_financing_capacity_usd is not None:
            interp += f" Unfinanced capacity at risk: ${eligible_financing_capacity_usd/1e6:.1f}M (replacement-funding requirement)."
        
        return MackenzieDateBoundaryResult(
            expected_acceptance_date=expected_acceptance_date,
            cliff_date=cliff_date,
            acceptance_slack_days=slack_days,
            is_collision=True,
            binding_boundary=f"Facility Availability Cliff ({cliff_date.isoformat()})",
            interpretation=interp,
            financing_capacity_at_risk_usd=eligible_financing_capacity_usd,
        )
