"""Test Suite for Phase 2 Level 1 Deterministic Delay Engine.

Verifies the 9 core contractual, legal, and financial invariants:
1. Strict Silo Isolation: Zero cash transfer or dependency between silos.
2. Exact Fixed Coupon Arithmetic: Coupon equals beginning principal * rate.
3. Silo 1 Amortization Boundary: Amortization strictly barred before Dec 15, 2027.
4. Silo 2 State-Dependent Amortization: Amortization start date shifts dynamically with commencement.
5. Construction Support Isolation: Parent completion support only funds capex shortfalls, not debt service.
6. DSRA Restriction: DSRA can only fund permitted debt-service uses, never capex.
7. Independent Milestones: T_completion_support triggers independently of T_DSRA or T_coverage.
8. Non-Monotonic Amortization Offset: Delay defers Silo 2 principal amortization, reducing near-term cash drain.
9. Parent Overlay Summation: Parent support sums strictly after independent silo waterfalls.
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
    create_default_pf1_silos,
)


@pytest.fixture
def engine():
    return DeterministicDelayEngine(simulation_months=60, start_date="2026-07-01")


def test_strict_silo_isolation(engine):
    """Invariant 1: Silo 1's cash ledger must be mathematically invariant to changes in Silo 2."""
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=150_000_000.0, operating_cash=20_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=3, monthly_capex_burn=10_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=15_000_000.0, monthly_opex=1_000_000.0)

    # Run Case A: Silo 2 has standard parameters
    s2_init_A = AccountState(construction_cash=150_000_000.0, dsra_cash=100_000_000.0, operating_cash=0.0)
    s2_const_A = ConstructionScenario(scheduled_commencement_month=18, delay_months=0, monthly_capex_burn=20_000_000.0)
    s2_rent_A = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=1_000_000.0)
    res_A = engine.run_pf1_simulation(s1_init, s2_init_A, s1_const, s2_const_A, s1_rent, s2_rent_A)

    # Run Case B: Silo 2 has extreme stress parameters (zero cash, huge burn, massive delay)
    s2_init_B = AccountState(construction_cash=0.0, dsra_cash=0.0, operating_cash=0.0)
    s2_const_B = ConstructionScenario(scheduled_commencement_month=18, delay_months=24, monthly_capex_burn=100_000_000.0)
    s2_rent_B = RentScenario(monthly_base_rent=0.0, monthly_opex=10_000_000.0)
    res_B = engine.run_pf1_simulation(s1_init, s2_init_B, s1_const, s2_const_B, s1_rent, s2_rent_B)

    # Assert Silo 1 columns in ledger are identical between Case A and Case B
    silo1_cols = [c for c in res_A.monthly_ledger.columns if c.endswith("_silo1")]
    for col in silo1_cols:
        pd.testing.assert_series_equal(
            res_A.monthly_ledger[col],
            res_B.monthly_ledger[col],
            check_names=True,
            obj=f"Silo isolation breached on column {col}",
        )


def test_fixed_coupon_arithmetic(engine):
    """Invariant 2: Monthly interest accrual must exactly equal remaining principal * coupon / 12."""
    s1_init = AccountState(construction_cash=50_000_000.0, dsra_cash=100_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=5_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)
    s1_terms, _ = create_default_pf1_silos()

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent)

    for _, row in df.iterrows():
        # Accrual basis check
        beginning_principal = row["principal_remaining"] + row["principal_amort_due"]
        expected_monthly = beginning_principal * (s1_terms.annual_coupon_rate / 12.0)
        assert np.isclose(row["monthly_interest_accrual"], expected_monthly, atol=1e-2)

        # Semiannual payment month check
        if row["date"].endswith("-06") or row["date"].endswith("-12"):
            expected_cash = beginning_principal * (s1_terms.annual_coupon_rate / 2.0)
            assert np.isclose(row["coupon_cash_due"], expected_cash, atol=1e-2)
        else:
            assert row["coupon_cash_due"] == 0.0


def test_silo1_amortization_boundary(engine):
    """Invariant 3: Silo 1 principal amortization cannot begin before December 15, 2027 (month 18)."""
    s1_terms, _ = create_default_pf1_silos()
    s1_init = AccountState(construction_cash=100_000_000.0, dsra_cash=200_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=1_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=25_000_000.0, monthly_opex=1_000_000.0)

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent)

    # Prior to month 18, amortization must be zero
    pre_18_amort = df[df["month"] < 18]["principal_amort_due"].sum()
    assert pre_18_amort == 0.0

    # In month 18 (Dec 2027), amortization must be positive
    month_18_amort = df[df["month"] == 18]["principal_amort_due"].iloc[0]
    assert month_18_amort > 0.0


def test_silo2_state_dependent_amortization(engine):
    """Invariant 4: Silo 2 amortization start date shifts dynamically with commencement delay."""
    _, s2_terms = create_default_pf1_silos()
    s2_init = AccountState(construction_cash=200_000_000.0, dsra_cash=150_000_000.0, operating_cash=50_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)

    # Case 1: Scheduled commencement at month 12 (June 2027), 0 delay.
    # First payment date after June 2027 is Dec 2027 (month 18).
    const_early = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=5_000_000.0)
    df_early, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_early, s2_rent)
    amort_early_start = df_early[df_early["principal_amort_due"] > 0]["month"].iloc[0]
    assert amort_early_start == 18

    # Case 2: 6 months of delay -> actual commencement is month 18 (Dec 2027).
    # First payment date after Dec 2027 is June 2028 (month 24).
    const_delayed = ConstructionScenario(scheduled_commencement_month=12, delay_months=6, monthly_capex_burn=5_000_000.0)
    df_delayed, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_delayed, s2_rent)
    amort_delayed_start = df_delayed[df_delayed["principal_amort_due"] > 0]["month"].iloc[0]
    assert amort_delayed_start == 24

    # Verify dynamic postponement of amortization
    assert amort_delayed_start > amort_early_start


