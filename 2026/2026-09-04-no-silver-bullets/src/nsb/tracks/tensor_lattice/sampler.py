"""Lattice reduction and candidate relation samplers for Track A.

Includes:
1. BabaiSchnorrLatticeSampler: Genuine lattice-guided relation discovery using LLL-reduced
   basis vectors and Babai nearest plane algorithm on Schnorr's lattice.
2. SqrtNeighborhoodSmoothnessSampler: Explicit baseline control performing naive near-square search
   around sqrt(N) for A/B comparative evaluation.
"""

from fractions import Fraction
import math
import time
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple
import gmpy2
from nsb.tracks.partial_information.lattice_root import lll_reduction
from nsb.tracks.tensor_lattice.lattice import (
    build_schnorr_lattice,
    build_schnorr_target_lattice,
    get_factor_base,
    make_schnorr_target,
)



def get_smoothness_residual(val: int, primes: List[int]) -> Tuple[int, List[int]]:
    """Trial divide val by primes, returning (residual_cofactor, exponents)."""
    if val <= 0:
        return val, [0] * len(primes)
    rem = val
    exponents = [0] * len(primes)
    for i, p in enumerate(primes):
        while rem % p == 0:
            exponents[i] += 1
            rem //= p
            if rem == 1:
                return 1, exponents
    return rem, exponents


def check_smooth_and_factor(val: int, primes: List[int]) -> Optional[List[int]]:
    """Check if val is smooth over primes and return list of exponents [e_1, ..., e_k]."""
    rem, exponents = get_smoothness_residual(val, primes)
    return exponents if rem == 1 else None


class SqrtNeighborhoodSmoothnessSampler:
    """Baseline control: Naive near-square search around sqrt(N) without lattice information."""

    def __init__(self, factor_base_size: int = 15):
        self.factor_base_size = factor_base_size
        self.primes = get_factor_base(factor_base_size)

    def sample_relations(
        self,
        N: int,
        max_candidates: int = 2000,
    ) -> List[Dict[str, Any]]:
        valid_relations: List[Dict[str, Any]] = []
        seen_x: Set[int] = set()
        sqrt_n = int(gmpy2.isqrt(N))

        for delta in range(1, max_candidates + 1):
            x = sqrt_n + delta
            if x <= 1 or x in seen_x:
                continue
            seen_x.add(x)

            # Non-trivial congruence: x > sqrt(N) so x^2 > N
            u = (x * x) % N
            if u == 0:
                continue

            exponents = check_smooth_and_factor(u, self.primes)
            if exponents is not None:
                valid_relations.append({
                    "x": x,
                    "val": u,
                    "exponents": exponents,
                    "generator": "sqrt_neighborhood_control",
                })

            if len(valid_relations) >= self.factor_base_size + 5:
                return valid_relations

        return valid_relations


_SCHNORR_REDUCED_BASIS_CACHE: Dict[Tuple[int, int], Tuple[List[List[Fraction]], List[List[Fraction]], List[Fraction]]] = {}


def get_cached_schnorr_basis(
    primes: List[int], scale_c: int
) -> Tuple[List[List[Fraction]], List[List[Fraction]], List[Fraction]]:
    """Retrieve or compute LLL-reduced Schnorr target lattice basis and Gram-Schmidt vectors."""
    key = (len(primes), scale_c)
    if key in _SCHNORR_REDUCED_BASIS_CACHE:
        return _SCHNORR_REDUCED_BASIS_CACHE[key]

    n = len(primes)
    basis = build_schnorr_target_lattice(primes, scale_c)
    reduced = lll_reduction(basis)

    def dot(u_vec: List[Fraction], v_vec: List[Fraction]) -> Fraction:
        return sum(a * b for a, b in zip(u_vec, v_vec))

    b_star: List[List[Fraction]] = []
    b_star_sq: List[Fraction] = []
    for i in range(n):
        v_curr = [Fraction(x) for x in reduced[i]]
        for j in range(i):
            mu = dot(reduced[i], b_star[j]) / b_star_sq[j] if b_star_sq[j] != 0 else Fraction(0)
            v_curr = [v_curr[col] - mu * b_star[j][col] for col in range(n + 1)]
        b_star.append(v_curr)
        b_star_sq.append(dot(v_curr, v_curr))

    _SCHNORR_REDUCED_BASIS_CACHE[key] = (reduced, b_star, b_star_sq)
    return _SCHNORR_REDUCED_BASIS_CACHE[key]


