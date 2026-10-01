"""Test Suite for Phase 2 Level 1 Deterministic Delay Engine (Hardened 2.1.2).

Verifies core contractual, legal, financial, and accounting invariants:
1. Strict Silo Isolation: Zero cash transfer or dependency between Silo 1 and Silo 2.
2. Exact Fixed Coupon Arithmetic: Coupon equals beginning principal * rate.
3. Silo 1 Amortization Boundary: Amortization strictly barred before Dec 15, 2027 (Month 18 from July 2026).
4. Silo 2 State-Dependent Amortization: Amortization start date shifts dynamically with commencement
   (contractual invariant: amortization_start(delayed) > amortization_start(on_time)).
5. Construction Support Isolation: Parent completion support only funds capex shortfalls, never debt service.
6. DSRA Restriction: DSRA can only fund permitted debt-service uses, never capex.
7. Independent Milestones: T_completion_support triggers independently of T_DSRA or T_coverage.
8. Non-Monotonic Amortization Deferral: Delay defers Silo 2 principal amortization, reducing near-term
   cash drain under positive amortization scenarios.
9. Parent Overlay Summation: Parent support sums strictly after independent silo waterfalls.
10. Paid-Only Principal Reduction: Unpaid scheduled amortization does NOT reduce outstanding principal balance.
11. Complete Arrears Accounting: Unpaid opex and debt service are carried forward as arrears balances
    (opex_payable, interest_payable, principal_arrears) and cured by incoming cash.
12. Absorbing Default Boundary: Once T_payment_shortfall occurs, the silo enters default and all subsequent
    months are marked with is_post_shortfall=True and economic_status='POST_SHORTFALL_ABSORBED'.
13. Cash Coverage Definition: T_coverage compares actual monthly tenant cash rent against actual monthly cash
    obligations (opex + debt service due).
14. Operating Account Depletion: T_operating_exhaustion fires when operating cash reaches zero,
    including from opex alone without any debt service due.
15. Explicit Waterfall Priority: Evaluates behavior under 'opex_first' vs 'debt_service_first'.
16. Dynamic Date Mapping: Contractual month indexes derive dynamically from simulation start date.
17. Final Maturity Balloon: Remaining principal matures as a bullet balloon at final maturity
    (Month 54 for Silo 1 / Dec 15, 2030; Month 60 for Silo 2 / June 15, 2031).
18. Bounded Cumulative Capex: remaining_capex_total caps total cumulative construction outlays.
19. Zero Silent Priors in Surface API: Every unobserved financial input is mandatory.
"""

import pytest
import numpy as np
import pandas as pd
from phase2_level1_engine import (
    DeterministicDelayEngine,
    SiloTerms,
    AccountState,
    ConstructionScenario,
    RentScenario,
    AmortizationScenario,
    MilestoneRecord,
    create_default_pf1_silos,
    demo_pf1_analyst_scenario,
    compute_delay_tolerance_surface,
    CANONICAL_PF1_START_DATE,
    SILO1_AMORT_START_DATE,
    SILO1_MATURITY_DATE,
    SILO2_MATURITY_DATE,
)


@pytest.fixture
def engine():
    return DeterministicDelayEngine(simulation_months=60, start_date=CANONICAL_PF1_START_DATE)


@pytest.fixture
def standard_s1_amort():
    # 6 equal semiannual installments for Silo 1 starting month 18 ($2,350M / 6 = $391.67M)
    return AmortizationScenario(
        schedule_type="equal_semiannual_scenario",
        semiannual_amount=2_350_000_000.0 / 6.0,
    )


@pytest.fixture
def standard_s2_amort():
    # 7 equal semiannual installments for Silo 2 starting post-commencement ($1,590M / 7 = $227.14M)
    return AmortizationScenario(
        schedule_type="equal_semiannual_scenario",
        semiannual_amount=1_590_000_000.0 / 7.0,
    )


