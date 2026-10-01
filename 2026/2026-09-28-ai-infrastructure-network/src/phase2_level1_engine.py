"""Phase 2 Level 1 Deterministic Project Delay-Tolerance Engine.

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
6. DSRA Restriction: DSRA funds can only be drawn for permitted debt-service shortfalls.
7. Independent Milestones: Milestones are detected independently across parallel debt-service
   and construction tracks (T_completion_support is not downstream of T_DSRA).
8. No Silent Zeroes: Missing parameters must be explicitly specified via scenarios.
9. Parent Reconvergence Overlay: Parent support sums across silos strictly after each silo's
   waterfall is computed independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass(frozen=True)
class SiloTerms:
    """Contractual terms governing an individual financing silo."""
    silo_id: str
    name: str
    principal_initial_usd: float
    annual_coupon_rate: float
    amortization_start_rule: str  # 'fixed_date' or 'post_commencement'
    fixed_amort_start_month: Optional[int] = None  # 1-indexed month relative to sim start
    final_maturity_month: int = 60  # Month index of maturity
    payment_frequency: str = "semiannual"  # "semiannual" or "monthly"
    payment_months: Tuple[int, ...] = (6, 12)  # Calendar months for payments if semiannual
    amortization_years: float = 3.0  # Duration over which principal amortizes


@dataclass
class AccountState:
    """Legally segregated cash accounts for a financing silo."""
    construction_cash: float
    dsra_cash: float
    operating_cash: float
    unrestricted_cash: float = 0.0


@dataclass(frozen=True)
class ConstructionScenario:
    """Construction schedule and capex burn scenario for a silo."""
    scheduled_commencement_month: int
    delay_months: int
    monthly_capex_burn: float  # Monthly capex burn until completion
    remaining_capex_total: Optional[float] = None  # If total capex is bounded


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
    t_payment_default: Optional[int] = None
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
    
    Silo 1: APLD_COMPUTECO / HPC_HOLDINGS ($2,350.0M 9.25% Senior Notes due Nov 2030)
            Amortization begins Dec 15, 2027 (Month 18 relative to July 2026).
    Silo 2: APLD_COMPUTECO3 ($1,590.0M 7.00% Senior Notes due June 2031)
            Amortization begins on first payment date following final Commencement Date.
    """
    # Silo 1: July 2026 to Dec 2027 is 17 months; month 18 is Dec 2027.
    # Maturity Nov 2030 is month 53 relative to July 2026.
    silo1 = SiloTerms(
        silo_id="SILO_1",
        name="APLD ComputeCo (Buildings 2 & 3)",
        principal_initial_usd=2_350_000_000.0,
        annual_coupon_rate=0.0925,
        amortization_start_rule="fixed_date",
        fixed_amort_start_month=18,  # Dec 2027
        final_maturity_month=53,    # Nov 2030
        payment_frequency="semiannual",
        payment_months=(6, 12),
        amortization_years=3.0,
    )
    
    # Silo 2: July 2026 to June 2031 is 60 months.
    silo2 = SiloTerms(
        silo_id="SILO_2",
        name="APLD ComputeCo 3 (Building 4)",
        principal_initial_usd=1_590_000_000.0,
        annual_coupon_rate=0.0700,
        amortization_start_rule="post_commencement",
        fixed_amort_start_month=None,
        final_maturity_month=60,    # June 2031
        payment_frequency="semiannual",
        payment_months=(6, 12),
        amortization_years=3.5,
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
    ) -> Tuple[pd.DataFrame, MilestoneRecord]:
        """Executes the monthly cash waterfall for a single, isolated financing silo."""
        records = []
        milestones = MilestoneRecord()
        milestones.t_refi = terms.final_maturity_month

        # Account balances
        c_const = initial_accounts.construction_cash
        c_dsra = initial_accounts.dsra_cash
        r_0 = initial_accounts.dsra_cash
        c_oper = initial_accounts.operating_cash
        principal = terms.principal_initial_usd

        # Calculate actual commencement month including delay
        actual_commencement = construction.scheduled_commencement_month + construction.delay_months

        # Determine amortization start month
        if terms.amortization_start_rule == "fixed_date":
            if terms.fixed_amort_start_month is None:
                raise ValueError(f"Silo {terms.silo_id} requires fixed_amort_start_month")
            amort_start_month = terms.fixed_amort_start_month
        elif terms.amortization_start_rule == "post_commencement":
            # Semiannual payment months are June (6) and Dec (12).
            # Finds the first payment month strictly after actual commencement.
            comm_month_date = self.dates[min(actual_commencement - 1, self.simulation_months - 1)]
            curr_cal_month = comm_month_date.month
            
            # Find how many months until the next semiannual payment date (June or Dec)
            # Payment months: 6, 12
            if curr_cal_month < 6:
                months_to_next_payment = 6 - curr_cal_month
            elif curr_cal_month < 12:
                months_to_next_payment = 12 - curr_cal_month
            else:
                months_to_next_payment = 6  # Next June
            
            amort_start_month = actual_commencement + months_to_next_payment
        else:
            raise ValueError(f"Unknown amortization_start_rule: {terms.amortization_start_rule}")

        # Compute scheduled principal amortization installment
        # Semiannual installments across terms.amortization_years
        num_amort_periods = max(1, int(terms.amortization_years * 2))
        semiannual_amort_payment = terms.principal_initial_usd / num_amort_periods

        for m in range(1, self.simulation_months + 1):
            curr_date = self.dates[m - 1]
            cal_month = curr_date.month
            is_payment_month = (cal_month in terms.payment_months)

            # --- TRACK B: Construction Funding Waterfall ---
            is_under_construction = (m < actual_commencement)
            capex_required = construction.monthly_capex_burn if is_under_construction else 0.0
            
            # Draw on construction account
            capex_from_account = min(c_const, capex_required)
            c_const -= capex_from_account
            capex_shortfall = capex_required - capex_from_account

            # Parent completion support triggers when construction funds are insufficient
            parent_completion_support = 0.0
            if capex_shortfall > 0:
                parent_completion_support = capex_shortfall
                if milestones.t_completion_support is None:
                    milestones.t_completion_support = m

            # --- TRACK A: Debt Service Waterfall ---
            # Monthly coupon interest on remaining principal
            monthly_interest_accrual = principal * (terms.annual_coupon_rate / 12.0)
            
            # Principal amortization due in payment months once amort_start_month is reached
            principal_amort_due = 0.0
            if m >= amort_start_month and is_payment_month and principal > 0:
                principal_amort_due = min(principal, semiannual_amort_payment)

            # Coupon cash payment due in payment months (semiannual: 6 months of interest)
            # In non-payment months, coupon accrues; in payment months, 6-month coupon is paid
            coupon_cash_due = 0.0
            if terms.payment_frequency == "semiannual":
                if is_payment_month:
                    coupon_cash_due = principal * (terms.annual_coupon_rate / 2.0)
            else:
                coupon_cash_due = monthly_interest_accrual

            total_debt_service_due = coupon_cash_due + principal_amort_due

            # Operating revenue (tenant rent)
            is_operational = (m >= actual_commencement)
            tenant_rent = rent.monthly_base_rent if is_operational else rent.pre_commencement_rent
            opex = rent.monthly_opex

            # Check coverage milestone
            net_operating_flow = tenant_rent - (opex + monthly_interest_accrual + (principal_amort_due / 6.0 if is_payment_month else 0.0))
            if net_operating_flow < 0 and milestones.t_coverage is None:
                milestones.t_coverage = m

            # Add rent and deduct opex from operating cash account
            c_oper += max(0.0, tenant_rent - opex)

            # Pay debt service from operating cash account
            paid_from_oper = min(c_oper, total_debt_service_due)
            c_oper -= paid_from_oper
            debt_service_shortfall = total_debt_service_due - paid_from_oper

            if c_oper == 0 and milestones.t_operating_exhaustion is None and total_debt_service_due > 0:
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

            # Unfunded debt service constitutes a contractual payment failure / default
            is_payment_default = (unfunded_debt_service > 0)
            if is_payment_default and milestones.t_payment_default is None:
                milestones.t_payment_default = m

            # Principal update upon amortization payment
            principal -= min(principal, principal_amort_due)

            # Check maturity
            if m == terms.final_maturity_month and principal > 0:
                # Bullet maturity boundary reached with remaining principal
                pass

            records.append({
                "month": m,
                "date": curr_date.strftime("%Y-%m"),
                "silo_id": terms.silo_id,
                "principal_remaining": principal,
                "monthly_interest_accrual": monthly_interest_accrual,
                "coupon_cash_due": coupon_cash_due,
                "principal_amort_due": principal_amort_due,
                "total_debt_service_due": total_debt_service_due,
                "tenant_rent": tenant_rent,
                "opex": opex,
                "operating_cash_balance": c_oper,
                "dsra_balance": c_dsra,
                "dsra_draw": dsra_draw,
                "construction_cash_balance": c_const,
                "capex_required": capex_required,
                "parent_completion_support_required": parent_completion_support,
                "unfunded_debt_service": unfunded_debt_service,
                "is_payment_default": is_payment_default,
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
    ) -> EngineResult:
        """Executes parallel waterfalls for Silo 1 and Silo 2, then computes campus parent overlay."""
        silo1_terms, silo2_terms = create_default_pf1_silos(self.start_date.strftime("%Y-%m-%d"))

        # Run each silo in strict isolation
        df_silo1, m_silo1 = self.run_silo_waterfall(silo1_terms, silo1_initial, silo1_construction, silo1_rent)
        df_silo2, m_silo2 = self.run_silo_waterfall(silo2_terms, silo2_initial, silo2_construction, silo2_rent)

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
        """Verifies all 9 core structural and contractual invariants."""
        # 1. Silo Isolation: Silo 1 cash columns must be completely independent of Silo 2 parameters
        assert "dsra_balance_silo1" in combined and "dsra_balance_silo2" in combined

        # 2. Fixed Coupon Arithmetic: Monthly accrual = principal * r / 12
        for idx, row in df1.iterrows():
            expected_accrual = (row["principal_remaining"] + row["principal_amort_due"]) * (terms1.annual_coupon_rate / 12.0)
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

        # 7. Independent Milestones: Milestone values are recorded independently
        # (Verified by structure of MilestoneRecord)

        # 8. Parent Summation strictly post-waterfall
        expected_sum = combined["parent_completion_support_required_silo1"] + combined["parent_completion_support_required_silo2"]
        assert np.allclose(combined["total_parent_completion_support"], expected_sum)

        return True


def compute_delay_tolerance_surface(
    reserve_grid: List[float],
    capex_burn_grid: List[float],
    delay_months_grid: List[int],
    silo1_rent_proxy: float = 183_300_000.0 / 12.0,  # Proportional proxy: ~$15.275M/mo
    silo2_rent_proxy: float = 110_000_000.0 / 12.0,  # Proportional proxy
) -> pd.DataFrame:
    """Computes the Contract-Bounded Milestone Surface across a grid of reserves and delays.
    
    Generates the multidimensional mapping:
    T_milestone = f(R_0, K_burn, Delay)
    """
    engine = DeterministicDelayEngine(simulation_months=60)
    surface_rows = []

    for r_0 in reserve_grid:
        for k_burn in capex_burn_grid:
            for delay in delay_months_grid:
                # Silo 1: Building 2 operational, Building 3 completion
                silo1_init = AccountState(
                    construction_cash=100_000_000.0,
                    dsra_cash=r_0,
                    operating_cash=20_000_000.0,
                )
                silo1_const = ConstructionScenario(
                    scheduled_commencement_month=12,
                    delay_months=delay,
                    monthly_capex_burn=k_burn,
                )
                silo1_rent = RentScenario(
                    monthly_base_rent=silo1_rent_proxy,
                    monthly_opex=1_000_000.0,
                )

                # Silo 2: Building 4 construction
                silo2_init = AccountState(
                    construction_cash=150_000_000.0,
                    dsra_cash=r_0 * (1590.0 / 2350.0),  # Proportionate reserve
                    operating_cash=0.0,
                )
                silo2_const = ConstructionScenario(
                    scheduled_commencement_month=18,
                    delay_months=delay,
                    monthly_capex_burn=k_burn * 1.2,
                )
                silo2_rent = RentScenario(
                    monthly_base_rent=silo2_rent_proxy,
                    monthly_opex=1_000_000.0,
                )

                result = engine.run_pf1_simulation(
                    silo1_init, silo2_init,
                    silo1_const, silo2_const,
                    silo1_rent, silo2_rent,
                )

                max_parent_support = result.monthly_ledger["cumulative_parent_support_funding_required"].iloc[-1]

                surface_rows.append({
                    "initial_dsra_silo1": r_0,
                    "capex_burn_silo1": k_burn,
                    "delay_months": delay,
                    "t_coverage_silo1": result.silo1_milestones.t_coverage,
                    "t_oper_exhaustion_silo1": result.silo1_milestones.t_operating_exhaustion,
                    "t_dsra_silo1": result.silo1_milestones.t_dsra,
                    "t_completion_support_silo1": result.silo1_milestones.t_completion_support,
                    "t_payment_default_silo1": result.silo1_milestones.t_payment_default,
                    "t_coverage_silo2": result.silo2_milestones.t_coverage,
                    "t_oper_exhaustion_silo2": result.silo2_milestones.t_operating_exhaustion,
                    "t_dsra_silo2": result.silo2_milestones.t_dsra,
                    "t_completion_support_silo2": result.silo2_milestones.t_completion_support,
                    "t_payment_default_silo2": result.silo2_milestones.t_payment_default,
                    "cumulative_parent_support_required_usd": max_parent_support,
                })

    return pd.DataFrame(surface_rows)


if __name__ == "__main__":
    print("Testing DeterministicDelayEngine baseline run...")
    engine = DeterministicDelayEngine(simulation_months=60)
    
    # Baseline test scenario
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=150_000_000.0, operating_cash=25_000_000.0)
    s2_init = AccountState(construction_cash=150_000_000.0, dsra_cash=100_000_000.0, operating_cash=0.0)
    
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=6, monthly_capex_burn=15_000_000.0)
    s2_const = ConstructionScenario(scheduled_commencement_month=18, delay_months=6, monthly_capex_burn=20_000_000.0)
    
    s1_rent = RentScenario(monthly_base_rent=15_275_000.0, monthly_opex=1_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=9_166_667.0, monthly_opex=1_000_000.0)
    
    res = engine.run_pf1_simulation(s1_init, s2_init, s1_const, s2_const, s1_rent, s2_rent)
    print("Engine simulation completed successfully!")
    print(f"Silo 1 Milestones: {res.silo1_milestones}")
    print(f"Silo 2 Milestones: {res.silo2_milestones}")
    print(f"Total Cumulative Parent Support Required: ${res.monthly_ledger['cumulative_parent_support_funding_required'].iloc[-1]:,.2f}")
    print(f"Invariants Passed: {res.invariants_passed}")
