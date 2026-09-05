"""Murphy's alpha, size property, and Kleinjung-style NFS polynomial selection.

Implements standard Number Field Sieve (NFS) polynomial ranking metrics:
- Projective root counts and Murphy's alpha(f)
- Optimal skew estimation
- Murphy's E rating combining size and root properties
- Kleinjung/Murphy baseline polynomial selector
"""

import math
from typing import Any, Dict, List, Optional, Tuple
import gmpy2
from pydantic import BaseModel

from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
)


def count_projective_roots_mod_p(coeffs: List[int], p: int) -> int:
    """Count the number of projective roots of f(x) = sum c_i * x^i in P^1(F_p).

    Affine roots: r in {0, ..., p-1} such that f(r) == 0 (mod p).
    Projective root at infinity: 1 if p divides the leading coefficient c_d, else 0.
    """
    d = len(coeffs) - 1
    if d <= 0:
        return 0

    # Projective root at infinity: c_d == 0 (mod p)
    root_at_inf = 1 if (coeffs[-1] % p == 0) else 0

    # Count affine roots
    affine_roots = 0
    for r in range(p):
        # Horner evaluation mod p
        val = 0
        for c in reversed(coeffs):
            val = (val * r + c) % p
        if val == 0:
            affine_roots += 1

    return affine_roots + root_at_inf


def compute_murphy_alpha(coeffs: List[int], prime_bound: int = 2000) -> float:
    """Compute Murphy's alpha(f) measuring logarithmic root smoothness bias.

    alpha(f) = sum_{p <= B} (1/(p-1) - n_p(f)/(p+1)) * (log(p) / p)
    Negative values indicate that f(x) has more roots mod small primes than average,
    yielding smaller smooth cofactors and higher smoothness yield.
    """
    if len(coeffs) < 2:
        return 0.0

    total_alpha = 0.0
    p = 2
    while p <= prime_bound:
        np = count_projective_roots_mod_p(coeffs, p)
        # Expected roots for a random polynomial is 1
        # Contribution: (1/(p - 1) - np / (p + 1)) * (log(p) / p)
        contrib = (1.0 / (p - 1) - float(np) / (p + 1)) * (math.log(p) / p)
        total_alpha += contrib
        p = int(gmpy2.next_prime(p))

    return round(total_alpha, 5)


def estimate_optimal_skew(coeffs: List[int]) -> float:
    """Estimate optimal skew s minimizing the coefficient disparity of f(s*x, y/s)."""
    d = len(coeffs) - 1
    if d <= 1:
        return 1.0

    c0 = abs(coeffs[0])
    cd = abs(coeffs[-1])
    if c0 == 0 or cd == 0:
        return 1.0

    # Rough analytical estimate: s = (|c0| / |cd|)**(1 / (2 * d))
    ratio = c0 / cd
    skew = ratio ** (1.0 / (2.0 * d))
    return max(0.1, min(100.0, round(skew, 4)))


def dickman_rho_approx(u: float) -> float:
    """Accurate approximation of Dickman-de Bruijn rho(u) function."""
    if u <= 0.0:
        return 1.0
    if u <= 1.0:
        return 1.0
    if u <= 2.0:
        return 1.0 - math.log(u)
    if u <= 3.0:
        # Analytic integral for 2 <= u <= 3
        # rho(u) = 1 - log(u) + int_2^u log(t-1)/t dt
        # Approximation:
        return max(1e-15, (1.0 - math.log(u)) + 0.5 * (math.log(u - 1) ** 2))
    # Asymptotic approximation for u > 3
    # rho(u) ~ (1 / sqrt(2*pi*u)) * exp(-u * xi + int_0^xi (exp(t)-1)/t dt)
    # Practical De Bruijn bound: rho(u) ~ u^(-u)
    return max(1e-15, math.exp(-u * (math.log(u) + math.log(math.log(u)) - 1.0)))