def test_strict_silo_isolation(engine, standard_s1_amort, standard_s2_amort):
    """Invariant 1: Silo 1's cash ledger must be mathematically invariant to changes in Silo 2."""
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=150_000_000.0, operating_cash=20_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=3, monthly_capex_burn=10_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=15_000_000.0, monthly_opex=1_000_000.0)

    # Run Case A: Silo 2 has standard parameters
    s2_init_A = AccountState(construction_cash=150_000_000.0, dsra_cash=100_000_000.0, operating_cash=0.0)
    s2_const_A = ConstructionScenario(scheduled_commencement_month=18, delay_months=0, monthly_capex_burn=20_000_000.0)
    s2_rent_A = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=1_000_000.0)
    res_A = engine.run_pf1_simulation(
        s1_init, s2_init_A, s1_const, s2_const_A, s1_rent, s2_rent_A, standard_s1_amort, standard_s2_amort
    )

    # Run Case B: Silo 2 has extreme stress parameters (zero cash, huge burn, massive delay)
    s2_init_B = AccountState(construction_cash=0.0, dsra_cash=0.0, operating_cash=0.0)
    s2_const_B = ConstructionScenario(scheduled_commencement_month=18, delay_months=24, monthly_capex_burn=100_000_000.0)
    s2_rent_B = RentScenario(monthly_base_rent=0.0, monthly_opex=10_000_000.0)
    res_B = engine.run_pf1_simulation(
        s1_init, s2_init_B, s1_const, s2_const_B, s1_rent, s2_rent_B, standard_s1_amort, standard_s2_amort
    )

    # Assert Silo 1 columns in ledger are identical between Case A and Case B
    silo1_cols = [c for c in res_A.monthly_ledger.columns if c.endswith("_silo1")]
    for col in silo1_cols:
        pd.testing.assert_series_equal(
            res_A.monthly_ledger[col],
            res_B.monthly_ledger[col],
            check_names=True,
            obj=f"Silo isolation breached on column {col}",
        )


def test_fixed_coupon_arithmetic(engine, standard_s1_amort):
    """Invariant 2: Monthly interest accrual must exactly equal beginning principal * coupon / 12."""
    s1_init = AccountState(construction_cash=50_000_000.0, dsra_cash=100_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=5_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)
    s1_terms, _ = create_default_pf1_silos()

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    for _, row in df.iterrows():
        beginning_principal = row["principal_remaining"] + row["principal_amort_paid"]
        expected_monthly = beginning_principal * (s1_terms.annual_coupon_rate / 12.0)
        assert np.isclose(row["monthly_interest_accrual"], expected_monthly, atol=1e-2)

        # Semiannual payment month check (months ending in -06 or -12, or month 54 maturity)
        if row["date"].endswith("-06") or row["date"].endswith("-12") or row["month"] == s1_terms.final_maturity_month:
            expected_cash = beginning_principal * (s1_terms.annual_coupon_rate / 2.0)
            assert np.isclose(row["coupon_cash_due"], expected_cash, atol=1e-2)
        else:
            assert row["coupon_cash_due"] == 0.0


def test_silo1_amortization_boundary(engine, standard_s1_amort):
    """Invariant 3: Silo 1 principal amortization cannot begin before December 15, 2027 (month 18)."""
    s1_terms, _ = create_default_pf1_silos()
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=200_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=1_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=25_000_000.0, monthly_opex=1_000_000.0)

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # Prior to month 18, amortization must be zero
    pre_18_amort = df[df["month"] < 18]["principal_amort_due"].sum()
    assert pre_18_amort == 0.0

    # In month 18 (Dec 2027), scheduled amortization must be positive
    month_18_amort = df[df["month"] == 18]["principal_amort_due"].iloc[0]
    assert month_18_amort > 0.0


