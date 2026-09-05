"""Algebraic representation data models and base-m polynomial generators."""

import math
from typing import List, Optional, Tuple
import gmpy2
from pydantic import BaseModel, Field


class PolynomialPair(BaseModel):
    """Pair of polynomials f1, f2 having a common root m modulo N."""

    f1_coeffs: List[int]  # [c0, c1, ..., cd] for f1(x) = sum c_i * x^i
    f2_coeffs: List[int]  # [d0, d1] for f2(x) = x - m
    m: int
    degree: int
    name: str = "base_m"

    def eval_f1(self, x: int) -> int:
        """Evaluate f1(x) using Horner's method."""
        res = 0
        for c in reversed(self.f1_coeffs):
            res = res * x + c
        return res

    def eval_f2(self, x: int) -> int:
        """Evaluate f2(x) using Horner's method."""
        res = 0
        for c in reversed(self.f2_coeffs):
            res = res * x + c
        return res


def create_base_m_representation(N: int, degree: int = 2) -> PolynomialPair:
    """Construct canonical base-m polynomial pair for N where f2(x) = x - m and f1(m) = N.

    Args:
        N: Target integer modulus.
        degree: Degree d of f1.

    Returns:
        PolynomialPair with common root m modulo N.
    """
    if degree < 1:
        raise ValueError(f"Degree must be >= 1, got {degree}")

    # m = floor(N^(1/degree))
    # Using gmpy2 for integer root
    m, _ = gmpy2.iroot(N, degree)
    m_val = int(m)
    if m_val <= 1:
        m_val = 2

    # Base-m expansion of N: N = sum_{i=0}^d c_i * m^i
    coeffs: List[int] = []
    rem_n = N
    while rem_n > 0:
        c = rem_n % m_val
        coeffs.append(int(c))
        rem_n //= m_val

    # Ensure length matches degree + 1 (pad with zeros if needed)
    while len(coeffs) <= degree:
        coeffs.append(0)

    # f2(x) = x - m -> coeffs [-m, 1]
    f2_coeffs = [-m_val, 1]

    return PolynomialPair(
        f1_coeffs=coeffs,
        f2_coeffs=f2_coeffs,
        m=m_val,
        degree=len(coeffs) - 1,
        name=f"base_m_d{degree}",
    )


def generate_systematic_representation_grid(
    N: int,
    degree: int = 3,
    translation_radius: int = 5,
    rotation_u_bound: int = 2,
    rotation_v_bound: int = 2,
) -> List[Tuple[PolynomialPair, str]]:
    """Generate the deterministic systematic grid of up to 35 representation pairs.

    Returns list of (PolynomialPair, operation_name) pairs:
    1. 1 canonical base-m pair.
    2. Up to 10 translation pairs (m' = m + k for k in [-radius, radius], k != 0).
    3. Up to 24 linear rotation pairs of the canonical base-m:
       f1(x) + (u*x + v)*(x - m) for u in [-u_bound, u_bound], v in [-v_bound, v_bound], (u,v) != (0,0).
    """
    grid: List[Tuple[PolynomialPair, str]] = []
    canonical_base = create_base_m_representation(N, degree=degree)
    grid.append((canonical_base, "canonical_base_m"))

    # Phase 1: Translations (m' = m + k)
    m = canonical_base.m
    for k in range(-translation_radius, translation_radius + 1):
        if k == 0:
            continue
        m_cand = m + k
        if m_cand <= 2:
            continue

        coeffs: List[int] = []
        rem = N
        while rem > 0:
            coeffs.append(int(rem % m_cand))
            rem //= m_cand

        while len(coeffs) <= degree:
            coeffs.append(0)

        cand = PolynomialPair(
            f1_coeffs=coeffs,
            f2_coeffs=[-m_cand, 1],
            m=m_cand,
            degree=len(coeffs) - 1,
            name=f"search_trans_{k}",
        )
        grid.append((cand, f"translation_{k}"))

    # Phase 2: Systematic linear rotations of canonical base-m:
    # f1(x) + (u*x + v)*(x - m) = f1(x) + u*x^2 + (v - u*m)*x - v*m
    base_m = canonical_base.m
    c_orig = list(canonical_base.f1_coeffs)

    for u in range(-rotation_u_bound, rotation_u_bound + 1):
        for v in range(-rotation_v_bound, rotation_v_bound + 1):
            if u == 0 and v == 0:
                continue

            c_rot = list(c_orig)
            while len(c_rot) <= max(degree, 2):
                c_rot.append(0)

            c_rot[0] += -v * base_m
            c_rot[1] += (v - u * base_m)
            if len(c_rot) > 2:
                c_rot[2] += u
            else:
                c_rot.append(u)

            while len(c_rot) > 1 and c_rot[-1] == 0:
                c_rot.pop()

            if len(c_rot) - 1 != degree:
                continue

            cand = PolynomialPair(
                f1_coeffs=c_rot,
                f2_coeffs=[-base_m, 1],
                m=base_m,
                degree=degree,
                name=f"search_rot_u{u}_v{v}",
            )
            grid.append((cand, f"rotation_u{u}_v{v}"))

    return grid

