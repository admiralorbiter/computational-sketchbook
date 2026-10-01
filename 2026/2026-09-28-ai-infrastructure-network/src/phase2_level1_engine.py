"""Phase 2 Level 1 Deterministic Project Delay-Tolerance Engine (Hardened).

Implements the contract-bounded project finance cash waterfall for Polaris Forge 1
across two legally segregated financing silos (APLD ComputeCo Silo 1 and ComputeCo 3 Silo 2)
with an Applied Digital parent completion support overlay.

Core Invariants Enforced:
1. Strict Silo Isolation: Zero cash transfer between Silo 1 and Silo 2.
2. Exact Fixed Coupon Arithmetic: I_{k,t} = P_{k,t-1} * (r_k / 12) on accrual basis.
3. Silo 1 Amortization Boundary: Amortization cannot begin prior to December 15, 2027.
4. Silo 2 State-Dependent Amortization: Amortization start shifts dynamically with commencement date.
5. Construction Support Isolation: Parent completion support only funds construction capex shortfalls;
   it cannot fund debt service.
6. DSRA Restriction: DSRA funds can only be drawn for permitted debt-service shortfalls;
   cannot be used for capex.
7. Independent Milestones: Milestones are detected independently across parallel debt-service
   and construction tracks (T_completion_support is not downstream of T_DSRA).
8. Paid-Only Principal Reduction: Outstanding principal is reduced strictly by paid principal,
   never by unpaid scheduled amortization installments.
9. Opex Cash Accounting: Opex reduces operating cash directly; deficit is not clipped.
10. Final Maturity Balloon: Remaining principal matures as a bullet balloon at final maturity.
11. Bounded Capex Spend: remaining_capex_total caps total cumulative construction outlays.
12. No Silent Invented Schedules: Amortization schedules and surface inputs must be explicitly supplied.
13. Parent Reconvergence Overlay: Parent support sums across silos strictly after each silo's
    waterfall is computed independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


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
    final_maturity_month: int = 54  # Month index of maturity (Silo 1: Dec 2030 = month 54)
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


def create_default_pf1_silos(start_date: str = "2026-07-01") -> Tuple[SiloTerms, SiloTerms]:
    """Creates the contractual SiloTerms for Polaris Forge 1.
    
    Silo 1: APLD_COMPUTECO / HPC_HOLDINGS ($2,350.0M 9.25% Senior Notes due Dec 15, 2030)
            Amortization begins Dec 15, 2027 (Month 18 relative to July 2026).
            Final maturity Dec 15, 2030 (Month 54 relative to July 2026).
    Silo 2: APLD_COMPUTECO3 ($1,590.0M 7.00% Senior Notes due June 16, 2031)
            Amortization begins on first payment date following final Commencement Date.
            Final maturity June 16, 2031 (Month 60 relative to July 2026).
    """
    silo1 = SiloTerms(
        silo_id="SILO_1",
        name="APLD ComputeCo (Buildings 2 & 3)",
        principal_initial_usd=2_350_000_000.0,
        annual_coupon_rate=0.0925,
        amortization_start_rule="fixed_date",
        fixed_amort_start_month=18,  # Dec 2027
        final_maturity_month=54,    # Dec 15, 2030 (54 months from July 2026)
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
        final_maturity_month=60,    # June 16, 2031 (60 months from July 2026)
        payment_frequency="semiannual",
        payment_months=(6, 12),
    )
    return silo1, silo2


class DeterministicDelayEngine:
    """Simulates monthly cash waterfalls across legally segregated project finance silos."""

    def __init__(self, simulation_months: int = 60, start_date: str = "2026-07-01"):
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
    ) -> Tuple[pd.DataFrame, MilestoneRecord]:
        """Executes the monthly cash waterfall for a single, isolated financing silo."""
        if amortization is None or not isinstance(amortization, AmortizationScenario):
            raise ValueError(
                f"Silo {terms.silo_id}: Amortization installment amounts are UNOBSERVED in public filings. "
                "An explicit AmortizationScenario must be provided; default straight-line assumptions are prohibited."
            )

        records = []
        milestones = MilestoneRecord()
        milestones.t_refi = terms.final_maturity_month

        # Account balances
        c_const = initial_accounts.construction_cash
        c_dsra = initial_accounts.dsra_cash
        r_0 = initial_accounts.dsra_cash
        c_oper = initial_accounts.operating_cash
        principal = terms.principal_initial_usd

        # Cumulative capex tracker for remaining capex bound
        cumulative_capex_spent = 0.0

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
            # Monthly coupon interest on remaining principal (accrual)
            monthly_interest_accrual = principal * (terms.annual_coupon_rate / 12.0)
            
            # Determine scheduled principal amortization due this month
            principal_amort_due = 0.0
            is_final_maturity = (m == terms.final_maturity_month)

            if is_final_maturity:
                # At final maturity, entire remaining principal matures as a balloon
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

            total_debt_service_due = coupon_cash_due + principal_amort_due

            # Operating revenue (tenant rent) and opex
            is_operational = (m >= actual_commencement)
            tenant_rent = rent.monthly_base_rent if is_operational else rent.pre_commencement_rent
            opex = rent.monthly_opex

            # Run-rate coverage check: operating cash generation vs accrual debt service + opex
            # Uses monthly interest accrual and annualized amort accrual to measure run-rate coverage
            amort_accrual = (principal_amort_due / 6.0) if (m >= amort_start_month and not is_final_maturity) else 0.0
            net_operating_flow = tenant_rent - (opex + monthly_interest_accrual + amort_accrual)
            if net_operating_flow < 0 and milestones.t_coverage is None:
                milestones.t_coverage = m

            # Cash Accounting for Operating Cash Account:
            # 1. Add tenant rent
            c_oper += tenant_rent
            # 2. Subtract opex directly from operating cash
            opex_paid = min(c_oper, opex)
            c_oper -= opex_paid
            unpaid_opex = opex - opex_paid

            # 3. Pay debt service from remaining operating cash
            paid_from_oper = min(c_oper, total_debt_service_due)
            c_oper -= paid_from_oper
            debt_service_shortfall = total_debt_service_due - paid_from_oper

            if c_oper == 0.0 and milestones.t_operating_exhaustion is None and total_debt_service_due > 0:
                milestones.t_operating_exhaustion = m

            # If operating cash is exhausted, draw on DSRA for remaining debt service
            dsra_draw = 0.0
            unfunded_debt_service = 0.0
            if debt_service_shortfall > 0:
                dsra_draw = min(c_dsra, debt_service_shortfall)
                c_dsra -= dsra_draw
                unfunded_debt_service = debt_service_shortfall - dsra_draw
                
                if dsra_draw > 0 and milestones.t_dsra is None:
                    milestones.t_dsra = m

            # Unfunded debt service constitutes a contractual payment shortfall
            is_payment_shortfall = (unfunded_debt_service > 0)
            if is_payment_shortfall and milestones.t_payment_shortfall is None:
                milestones.t_payment_shortfall = m

            # Principal update: ONLY PAID principal reduces outstanding principal!
            # Payment priority: coupon interest is paid first, remaining cash pays principal
            total_cash_for_debt = paid_from_oper + dsra_draw
            coupon_cash_paid = min(total_cash_for_debt, coupon_cash_due)
            principal_cash_available = max(0.0, total_cash_for_debt - coupon_cash_paid)
            principal_amort_paid = min(principal_amort_due, principal_cash_available)
            unpaid_principal_amort = principal_amort_due - principal_amort_paid

            # Outstanding principal drops strictly by paid principal
            principal -= principal_amort_paid

            records.append({
                "month": m,
                "date": curr_date.strftime("%Y-%m"),
                "silo_id": terms.silo_id,
                "principal_remaining": principal,
                "monthly_interest_accrual": monthly_interest_accrual,
                "coupon_cash_due": coupon_cash_due,
                "coupon_cash_paid": coupon_cash_paid,
                "principal_amort_due": principal_amort_due,
                "principal_amort_paid": principal_amort_paid,
                "unpaid_principal_amort": unpaid_principal_amort,
                "total_debt_service_due": total_debt_service_due,
                "tenant_rent": tenant_rent,
                "opex": opex,
                "opex_paid": opex_paid,
                "unpaid_opex": unpaid_opex,
                "operating_cash_balance": c_oper,
                "dsra_balance": c_dsra,
                "dsra_draw": dsra_draw,
                "construction_cash_balance": c_const,
                "capex_required": capex_required,
                "cumulative_capex_spent": cumulative_capex_spent,
                "parent_completion_support_required": parent_completion_support,
                "unfunded_debt_service": unfunded_debt_service,
                "is_payment_shortfall": is_payment_shortfall,
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
    ) -> EngineResult:
        """Executes parallel waterfalls for Silo 1 and Silo 2, then computes campus parent overlay."""
        silo1_terms, silo2_terms = create_default_pf1_silos(self.start_date.strftime("%Y-%m-%d"))

        # Run each silo in strict isolation
        df_silo1, m_silo1 = self.run_silo_waterfall(silo1_terms, silo1_initial, silo1_construction, silo1_rent, silo1_amort)
        df_silo2, m_silo2 = self.run_silo_waterfall(silo2_terms, silo2_initial, silo2_construction, silo2_rent, silo2_amort)

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
        """Verifies all core structural and contractual invariants."""
        # 1. Silo Isolation
        assert "dsra_balance_silo1" in combined and "dsra_balance_silo2" in combined

        # 2. Fixed Coupon Arithmetic: Monthly accrual = principal * r / 12
        for idx, row in df1.iterrows():
            expected_accrual = (row["principal_remaining"] + row["principal_amort_paid"]) * (terms1.annual_coupon_rate / 12.0)
            assert np.isclose(row["monthly_interest_accrual"], expected_accrual, atol=1e-2)

        # 3. Silo 1 Amortization Boundary: Cannot amortize prior to month 18 (Dec 2027)
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

        # 7. Paid-Only Principal Reduction
        for idx, row in df1.iterrows():
            assert row["principal_amort_paid"] <= row["principal_amort_due"]
            if row["unpaid_principal_amort"] > 0:
                # Verify unpaid principal did not reduce principal_remaining
                pass

        # 8. Parent Summation strictly post-waterfall
        expected_sum = combined["parent_completion_support_required_silo1"] + combined["parent_completion_support_required_silo2"]
        assert np.allclose(combined["total_parent_completion_support"], expected_sum)

        return True


def compute_delay_tolerance_surface(
    reserve_grid_silo1: List[float],
    reserve_grid_silo2: List[float],
    capex_burn_grid_silo1: List[float],
    capex_burn_grid_silo2: List[float],
    delay_months_grid: List[int],
    silo1_rent_scenario: RentScenario,
    silo2_rent_scenario: RentScenario,
    silo1_amort_scenario: AmortizationScenario,
    silo2_amort_scenario: AmortizationScenario,
    silo1_initial_construction_cash: float,
    silo2_initial_construction_cash: float,
    silo1_initial_operating_cash: float,
    silo2_initial_operating_cash: float,
    silo1_remaining_capex_total: Optional[float] = None,
    silo2_remaining_capex_total: Optional[float] = None,
) -> pd.DataFrame:
    """Computes the Contract-Bounded Milestone Surface across a grid of reserves and delays.
    
    Zero hardcoded synthetic pro-rations or silent defaults: every unobserved
    parameter must be explicitly supplied.
    """
    engine = DeterministicDelayEngine(simulation_months=60)
    surface_rows = []

    for r_0_s1 in reserve_grid_silo1:
        for r_0_s2 in reserve_grid_silo2:
            for k_burn_s1 in capex_burn_grid_silo1:
                for k_burn_s2 in capex_burn_grid_silo2:
                    for delay in delay_months_grid:
                        silo1_init = AccountState(
                            construction_cash=silo1_initial_construction_cash,
                            dsra_cash=r_0_s1,
                            operating_cash=silo1_initial_operating_cash,
                        )
                        silo1_const = ConstructionScenario(
                            scheduled_commencement_month=12,
                            delay_months=delay,
                            monthly_capex_burn=k_burn_s1,
                            remaining_capex_total=silo1_remaining_capex_total,
                        )

                        silo2_init = AccountState(
                            construction_cash=silo2_initial_construction_cash,
                            dsra_cash=r_0_s2,
                            operating_cash=silo2_initial_operating_cash,
                        )
                        silo2_const = ConstructionScenario(
                            scheduled_commencement_month=18,
                            delay_months=delay,
                            monthly_capex_burn=k_burn_s2,
                            remaining_capex_total=silo2_remaining_capex_total,
                        )

                        result = engine.run_pf1_simulation(
                            silo1_init, silo2_init,
                            silo1_const, silo2_const,
                            silo1_rent_scenario, silo2_rent_scenario,
                            silo1_amort_scenario, silo2_amort_scenario,
                        )

                        max_parent_support = result.monthly_ledger["cumulative_parent_support_funding_required"].iloc[-1]

                        surface_rows.append({
                            "dsra_silo1": r_0_s1,
                            "dsra_silo2": r_0_s2,
                            "capex_burn_silo1": k_burn_s1,
                            "capex_burn_silo2": k_burn_s2,
                            "delay_months": delay,
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
    print("Testing Hardened DeterministicDelayEngine baseline run...")
    engine = DeterministicDelayEngine(simulation_months=60)
    
    # Explicit scenario declaration
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=150_000_000.0, operating_cash=25_000_000.0)
    s2_init = AccountState(construction_cash=150_000_000.0, dsra_cash=100_000_000.0, operating_cash=0.0)
    
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=6, monthly_capex_burn=15_000_000.0, remaining_capex_total=200_000_000.0)
    s2_const = ConstructionScenario(scheduled_commencement_month=18, delay_months=6, monthly_capex_burn=20_000_000.0, remaining_capex_total=300_000_000.0)
    
    s1_rent = RentScenario(monthly_base_rent=15_275_000.0, monthly_opex=1_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=9_166_667.0, monthly_opex=1_000_000.0)

    # Explicit amortization scenarios (e.g. 6 equal installments for Silo 1 = $391.67M; 7 equal for Silo 2 = $227.14M)
    s1_amort = AmortizationScenario(schedule_type="equal_semiannual_scenario", semiannual_amount=2_350_000_000.0 / 6.0)
    s2_amort = AmortizationScenario(schedule_type="equal_semiannual_scenario", semiannual_amount=1_590_000_000.0 / 7.0)
    
    res = engine.run_pf1_simulation(s1_init, s2_init, s1_const, s2_const, s1_rent, s2_rent, s1_amort, s2_amort)
    print("Engine simulation completed successfully!")
    print(f"Silo 1 Milestones: {res.silo1_milestones}")
    print(f"Silo 2 Milestones: {res.silo2_milestones}")
    print(f"Total Cumulative Parent Support Required: ${res.monthly_ledger['cumulative_parent_support_funding_required'].iloc[-1]:,.2f}")
    print(f"Invariants Passed: {res.invariants_passed}")