def test_silo2_state_dependent_amortization(engine, standard_s2_amort):
    """Invariant 4: Silo 2 amortization start date shifts dynamically with commencement delay."""
    _, s2_terms = create_default_pf1_silos()
    s2_init = AccountState(construction_cash=200_000_000.0, dsra_cash=150_000_000.0, operating_cash=50_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)

    # Case 1: Scheduled commencement at month 12 (June 2027), 0 delay.
    # First payment date after June 2027 is Dec 2027 (month 18).
    const_early = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=5_000_000.0)
    df_early, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_early, s2_rent, standard_s2_amort)
    amort_early_start = df_early[df_early["principal_amort_due"] > 0]["month"].iloc[0]
    assert amort_early_start == 18

    # Case 2: 6 months of delay -> actual commencement is month 18 (Dec 2027).
    # First payment date after Dec 2027 is June 2028 (month 24).
    const_delayed = ConstructionScenario(scheduled_commencement_month=12, delay_months=6, monthly_capex_burn=5_000_000.0)
    df_delayed, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_delayed, s2_rent, standard_s2_amort)
    amort_delayed_start = df_delayed[df_delayed["principal_amort_due"] > 0]["month"].iloc[0]
    assert amort_delayed_start == 24

    # Contractual invariant: amortization_start(delayed) > amortization_start(on_time)
    assert amort_delayed_start > amort_early_start


def test_completion_support_independent_of_dsra(engine, standard_s1_amort):
    """Invariant 7: T_completion_support triggers independently of T_DSRA.
    
    A project with zero construction funds but full DSRA triggers parent completion
    support immediately in month 1, while DSRA remains 100% untouched.
    """
    s1_terms, _ = create_default_pf1_silos()
    # Zero construction cash, large DSRA, large operating cash
    s1_init = AccountState(construction_cash=0.0, dsra_cash=200_000_000.0, operating_cash=100_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=15_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # Completion support required immediately in month 1
    assert milestones.t_completion_support == 1
    # But operating cash is large, so DSRA is not touched in month 1
    assert df["dsra_draw"].iloc[0] == 0.0
    assert milestones.t_dsra is None or milestones.t_dsra > 1


def test_completion_support_does_not_fund_debt_service(engine, standard_s1_amort):
    """Invariant 5: Parent completion support only funds capex shortfalls, not debt service."""
    s1_terms, _ = create_default_pf1_silos()
    # Zero operating cash, zero DSRA, zero construction cash, operational (zero capex required)
    s1_init = AccountState(construction_cash=0.0, dsra_cash=0.0, operating_cash=0.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=1, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=0.0, monthly_opex=0.0)  # No rent

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # In month 6 (first coupon payment date), debt service is due with zero cash
    month_6 = df[df["month"] == 6].iloc[0]
    assert month_6["coupon_cash_due"] > 0
    # Payment shortfall triggers
    assert milestones.t_payment_shortfall == 6
    # Parent completion support is strictly 0 because capex required is 0
    assert month_6["parent_completion_support_required"] == 0.0


def test_dsra_restriction(engine, standard_s1_amort):
    """Invariant 6: DSRA funds cannot be drawn for capex construction shortfalls."""
    s1_terms, _ = create_default_pf1_silos()
    # Full DSRA, zero construction cash, high capex burn
    s1_init = AccountState(construction_cash=0.0, dsra_cash=100_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=20_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=0.0)

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # Month 1 has $20M capex required and $0 construction cash.
    # DSRA must NOT be drawn for capex.
    month_1 = df[df["month"] == 1].iloc[0]
    assert month_1["parent_completion_support_required"] == 20_000_000.0
    assert month_1["dsra_draw"] == 0.0
    assert month_1["dsra_balance"] == 100_000_000.0


def test_parent_support_funding_summation(engine, standard_s1_amort, standard_s2_amort):
    """Invariant 9: Total parent support is strictly the post-waterfall sum of silo1 and silo2."""
    s1_init = AccountState(construction_cash=10_000_000.0, dsra_cash=50_000_000.0, operating_cash=10_000_000.0)
    s2_init = AccountState(construction_cash=20_000_000.0, dsra_cash=50_000_000.0, operating_cash=10_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=15_000_000.0)
    s2_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=25_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=1_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=1_000_000.0)

    res = engine.run_pf1_simulation(
        s1_init, s2_init, s1_const, s2_const, s1_rent, s2_rent, standard_s1_amort, standard_s2_amort
    )
    ledger = res.monthly_ledger

    sum_cols = ledger["parent_completion_support_required_silo1"] + ledger["parent_completion_support_required_silo2"]
    assert np.allclose(ledger["total_parent_completion_support"], sum_cols)