class BabaiSchnorrLatticeSampler:
    """Lattice-directed relation discovery using LLL reduction and Babai nearest plane on Schnorr's lattice."""

    def __init__(self, factor_base_size: int = 15, scale_c: int = 4):
        self.factor_base_size = factor_base_size
        self.scale_c = scale_c
        self.primes = get_factor_base(factor_base_size)

    def sample_relations(
        self,
        N: int,
        max_candidates: int = 2000,
    ) -> List[Dict[str, Any]]:
        """Extract relations via genuine Schnorr CVP target approximation and (u, v) decoding."""
        relations, _ = self.sample_relations_with_diagnostics(N, max_candidates=max_candidates)
        return relations

    def sample_relations_with_diagnostics(
        self,
        N: int,
        max_candidates: int = 2000,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Extract relations and record rich diagnostics (Babai distance, norms, residuals, entropy)."""
        t_start = time.perf_counter()
        n = len(self.primes)
        reduced, b_star, b_star_sq = get_cached_schnorr_basis(self.primes, self.scale_c)

        def dot(u_vec: List[Fraction], v_vec: List[Fraction]) -> Fraction:
            return sum(a * b for a, b in zip(u_vec, v_vec))

        valid_relations: List[Dict[str, Any]] = []
        seen_pairs: Set[Tuple[int, int, int]] = set()

        candidates_tested = 0
        max_targets = max(50, max_candidates // 10)

        babai_distances: List[float] = []
        l1_norms: List[int] = []
        l2_norms: List[float] = []
        linf_norms: List[int] = []
        diff_bits: List[float] = []
        residual_bits: List[float] = []
        e_patterns: List[Tuple[int, ...]] = []

        for k_mult in range(1, max_targets + 1):
            target = make_schnorr_target(N, n, scale_c=self.scale_c, k=k_mult)

            # Babai nearest plane with small search neighborhood around top coefficients
            offsets = [0, -1, 1, -2, 2] if n <= 20 else [0]
            for offset in offsets:
                candidates_tested += 1
                curr = [Fraction(x) for x in target]
                coeffs = [0] * n

                for i in reversed(range(n)):
                    proj = dot(curr, b_star[i]) / b_star_sq[i] if b_star_sq[i] != 0 else Fraction(0)
                    k_val = int(round(proj)) + (offset if i == n - 1 else 0)
                    coeffs[i] = k_val
                    for col in range(n + 1):
                        curr[col] -= k_val * reduced[i][col]

                # Reconstruct lattice point
                lat_point = [Fraction(0)] * (n + 1)
                for i in range(n):
                    for col in range(n + 1):
                        lat_point[col] += coeffs[i] * reduced[i][col]

                # Target to Babai point distance in R^{n+1}
                dist_sq = sum(float(target[col] - lat_point[col]) ** 2 for col in range(n + 1))
                babai_distances.append(math.sqrt(dist_sq))

                # Coordinates 0..n-1 are exponents e_0..e_{n-1}
                e = [int(lat_point[i]) for i in range(n)]
                e_tuple = tuple(e)
                e_patterns.append(e_tuple)

                l1 = sum(abs(x) for x in e)
                l2 = math.sqrt(sum(x * x for x in e))
                linf = max(abs(x) for x in e) if e else 0
                l1_norms.append(l1)
                l2_norms.append(l2)
                linf_norms.append(linf)

                # Decode u and v
                u = 1
                v = 1
                u_exp = [0] * n
                for idx, (p, exp) in enumerate(zip(self.primes, e)):
                    if exp > 0:
                        u *= (p**exp)
                        u_exp[idx] = exp
                    elif exp < 0:
                        v *= (p**(-exp))

                diff_val = u - v * k_mult * N
                if abs(diff_val) > 1 and diff_val % N != 0:
                    diff = abs(diff_val)
                    diff_bits.append(math.log2(diff))

                    res_cofactor, exp_diff = get_smoothness_residual(diff, self.primes)
                    res_bit_len = math.log2(res_cofactor) if res_cofactor > 1 else 0.0
                    residual_bits.append(res_bit_len)

                    sign = 0 if diff_val > 0 else 1
                    pair_key = (u, diff, sign)
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        if res_cofactor == 1:
                            combined_exp = [u_exp[i] + exp_diff[i] for i in range(n)]
                            valid_relations.append({
                                "u": u,
                                "diff": diff,
                                "sign": sign,
                                "k": k_mult,
                                "u_exp": u_exp,
                                "diff_exp": exp_diff,
                                "combined_exp": combined_exp,
                                "row_mod2": [sign] + [c % 2 for c in combined_exp],
                                "generator": "schnorr_cvp_babai",
                            })
                else:
                    residual_bits.append(float(N.bit_length()))

                target_relations = max(self.factor_base_size + 30, 48)
                if len(valid_relations) >= target_relations or candidates_tested >= max_candidates:
                    break

            if len(valid_relations) >= target_relations or candidates_tested >= max_candidates:
                break

        wall_sec = time.perf_counter() - t_start

        # Entropy calculation over candidate exponent patterns
        pattern_counts = Counter(e_patterns)
        total_p = len(e_patterns)
        entropy = 0.0
        if total_p > 0:
            for count in pattern_counts.values():
                p_i = count / total_p
                entropy -= p_i * math.log2(p_i)

        diagnostics = {
            "candidates_tested": candidates_tested,
            "valid_relations": len(valid_relations),
            "wall_seconds": wall_sec,
            "relation_rate": len(valid_relations) / wall_sec if wall_sec > 0 else 0.0,
            "mean_babai_distance": sum(babai_distances) / len(babai_distances) if babai_distances else 0.0,
            "mean_l1_norm": sum(l1_norms) / len(l1_norms) if l1_norms else 0.0,
            "mean_l2_norm": sum(l2_norms) / len(l2_norms) if l2_norms else 0.0,
            "max_linf_norm": max(linf_norms) if linf_norms else 0,
            "mean_diff_bits": sum(diff_bits) / len(diff_bits) if diff_bits else 0.0,
            "mean_residual_bits": sum(residual_bits) / len(residual_bits) if residual_bits else 0.0,
            "smooth_rate": len(valid_relations) / candidates_tested if candidates_tested > 0 else 0.0,
            "unique_candidates": len(pattern_counts),
            "duplicate_candidates": candidates_tested - len(pattern_counts),
            "duplicate_rate": (candidates_tested - len(pattern_counts)) / candidates_tested if candidates_tested > 0 else 0.0,
            "candidate_entropy": entropy,
        }

        return valid_relations, diagnostics

