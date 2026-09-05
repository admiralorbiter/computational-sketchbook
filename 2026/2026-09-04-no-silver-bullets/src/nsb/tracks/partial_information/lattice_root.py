"""Exact rational LLL basis reduction and Coppersmith/Howgrave-Graham small-root polynomial solver.

All reduction operations use exact rational Fraction arithmetic without IEEE-754 float conversions.
"""

from fractions import Fraction
import math
import time
from typing import List, Optional, Tuple
import gmpy2
import numpy as np


def lll_reduction(basis: List[List[Fraction]], delta: Fraction = Fraction(3, 4)) -> List[List[Fraction]]:
    """Lenstra-Lenstra-Lovasz (LLL) lattice basis reduction with incremental Gram-Schmidt updates.

    Uses exact rational Fraction arithmetic without IEEE-754 float conversions.
    Incremental updates reduce complexity from O(n^4) to O(n^2) per swap.
    """
    n = len(basis)
    if n <= 1:
        return [row[:] for row in basis]

    b = [[Fraction(val) for val in row] for row in basis]
    dim = len(b[0])

    def dot_product(v1: List[Fraction], v2: List[Fraction]) -> Fraction:
        return sum(a * b_val for a, b_val in zip(v1, v2))

    b_star: List[List[Fraction]] = []
    mu: List[List[Fraction]] = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    B: List[Fraction] = [Fraction(0) for _ in range(n)]

    for i in range(n):
        v = b[i][:]
        for j in range(i):
            m = dot_product(b[i], b_star[j]) / B[j] if B[j] != 0 else Fraction(0)
            mu[i][j] = m
            v = [v[col] - m * b_star[j][col] for col in range(dim)]
        b_star.append(v)
        B[i] = dot_product(v, v)
        mu[i][i] = Fraction(1)

    k = 1
    while k < n:
        # Exact rational size reduction
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                q = round(mu[k][j])
                b[k] = [b[k][c] - q * b[j][c] for c in range(dim)]
                for l in range(j + 1):
                    mu[k][l] -= q * mu[j][l]

        # Lovasz condition with exact rational arithmetic
        if B[k] >= (delta - mu[k][k - 1] ** 2) * B[k - 1]:
            k += 1
        else:
            # Incremental swap of b[k] and b[k-1]
            m = mu[k][k - 1]
            B_prime = B[k] + m * m * B[k - 1]
            mu_prime = m * B[k - 1] / B_prime if B_prime != 0 else Fraction(0)

            # Update orthogonal vectors b_star[k-1] and b_star[k]
            b_star_prev = b_star[k - 1][:]
            b_star_curr = b_star[k][:]
            b_star[k - 1] = [b_star_curr[c] + m * b_star_prev[c] for c in range(dim)]
            b_star[k] = (
                [-mu_prime * b_star_curr[c] + (B[k] / B_prime) * b_star_prev[c] for c in range(dim)]
                if B_prime != 0
                else b_star_curr
            )

            B[k] = B[k - 1] * B[k] / B_prime if B_prime != 0 else Fraction(0)
            B[k - 1] = B_prime

            # Swap basis rows
            b[k], b[k - 1] = b[k - 1], b[k]

            # Update Gram-Schmidt coefficients mu
            for j in range(k - 1):
                mu[k - 1][j], mu[k][j] = mu[k][j], mu[k - 1][j]
            mu[k][k - 1] = mu_prime
            for i in range(k + 1, n):
                mu[i][k - 1] = dot_product(b[i], b_star[k - 1]) / B[k - 1] if B[k - 1] != 0 else Fraction(0)
                mu[i][k] = dot_product(b[i], b_star[k]) / B[k] if B[k] != 0 else Fraction(0)

            k = max(k - 1, 1)

    return b


def poly_deg(poly: List[Fraction]) -> int:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return len(poly) - 1


