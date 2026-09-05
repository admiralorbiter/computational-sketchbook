"""Mathematical verifier for Number Field Sieve (NFS) polynomial pairs.

Verifies:
1. Valid degrees: d1 >= 1, d2 >= 1.
2. Non-zero leading coefficients.
3. Content coprimality: gcd(c0, ..., cd1) == 1 and gcd(Y0, ..., Yd2) == 1.
4. Algebraic validity modulo N:
   - Common root condition: f1(m) = 0 (mod N) and f2(m) = 0 (mod N).
   - Sylvester resultant condition: Res(f1, f2) = 0 (mod N).
"""

import math
from typing import List, Tuple
import gmpy2
from nsb.baselines.cado_nfs.models import NfsPolynomialPair


def compute_sylvester_resultant(f1_coeffs: List[int], f2_coeffs: List[int]) -> int:
    """Compute the integer Sylvester resultant Res(f1, f2).

    f1(x) = sum_{i=0}^p c_i x^i
    f2(x) = sum_{j=0}^q Y_j x^j
    """
    p = len(f1_coeffs) - 1
    q = len(f2_coeffs) - 1
    if p < 0 or q < 0:
        return 0

    n = p + q
    # Build Sylvester matrix of size n x n
    # Rows 0..q-1: coefficients of f1 shifted
    # Rows q..n-1: coefficients of f2 shifted
    matrix = [[0] * n for _ in range(n)]

    # f1 coefficients in descending order: c_p, c_{p-1}, ..., c_0
    f1_rev = list(reversed(f1_coeffs))
    for i in range(q):
        for j, c in enumerate(f1_rev):
            matrix[i][i + j] = c

    # f2 coefficients in descending order: Y_q, Y_{q-1}, ..., Y_0
    f2_rev = list(reversed(f2_coeffs))
    for i in range(p):
        for j, c in enumerate(f2_rev):
            matrix[q + i][i + j] = c

    # Compute determinant via Bareiss fraction-free algorithm
    return bareiss_determinant(matrix)


def bareiss_determinant(matrix: List[List[int]]) -> int:
    """Bareiss fraction-free algorithm for exact integer determinant."""
    n = len(matrix)
    if n == 0:
        return 1
    if n == 1:
        return matrix[0][0]

    # Create deep copy
    m = [row[:] for row in matrix]
    sign = 1
    prev = 1

    for k in range(n - 1):
        # Pivot if necessary
        if m[k][k] == 0:
            pivot = -1
            for r in range(k + 1, n):
                if m[r][k] != 0:
                    pivot = r
                    break
            if pivot == -1:
                return 0
            m[k], m[pivot] = m[pivot], m[k]
            sign = -sign

        diag_k = m[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                val = m[i][j] * diag_k - m[i][k] * m[k][j]
                m[i][j] = val // prev
        prev = diag_k

    return sign * m[n - 1][n - 1]


def verify_nfs_polynomial_pair(pair: NfsPolynomialPair) -> Tuple[bool, str]:
    """Perform independent mathematical verification of an NFS polynomial system."""
    # 1. Degree checks
    if pair.degree1 < 1:
        return False, f"f1 degree must be >= 1, got {pair.degree1}"
    if pair.degree2 < 1:
        return False, f"f2 degree must be >= 1, got {pair.degree2}"

    # 2. Leading coefficient checks
    if pair.f1_coeffs[-1] == 0:
        return False, "Leading coefficient of f1 cannot be zero"
    if pair.f2_coeffs[-1] == 0:
        return False, "Leading coefficient of f2 cannot be zero"

    # 3. Content checks gcd(coeffs) == 1
    c1_gcd = abs(pair.f1_coeffs[0])
    for c in pair.f1_coeffs[1:]:
        c1_gcd = math.gcd(c1_gcd, abs(c))
    if c1_gcd != 1:
        return False, f"Content of f1 is {c1_gcd} != 1 (f1 is not primitive)"

    c2_gcd = abs(pair.f2_coeffs[0])
    for c in pair.f2_coeffs[1:]:
        c2_gcd = math.gcd(c2_gcd, abs(c))
    if c2_gcd != 1:
        return False, f"Content of f2 is {c2_gcd} != 1 (f2 is not primitive)"

    # 4. Modulus compatibility checks
    if pair.N is not None:
        N = pair.N
        if N <= 1:
            return False, f"Modulus N must be > 1, got {N}"

        # 4a. Unconditional Sylvester resultant verification
        res = compute_sylvester_resultant(pair.f1_coeffs, pair.f2_coeffs)
        if res % N != 0:
            return False, f"Resultant Res(f1, f2) is not divisible by N: Res = {res} != 0 (mod {N})"

        # 4b. Common root verification if known or if f2 is linear
        m_root = pair.m
        if m_root is None and pair.degree2 == 1 and pair.f2_coeffs[1] != 0:
            try:
                y0 = pair.f2_coeffs[0]
                y1 = pair.f2_coeffs[1]
                inv_y1 = int(gmpy2.invert(y1, N))
                m_root = int((-y0 * inv_y1) % N)
            except Exception:
                m_root = None

        if m_root is not None:
            v1 = pair.eval_f1(m_root) % N
            v2 = pair.eval_f2(m_root) % N
            if v1 != 0:
                return False, f"Common root failure: f1({m_root}) = {v1} != 0 (mod {N})"
            if v2 != 0:
                return False, f"Common root failure: f2({m_root}) = {v2} != 0 (mod {N})"
        elif pair.degree1 > 1 and pair.degree2 > 1:
            # For nonlinear/nonlinear pairs, require common root or explicit construction witness
            if "common_root" not in pair.metadata and "construction_witness" not in pair.metadata:
                return False, "Nonlinear polynomial pair requires explicit common root or construction witness"

    return True, "Valid NFS polynomial pair"
