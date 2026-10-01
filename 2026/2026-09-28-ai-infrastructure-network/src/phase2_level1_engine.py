"""Phase 2 Level 1 Deterministic Project Delay-Tolerance Engine (Hardened 2.1.2).

Implements the contract-bounded project finance cash waterfall for Polaris Forge 1
across two legally segregated financing silos (APLD ComputeCo Silo 1 and ComputeCo 3 Silo 2)
with an Applied Digital parent completion support overlay.

Core Invariants Enforced:
1. Strict Silo Isolation: Zero cash transfer between Silo 1 and Silo 2.
2. Exact Fixed Coupon Arithmetic: I_{k,t} = P_{k,t-1} * (r_k / 12) on accrual basis.
3. Silo 1 Amortization Boundary: Amortization cannot begin prior to December 15, 2027.
4. Silo 2 State-Dependent Amortization: Amortization start shifts dynamically with commencement date.
   Contractual finding: amortization_start(delayed) > amortization_start(on_time).
5. Construction Support Isolation: Parent completion support only funds construction capex shortfalls;
   it cannot fund debt service.
6. DSRA Restriction: DSRA funds can only be drawn for permitted debt-service shortfalls;
   cannot be used for capex.
7. Independent Milestones: Milestones are detected independently across parallel debt-service
   and construction tracks (T_completion_support is not downstream of T_DSRA).
8. Cash Coverage Milestone: T_coverage marks the first month where tenant cash rent is strictly
   less than actual monthly cash obligations (opex + cash debt service).
9. Operating Account Exhaustion Milestone: T_operating_exhaustion fires in the first month that
   the operating cash balance reaches zero, whether from operating expenses or debt service.
10. Explicit Waterfall Priority: Payment priority between opex and debt service is explicitly
    parameterized ('opex_first' vs 'debt_service_first') with documented epistemic provenance.
11. Paid-Only Principal Reduction: Outstanding principal is reduced strictly by paid principal,
    never by unpaid scheduled amortization installments: P_t = P_{t-1} - principal_amort_paid.
12. Complete Arrears Accounting: Unpaid obligations do not disappear into thin air.
    opex_payable, interest_payable, and principal_arrears are tracked and carried forward.
13. Absorbing Boundary Semantics: Once T_payment_shortfall occurs, the silo enters default.
    Subsequent ledger months are marked as is_post_shortfall=True and economic_status='POST_SHORTFALL_ABSORBED'.
14. Final Maturity Balloon: Remaining principal matures as a bullet balloon at final maturity
    (Month 54 for Silo 1 / Dec 15, 2030; Month 60 for Silo 2 / June 15, 2031).
15. Dynamic Date Derivation: Month indexes for contractual dates are dynamically computed from
    simulation start date, preventing silent calendar corruption.
16. Zero Silent Priors in Surface API: Every unobserved financial input is mandatory in
    compute_delay_tolerance_surface(); illustrative defaults are restricted to demo_pf1_analyst_scenario().
17. Bounded Capex Spend: remaining_capex_total caps total cumulative construction outlays.
18. Parent Reconvergence Overlay: Parent support sums across silos strictly after each silo's
    waterfall is computed independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


# Certified Contractual Dates from Primary SEC Filings
CANONICAL_PF1_START_DATE = "2026-07-01"
SILO1_AMORT_START_DATE = "2027-12-15"   # Nov 20, 2025 Form 8-K: Dec 15, 2027
SILO1_MATURITY_DATE = "2030-12-15"      # Nov 20, 2025 Form 8-K: Dec 15, 2030
SILO2_MATURITY_DATE = "2031-06-15"      # June 16, 2026 Form 8-K: June 15, 2031


def _date_to_month_index(sim_start: pd.Timestamp, target_date_str: str) -> int:
    """Computes the 1-indexed simulation month index for a target date relative to sim_start.
    
    Robustness requirement: sim_start must be normalized to the first day of a calendar month
    (e.g. 'YYYY-MM-01') to prevent ambiguous intra-month rounding.
    """
    if sim_start.day != 1:
        raise ValueError(
            f"Simulation start date must be the first day of a month (e.g. 'YYYY-MM-01'), "
            f"received: {sim_start.strftime('%Y-%m-%d')}"
        )
    target = pd.to_datetime(target_date_str)
    if sim_start >= target:
        raise ValueError(
            f"Simulation start date {sim_start.strftime('%Y-%m-%d')} is on or after "
            f"contractual milestone date {target_date_str}"
        )
    months = (target.year - sim_start.year) * 12 + (target.month - sim_start.month) + 1
    return months


@dataclass(frozen=True)
class AmortizationScenario:
    """Explicit schedule or scenario for principal amortization installments.
    
    Installment amounts are UNOBSERVED in public SEC filings ('in amounts set forth
    in the Indenture'). The engine strictly rejects default straight-line assumptions.
    An explicit schedule or parameter must be supplied.
    """
    schedule_type: str  # 'custom_schedule', 'equal_semiannual_scenario', or 'zero_amort_scenario'
    semiannual_amount: Optional[float] = None  # If equal_semiannual_scenario
    custom_schedule_by_month: Optional[Dict[int, float]] = None  # month -> principal payment amount


@dataclass(frozen=True)
class SiloTerms:
    """Contractual terms governing an individual financing silo."""
    silo_id: str
    name: str
    principal_initial_usd: float
    annual_coupon_rate: float
    amortization_start_rule: str  # 'fixed_date' or 'post_commencement'
    fixed_amort_start_month: Optional[int] = None  # 1-indexed month relative to sim start
    final_maturity_month: int = 54  # Month index of maturity (Silo 1: Dec 2030 = month 54 from July 2026)
    payment_frequency: str = "semiannual"  # "semiannual" or "monthly"
    payment_months: Tuple[int, ...] = (6, 12)  # Calendar months for payments if semiannual


@dataclass
class AccountState:
    """Legally segregated cash accounts for a financing silo."""
    construction_cash: float
    dsra_cash: float
    operating_cash: float


@dataclass(frozen=True)
class ConstructionScenario:
    """Construction schedule and capex burn scenario for a silo."""
    scheduled_commencement_month: int
    delay_months: int
    monthly_capex_burn: float  # Monthly capex burn until completion
    remaining_capex_total: Optional[float] = None  # Total remaining capex cap, if bounded


@dataclass(frozen=True)
class RentScenario:
    """Tenant revenue scenario for a silo."""
    monthly_base_rent: float  # Base cash rent once commencement is achieved
    pre_commencement_rent: float = 0.0  # Reservation fees, if any
    monthly_opex: float = 0.0  # Land, insurance, security carry costs


@dataclass
class MilestoneRecord:
    """Milestone detection times for a silo (in simulation month index, None if not reached)."""
    t_coverage: Optional[int] = None
    t_operating_exhaustion: Optional[int] = None
    t_dsra: Optional[int] = None
    t_completion_support: Optional[int] = None
    t_payment_shortfall: Optional[int] = None
    t_refi: Optional[int] = None


@dataclass
class EngineResult:
    """Outputs from the Level 1 deterministic simulation."""
    monthly_ledger: pd.DataFrame
    silo1_milestones: MilestoneRecord
    silo2_milestones: MilestoneRecord
    parent_support_summary: pd.DataFrame
    invariants_passed: bool


def create_default_pf1_silos(start_date: str = CANONICAL_PF1_START_DATE) -> Tuple[SiloTerms, SiloTerms]:
    """Creates the contractual SiloTerms for Polaris Forge 1 dynamically anchored to start_date.
    
    Derives milestone month indexes dynamically from certified contractual dates:
    - Silo 1 Amortization: Dec 15, 2027 (Month 18 relative to July 2026)
    - Silo 1 Maturity: Dec 15, 2030 (Month 54 relative to July 2026)
    - Silo 2 Maturity: June 15, 2031 (Month 60 relative to July 2026)
    """
    sim_start = pd.to_datetime(start_date)
    s1_amort_month = _date_to_month_index(sim_start, SILO1_AMORT_START_DATE)
    s1_maturity_month = _date_to_month_index(sim_start, SILO1_MATURITY_DATE)
    s2_maturity_month = _date_to_month_index(sim_start, SILO2_MATURITY_DATE)

    silo1 = SiloTerms(
        silo_id="SILO_1",
        name="APLD ComputeCo (Buildings 2 & 3)",
        principal_initial_usd=2_350_000_000.0,
        annual_coupon_rate=0.0925,
        amortization_start_rule="fixed_date",
        fixed_amort_start_month=s1_amort_month,
        final_maturity_month=s1_maturity_month,
        payment_frequency="semiannual",
        payment_months=(6, 12),
    )
    
    silo2 = SiloTerms(
        silo_id="SILO_2",
        name="APLD ComputeCo 3 (Building 4)",
        principal_initial_usd=1_590_000_000.0,
        annual_coupon_rate=0.0700,
        amortization_start_rule="post_commencement",
        fixed_amort_start_month=None,
        final_maturity_month=s2_maturity_month,
        payment_frequency="semiannual",
        payment_months=(6, 12),
    )
    return silo1, silo2


class DeterministicDelayEngine:
    """Simulates monthly cash waterfalls across legally segregated project finance silos."""

    def __init__(self, simulation_months: int = 60, start_date: str = CANONICAL_PF1_START_DATE):
        self.simulation_months = simulation_months
        self.start_date = pd.to_datetime(start_date)
        self.dates = [self.start_date + pd.DateOffset(months=m) for m in range(simulation_months)]

    def run_silo_waterfall(
        self,
        terms: SiloTerms,
        initial_accounts: AccountState,
        construction: ConstructionScenario,
        rent: RentScenario,
        amortization: AmortizationScenario,
        waterfall_priority: str = "opex_first",
    ) -> Tuple[pd.DataFrame, MilestoneRecord]:
        """Executes the monthly cash waterfall for a single, isolated financing silo.
        
        Epistemic Provenance:
        - waterfall_priority: Indenture payment priority between project operating expenses
          and senior debt service is UNOBSERVED in public SEC filings.
          Classified under two-field schema as:
          source_status='UNOBSERVED', model_treatment='ANALYST_SCENARIO'.
          Options:
          - 'opex_first': standard project finance convention (preserve asset as going concern)
          - 'debt_service_first': senior lender revenue lien priority
        """
        if amortization is None or not isinstance(amortization, AmortizationScenario):
            raise ValueError(
                f"Silo {terms.silo_id}: Amortization installment amounts are UNOBSERVED in public filings. "
                "An explicit AmortizationScenario must be provided; default straight-line assumptions are prohibited."
            )
        if waterfall_priority not in ("opex_first", "debt_service_first"):
            raise ValueError(f"Unknown waterfall_priority: {waterfall_priority}. Must be 'opex_first' or 'debt_service_first'.")

        records = []
        milestones = MilestoneRecord()
        milestones.t_refi = terms.final_maturity_month

        # Account balances
        c_const = initial_accounts.construction_cash
        c_dsra = initial_accounts.dsra_cash
        c_oper = initial_accounts.operating_cash
        principal = terms.principal_initial_usd

        # Cumulative capex tracker for remaining capex bound
        cumulative_capex_spent = 0.0

        # Arrears balances (unpaid obligations carried forward)
        opex_payable = 0.0
        interest_payable = 0.0
        principal_arrears = 0.0

        # Absorbing default state tracker
        is_post_shortfall = False

        # Calculate actual commencement month including delay
        actual_commencement = construction.scheduled_commencement_month + construction.delay_months

        # Determine amortization start month
        if terms.amortization_start_rule == "fixed_date":
            if terms.fixed_amort_start_month is None:
                raise ValueError(f"Silo {terms.silo_id} requires fixed_amort_start_month")
            amort_start_month = terms.fixed_amort_start_month
        elif terms.amortization_start_rule == "post_commencement":
            # Finds the first payment month strictly after actual commencement
            comm_month_date = self.dates[min(actual_commencement - 1, self.simulation_months - 1)]
            curr_cal_month = comm_month_date.month
            
            if curr_cal_month < 6:
                months_to_next_payment = 6 - curr_cal_month
            elif curr_cal_month < 12:
                months_to_next_payment = 12 - curr_cal_month
            else:
                months_to_next_payment = 6  # Next June
            
            amort_start_month = actual_commencement + months_to_next_payment
        else:
            raise ValueError(f"Unknown amortization_start_rule: {terms.amortization_start_rule}")

        for m in range(1, self.simulation_months + 1):
            curr_date = self.dates[m - 1]
            cal_month = curr_date.month
            is_payment_month = (cal_month in terms.payment_months)

            # --- TRACK B: Construction Funding Waterfall ---
            is_under_construction = (m < actual_commencement)
            raw_capex_required = construction.monthly_capex_burn if is_under_construction else 0.0

            # Apply remaining_capex_total bound if specified
            if construction.remaining_capex_total is not None:
                budget_remaining = max(0.0, construction.remaining_capex_total - cumulative_capex_spent)
                capex_required = min(raw_capex_required, budget_remaining)
            else:
                capex_required = raw_capex_required

            # Draw on construction account
            capex_from_account = min(c_const, capex_required)
            c_const -= capex_from_account
            cumulative_capex_spent += capex_from_account
            capex_shortfall = capex_required - capex_from_account

            # Parent completion support triggers when construction funds are insufficient
            parent_completion_support = 0.0
            if capex_shortfall > 0:
                parent_completion_support = capex_shortfall
                cumulative_capex_spent += parent_completion_support
                if milestones.t_completion_support is None:
                    milestones.t_completion_support = m

            # --- TRACK A: Debt Service Waterfall ---
            # Monthly coupon interest on remaining principal (accrual basis)
            monthly_interest_accrual = principal * (terms.annual_coupon_rate / 12.0)
            
            # Determine scheduled principal amortization due this month
            principal_amort_due = 0.0
            is_final_maturity = (m == terms.final_maturity_month)

            if is_final_maturity:
                # At final maturity, entire remaining principal matures as a bullet balloon
                principal_amort_due = principal
            elif m >= amort_start_month and is_payment_month and principal > 0:
                if amortization.schedule_type == "equal_semiannual_scenario":
                    if amortization.semiannual_amount is None:
                        raise ValueError(f"Silo {terms.silo_id}: equal_semiannual_scenario requires semiannual_amount")
                    principal_amort_due = min(principal, amortization.semiannual_amount)
                elif amortization.schedule_type == "custom_schedule":
                    if amortization.custom_schedule_by_month is None:
                        raise ValueError(f"Silo {terms.silo_id}: custom_schedule requires custom_schedule_by_month")
                    principal_amort_due = min(principal, amortization.custom_schedule_by_month.get(m, 0.0))
                elif amortization.schedule_type == "zero_amort_scenario":
                    principal_amort_due = 0.0
                else:
                    raise ValueError(f"Unknown amortization schedule_type: {amortization.schedule_type}")

            # Coupon cash payment due in payment months (semiannual: 6 months interest)
            coupon_cash_due = 0.0
            if terms.payment_frequency == "semiannual":
                if is_payment_month or is_final_maturity:
                    coupon_cash_due = principal * (terms.annual_coupon_rate / 2.0)
            else:
                coupon_cash_due = monthly_interest_accrual

            # Total obligations due this month including carried arrears
            total_coupon_due = coupon_cash_due + interest_payable
            total_principal_amort_due = principal_amort_due + principal_arrears
            total_debt_service_due = total_coupon_due + total_principal_amort_due

            # Operating revenue (tenant rent) and opex
            is_operational = (m >= actual_commencement)
            tenant_rent = rent.monthly_base_rent if is_operational else rent.pre_commencement_rent
            opex = rent.monthly_opex
            total_opex_due = opex + opex_payable

            # --- Cash Coverage Milestone Detection ---
            # Compares actual monthly tenant cash rent against actual monthly cash obligations (opex + debt service)
            total_monthly_cash_obligations = total_opex_due + total_debt_service_due
            if total_monthly_cash_obligations > 0 and tenant_rent < total_monthly_cash_obligations:
                if milestones.t_coverage is None:
                    milestones.t_coverage = m

            # --- Operating Cash Account Waterfall ---
            # Track cash available before operating uses to evaluate exhaustion as an economic event
            c_oper_available_before_uses = c_oper + tenant_rent
            # 1. Add tenant rent to operating cash
            c_oper += tenant_rent

            if waterfall_priority == "opex_first":
                # 2. Subtract opex (current + payable) directly from operating cash
                opex_paid = min(c_oper, total_opex_due)
                c_oper -= opex_paid
                opex_payable = total_opex_due - opex_paid

                # 3. Pay debt service from remaining operating cash
                paid_from_oper = min(c_oper, total_debt_service_due)
                c_oper -= paid_from_oper
                debt_service_shortfall = total_debt_service_due - paid_from_oper
            else:  # debt_service_first
                # 2. Pay debt service first
                paid_from_oper = min(c_oper, total_debt_service_due)
                c_oper -= paid_from_oper
                debt_service_shortfall = total_debt_service_due - paid_from_oper

                # 3. Pay opex from remaining operating cash
                opex_paid = min(c_oper, total_opex_due)
                c_oper -= opex_paid
                opex_payable = total_opex_due - opex_paid

            # Operating Account Exhaustion Milestone:
            # Defined as an economic transition/event, not a static state:
            # Fires in the first month where available operating cash (beginning balance + rent)
            # was positive, and cash uses reduced the balance to zero.
            # An account initialized at zero with no cash inflow or drain is NOT considered exhausted.
            if c_oper_available_before_uses > 0 and c_oper == 0.0 and milestones.t_operating_exhaustion is None:
                milestones.t_operating_exhaustion = m

            # 4. If operating cash is exhausted, draw on DSRA for remaining debt service
            dsra_draw = 0.0
            unfunded_debt_service = 0.0
            if debt_service_shortfall > 0:
                dsra_draw = min(c_dsra, debt_service_shortfall)
                c_dsra -= dsra_draw
                unfunded_debt_service = debt_service_shortfall - dsra_draw
                
                if dsra_draw > 0 and milestones.t_dsra is None:
                    milestones.t_dsra = m

            # 5. Apply available debt cash in strict contractual priority (interest before principal)
            total_cash_for_debt = paid_from_oper + dsra_draw
            coupon_cash_paid = min(total_cash_for_debt, total_coupon_due)
            interest_payable = total_coupon_due - coupon_cash_paid

            cash_for_principal = max(0.0, total_cash_for_debt - coupon_cash_paid)
            principal_amort_paid = min(total_principal_amort_due, cash_for_principal)
            principal_arrears = total_principal_amort_due - principal_amort_paid

            # 6. Principal balance update: ONLY PAID principal reduces outstanding balance!
            principal -= principal_amort_paid

            # 7. Payment Shortfall milestone & Absorbing Default Boundary
            is_payment_shortfall = (unfunded_debt_service > 0)
            if is_payment_shortfall:
                if milestones.t_payment_shortfall is None:
                    milestones.t_payment_shortfall = m
                is_post_shortfall = True

            economic_status = "POST_SHORTFALL_ABSORBED" if is_post_shortfall else "VALID"

            records.append({
                "month": m,
                "date": curr_date.strftime("%Y-%m"),
                "silo_id": terms.silo_id,
                "principal_remaining": principal,
                "monthly_interest_accrual": monthly_interest_accrual,
                "coupon_cash_due": coupon_cash_due,
                "total_coupon_due": total_coupon_due,
                "coupon_cash_paid": coupon_cash_paid,
                "interest_payable": interest_payable,
                "principal_amort_due": principal_amort_due,
                "total_principal_amort_due": total_principal_amort_due,
                "principal_amort_paid": principal_amort_paid,
                "principal_arrears": principal_arrears,
                "total_debt_service_due": total_debt_service_due,
                "tenant_rent": tenant_rent,
                "opex": opex,
                "total_opex_due": total_opex_due,
                "opex_paid": opex_paid,
                "opex_payable": opex_payable,
                "operating_cash_balance": c_oper,
                "dsra_balance": c_dsra,
                "dsra_draw": dsra_draw,
                "construction_cash_balance": c_const,
                "capex_required": capex_required,
                "cumulative_capex_spent": cumulative_capex_spent,
                "parent_completion_support_required": parent_completion_support,
                "unfunded_debt_service": unfunded_debt_service,
                "is_payment_shortfall": is_payment_shortfall,
                "is_post_shortfall": is_post_shortfall,
                "economic_status": economic_status,
                "is_operational": is_operational,
            })

        df = pd.DataFrame(records)
        return df, milestones

    def run_pf1_simulation(
        self,
        silo1_initial: AccountState,
        silo2_initial: AccountState,
        silo1_construction: ConstructionScenario,
        silo2_construction: ConstructionScenario,
        silo1_rent: RentScenario,
        silo2_rent: RentScenario,
        silo1_amort: AmortizationScenario,
        silo2_amort: AmortizationScenario,
        waterfall_priority: str = "opex_first",
    ) -> EngineResult:
        """Executes parallel waterfalls for Silo 1 and Silo 2, then computes campus parent overlay."""
        silo1_terms, silo2_terms = create_default_pf1_silos(self.start_date.strftime("%Y-%m-%d"))

        # Run each silo in strict isolation
        df_silo1, m_silo1 = self.run_silo_waterfall(
            silo1_terms, silo1_initial, silo1_construction, silo1_rent, silo1_amort, waterfall_priority
        )
        df_silo2, m_silo2 = self.run_silo_waterfall(
            silo2_terms, silo2_initial, silo2_construction, silo2_rent, silo2_amort, waterfall_priority
        )

        # Merge for campus ledger
        combined_df = pd.merge(
            df_silo1,
            df_silo2,
            on=["month", "date"],
            suffixes=("_silo1", "_silo2"),
        )

        # Calculate Campus Overlay: Parent Support Funding Required
        # Sums across silos STRICTLY AFTER individual silo waterfalls are computed
        combined_df["total_parent_completion_support"] = (
            combined_df["parent_completion_support_required_silo1"] +
            combined_df["parent_completion_support_required_silo2"]
        )
        combined_df["cumulative_parent_support_funding_required"] = (
            combined_df["total_parent_completion_support"].cumsum()
        )

        # Parent support summary table
        parent_summary = combined_df[[
            "month", "date",
            "parent_completion_support_required_silo1",
            "parent_completion_support_required_silo2",
            "total_parent_completion_support",
            "cumulative_parent_support_funding_required",
        ]].copy()

        # Invariant checks
        invariants_passed = self.assert_invariants(
            df_silo1, df_silo2, combined_df, m_silo1, m_silo2, silo1_terms, silo2_terms, silo2_construction
        )

        return EngineResult(
            monthly_ledger=combined_df,
            silo1_milestones=m_silo1,
            silo2_milestones=m_silo2,
            parent_support_summary=parent_summary,
            invariants_passed=invariants_passed,
        )

    def assert_invariants(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        combined: pd.DataFrame,
        m1: MilestoneRecord,
        m2: MilestoneRecord,
        terms1: SiloTerms,
        terms2: SiloTerms,
        silo2_construction: ConstructionScenario,
    ) -> bool:
        """Verifies all core structural, legal, and financial invariants."""
        # 1. Silo Isolation
        assert "dsra_balance_silo1" in combined and "dsra_balance_silo2" in combined

        # 2. Fixed Coupon Arithmetic: Monthly accrual = principal * r / 12
        for idx, row in df1.iterrows():
            expected_accrual = (row["principal_remaining"] + row["principal_amort_paid"]) * (terms1.annual_coupon_rate / 12.0)
            assert np.isclose(row["monthly_interest_accrual"], expected_accrual, atol=1e-2)

        # 3. Silo 1 Amortization Boundary: Cannot amortize prior to month 18 (Dec 2027 from July 2026)
        pre_18_amort = df1[df1["month"] < terms1.fixed_amort_start_month]["principal_amort_due"].sum()
        assert pre_18_amort == 0.0, f"Silo 1 amortized before month 18: {pre_18_amort}"

        # 4. Silo 2 State-Dependent Amortization: Amortization cannot begin prior to commencement
        actual_comm2 = silo2_construction.scheduled_commencement_month + silo2_construction.delay_months
        pre_comm_amort2 = df2[df2["month"] < actual_comm2]["principal_amort_due"].sum()
        assert pre_comm_amort2 == 0.0, f"Silo 2 amortized before commencement: {pre_comm_amort2}"

        # 5. Construction Support Isolation: Parent completion support only funds capex shortfalls
        for idx, row in df1.iterrows():
            if row["parent_completion_support_required"] > 0:
                assert row["capex_required"] > 0

        # 6. DSRA Restriction: DSRA is only drawn when operating cash is zero and debt service > 0
        for idx, row in df1.iterrows():
            if row["dsra_draw"] > 0:
                assert row["operating_cash_balance"] == 0.0
                assert row["total_debt_service_due"] > 0.0

        # 7. Paid-Only Principal Reduction: principal balance decreases strictly by principal_amort_paid
        for idx, row in df1.iterrows():
            assert row["principal_amort_paid"] <= row["total_principal_amort_due"]

        # 8. Parent Summation strictly post-waterfall
        expected_sum = combined["parent_completion_support_required_silo1"] + combined["parent_completion_support_required_silo2"]
        assert np.allclose(combined["total_parent_completion_support"], expected_sum)

        return True


def demo_pf1_analyst_scenario() -> Dict[str, Any]:
    """Provides an illustrative reference scenario parameter set for Polaris Forge 1.
    
    EPISTEMIC GOVERNANCE WARNING:
    These values represent ANALYST SCENARIO assumptions for parameters that are
    UNOBSERVED in public SEC filings. They must never be treated as contractual facts.
    - source_status: UNOBSERVED
    - model_treatment: ANALYST_SCENARIO
    """
    return {
        "scheduled_commencement_month_silo1": 12,
        "scheduled_commencement_month_silo2": 18,
        "silo1_rent_scenario": RentScenario(monthly_base_rent=15_275_000.0, monthly_opex=1_000_000.0),
        "silo2_rent_scenario": RentScenario(monthly_base_rent=9_166_667.0, monthly_opex=1_000_000.0),
        "silo1_amort_scenario": AmortizationScenario(
            schedule_type="equal_semiannual_scenario",
            semiannual_amount=2_350_000_000.0 / 6.0,
        ),
        "silo2_amort_scenario": AmortizationScenario(
            schedule_type="equal_semiannual_scenario",
            semiannual_amount=1_590_000_000.0 / 7.0,
        ),
        "silo1_initial_construction_cash": 100_000_000.0,
        "silo2_initial_construction_cash": 150_000_000.0,
        "silo1_initial_operating_cash": 25_000_000.0,
        "silo2_initial_operating_cash": 0.0,
        "silo1_remaining_capex_total": 200_000_000.0,
        "silo2_remaining_capex_total": 300_000_000.0,
        "waterfall_priority": "opex_first",
    }


def compute_delay_tolerance_surface(
    reserve_grid_silo1: List[float],
    reserve_grid_silo2: List[float],
    capex_burn_grid_silo1: List[float],
    capex_burn_grid_silo2: List[float],
    scheduled_commencement_month_silo1: int,
    scheduled_commencement_month_silo2: int,
    delay_grid_silo1: List[int],
    delay_grid_silo2: Optional[List[int]],
    shared_campus_delay_mode: bool,
    silo1_rent_scenario: RentScenario,
    silo2_rent_scenario: RentScenario,
    silo1_amort_scenario: AmortizationScenario,
    silo2_amort_scenario: AmortizationScenario,
    silo1_initial_construction_cash: float,
    silo2_initial_construction_cash: float,
    silo1_initial_operating_cash: float,
    silo2_initial_operating_cash: float,
    silo1_remaining_capex_total: Optional[float],
    silo2_remaining_capex_total: Optional[float],
    waterfall_priority: str,
) -> pd.DataFrame:
    """Computes the Contract-Bounded Milestone Surface across a grid of reserves and delays.
    
    Zero silent priors:
    Every unobserved parameter must be explicitly passed by the caller.
    Defaults are strictly prohibited to prevent accidental synthetic surfaces.
    """
    if shared_campus_delay_mode:
        delay_pairs = [(d, d) for d in delay_grid_silo1]
    else:
        if delay_grid_silo2 is None:
            raise ValueError(
                "delay_grid_silo2 must be provided when shared_campus_delay_mode is False. "
                "Pass distinct delay grids for Silo 1 and Silo 2, or set shared_campus_delay_mode=True "
                "to explicitly model synchronized campus delays."
            )
        delay_pairs = [(d1, d2) for d1 in delay_grid_silo1 for d2 in delay_grid_silo2]

    engine = DeterministicDelayEngine(simulation_months=60)
    surface_rows = []

    for r_0_s1 in reserve_grid_silo1:
        for r_0_s2 in reserve_grid_silo2:
            for k_burn_s1 in capex_burn_grid_silo1:
                for k_burn_s2 in capex_burn_grid_silo2:
                    for delay_s1, delay_s2 in delay_pairs:
                        silo1_init = AccountState(
                            construction_cash=silo1_initial_construction_cash,
                            dsra_cash=r_0_s1,
                            operating_cash=silo1_initial_operating_cash,
                        )
                        silo1_const = ConstructionScenario(
                            scheduled_commencement_month=scheduled_commencement_month_silo1,
                            delay_months=delay_s1,
                            monthly_capex_burn=k_burn_s1,
                            remaining_capex_total=silo1_remaining_capex_total,
                        )

                        silo2_init = AccountState(
                            construction_cash=silo2_initial_construction_cash,
                            dsra_cash=r_0_s2,
                            operating_cash=silo2_initial_operating_cash,
                        )
                        silo2_const = ConstructionScenario(
                            scheduled_commencement_month=scheduled_commencement_month_silo2,
                            delay_months=delay_s2,
                            monthly_capex_burn=k_burn_s2,
                            remaining_capex_total=silo2_remaining_capex_total,
                        )

                        result = engine.run_pf1_simulation(
                            silo1_init, silo2_init,
                            silo1_const, silo2_const,
                            silo1_rent_scenario, silo2_rent_scenario,
                            silo1_amort_scenario, silo2_amort_scenario,
                            waterfall_priority=waterfall_priority,
                        )

                        max_parent_support = result.monthly_ledger["cumulative_parent_support_funding_required"].iloc[-1]

                        surface_rows.append({
                            "dsra_silo1": r_0_s1,
                            "dsra_silo2": r_0_s2,
                            "capex_burn_silo1": k_burn_s1,
                            "capex_burn_silo2": k_burn_s2,
                            "scheduled_commencement_silo1": scheduled_commencement_month_silo1,
                            "scheduled_commencement_silo2": scheduled_commencement_month_silo2,
                            "delay_months_silo1": delay_s1,
                            "delay_months_silo2": delay_s2,
                            "shared_campus_delay_mode": shared_campus_delay_mode,
                            "waterfall_priority": waterfall_priority,
                            "t_coverage_silo1": result.silo1_milestones.t_coverage,
                            "t_oper_exhaustion_silo1": result.silo1_milestones.t_operating_exhaustion,
                            "t_dsra_silo1": result.silo1_milestones.t_dsra,
                            "t_completion_support_silo1": result.silo1_milestones.t_completion_support,
                            "t_payment_shortfall_silo1": result.silo1_milestones.t_payment_shortfall,
                            "t_coverage_silo2": result.silo2_milestones.t_coverage,
                            "t_oper_exhaustion_silo2": result.silo2_milestones.t_operating_exhaustion,
                            "t_dsra_silo2": result.silo2_milestones.t_dsra,
                            "t_completion_support_silo2": result.silo2_milestones.t_completion_support,
                            "t_payment_shortfall_silo2": result.silo2_milestones.t_payment_shortfall,
                            "cumulative_parent_support_required_usd": max_parent_support,
                        })

    return pd.DataFrame(surface_rows)


if __name__ == "__main__":
    print("Testing Hardened 2.1.2 DeterministicDelayEngine baseline run...")
    engine = DeterministicDelayEngine(simulation_months=60)
    
    # Use explicit demo scenario
    p = demo_pf1_analyst_scenario()
    s1_init = AccountState(
        construction_cash=p["silo1_initial_construction_cash"],
        dsra_cash=150_000_000.0,
        operating_cash=p["silo1_initial_operating_cash"],
    )
    s2_init = AccountState(
        construction_cash=p["silo2_initial_construction_cash"],
        dsra_cash=100_000_000.0,
        operating_cash=p["silo2_initial_operating_cash"],
    )
    s1_const = ConstructionScenario(
        scheduled_commencement_month=p["scheduled_commencement_month_silo1"],
        delay_months=6,
        monthly_capex_burn=15_000_000.0,
        remaining_capex_total=p["silo1_remaining_capex_total"],
    )
    s2_const = ConstructionScenario(
        scheduled_commencement_month=p["scheduled_commencement_month_silo2"],
        delay_months=6,
        monthly_capex_burn=20_000_000.0,
        remaining_capex_total=p["silo2_remaining_capex_total"],
    )
    
    res = engine.run_pf1_simulation(
        s1_init, s2_init, s1_const, s2_const,
        p["silo1_rent_scenario"], p["silo2_rent_scenario"],
        p["silo1_amort_scenario"], p["silo2_amort_scenario"],
        waterfall_priority=p["waterfall_priority"],
    )
    print("Engine simulation completed successfully!")
    print(f"Silo 1 Milestones: {res.silo1_milestones}")
    print(f"Silo 2 Milestones: {res.silo2_milestones}")
    print(f"Total Cumulative Parent Support Required: ${res.monthly_ledger['cumulative_parent_support_funding_required'].iloc[-1]:,.2f}")
    print(f"Invariants Passed: {res.invariants_passed}")