def poly_div_rem(p1: List[Fraction], p2: List[Fraction]) -> Tuple[List[Fraction], List[Fraction]]:
    deg1 = poly_deg(p1)
    deg2 = poly_deg(p2)
    if deg2 < 0 or (deg2 == 0 and p2[0] == 0):
        raise ZeroDivisionError()
    if deg1 < deg2:
        return [Fraction(0)], [Fraction(x) for x in p1]

    rem = [Fraction(x) for x in p1]
    quot = [Fraction(0)] * (deg1 - deg2 + 1)

    for i in range(deg1 - deg2, -1, -1):
        d_rem = poly_deg(rem)
        if d_rem == deg2 + i:
            coeff = rem[d_rem] / p2[deg2]
            quot[i] = coeff
            for j in range(deg2 + 1):
                rem[i + j] -= coeff * p2[j]
    return quot, rem


def build_sturm_chain(coeffs: List[Fraction]) -> List[List[Fraction]]:
    p0 = [Fraction(x) for x in coeffs]
    while len(p0) > 1 and p0[-1] == 0:
        p0.pop()
    if len(p0) <= 1:
        return []

    p1 = [p0[i] * i for i in range(1, len(p0))]
    chain = [p0, p1]

    while True:
        p_prev2 = chain[-2]
        p_prev1 = chain[-1]
        if poly_deg(p_prev1) <= 0:
            break
        _, rem = poly_div_rem(p_prev2, p_prev1)
        if poly_deg(rem) < 0 or all(x == 0 for x in rem):
            break
        neg_rem = [-x for x in rem]
        while len(neg_rem) > 1 and neg_rem[-1] == 0:
            neg_rem.pop()
        chain.append(neg_rem)
    return chain


def eval_poly_frac(p: List[Fraction], x: Fraction) -> Fraction:
    val = Fraction(0)
    for c in reversed(p):
        val = val * x + c
    return val


def sturm_sign_changes(chain: List[List[Fraction]], x: Fraction) -> int:
    signs = []
    for p in chain:
        val = eval_poly_frac(p, x)
        if val > 0:
            signs.append(1)
        elif val < 0:
            signs.append(-1)
    changes = 0
    for i in range(len(signs) - 1):
        if signs[i] * signs[i + 1] < 0:
            changes += 1
    return changes


def isolate_integer_roots_sturm(coeffs: List[int], X: int) -> List[int]:
    """Isolate all exact integer roots of polynomial in [-X, X] using exact rational Sturm chains."""
    frac_coeffs = [Fraction(x) for x in coeffs]
    while len(frac_coeffs) > 1 and frac_coeffs[-1] == 0:
        frac_coeffs.pop()
    if len(frac_coeffs) <= 1:
        return []

    roots = []
    if frac_coeffs[0] == 0:
        roots.append(0)
        while len(frac_coeffs) > 1 and frac_coeffs[0] == 0:
            frac_coeffs.pop(0)
        if len(frac_coeffs) <= 1:
            return roots

    chain = build_sturm_chain(frac_coeffs)
    if not chain:
        return roots

    intervals = [(-X, X)]
    isolated_intervals = []

    while intervals:
        a, b = intervals.pop()
        va = sturm_sign_changes(chain, Fraction(a))
        vb = sturm_sign_changes(chain, Fraction(b))
        roots_in_interval = va - vb
        if roots_in_interval == 0:
            continue
        if b - a <= 1:
            isolated_intervals.append((a, b))
        else:
            mid = (a + b) // 2
            intervals.append((a, mid))
            intervals.append((mid, b))

    integer_roots = set(roots)
    for a, b in isolated_intervals:
        for cand in [a, b]:
            if abs(cand) <= X and eval_poly_frac(frac_coeffs, Fraction(cand)) == 0:
                integer_roots.add(cand)

    return sorted(list(integer_roots))


def direct_residual_search_baseline(N: int, P0: int, X: int) -> Optional[int]:
    """Brute-force baseline search over |x0| <= X (for control benchmarking only)."""
    for cand in range(X + 1):
        p_cand = P0 + cand
        if p_cand > 1 and N % p_cand == 0:
            return cand
        p_cand = P0 - cand
        if p_cand > 1 and N % p_cand == 0:
            return -cand
    return None


