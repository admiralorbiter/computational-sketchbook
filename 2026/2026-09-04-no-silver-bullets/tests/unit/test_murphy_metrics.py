"""Tests for Murphy alpha, optimal skew, and Kleinjung baseline polynomial selection."""

from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
)
from nsb.tracks.algebraic_evolution.murphy import (
    count_projective_roots_mod_p,
    compute_murphy_alpha,
    estimate_optimal_skew,
    dickman_rho_approx,
    compute_murphy_e,
    select_kleinjung_murphy_baseline,
)


def test_count_projective_roots():
    # f(x) = x^2 - 1 has roots +1, -1 mod 5 -> 2 roots (neither is at inf since c2 = 1)
    roots = count_projective_roots_mod_p([-1, 0, 1], 5)
    assert roots == 2

    # f(x) = 5*x + 1 mod 5: leading coeff is 0 mod 5, so 1 root at inf + 0 affine roots
    roots_inf = count_projective_roots_mod_p([1, 5], 5)
    assert roots_inf == 1


def test_compute_murphy_alpha():
    # Test on simple quadratic polynomial
    alpha = compute_murphy_alpha([-1, 0, 1], prime_bound=50)
    assert isinstance(alpha, float)


def test_estimate_optimal_skew():
    # c0 = 1000, cd = 1, d = 3 -> skew approx (1000/1)^(1/6) approx 3.16
    skew = estimate_optimal_skew([1000, 100, 10, 1])
    assert 2.0 <= skew <= 5.0


def test_dickman_rho():
    assert dickman_rho_approx(0.5) == 1.0
    assert dickman_rho_approx(1.0) == 1.0
    assert 0.0 < dickman_rho_approx(2.0) < 1.0
    assert 0.0 < dickman_rho_approx(3.0) < dickman_rho_approx(2.0)


def test_compute_murphy_e():
    N = 10403
    p = create_base_m_representation(N, degree=3)
    res = compute_murphy_e(p, factor_base_bound=100, alpha_bound=100)
    assert "murphy_e" in res
    assert res["murphy_e"] >= 0.0
    assert res["valid_samples"] > 0


def test_select_kleinjung_murphy_baseline():
    N = 10403
    best_p, best_stat = select_kleinjung_murphy_baseline(N, degree=3, search_radius=2)
    assert isinstance(best_p, PolynomialPair)
    assert best_p.degree == 3
    assert best_stat["murphy_e"] > 0.0