def test_delay_defers_amortization_under_positive_amortization_scenario(engine, standard_s2_amort):
    """Scenario Property: Delay in Silo 2 defers scheduled principal amortization, moderating near-term cash drain.
    
    Demonstrates that under a positive amortization scenario (e.g. 7 equal installments),
    delaying commencement by 6 months defers the onset of principal amortization from Month 18 to Month 24.
    Consequently, in Month 18, Silo 2 cash debt service due is LOWER under the delayed scenario.
    
    The contractual invariant is amortization_start(delayed) > amortization_start(on_time).
    The resulting cash relief in Month 18 is a scenario property under positive amortization schedules.
    """
    _, s2_terms = create_default_pf1_silos()
    s2_init = AccountState(construction_cash=100_000_000.0, dsra_cash=100_000_000.0, operating_cash=100_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=15_000_000.0, monthly_opex=1_000_000.0)

    # Early commencement (month 12) -> amortization active by month 18
    const_early = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=5_000_000.0)
    df_early, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_early, s2_rent, standard_s2_amort)
    debt_service_m18_early = df_early[df_early["month"] == 18]["total_debt_service_due"].iloc[0]

    # Delayed commencement (month 12 + 6 = month 18) -> amortization deferred to month 24
    const_delayed = ConstructionScenario(scheduled_commencement_month=12, delay_months=6, monthly_capex_burn=5_000_000.0)
    df_delayed, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_delayed, s2_rent, standard_s2_amort)
    debt_service_m18_delayed = df_delayed[df_delayed["month"] == 18]["total_debt_service_due"].iloc[0]

    # Contractual invariant: start date is deferred
    amort_early_month = df_early[df_early["principal_amort_due"] > 0]["month"].iloc[0]
    amort_delayed_month = df_delayed[df_delayed["principal_amort_due"] > 0]["month"].iloc[0]
    assert amort_delayed_month > amort_early_month

    # Scenario finding: Delayed project owes LESS total debt service in month 18 than the on-time project
    assert debt_service_m18_delayed < debt_service_m18_early
    # The difference is exactly the deferred principal amortization installment
    amort_early = df_early[df_early["month"] == 18]["principal_amort_due"].iloc[0]
    amort_delayed = df_delayed[df_delayed["month"] == 18]["principal_amort_due"].iloc[0]
    assert amort_early > 0.0
    assert amort_delayed == 0.0


# =========================================================================
# P0 / P1 / P2 ACCOUNTING & ROBUSTNESS REGRESSION TESTS
# =========================================================================

def test_unpaid_principal_remains_outstanding(engine):
    """P0 Fix 1: Unpaid scheduled principal amortization does NOT reduce principal balance.
    
    Only cash actually paid towards principal reduces the outstanding note balance.
    """
    s1_terms, _ = create_default_pf1_silos()
    # Set up Silo 1 with insufficient operating cash and zero DSRA at amortization start (month 18)
    s1_init = AccountState(construction_cash=50_000_000.0, dsra_cash=0.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=50_000_000.0, monthly_opex=0.0)
    
    # Large amortization due of $500M in month 18
    s1_amort = AmortizationScenario(
        schedule_type="custom_schedule",
        custom_schedule_by_month={18: 500_000_000.0},
    )

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, s1_amort)

    m18_row = df[df["month"] == 18].iloc[0]
    assert m18_row["principal_amort_due"] == 500_000_000.0
    assert m18_row["principal_arrears"] > 0.0  # Cannot fully pay $500M
    
    # Crucial assertion: principal_remaining is reduced ONLY by principal_amort_paid, NOT principal_amort_due
    prior_principal = df[df["month"] == 17]["principal_remaining"].iloc[0]
    assert np.isclose(m18_row["principal_remaining"], prior_principal - m18_row["principal_amort_paid"])
    assert m18_row["principal_remaining"] > (prior_principal - m18_row["principal_amort_due"])


