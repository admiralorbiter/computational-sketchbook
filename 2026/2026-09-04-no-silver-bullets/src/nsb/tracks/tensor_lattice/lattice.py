"""Schnorr-style lattice builder for relation discovery."""

from fractions import Fraction
import math
from typing import List, Tuple
import gmpy2


def get_factor_base(k: int) -> List[int]:
    """Return the first k prime numbers starting from 2."""
    primes: List[int] = []
    p = 2
    while len(primes) < k:
        if gmpy2.is_prime(p):
            primes.append(int(p))
        p = int(gmpy2.next_prime(p))
    return primes


def build_schnorr_lattice(
    N: int,
    factor_base: List[int],
    scale_c: int = 1000,
) -> List[List[Fraction]]:
    """Legacy compatibility: construct augmented lattice."""
    return build_schnorr_target_lattice(factor_base, scale_c=scale_c)


def build_schnorr_target_lattice(
    factor_base: List[int],
    scale_c: int = 4,
) -> List[List[Fraction]]:
    """Construct Schnorr n-rank lattice embedded in (n+1) dimensions.

    For factor base p_1, ..., p_n:
    Basis matrix B has size n x (n+1).
    Row j (0 <= j < n) has:
      col j: diagonal weight (1)
      col n: round(10^c * ln(p_j))
      all other cols: 0
    """
    n = len(factor_base)
    basis: List[List[Fraction]] = []
    scale = 10**scale_c if scale_c <= 10 else scale_c

    for i, p in enumerate(factor_base):
        row = [Fraction(0)] * (n + 1)
        row[i] = Fraction(1)
        scaled_log = int(round(scale * math.log(p)))
        row[n] = Fraction(scaled_log)
        basis.append(row)

    return basis


def make_schnorr_target(
    N: int,
    n: int,
    scale_c: int = 4,
    k: int = 1,
) -> List[Fraction]:
    """Target vector t_{k*N, c} = (0, ..., 0, round(C * ln(k * N)))^T in (n+1) dimensions."""
    target = [Fraction(0)] * (n + 1)
    scale = 10**scale_c if scale_c <= 10 else scale_c
    scaled_log = int(round(scale * math.log(k * N)))
    target[n] = Fraction(scaled_log)
    return target
