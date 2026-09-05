import math
from fractions import Fraction
from typing import List, Tuple
import gmpy2
from nsb.tracks.tensor_lattice.lattice import get_factor_base
from nsb.tracks.partial_information.lattice_root import lll_reduction

def test_babai_schnorr():
    # Target semiprime: balanced Family R instance
    # Let's take p = 641, q = 1061 -> N = 680101 (20-bit, |p-q| = 420 >> N^0.25)
    p_true = 641
    q_true = 1061
    N = p_true * q_true

    factor_base = get_factor_base(12)
    print("Factor base:", factor_base)

    scale_c = 3
    n = len(factor_base)
    basis = []
    for i, p in enumerate(factor_base):
        row = [Fraction(0)] * (n + 1)
        row[i] = Fraction(1)
        row[n] = Fraction(int(round((10**scale_c) * math.log(p))))
        basis.append(row)

    print("Running LLL on basis...")
    red = lll_reduction(basis)

    # Gram-Schmidt on reduced basis
    def dot(u, v):
        return sum(a * b for a, b in zip(u, v))

    b_star = []
    for i in range(n):
        v = [Fraction(x) for x in red[i]]
        for j in range(i):
            mu = dot(red[i], b_star[j]) / dot(b_star[j], b_star[j])
            v = [v[k] - mu * b_star[j][k] for k in range(n + 1)]
        b_star.append(v)

    target = [Fraction(0)] * (n + 1)
    target[n] = Fraction(int(round((10**scale_c) * math.log(N))))

    def babai_cvp(tgt, pert=None):
        curr = [Fraction(x) for x in tgt]
        coeffs = [0] * n
        for i in reversed(range(n)):
            proj = dot(curr, b_star[i]) / dot(b_star[i], b_star[i])
            offset = pert[i] if pert else 0
            k = int(round(proj)) + offset
            coeffs[i] = k
            for col in range(n + 1):
                curr[col] -= k * red[i][col]

        # Reconstruct lattice point
        lat_point = [Fraction(0)] * (n + 1)
        for i in range(n):
            for col in range(n + 1):
                lat_point[col] += coeffs[i] * red[i][col]

        # First n coordinates are e_0 .. e_{n-1}
        e = [int(lat_point[i]) for i in range(n)]
        return e

    # Test Babai without perturbation
    e0 = babai_cvp(target)
    print("Babai exponents:", e0)

    # Decode e into u and v
    u = 1
    v = 1
    for prime, exp in zip(factor_base, e0):
        if exp > 0:
            u *= (prime ** exp)
        elif exp < 0:
            v *= (prime ** (-exp))

    print(f"u: {u}, v: {v}")
    print(f"u - v*N: {u - v * N}")
    diff = abs(u - v * N)
    print(f"diff: {diff}")

test_babai_schnorr()