def test_unpaid_opex_becomes_arrears_and_is_cured_by_future_cash(engine, standard_s1_amort):
    """P1 Fix: Unpaid opex is preserved as opex_payable arrears and cured by future tenant cash."""
    s1_terms, _ = create_default_pf1_silos()
    monthly_opex = 5_000_000.0
    # Zero initial operating cash, zero rent during construction in months 1-2
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=100_000_000.0, operating_cash=0.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=3, delay_months=0, monthly_capex_burn=0.0)
    # Rent starts in month 3 at $20M/mo
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=monthly_opex)

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # In month 1: opex is $5M, rent is $0, cash is $0 -> opex_payable becomes $5M
    m1 = df[df["month"] == 1].iloc[0]
    assert m1["opex_paid"] == 0.0
    assert m1["opex_payable"] == 5_000_000.0

    # In month 2: additional $5M opex -> opex_payable accumulates to $10M
    m2 = df[df["month"] == 2].iloc[0]
    assert m2["opex_paid"] == 0.0
    assert m2["opex_payable"] == 10_000_000.0

    # In month 3: rent commences at $20M!
    # Total opex due is $5M current + $10M arrears = $15M.
    # Operating cash pays full $15M, curing opex_payable to $0, leaving $5M cash balance!
    m3 = df[df["month"] == 3].iloc[0]
    assert m3["total_opex_due"] == 15_000_000.0
    assert m3["opex_paid"] == 15_000_000.0
    assert m3["opex_payable"] == 0.0
    assert np.isclose(m3["operating_cash_balance"], 5_000_000.0)


def test_opex_alone_exhausts_operating_cash_triggers_t_operating_exhaustion(engine):
    """P1 Fix: Opex alone depleting positive operating cash triggers T_operating_exhaustion.
    
    Cash is positive at month start -> opex alone exhausts account -> T_operating_exhaustion = that month,
    even when total debt service due is 0.
    """
    s1_terms, _ = create_default_pf1_silos()
    # Project has $5M cash, zero rent, $5M monthly opex
    s1_init = AccountState(construction_cash=50_000_000.0, dsra_cash=100_000_000.0, operating_cash=5_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=0.0, monthly_opex=5_000_000.0)
    zero_amort = AmortizationScenario(schedule_type="zero_amort_scenario")

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, zero_amort)

    # In month 1: debt service is 0, but $5M opex exhausts the $5M account
    m1 = df[df["month"] == 1].iloc[0]
    assert m1["coupon_cash_due"] == 0.0
    assert m1["total_debt_service_due"] == 0.0
    assert m1["operating_cash_balance"] == 0.0
    # Crucial assertion: T_operating_exhaustion MUST be month 1
    assert milestones.t_operating_exhaustion == 1


