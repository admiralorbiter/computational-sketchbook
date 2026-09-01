from app.services.supply_demand import (
    compute_linear_equilibrium,
    compute_welfare_linear,
    baseline_summary,
    apply_per_unit_tax_linear,
)


def test_closed_form_equilibrium():
    a_d, b_d, a_s, b_s = 10.0, 1.0, 2.0, 1.0
    p_star, q_star = compute_linear_equilibrium(a_d, b_d, a_s, b_s)
    assert abs(p_star - 6.0) < 1e-9
    assert abs(q_star - 4.0) < 1e-9


def test_welfare_triangles():
    a_d, b_d, a_s, b_s = 10.0, 1.0, 2.0, 1.0
    p_star, q_star = compute_linear_equilibrium(a_d, b_d, a_s, b_s)
    cs, ps, p_int_d, p_int_s = compute_welfare_linear(a_d, b_d, a_s, b_s, p_star, q_star)
    # Demand intercept: 10, Supply intercept: 2
    assert abs(p_int_d - 10.0) < 1e-9
    assert abs(p_int_s - 2.0) < 1e-9
    # CS triangle: 0.5 * (10 - 6) * 4 = 8
    # PS triangle: 0.5 * (6 - 2) * 4 = 8
    assert abs(cs - 8.0) < 1e-9
    assert abs(ps - 8.0) < 1e-9


def test_tax_monotonicity_and_dwl():
    a_d, b_d, a_s, b_s = 10.0, 1.0, 2.0, 1.0
    base = baseline_summary(a_d, b_d, a_s, b_s)
    out_lo = apply_per_unit_tax_linear(a_d, b_d, a_s, b_s, 0.5)
    out_hi = apply_per_unit_tax_linear(a_d, b_d, a_s, b_s, 1.0)
    assert out_lo.quantity <= base.quantity_star
    assert out_hi.quantity <= out_lo.quantity
    assert out_lo.deadweight_loss <= out_hi.deadweight_loss


