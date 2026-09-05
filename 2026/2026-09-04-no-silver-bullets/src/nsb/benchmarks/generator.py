"""Deterministic prime and semiprime generator for benchmark families.

Families:
- Family R: Balanced random semiprimes (primary research target).
- Family F: Fermat-positive controls (|p - q| is small).
- Family P1: Pollard p-1 positive controls (p-1 is B1-smooth).
- Family C: Partial-information controls (paired with oracle bit slice metadata).
- Family E: Encoding controls (small toy semiprimes for SAT/CSP validation).
"""

import math
import random
from typing import Any, Dict, List, Optional, Set, Tuple
import gmpy2


def generate_random_prime(bits: int, rng: random.Random) -> int:
    """Generate a random prime with exactly `bits` bit length using Miller-Rabin test."""
    if bits < 2:
        raise ValueError(f"Bits must be >= 2, got {bits}")
    if bits == 2:
        return rng.choice([2, 3])

    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1

    while True:
        # Generate an odd number in [lower, upper] with MSB set
        candidate = rng.randrange(lower | 1, upper + 1, 2)
        if gmpy2.is_prime(candidate, 25):
            return int(candidate)


def generate_smooth_number(target_bits: int, prime_bound: int, rng: random.Random) -> int:
    """Generate a smooth number by multiplying small primes <= prime_bound."""
    # Sieve primes up to prime_bound
    primes: List[int] = []
    for candidate in range(2, prime_bound + 1):
        if gmpy2.is_prime(candidate, 25):
            primes.append(candidate)

    if not primes:
        raise ValueError(f"No primes <= {prime_bound}")

    product = 1
    target_val = 1 << target_bits
    while product.bit_length() < target_bits:
        p = rng.choice(primes)
        if product * p <= target_val * 2:
            product *= p
        else:
            break
    return product


def generate_family_r(bits: int, rng: random.Random, used_primes: Optional[Set[int]] = None) -> Tuple[int, int, int]:
    """Generate balanced random semiprime N = p * q with unique factors.

    Returns:
        Tuple[N, p, q] where p <= q, bit_length(N) == bits, and p, q not in used_primes.
    """
    if bits < 4:
        raise ValueError("Balanced semiprimes require at least 4 bits")

    bp = bits // 2
    bq = bits - bp

    min_diff = 1 << max(1, bp - 10)

    for _ in range(10000):
        p = generate_random_prime(bp, rng)
        if used_primes is not None and p in used_primes:
            continue
        q = generate_random_prime(bq, rng)
        if used_primes is not None and q in used_primes:
            continue

        if p == q:
            continue
        if p > q:
            p, q = q, p
        if (q - p) < min_diff and bp >= 16:
            continue

        N = p * q
        if N.bit_length() == bits:
            if used_primes is not None:
                used_primes.add(p)
                used_primes.add(q)
            return N, p, q

    raise RuntimeError(f"Failed to generate balanced semiprime of {bits} bits within iteration limit")


def generate_family_f(bits: int, rng: random.Random, max_delta: int = 256) -> Tuple[int, int, int]:
    """Generate Fermat-positive control semiprime where |p - q| is small."""
    bp = bits // 2
    p = generate_random_prime(bp, rng)

    # Search for close prime q
    delta = 2
    while delta <= max_delta:
        q = p + delta
        if gmpy2.is_prime(q, 25):
            N = p * q
            return N, p, q
        delta += 2

    # Fallback: start at p and check forward
    candidate = p + 2
    while True:
        if gmpy2.is_prime(candidate, 25):
            q = int(candidate)
            N = p * q
            return N, p, q
        candidate += 2


def generate_family_p1(bits: int, rng: random.Random, prime_bound: int = 2000) -> Tuple[int, int, int]:
    """Generate Pollard p-1 positive control where p-1 is smooth."""
    bp = bits // 2
    bq = bits - bp
    q = generate_random_prime(bq, rng)

    # Generate smooth p-1
    for _ in range(500):
        # We need p = smooth + 1 to be prime
        smooth = generate_smooth_number(bp - 1, prime_bound, rng)
        # ensure smooth is even so p = smooth + 1 can be prime
        if smooth % 2 != 0:
            smooth *= 2
        p_cand = smooth + 1
        if p_cand.bit_length() == bp and gmpy2.is_prime(p_cand, 25):
            p = int(p_cand)
            if p != q:
                if p > q:
                    p, q = q, p
                return p * q, p, q

    # Fallback to standard next_prime from smooth
    smooth = generate_smooth_number(bp - 1, prime_bound, rng)
    if smooth % 2 != 0:
        smooth *= 2
    p = int(gmpy2.next_prime(smooth))
    if p > q:
        p, q = q, p
    return p * q, p, q


def generate_family_c(
    bits: int, rng: random.Random, msb_fraction: float = 0.5
) -> Tuple[int, int, int, Dict[str, Any]]:
    """Generate partial-information control with oracle bit-slice metadata."""
    N, p, q = generate_family_r(bits, rng)
    p_bits = p.bit_length()
    known_msb_count = max(1, int(round(p_bits * msb_fraction)))
    shift = p_bits - known_msb_count
    msb_value = p >> shift

    fractions = [0.25, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    oracle_ladder = {}
    for frac in fractions:
        k = max(1, int(round(p_bits * frac)))
        s = p_bits - k
        oracle_ladder[str(int(round(frac * 100)))] = {
            "fraction": frac,
            "known_bits": k,
            "shift": s,
            "msb_value": p >> s,
        }

    oracle_meta = {
        "target": "p",
        "factor_bit_length": p_bits,
        "oracle_type": "msb",
        "known_bits": known_msb_count,
        "fraction": msb_fraction,
        "msb_value": msb_value,
        "shift": shift,
        "oracle_ladder": oracle_ladder,
    }
    return N, p, q, oracle_meta


def generate_family_e(bits: int, rng: random.Random) -> Tuple[int, int, int]:
    """Generate toy balanced semiprime for constraint-graph validation."""
    return generate_family_r(bits, rng)
