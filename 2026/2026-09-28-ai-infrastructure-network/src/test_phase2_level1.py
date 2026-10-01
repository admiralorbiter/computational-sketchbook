"""Test Suite for Phase 2 Level 1 Deterministic Delay Engine (Hardened).

Verifies core contractual, legal, financial, and accounting invariants:
1. Strict Silo Isolation: Zero cash transfer or dependency between Silo 1 and Silo 2.
2. Exact Fixed Coupon Arithmetic: Coupon equals beginning principal * rate.
3. Silo 1 Amortization Boundary: Amortization strictly barred before Dec 15, 2027 (Month 18).
4. Silo 2 State-Dependent Amortization: Amortization start date shifts dynamically with commencement.
5. Construction Support Isolation: Parent completion support only funds capex shortfalls, never debt service.
6. DSRA Restriction: DSRA can only fund permitted debt-service uses, never capex.
7. Independent Milestones: T_completion_support triggers independently of T_DSRA or T_coverage.
8. Non-Monotonic Amortization Offset: Delay defers Silo 2 principal amortization, reducing near-term cash drain.
9. Parent Overlay Summation: Parent support sums strictly after independent silo waterfalls.
10. Paid-Only Principal Reduction: Unpaid scheduled amortization does NOT reduce outstanding principal balance.
11. Opex Direct Cash Reduction: Opex depletes operating cash account directly even when tenant rent is zero.
12. Final Maturity Balloon: Remaining principal matures as a bullet balloon at final maturity (Month 54 for Silo 1, Month 60 for Silo 2).
13. Bounded Cumulative Capex: remaining_capex_total caps total cumulative construction outlays.
14. Explicit Amortization Requirement: Missing or invalid AmortizationScenario raises an explicit ValueError.
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
    compute_delay_tolerance_surface,
)


@pytest.fixture
def engine():
    return DeterministicDelayEngine(simulation_months=60, start_date="2026-07-01")


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

    # Verify dynamic postponement of amortization
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


def test_non_monotonic_amortization_offset(engine, standard_s2_amort):
    """Invariant 8: Delay in Silo 2 defers scheduled principal amortization, moderating near-term cash drain.
    
    Demonstrates that in month 18, Silo 2 debt service is LOWER under 6 months of delay
    because principal amortization has been postponed.
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

    # Delayed project owes LESS total debt service in month 18 than the on-time project!
    assert debt_service_m18_delayed < debt_service_m18_early
    # The difference is exactly the deferred principal amortization
    amort_early = df_early[df_early["month"] == 18]["principal_amort_due"].iloc[0]
    amort_delayed = df_delayed[df_delayed["month"] == 18]["principal_amort_due"].iloc[0]
    assert amort_early > 0.0
    assert amort_delayed == 0.0


# =========================================================================
# P0 ACCOUNTING REGRESSION TESTS
# =========================================================================

def test_unpaid_principal_remains_outstanding(engine):
    """P0 Fix 1: Unpaid scheduled principal amortization does NOT reduce principal balance.
    
    Only cash actually paid towards principal reduces the outstanding note balance.
    """
    s1_terms, _ = create_default_pf1_silos()
    # Set up Silo 1 with insufficient operating cash and zero DSRA at amortization start (month 18)
    s1_init = AccountState(construction_cash=50_000_000.0, dsra_cash=0.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=0.0)
    # Rent is $50M/mo, enough for coupon ($108.6875M semiannual) but NOT enough for both coupon + $391.67M principal amort
    s1_rent = RentScenario(monthly_base_rent=50_000_000.0, monthly_opex=0.0)
    
    # Large amortization due of $500M in month 18
    s1_amort = AmortizationScenario(
        schedule_type="custom_schedule",
        custom_schedule_by_month={18: 500_000_000.0},
    )

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, s1_amort)

    m18_row = df[df["month"] == 18].iloc[0]
    assert m18_row["principal_amort_due"] == 500_000_000.0
    assert m18_row["unpaid_principal_amort"] > 0.0  # Cannot fully pay $500M
    
    # Crucial assertion: principal_remaining is reduced ONLY by principal_amort_paid, NOT principal_amort_due
    prior_principal = df[df["month"] == 17]["principal_remaining"].iloc[0]
    assert np.isclose(m18_row["principal_remaining"], prior_principal - m18_row["principal_amort_paid"])
    assert m18_row["principal_remaining"] > (prior_principal - m18_row["principal_amort_due"])


def test_opex_reduces_cash_when_rent_zero(engine, standard_s1_amort):
    """P0 Fix 2: Opex reduces operating cash directly even when tenant rent is zero."""
    s1_terms, _ = create_default_pf1_silos()
    initial_oper = 25_000_000.0
    monthly_opex = 5_000_000.0
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=100_000_000.0, operating_cash=initial_oper)
    # Project is under construction through month 12, rent = 0
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=monthly_opex)

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent, standard_s1_amort)

    # In month 1, operating cash must decrease from $25M to $20M
    m1_row = df[df["month"] == 1].iloc[0]
    assert m1_row["tenant_rent"] == 0.0
    assert m1_row["opex_paid"] == monthly_opex
    assert np.isclose(m1_row["operating_cash_balance"], initial_oper - monthly_opex)

    # In month 2, operating cash must decrease to $15M
    m2_row = df[df["month"] == 2].iloc[0]
    assert np.isclose(m2_row["operating_cash_balance"], initial_oper - (2 * monthly_opex))


def test_maturity_balloons_remaining_principal(engine):
    """P0 Fix 3: Remaining principal matures as a bullet balloon at final maturity.
    
    Silo 1 final maturity: Month 54 (Dec 15, 2030)
    Silo 2 final maturity: Month 60 (June 16, 2031)
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
    """Verifies that compute_delay_tolerance_surface executes cleanly without synthetic defaults."""
    s1_rent = RentScenario(monthly_base_rent=15_275_000.0, monthly_opex=1_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=9_166_667.0, monthly_opex=1_000_000.0)

    surface = compute_delay_tolerance_surface(
        reserve_grid_silo1=[100_000_000.0],
        reserve_grid_silo2=[50_000_000.0],
        capex_burn_grid_silo1=[10_000_000.0],
        capex_burn_grid_silo2=[15_000_000.0],
        delay_months_grid=[0, 6],
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

    assert len(surface) == 2
    assert "t_payment_shortfall_silo1" in surface.columns
    assert "t_payment_shortfall_silo2" in surface.columns
    assert "cumulative_parent_support_required_usd" in surface.columns