def test_completion_support_independent_of_dsra(engine):
    """Invariant 7: T_completion_support triggers independently of T_DSRA.
    
    A project with zero construction funds but full DSRA triggers parent completion
    support immediately in month 1, while DSRA remains 100% untouched.
    """
    s1_terms, _ = create_default_pf1_silos()
    # Zero construction cash, large DSRA, large operating cash
    s1_init = AccountState(construction_cash=0.0, dsra_cash=200_000_000.0, operating_cash=100_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=15_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=20_000_000.0, monthly_opex=1_000_000.0)

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent)

    # Completion support required immediately in month 1
    assert milestones.t_completion_support == 1
    # But operating cash is large, so DSRA is not touched in month 1
    assert df["dsra_draw"].iloc[0] == 0.0
    assert milestones.t_dsra is None or milestones.t_dsra > 1


def test_completion_support_does_not_fund_debt_service(engine):
    """Invariant 5: Parent completion support only funds capex shortfalls, not debt service."""
    s1_terms, _ = create_default_pf1_silos()
    # Zero operating cash, zero DSRA, zero construction cash, but project is operational (zero capex required)
    s1_init = AccountState(construction_cash=0.0, dsra_cash=0.0, operating_cash=0.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=1, delay_months=0, monthly_capex_burn=0.0)
    s1_rent = RentScenario(monthly_base_rent=0.0, monthly_opex=0.0)  # No rent

    df, milestones = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent)

    # In month 6 (first coupon payment date), debt service is due with zero cash
    month_6 = df[df["month"] == 6].iloc[0]
    assert month_6["coupon_cash_due"] > 0
    # Payment default triggers
    assert milestones.t_payment_default == 6
    # Parent completion support is strictly 0 because capex required is 0
    assert month_6["parent_completion_support_required"] == 0.0


def test_dsra_restriction(engine):
    """Invariant 6: DSRA funds cannot be drawn for capex construction shortfalls."""
    s1_terms, _ = create_default_pf1_silos()
    # Full DSRA, zero construction cash, high capex burn
    s1_init = AccountState(construction_cash=0.0, dsra_cash=100_000_000.0, operating_cash=50_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=20_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=0.0)

    df, _ = engine.run_silo_waterfall(s1_terms, s1_init, s1_const, s1_rent)

    # Month 1 has $20M capex required and $0 construction cash.
    # DSRA must NOT be drawn for capex.
    month_1 = df[df["month"] == 1].iloc[0]
    assert month_1["parent_completion_support_required"] == 20_000_000.0
    assert month_1["dsra_draw"] == 0.0
    assert month_1["dsra_balance"] == 100_000_000.0


def test_parent_support_funding_summation(engine):
    """Invariant 9: Total parent support is strictly the post-waterfall sum of silo1 and silo2."""
    s1_init = AccountState(construction_cash=10_000_000.0, dsra_cash=50_000_000.0, operating_cash=10_000_000.0)
    s2_init = AccountState(construction_cash=20_000_000.0, dsra_cash=50_000_000.0, operating_cash=10_000_000.0)
    s1_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=15_000_000.0)
    s2_const = ConstructionScenario(scheduled_commencement_month=6, delay_months=0, monthly_capex_burn=25_000_000.0)
    s1_rent = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=1_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=10_000_000.0, monthly_opex=1_000_000.0)

    res = engine.run_pf1_simulation(s1_init, s2_init, s1_const, s2_const, s1_rent, s2_rent)
    ledger = res.monthly_ledger

    sum_cols = ledger["parent_completion_support_required_silo1"] + ledger["parent_completion_support_required_silo2"]
    assert np.allclose(ledger["total_parent_completion_support"], sum_cols)


def test_non_monotonic_amortization_offset(engine):
    """Invariant 8: Delay in Silo 2 defers scheduled principal amortization, moderating near-term cash drain.
    
    Demonstrates that in month 18, Silo 2 debt service is LOWER under 6 months of delay
    because principal amortization has been postponed.
    """
    _, s2_terms = create_default_pf1_silos()
    s2_init = AccountState(construction_cash=100_000_000.0, dsra_cash=100_000_000.0, operating_cash=100_000_000.0)
    s2_rent = RentScenario(monthly_base_rent=15_000_000.0, monthly_opex=1_000_000.0)

    # Early commencement (month 12) -> amortization active by month 18
    const_early = ConstructionScenario(scheduled_commencement_month=12, delay_months=0, monthly_capex_burn=5_000_000.0)
    df_early, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_early, s2_rent)
    debt_service_m18_early = df_early[df_early["month"] == 18]["total_debt_service_due"].iloc[0]

    # Delayed commencement (month 12 + 6 = month 18) -> amortization deferred to month 24
    const_delayed = ConstructionScenario(scheduled_commencement_month=12, delay_months=6, monthly_capex_burn=5_000_000.0)
    df_delayed, _ = engine.run_silo_waterfall(s2_terms, s2_init, const_delayed, s2_rent)
    debt_service_m18_delayed = df_delayed[df_delayed["month"] == 18]["total_debt_service_due"].iloc[0]

    # Delayed project owes LESS total debt service in month 18 than the on-time project!
    assert debt_service_m18_delayed < debt_service_m18_early
    # The difference is exactly the deferred principal amortization
    amort_early = df_early[df_early["month"] == 18]["principal_amort_due"].iloc[0]
    amort_delayed = df_delayed[df_delayed["month"] == 18]["principal_amort_due"].iloc[0]
    assert amort_early > 0.0
    assert amort_delayed == 0.0