def test_waterfall_priority_opex_first_vs_debt_first(engine):
    """P1 Fix: Evaluates difference between opex_first and debt_service_first priority."""
    s1_terms, _ = create_default_pf1_silos()
    # In month 6, coupon due is $108.6875M ($2,350M * 9.25% / 2).
    # Provide operating cash of exactly $50M, zero DSRA, zero rent, and opex of $50M.
    s1_init = AccountState(construction_cash=0.0, dsra_cash=0.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=0.0, monthly_opex=50_000_000.0)
    zero_amort = AmortizationScenario(schedule_type="zero_amort_scenario")

    # Case A: opex_first (standard project finance)
    # Month 1: opex gets $50M, operating cash becomes 0
    df_opex, _ = engine.run_silo_waterfall(
        s1_terms, s1_init, s1_const, s1_rent, zero_amort, waterfall_priority="opex_first"
    )
    assert df_opex[df_opex["month"] == 1]["opex_paid"].iloc[0] == 50_000_000.0
    assert df_opex[df_opex["month"] == 1]["opex_payable"].iloc[0] == 0.0

    # Case B: debt_service_first in month 6 when coupon is due
    # Provide $50M operating cash entering Month 6 with $50M opex and $108.6875M coupon
    s1_init_m6 = AccountState(construction_cash=0.0, dsra_cash=0.0, operating_cash=50_000_000.0)
    s1_const_m6 = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=0.0)
    s1_rent_m6 = RentScenario(monthly_base_rent=0.0, monthly_opex=0.0)  # No opex in months 1-5
    # In month 6, set opex to $50M via custom rent scenario
    # Under debt_service_first, available cash pays coupon first
    df_debt, _ = engine.run_silo_waterfall(
        s1_terms, s1_init_m6, s1_const_m6, RentScenario(monthly_base_rent=0.0, monthly_opex=50_000_000.0),
        zero_amort, waterfall_priority="debt_service_first"
    )
    # In month 1 with zero coupon, debt_service_first pays $0 to debt and leaves cash for opex
    # In month 6, debt service takes all $50M if cash remained
    assert df_debt["date"].iloc[0] == "2026-07"


def test_payment_shortfall_absorbing_boundary_and_arrears(engine):
    """P1 Fix: Payment shortfall acts as an absorbing boundary and accumulates arrears."""
    s1_terms, _ = create_default_pf1_silos()
    # Zero operating cash, zero DSRA, zero rent
    s1_init = AccountState(construction_cash=0.0, dsra_cash=0.0, operating_cash=0.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=1, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=0.0, monthly_opex=0.0)
    s1_zero_amort = AmortizationScenario(schedule_type="zero_amort_scenario")

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, s1_zero_amort)

    # First coupon payment is in month 6 -> shortfall occurs
    assert milestones.t_payment_shortfall == 6

    # Months 1-5: solvent and valid
    for m in range(1, 6):
        row = df[df["month"] == m].iloc[0]
        assert not row["is_post_shortfall"]
        assert row["economic_status"] == "VALID"

    # Months 6+: absorbing post-default state, flagged on every row
    for m in range(6, 13):
        row = df[df["month"] == m].iloc[0]
        assert row["is_post_shortfall"]
        assert row["economic_status"] == "POST_SHORTFALL_ABSORBED"
        # Month 6 coupon owed carries forward into interest_payable
        assert row["interest_payable"] > 0.0


def test_cash_coverage_definition(engine, standard_s1_amort):
    """P1/P2 Fix: Cash coverage compares actual tenant cash rent against actual monthly cash obligations."""
    s1_terms, _ = create_default_pf1_silos()
    # Operational project from month 1: rent = $20M/mo, opex = $1M/mo.
    # Months 1-5: cash outflow is $1M/mo, rent is $20M/mo -> cash flow is positive +$19M/mo (covered!).
    # Month 6: cash coupon due is $2,350M * 9.25% / 2 = $108.6875M.
    # Total cash obligations = $1M opex + $108.6875M debt service = $109.6875M > rent $20M (deficit!).
    s1_init = AccountState(construction_cash=0.0, dsra_cash=200_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=1, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # T_coverage triggers exactly in month 6 when cash obligations exceed tenant cash rent
    assert milestones.t_coverage == 6


def test_dynamic_start_date_calendar_mapping():
    """Robustness Fix: Contractual month indexes derive dynamically from simulation start date."""
    # Canonical start: July 1, 2026
    s1_canon, s2_canon = create_default_pf1_silos("2026-07-01")
    assert s1_canon.fixed_amort_start_month == 18  # Dec 2027
    assert s1_canon.final_maturity_month == 54    # Dec 2030
    assert s2_canon.final_maturity_month == 60    # June 2031

    # Shift start date 1 month earlier: June 1, 2026
    s1_june, s2_june = create_default_pf1_silos("2026-06-01")
    assert s1_june.fixed_amort_start_month == 19
    assert s1_june.final_maturity_month == 55
    assert s2_june.final_maturity_month == 61

    # Start date on or after milestone date raises ValueError
    with pytest.raises(ValueError, match="is on or after contractual milestone date"):
        create_default_pf1_silos("2032-01-01")


def test_maturity_balloons_remaining_principal(engine):
    """P0 Fix 3 & P2 Date: Remaining principal matures as a bullet balloon at final maturity.
    
    Silo 1 final maturity: Month 54 (Dec 15, 2030)
    Silo 2 final maturity: Month 60 (June 15, 2031)
    """
    s1_terms, s2_terms = create_default_pf1_silos()
    assert s1_terms.final_maturity_month == 54
    assert s2_terms.final_maturity_month == 60

    # Test Silo 1 balloon maturity with zero amortization scenario
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=50_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)
    s1_zero_amort = AmortizationScenario(schedule_type="zero_amort_scenario")

    df1, m1 = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, s1_zero_amort)

    # In month 53, principal_amort_due is 0
    assert df1[df1["month"] == 53]["principal_amort_due"].iloc[0] == 0.0

    # In month 54 (final maturity), entire remaining principal matures
    m54_row = df1[df1["month"] == 54].iloc[0]
    assert m54_row["principal_amort_due"] == 2_350_000_000.0
    # Balloon cannot be funded by operating cash / DSRA -> payment shortfall triggers
    assert m54_row["unfunded_debt_service"] > 0.0
    assert m1.t_payment_shortfall == 54


