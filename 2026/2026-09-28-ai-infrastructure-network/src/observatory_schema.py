"""Observatory Schema & Clock-Collision Detector Data Model.

This module provides the formal typing, data structures, and catalog registry
for the Infrastructure Stress Observatory. It operationalizes the paradigm pivot
from speculative scalar default predictions to deterministic clock-collision detection
across the four fundamental infrastructure-financing clocks:
    1. Physical Clocks (permits, grid interconnections, civil works, hardware delivery, acceptance)
    2. Contract Clocks (lease commencement, rent step-up, development carry, force majeure, acceptance windows)
    3. Financial Clocks (coupon dates, reserve exhaustion, facility availability expiration, debt maturity)
    4. Support Clocks (completion guarantee cash calls, parent equity liquidity, capital raises)

Rigorous Epistemic Standards:
    - Separates OBSERVED, RIGHT_CENSORED_OBSERVED, MONITORING_WINDOW, and HYPOTHESIZED_WINDOW.
    - Zero hidden priors: separates committed facility capacity from drawn debt.
    - Subordinates modeling to deterministic threshold / boundary calculation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd


class ClockType(str, Enum):
    """The four fundamental clocks operating in infrastructure project financings."""
    PHYSICAL = "PHYSICAL"
    CONTRACT = "CONTRACT"
    FINANCIAL = "FINANCIAL"
    SUPPORT = "SUPPORT"


class LeadTimeStatus(str, Enum):
    """Epistemic classification of indicator lead times."""
    OBSERVED = "OBSERVED"
    RIGHT_CENSORED_OBSERVED = "RIGHT_CENSORED_OBSERVED"
    MONITORING_WINDOW = "MONITORING_WINDOW"
    HYPOTHESIZED_WINDOW = "HYPOTHESIZED_WINDOW"


class ProjectArchetype(str, Enum):
    """The three empirical structural archetypes in the observatory corpus."""
    BINARY_RENT_STEPUP = "BINARY_RENT_STEPUP"                     # Polaris Forge 1
    MULTI_STATE_OFFTAKE_CARRY = "MULTI_STATE_OFFTAKE_CARRY"       # Project Jupiter
    STAGED_EQUIPMENT_ACCEPTANCE_CLIFF = "STAGED_EQUIPMENT_ACCEPTANCE_CLIFF"  # IREN Mackenzie


class PhysicalDimension(str, Enum):
    """Typed physical completion dimensions eliminating scalar MW conflation."""
    UTILITY_LOAD_ONLINE_MW = "utility_load_online_mw"
    SERVICE_READY_IT_MW = "service_ready_it_mw"
    PIPELINE_ROW_PERMITTED_MILES = "pipeline_row_permitted_miles"
    GPU_EQUIPMENT_ACCEPTED_UNITS = "gpu_equipment_accepted_units"
    GPU_COMPUTE_OPERATIONAL_MW = "gpu_compute_operational_mw"


@dataclass(frozen=True)
class ObservableIndicator:
    """An observable public or regulatory signal preceding financial distress."""
    indicator_id: str
    project_id: str
    archetype: ProjectArchetype
    name: str
    layer: str  # REGULATORY, UTILITY_DOCKET, PHYSICAL_LOGISTICS, CONTRACT_LEGAL, DEBT_MARKET, EDGAR_FILING
    source_description: str
    trigger_event: str
    affected_clock: ClockType
    threatened_boundary: str
    lead_time_status: LeadTimeStatus
    lead_time_days_min: float
    lead_time_days_max: float
    lead_time_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "project_id": self.project_id,
            "archetype": self.archetype.value,
            "name": self.name,
            "layer": self.layer,
            "source_description": self.source_description,
            "trigger_event": self.trigger_event,
            "affected_clock": self.affected_clock.value,
            "threatened_boundary": self.threatened_boundary,
            "lead_time_status": self.lead_time_status.value,
            "lead_time_days_min": self.lead_time_days_min,
            "lead_time_days_max": self.lead_time_days_max,
            "lead_time_notes": self.lead_time_notes,
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
        }


def get_default_scenario_library() -> List[ClockCollisionScenario]:
    """Returns the 6 certified reusable failure archetypes in the observatory."""
    return [
        ClockCollisionScenario(
            scenario_id="SCN-ARCH-001",
            title="Physical Milestone Misses Financial Payment Date",
            archetype_exemplar="BINARY_RENT_STEPUP",
            project_exemplar="Polaris Forge 1",
            physical_clock_event="Utility substation energization delayed past target date",
            contract_clock_event="Commercial rent commencement blocked (stays at $0)",
            financial_clock_event="Semiannual coupon payment date arrives (Months 6, 12, 18)",
            support_clock_event="DSRA / interest reserve drains toward zero",
            binding_collision_condition="T_energize > T_coupon_date AND DSRA_cash < InterestDue",
            reconverging_entity="Project SPV -> Bondholders (payment default)",
            subordinate_boundary_mechanic="Discrete semiannual interest shortfall boundary; DSRA exhaustion threshold",
        ),
        ClockCollisionScenario(
            scenario_id="SCN-ARCH-002",
            title="Contract Cash-Flow State Step-Down (Force-Majeure Dispute)",
            archetype_exemplar="MULTI_STATE_OFFTAKE_CARRY",
            project_exemplar="Project Jupiter",
            physical_clock_event="Pipeline ROW permit denied or delayed, impairing fuel delivery",
            contract_clock_event="Tenant declares force majeure, disputing rent step-up and extending dev carry",
            financial_clock_event="Floating SOFR + 250 bps monthly debt interest accrues on drawn loan",
            support_clock_event="Carry cash covers interest only if dev carry payment >= debt carry liability",
            binding_collision_condition="T_permit_delay > T_carry_obligation_limit (3 years) OR DevCarry < DebtInterestDue",
            reconverging_entity="Project SPV -> Syndicated Bank Consortium (trades at 89-91c discount)",
            subordinate_boundary_mechanic="Monthly debt-service runway: T_runway = f(Liquidity, DevCarry, DebtService)",
        ),
        ClockCollisionScenario(
            scenario_id="SCN-ARCH-003",
            title="Reserve / Liquidity Exhaustion Before Commercial Operation",
            archetype_exemplar="BINARY_RENT_STEPUP / MULTI_STATE_OFFTAKE_CARRY",
            project_exemplar="Polaris Forge 1 (Silo 2)",
            physical_clock_event="Continuous physical commissioning slippage",
            contract_clock_event="Pre-operational period extended",
            financial_clock_event="Reserve tier exhausted (e.g. 6-month or 12-month DSRA exhausted at coupon date)",
            support_clock_event="Operating cash drains to $0",
            binding_collision_condition="CumulativePreOperationalInterest > InitialReserves + OperatingCashInflows",
            reconverging_entity="Project SPV -> External liquidity / Sponsor equity cure",
            subordinate_boundary_mechanic="Exact cents-level reserve exhaustion milestone T_reserve_exhaustion",
        ),
        ClockCollisionScenario(
            scenario_id="SCN-ARCH-004",
            title="Financing Availability Window Expiration Cliff",
            archetype_exemplar="STAGED_EQUIPMENT_ACCEPTANCE_CLIFF",
            project_exemplar="IREN Mackenzie",
            physical_clock_event="GPU hardware delivery or customer qualification testing delayed",
            contract_clock_event="Equipment acceptance unachieved prior to December 31, 2026",
            financial_clock_event="Hard December 31, 2026 credit facility availability period ends",
            support_clock_event="Unaccepted equipment loses loan draw eligibility permanently",
            binding_collision_condition="T_acceptance > December 31, 2026 AND HardwareCommitted > DrawnPrincipal",
            reconverging_entity="Project SPV -> Parent Sponsor Equity (IREN Limited)",
            subordinate_boundary_mechanic="Unfunded capex call: UnfundedCapex = CommittedHardware - DrawnDebt",
        ),
        ClockCollisionScenario(
            scenario_id="SCN-ARCH-005",
            title="Shared Sponsor / Parent Support Reconvergence",
            archetype_exemplar="SHARED_SPONSOR_RECONVERGENCE",
            project_exemplar="Polaris Forge 1 (Dual Silos)",
            physical_clock_event="Independent construction cost overruns across multiple legal silos",
            contract_clock_event="Completion guarantees triggered across both silos simultaneously",
            financial_clock_event="Separate project debt remains non-recourse, but parent balance sheet absorbs capex",
            support_clock_event="Parent unrestricted corporate cash depleted by simultaneous cash calls",
            binding_collision_condition="Sum(Silo_i_CapexDeficit) > ParentCorporateCashAvailable",
            reconverging_entity="Independent Project SPVs -> Single Parent Sponsor (Applied Digital)",
            subordinate_boundary_mechanic="Multi-silo capex deficit summation and pre-shortfall cash relief analysis",
        ),
        ClockCollisionScenario(
            scenario_id="SCN-ARCH-006",
            title="Refinancing / Maturity Collision in Dislocated Capital Markets",
            archetype_exemplar="MULTI_STATE_OFFTAKE_CARRY / BINARY_RENT_STEPUP",
            project_exemplar="Project Jupiter / Polaris Forge 1",
            physical_clock_event="Delayed commissioning or prolonged dispute unresolved at facility maturity",
            contract_clock_event="Extension conditions (e.g. operational hurdles) unfulfilled",
            financial_clock_event="Four-year construction loan maturity (Jupiter) or 2030/2031 bullet maturity (PF1)",
            support_clock_event="Refinancing window blocked by debt market discount or rate environment",
            binding_collision_condition="T_refinance_date arrives WHILE SecondaryDiscount > Threshold OR RateSpike",
            reconverging_entity="Borrower SPV -> Restructuring / Equity Recapitalization",
            subordinate_boundary_mechanic="Maturity cliff evaluation vs debt yield and extension covenants",
        ),
    ]


def get_default_indicator_catalog() -> List[ObservableIndicator]:
    """Returns the certified cross-project early-warning indicators."""
    return [
        ObservableIndicator(
            indicator_id="IND-JUP-001",
            project_id="PROJECT_JUPITER",
            archetype=ProjectArchetype.MULTI_STATE_OFFTAKE_CARRY,
            name="State Trust Land Pipeline Right-of-Way Denial",
            layer="REGULATORY",
            source_description="New Mexico State Land Office (NMSLO) formal denial order and press release",
            trigger_event="Denial of ROW permit for 0.6-mile segment of 17-mile natural gas pipeline across state trust land",
            affected_clock=ClockType.PHYSICAL,
            threatened_boundary="Fuel availability and operational energization date of 2,450 MW Bloom Energy microgrid",
            lead_time_status=LeadTimeStatus.OBSERVED,
            lead_time_days_min=65.0,
            lead_time_days_max=65.0,
            lead_time_notes="July 15, 2026 (NMSLO denial) -> September 18, 2026 (syndicated loan trading discount at 89-91c)",
        ),
        ObservableIndicator(
            indicator_id="IND-JUP-002",
            project_id="PROJECT_JUPITER",
            archetype=ProjectArchetype.MULTI_STATE_OFFTAKE_CARRY,
            name="Tenant Offtake Force-Majeure Declaration",
            layer="CONTRACT_LEGAL",
            source_description="Oracle formal legal notice citing pipeline permitting impasse",
            trigger_event="Notice invoking force majeure to extend development-stage carry and delay full operational rent",
            affected_clock=ClockType.CONTRACT,
            threatened_boundary="Transition from development-stage carry to higher operational rent",
            lead_time_status=LeadTimeStatus.OBSERVED,
            lead_time_days_min=71.0,
            lead_time_days_max=71.0,
            lead_time_notes="July 15, 2026 (NMSLO denial) -> September 24, 2026 (Oracle force-majeure notice)",
        ),
        ObservableIndicator(
            indicator_id="IND-JUP-003",
            project_id="PROJECT_JUPITER",
            archetype=ProjectArchetype.MULTI_STATE_OFFTAKE_CARRY,
            name="SEC EDGAR Public Corporate Disclosure Lag",
            layer="EDGAR_FILING",
            source_description="SEC Form 8-K / 10-Q filings by public sponsors (ORCL, OBDC)",
            trigger_event="Material disclosure of project permitting bottleneck or loan valuation impairment on EDGAR",
            affected_clock=ClockType.FINANCIAL,
            threatened_boundary="Public market recognition of project delay and loan discount",
            lead_time_status=LeadTimeStatus.RIGHT_CENSORED_OBSERVED,
            lead_time_days_min=77.0,
            lead_time_days_max=77.0,
            lead_time_notes="July 15, 2026 (NMSLO denial) -> September 30, 2026 (0 filings made on EDGAR; right-censored >= 77 days)",
        ),
        ObservableIndicator(
            indicator_id="IND-PF1-001",
            project_id="POLARIS_FORGE_1",
            archetype=ProjectArchetype.BINARY_RENT_STEPUP,
            name="Electric Utility Substation Interconnection Queue Filing",
            layer="UTILITY_DOCKET",
            source_description="Montana-Dakota Utilities (MDU) / Otter Tail Power public regulatory dockets",
            trigger_event="Interconnection study report detailing transmission upgrade schedules or energization delays",
            affected_clock=ClockType.PHYSICAL,
            threatened_boundary="Commercial commencement date gating Silo 1 / Silo 2 tenant operational rent",
            lead_time_status=LeadTimeStatus.MONITORING_WINDOW,
            lead_time_days_min=90.0,
            lead_time_days_max=180.0,
            lead_time_notes="Standard utility RTO interconnection study and filing revision cycle window",
        ),
        ObservableIndicator(
            indicator_id="IND-PF1-002",
            project_id="POLARIS_FORGE_1",
            archetype=ProjectArchetype.BINARY_RENT_STEPUP,
            name="Sponsor Balance Sheet Liquidity Depletion",
            layer="EDGAR_FILING",
            source_description="Applied Digital (APLD) SEC Form 10-Q / 8-K cash & capital disclosures",
            trigger_event="Emergency convertible debt issuance, ATM equity offerings, or parent revolver exhaustion",
            affected_clock=ClockType.SUPPORT,
            threatened_boundary="Parent ability to honor completion guarantees funding dual-silo construction deficits",
            lead_time_status=LeadTimeStatus.HYPOTHESIZED_WINDOW,
            lead_time_days_min=30.0,
            lead_time_days_max=90.0,
            lead_time_notes="Corporate liquidity burn trajectory preceding parent cash exhaustion",
        ),
        ObservableIndicator(
            indicator_id="IND-MAC-001",
            project_id="IREN_MACKENZIE",
            archetype=ProjectArchetype.STAGED_EQUIPMENT_ACCEPTANCE_CLIFF,
            name="GPU Equipment Delivery & Acceptance Testing Progress",
            layer="PHYSICAL_LOGISTICS",
            source_description="Hardware delivery manifests, customer acceptance testing logs, cloud RFS press releases",
            trigger_event="Hardware delivery slippage or customer qualification testing delays approaching December 31, 2026",
            affected_clock=ClockType.PHYSICAL,
            threatened_boundary="Hard December 31, 2026 facility availability window expiration cliff",
            lead_time_status=LeadTimeStatus.MONITORING_WINDOW,
            lead_time_days_min=30.0,
            lead_time_days_max=60.0,
            lead_time_notes="Final equipment delivery and qualification window preceding December 31, 2026 facility expiration",
        ),
        ObservableIndicator(
            indicator_id="IND-MAC-002",
            project_id="IREN_MACKENZIE",
            archetype=ProjectArchetype.STAGED_EQUIPMENT_ACCEPTANCE_CLIFF,
            name="Quarterly Debt Draw Exhibit Disclosure",
            layer="EDGAR_FILING",
            source_description="IREN Limited SEC Form 10-Q Note on August 2026 Financing Agreements",
            trigger_event="Disclosed cumulative drawn borrowings under MFSA and Notes relative to $2.4B capacity",
            affected_clock=ClockType.FINANCIAL,
            threatened_boundary="Unused commitment expiration and residual capex cash call on parent equity",
            lead_time_status=LeadTimeStatus.MONITORING_WINDOW,
            lead_time_days_min=45.0,
            lead_time_days_max=60.0,
            lead_time_notes="Q1 FY27 Form 10-Q filing window (period ended Sept 30, 2026, filed Nov 2026)",
        ),
    ]


def export_indicators_to_df(indicators: Optional[List[ObservableIndicator]] = None) -> pd.DataFrame:
    """Exports indicators to a structured pandas DataFrame."""
    if indicators is None:
        indicators = get_default_indicator_catalog()
    return pd.DataFrame([ind.to_dict() for ind in indicators])


def export_scenarios_to_df(scenarios: Optional[List[ClockCollisionScenario]] = None) -> pd.DataFrame:
    """Exports scenarios to a structured pandas DataFrame."""
    if scenarios is None:
        scenarios = get_default_scenario_library()
    return pd.DataFrame([scn.to_dict() for scn in scenarios])


@dataclass
class ClockEvaluationResult:
    """Result of evaluating which clock binds first for a monitored asset."""
    project_id: str
    binding_clock: ClockType
    binding_boundary_name: str
    binding_time_months: float
    secondary_clock: Optional[ClockType] = None
    secondary_boundary_name: Optional[str] = None
    secondary_time_months: Optional[float] = None
    margin_months: float = 0.0
    observable_signals_active: List[str] = field(default_factory=list)
    interpretation: str = ""


def evaluate_mackenzie_availability_collision(
    current_month: float,  # Months elapsed since Aug 25, 2026 (0 to 4.2)
    expected_acceptance_month: float,
    total_committed_capex_usd: float = 2_400_000_000.0,
    capex_per_month_usd: float = 600_000_000.0,
) -> ClockEvaluationResult:
    """Calculates whether customer acceptance collides with the Dec 31, 2026 cliff.
    
    August 25, 2026 to December 31, 2026 is exactly 128 days (~4.2 months).
    """
    availability_cliff_months = 128.0 / 30.4375  # ~4.205 months
    
    if expected_acceptance_month <= availability_cliff_months:
        drawn_ratio = min(1.0, (availability_cliff_months - current_month) * capex_per_month_usd / total_committed_capex_usd)
        return ClockEvaluationResult(
            project_id="IREN_MACKENZIE",
            binding_clock=ClockType.PHYSICAL,
            binding_boundary_name="Customer Acceptance Qualified",
            binding_time_months=expected_acceptance_month,
            secondary_clock=ClockType.FINANCIAL,
            secondary_boundary_name="Dec 31 2026 Availability Window Expiration",
            secondary_time_months=availability_cliff_months,
            margin_months=availability_cliff_months - expected_acceptance_month,
            observable_signals_active=["IND-MAC-001"],
            interpretation=f"Acceptance on track; estimated {drawn_ratio*100:.1f}% of facility drawn before cliff.",
        )
    else:
        unfunded_months = expected_acceptance_month - availability_cliff_months
        unfunded_capex = min(total_committed_capex_usd, unfunded_months * capex_per_month_usd)
        return ClockEvaluationResult(
            project_id="IREN_MACKENZIE",
            binding_clock=ClockType.FINANCIAL,
            binding_boundary_name="Dec 31 2026 Availability Window Expiration",
            binding_time_months=availability_cliff_months,
            secondary_clock=ClockType.PHYSICAL,
            secondary_boundary_name="Customer Acceptance Qualified",
            secondary_time_months=expected_acceptance_month,
            margin_months=expected_acceptance_month - availability_cliff_months,
            observable_signals_active=["IND-MAC-001", "IND-MAC-002"],
            interpretation=f"CLOCK COLLISION: Acceptance slips past Dec 31 cliff by {unfunded_months:.1f} months. "
                           f"Facility expires; estimated ${unfunded_capex/1e6:.1f}M unfinanced capex calls on IREN Limited equity.",
        )