def compute_murphy_e(
    pair: PolynomialPair,
    factor_base_bound: int = 250,
    alpha_bound: int = 2000,
    sample_points: int = 100,
) -> Dict[str, Any]:
    """Compute Murphy's E(f1, f2) rating combining size and root properties.

    E measures the expected simultaneous smoothness probability over the sieve rectangle.
    """
    alpha1 = compute_murphy_alpha(pair.f1_coeffs, prime_bound=alpha_bound)
    alpha2 = compute_murphy_alpha(pair.f2_coeffs, prime_bound=min(500, alpha_bound))
    skew = estimate_optimal_skew(pair.f1_coeffs)

    log_b = math.log(factor_base_bound)
    d1 = pair.degree
    c1 = pair.f1_coeffs

    total_rho_prod = 0.0
    valid_samples = 0

    # Sample coprime pairs scaled by skew
    bound_b = 10
    bound_a = 50
    for b in range(1, bound_b + 1):
        for a in range(-bound_a, bound_a + 1):
            if a == 0 or math.gcd(abs(a), b) != 1:
                continue

            # Skew-adjusted coordinates
            x = a * skew
            y = b / skew

            # Homogeneous values
            v1 = abs(sum(coeff * (x ** i) * (y ** (d1 - i)) for i, coeff in enumerate(c1)))
            v2 = abs(a - b * pair.m)

            if v1 <= 1 or v2 <= 1:
                continue

            # Size + root adjusted smoothness parameter u
            u1 = max(1.0, (math.log(v1) + alpha1) / log_b)
            u2 = max(1.0, (math.log(v2) + alpha2) / log_b)

            rho1 = dickman_rho_approx(u1)
            rho2 = dickman_rho_approx(u2)

            total_rho_prod += rho1 * rho2
            valid_samples += 1

    murphy_e = total_rho_prod / valid_samples if valid_samples > 0 else 0.0

    return {
        "murphy_e": murphy_e,
        "alpha_f1": alpha1,
        "alpha_f2": alpha2,
        "optimal_skew": skew,
        "valid_samples": valid_samples,
    }


def select_in_house_murphy_e_baseline(
    N: int,
    degree: int = 3,
    translation_radius: int = 5,
    rotation_u_bound: int = 2,
    rotation_v_bound: int = 2,
    budget: int = 50,
) -> Tuple[PolynomialPair, Dict[str, Any]]:
    """Construct the symmetrical in-house Murphy-E NFS baseline polynomial pair.

    Searches the identical systematic 35-representation space (canonical base-m +
    10 translations + 24 linear rotations) evaluated by FrozenSearchOptimizer,
    selecting the pair that maximizes Murphy's E score.
    """
    from nsb.tracks.algebraic_evolution.representation import generate_systematic_representation_grid
    from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator

    grid = generate_systematic_representation_grid(
        N,
        degree=degree,
        translation_radius=translation_radius,
        rotation_u_bound=rotation_u_bound,
        rotation_v_bound=rotation_v_bound,
    )

    evaluator = AlgebraicEvaluator()
    canonical_base, _ = grid[0]
    best_pair = canonical_base
    best_stats = compute_murphy_e(canonical_base)
    best_e = best_stats["murphy_e"]
    best_op = "canonical_base_m"

    evals_count = 0
    evaluated_ops: List[str] = []
    for cand, op_name in grid:
        if evals_count >= budget:
            break

        is_valid, _ = evaluator.validate_b0(cand, N)
        if not is_valid:
            continue

        evaluated_ops.append(op_name)
        stats = compute_murphy_e(cand)
        evals_count += 1

        if stats["murphy_e"] > best_e:
            best_e = stats["murphy_e"]
            best_pair = cand
            best_stats = stats
            best_op = op_name

    best_stats["operation"] = best_op
    best_stats["evaluations_run"] = evals_count
    best_stats["evaluated_operations"] = evaluated_ops
    return best_pair, best_stats


def select_kleinjung_murphy_baseline(
    N: int,
    degree: int = 3,
    search_radius: int = 5,
) -> Tuple[PolynomialPair, Dict[str, Any]]:
    """Legacy alias: calls select_in_house_murphy_e_baseline."""
    return select_in_house_murphy_e_baseline(
        N,
        degree=degree,
        translation_radius=search_radius,
    )