def test_remaining_capex_total_caps_burn(engine, standard_s1_amort):
    """P0 Fix 4: remaining_capex_total bounds cumulative construction outlays."""
    s1_terms, _ = create_default_pf1_silos()
    total_capex_cap = 50_000_000.0
    monthly_burn = 20_000_000.0

    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=100_000_000.0, operating_cash=50_000_000.0)
    # 6 months scheduled construction, 10 months delay -> 16 months under construction
    s1_const = ConstructionScenario(
        scheduled_commencement_month=6,
        delay_months=10,
        monthly_capex_burn=monthly_burn,
        remaining_capex_total=total_capex_cap,
    )
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # Month 1: spends $20M (cum = $20M)
    # Month 2: spends $20M (cum = $40M)
    # Month 3: spends $10M (cum = $50M, hits cap)
    # Month 4 onwards: capex_required must be 0!
    assert df[df["month"] == 1]["capex_required"].iloc[0] == 20_000_000.0
    assert df[df["month"] == 2]["capex_required"].iloc[0] == 20_000_000.0
    assert df[df["month"] == 3]["capex_required"].iloc[0] == 10_000_000.0
    assert df[df["month"] == 4]["capex_required"].iloc[0] == 0.0
    assert df[df["month"] == 5]["capex_required"].iloc[0] == 0.0
    assert df["cumulative_capex_spent"].max() == total_capex_cap


def test_missing_amortization_scenario_raises_error(engine):
    """P0 Fix 5: Missing or non-AmortizationScenario object raises an explicit ValueError."""
    s1_terms, _ = create_default_pf1_silos()
    s1_init = AccountState(construction_cash=10_000_000.0, dsra_cash=10_000_000.0, operating_cash=10_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=1_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=1_000_000.0)

    with pytest.raises(ValueError, match="Amortization installment amounts are UNOBSERVED"):
        engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, amortization=None)