def solve_univariate_small_root_linear(
    N: int,
    P0: int,
    X: int,
    max_seconds: Optional[float] = None,
    no_fallback: bool = True,
) -> Optional[int]:
    """Recover x0 such that (P0 + x0) divides N, where |x0| <= X.
    
    Uses exact rational Coppersmith/Howgrave-Graham lattice formulations with
    exact rational Sturm chain root isolation.
    """
    start_time = time.perf_counter()

    def check_timeout() -> bool:
        if max_seconds is not None and (time.perf_counter() - start_time) > max_seconds:
            return True
        return False

    if P0 <= 0 or X <= 0:
        return None

    basis = [
        [Fraction(N), Fraction(0), Fraction(0)],
        [Fraction(P0), Fraction(X), Fraction(0)],
        [Fraction(0), Fraction(P0 * X), Fraction(X * X)],
    ]
    reduced = lll_reduction(basis)

    for row in reduced:
        f0 = row[0]
        f1 = row[1] / Fraction(X)
        f2 = row[2] / Fraction(X * X)

        if f0.denominator != 1 or f1.denominator != 1 or f2.denominator != 1:
            continue

        c0 = f0.numerator
        c1 = f1.numerator
        c2 = f2.numerator

        if c2 == 0 and c1 == 0:
            continue

        if c2 == 0:
            if c1 != 0 and (-c0) % c1 == 0:
                cand = (-c0) // c1
                if abs(cand) <= X:
                    p_cand = P0 + cand
                    if p_cand > 1 and N % p_cand == 0:
                        return cand
        else:
            disc = c1 * c1 - 4 * c2 * c0
            if disc >= 0 and gmpy2.is_square(disc):
                s_disc = int(gmpy2.isqrt(disc))
                for num in [-c1 + s_disc, -c1 - s_disc]:
                    den = 2 * c2
                    if num % den == 0:
                        cand = num // den
                        if abs(cand) <= X:
                            p_cand = P0 + cand
                            if p_cand > 1 and N % p_cand == 0:
                                return cand

    # If dimension 3 does not recover the root, advance to dimension 5 (m=2, t=2)
    basis_5d = [
        [Fraction(N * N), Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(N * P0), Fraction(N * X), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(P0 * P0), Fraction(2 * P0 * X), Fraction(X * X), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(P0 * P0 * X), Fraction(2 * P0 * X * X), Fraction(X**3), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(P0 * P0 * X * X), Fraction(2 * P0 * X**3), Fraction(X**4)],
    ]
    reduced_5d = lll_reduction(basis_5d)

    polys_5d = []
    for r in reduced_5d:
        f = [r[i] / Fraction(X**i) for i in range(5)]
        if all(fi.denominator == 1 for fi in f):
            polys_5d.append([int(fi) for fi in f])

    def _test_poly_roots(c: List[int]) -> Optional[int]:
        roots = isolate_integer_roots_sturm(c, X)
        for cand in roots:
            p_cand = P0 + cand
            if p_cand > 1 and N % p_cand == 0:
                return cand
        return None

    # Test individual polynomials from 5D lattice
    for p_vec in polys_5d:
        if check_timeout():
            return None
        cand = _test_poly_roots(p_vec)
        if cand is not None:
            return cand

    # Test pairwise integer combinations (k1 * P_i - k2 * P_j)
    for i in range(len(polys_5d)):
        for j in range(i + 1, len(polys_5d)):
            for k1 in [1, 2, 3]:
                for k2 in [1, 2, 3]:
                    if check_timeout():
                        return None
                    comb = [k1 * polys_5d[i][idx] - k2 * polys_5d[j][idx] for idx in range(5)]
                    cand = _test_poly_roots(comb)
                    if cand is not None:
                        return cand
                    comb_add = [k1 * polys_5d[i][idx] + k2 * polys_5d[j][idx] for idx in range(5)]
                    cand = _test_poly_roots(comb_add)
                    if cand is not None:
                        return cand

    if not no_fallback:
        if check_timeout():
            return None
        return direct_residual_search_baseline(N, P0, X)

    return None