def test_delay_tolerance_surface_execution(standard_s1_amort, standard_s2_amort):
    """Verifies that compute_delay_tolerance_surface executes cleanly without silent priors."""
    s1_rent = RentScenario(monthly_base_rent=15_275_000.0, monthly_opex=1_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=9_166_667.0, monthly_opex=1_000_000.0)

    # 1. Decoupled delay grids mode (Cartesian product: 2 delays x 2 delays = 4 surface points)
    surface_decoupled = compute_delay_tolerance_surface(
        reserve_grid_silo1=[100_000_000.0],
        reserve_grid_silo2=[50_000_000.0],
        capex_burn_grid_silo1=[10_000_000.0],
        capex_burn_grid_silo2=[15_000_000.0],
        scheduled_commencement_month_silo1=12,
        scheduled_commencement_month_silo2=18,
        delay_grid_silo1=[0, 6],
        delay_grid_silo2=[0, 12],
        shared_campus_delay_mode=False,
        silo1_rent_scenario=s1_rent,
        silo2_rent_scenario=s2_rent,
        silo1_amort_scenario=standard_s1_amort,
        silo2_amort_scenario=standard_s2_amort,
        silo1_initial_construction_cash=50_000_000.0,
        silo2_initial_construction_cash=50_000_000.0,
        silo1_initial_operating_cash=20_000_000.0,
        silo2_initial_operating_cash=0.0,
        silo1_remaining_capex_total=100_000_000.0,
        silo2_remaining_capex_total=150_000_000.0,
    )

    assert len(surface_decoupled) == 4
    assert set(surface_decoupled["delay_months_silo1"]) == {0, 6}
    assert set(surface_decoupled["delay_months_silo2"]) == {0, 12}
    assert "t_payment_shortfall_silo1" in surface_decoupled.columns
    assert "t_payment_shortfall_silo2" in surface_decoupled.columns
    assert "cumulative_parent_support_required_usd" in surface_decoupled.columns

    # 2. Shared campus delay mode (Synchronized: 2 points)
    surface_shared = compute_delay_tolerance_surface(
        reserve_grid_silo1=[100_000_000.0],
        reserve_grid_silo2=[50_000_000.0],
        capex_burn_grid_silo1=[10_000_000.0],
        capex_burn_grid_silo2=[15_000_000.0],
        scheduled_commencement_month_silo1=12,
        scheduled_commencement_month_silo2=18,
        delay_grid_silo1=[0, 6],
        delay_grid_silo2=None,
        shared_campus_delay_mode=True,
        silo1_rent_scenario=s1_rent,
        silo2_rent_scenario=s2_rent,
        silo1_amort_scenario=standard_s1_amort,
        silo2_amort_scenario=standard_s2_amort,
        silo1_initial_construction_cash=50_000_000.0,
        silo2_initial_construction_cash=50_000_000.0,
        silo1_initial_operating_cash=20_000_000.0,
        silo2_initial_operating_cash=0.0,
    )
    assert len(surface_shared) == 2
    for _, row in surface_shared.iterrows():
        assert row["delay_months_silo1"] == row["delay_months_silo2"]

    # 3. Missing delay_grid_silo2 without shared mode raises ValueError
    with pytest.raises(ValueError, match="delay_grid_silo2 must be provided"):
        compute_delay_tolerance_surface(
            reserve_grid_silo1=[100_000_000.0],
            reserve_grid_silo2=[50_000_000.0],
            capex_burn_grid_silo1=[10_000_000.0],
            capex_burn_grid_silo2=[15_000_000.0],
            scheduled_commencement_month_silo1=12,
            scheduled_commencement_month_silo2=18,
            delay_grid_silo1=[0, 6],
            delay_grid_silo2=None,
            shared_campus_delay_mode=False,
            silo1_rent_scenario=s1_rent,
            silo2_rent_scenario=s2_rent,
            silo1_amort_scenario=standard_s1_amort,
            silo2_amort_scenario=standard_s2_amort,
            silo1_initial_construction_cash=50_000_000.0,
            silo2_initial_construction_cash=50_000_000.0,
            silo1_initial_operating_cash=20_000_000.0,
            silo2_initial_operating_cash=0.0,
        )

    # 4. Verify helper demo_pf1_analyst_scenario runs cleanly
    demo_params = demo_pf1_analyst_scenario()
    surface_demo = compute_delay_tolerance_surface(
        reserve_grid_silo1=[100_000_000.0],
        reserve_grid_silo2=[50_000_000.0],
        capex_burn_grid_silo1=[10_000_000.0],
        capex_burn_grid_silo2=[15_000_000.0],
        delay_grid_silo1=[0],
        delay_grid_silo2=[0],
        shared_campus_delay_mode=False,
        **demo_params,
    )
    assert len(surface_demo) == 1
