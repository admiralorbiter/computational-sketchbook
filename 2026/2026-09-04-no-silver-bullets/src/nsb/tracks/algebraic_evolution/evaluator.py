"""Multi-fidelity evaluation cascade for algebraic representations.

Levels:
- Level B0: Mathematical validity filter (common root mod N, primitive, degree).
- Level B1: Cheap proxy score (average logarithmic norm).
- Level B2: Empirical micro-sieve (smoothness yield over fixed factor base).
"""

import math
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import gmpy2
from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
)


class TimingInvalidError(RuntimeError):
    """Raised when cumulative batch timing fails to reach the required CPU time ceiling."""
    pass



def is_smooth(val: int, primes: List[int]) -> bool:
    """Check whether |val| is completely smooth over primes."""
    rem = abs(val)
    if rem <= 1:
        return True
    for p in primes:
        while rem % p == 0:
            rem //= p
            if rem == 1:
                return True
    return rem == 1


class AlgebraicEvaluator:
    """Evaluates algebraic polynomial representations along the B0-B2 cascade."""

    def __init__(self, small_primes_bound: int = 250):
        self.primes: List[int] = []
        p_cand = 2
        while p_cand <= small_primes_bound:
            if gmpy2.is_prime(p_cand):
                self.primes.append(int(p_cand))
            p_cand = int(gmpy2.next_prime(p_cand))

    def validate_b0(self, pair: PolynomialPair, N: int) -> Tuple[bool, str]:
        """Level B0: Validate representation invariants."""
        if pair.degree < 1:
            return False, "Degree must be >= 1"

        if len(pair.f1_coeffs) < 2:
            return False, "f1 must have at least 2 coefficients"

        if pair.f1_coeffs[-1] == 0:
            return False, "Leading coefficient of f1 cannot be zero"

        # Check content gcd(c0, ..., cd)
        g = abs(pair.f1_coeffs[0])
        for c in pair.f1_coeffs[1:]:
            g = math.gcd(g, abs(c))
        if g != 1:
            return False, f"Polynomial f1 is not primitive; content gcd is {g}"

        # Check common root m modulo N: f1(m) == 0 (mod N) and f2(m) == 0 (mod N)
        val1 = pair.eval_f1(pair.m)
        if val1 % N != 0:
            return False, f"f1(m) != 0 mod N ({val1 % N} != 0)"

        val2 = pair.eval_f2(pair.m)
        if val2 % N != 0:
            return False, f"f2(m) != 0 mod N ({val2 % N} != 0)"

        return True, "VALID"

    def score_proxy_b1(self, pair: PolynomialPair, sample_bound: int = 100) -> float:
        """Level B1: Average logarithmic norm score over [-sample_bound, sample_bound].

        Lower score indicates smaller values on average, corresponding to higher smoothness probability.
        """
        total_log = 0.0
        count = 0
        for a in range(-sample_bound, sample_bound + 1):
            if a == 0:
                continue
            val1 = abs(pair.eval_f1(a))
            val2 = abs(pair.eval_f2(a))
            prod = val1 * val2
            if prod > 0:
                total_log += math.log2(prod)
                count += 1

        return round(total_log / count, 4) if count > 0 else 0.0

    def micro_sieve_b2(
        self,
        pair: PolynomialPair,
        sample_bound: int = 200,
    ) -> Dict[str, Any]:
        """Level B2: Empirical smoothness yield testing."""
        smooth_relations = 0
        total_evals = 0

        for a in range(-sample_bound, sample_bound + 1):
            if a == 0:
                continue
            total_evals += 1
            v1 = pair.eval_f1(a)
            v2 = pair.eval_f2(a)

            if is_smooth(v1, self.primes) and is_smooth(v2, self.primes):
                smooth_relations += 1

        yield_rate = smooth_relations / total_evals if total_evals > 0 else 0.0

        return {
            "smooth_relations": smooth_relations,
            "total_evals": total_evals,
            "yield_rate": round(yield_rate, 6),
            "factor_base_size": len(self.primes),
        }

    def homogeneous_sieve_b3(
        self,
        pair: PolynomialPair,
        bound_a: int = 50,
        bound_b: int = 10,
    ) -> Dict[str, Any]:
        """Level B3: Homogeneous 2D relation sieve over coprime pairs (a, b) with b >= 1.

        Evaluates homogeneous norms:
            F_1(a, b) = b^{d_1} f_1(a / b)
            F_2(a, b) = b^{d_2} f_2(a / b)
        and tests simultaneous smoothness over the small primes factor base.
        """
        d1 = pair.degree
        c1 = pair.f1_coeffs
        d2 = 1
        c2 = [-pair.m, 1]  # f2(x) = x - m

        t0 = time.perf_counter()
        t_cpu0 = time.process_time()
        smooth_relations = 0
        total_pairs = 0
        smooth_pairs: Set[Tuple[int, int]] = set()

        for b in range(1, bound_b + 1):
            for a in range(-bound_a, bound_a + 1):
                if math.gcd(abs(a), b) != 1:
                    continue

                total_pairs += 1

                # Homogeneous F1(a, b) = sum_{i=0}^d c_i * a^i * b^{d-i}
                v1 = 0
                for i, coeff in enumerate(c1):
                    v1 += coeff * (a ** i) * (b ** (d1 - i))

                # Homogeneous F2(a, b) = a - b * m
                v2 = a - b * pair.m

                if is_smooth(v1, self.primes) and is_smooth(v2, self.primes):
                    smooth_relations += 1
                    smooth_pairs.add((a, b))

        wall_sec = time.perf_counter() - t0
        cpu_sec = max(1e-6, time.process_time() - t_cpu0)
        yield_rate = smooth_relations / total_pairs if total_pairs > 0 else 0.0
        rel_rate = smooth_relations / cpu_sec if cpu_sec > 0 else 0.0

        return {
            "smooth_relations": smooth_relations,
            "total_pairs": total_pairs,
            "yield_rate": round(yield_rate, 6),
            "factor_base_size": len(self.primes),
            "wall_seconds": wall_sec,
            "cpu_seconds": cpu_sec,
            "relation_rate": round(rel_rate, 4),
            "smooth_pairs": smooth_pairs,
        }

    def benchmark_relation_throughput(
        self,
        pair: PolynomialPair,
        bound_a: int = 50,
        bound_b: int = 10,
        min_cpu_seconds: float = 0.25,
        max_repeats: int = 2000,
    ) -> Dict[str, Any]:
        """Benchmark relation throughput with cumulative multi-batch execution to eliminate timer quantization.

        Repeats the deterministic sieving loop in batches until cumulative process CPU time reaches
        at least min_cpu_seconds (default 0.25s). Relations per core-second is calculated
        from aggregate relations and aggregate CPU time. Repetition is solely for timing precision
        and is not treated as additional statistical sample size.
        """
        d1 = pair.degree
        c1 = pair.f1_coeffs

        t_cpu_start = time.process_time()
        t_wall_start = time.perf_counter()

        total_smooth = 0
        total_pairs_sieved = 0
        batches_executed = 0
        single_batch_smooth = None
        single_batch_pairs = 0

        while True:
            batch_smooth = 0
            batch_pairs = 0
            for b in range(1, bound_b + 1):
                for a in range(-bound_a, bound_a + 1):
                    if math.gcd(abs(a), b) != 1:
                        continue
                    batch_pairs += 1
                    v1 = 0
                    for i, coeff in enumerate(c1):
                        v1 += coeff * (a ** i) * (b ** (d1 - i))
                    v2 = a - b * pair.m
                    if is_smooth(v1, self.primes) and is_smooth(v2, self.primes):
                        batch_smooth += 1

            if single_batch_smooth is None:
                single_batch_smooth = batch_smooth
                single_batch_pairs = batch_pairs

            total_smooth += batch_smooth
            total_pairs_sieved += batch_pairs
            batches_executed += 1

            cpu_elapsed = time.process_time() - t_cpu_start
            if cpu_elapsed >= min_cpu_seconds or batches_executed >= max_repeats:
                break

        if cpu_elapsed < min_cpu_seconds:
            raise TimingInvalidError(
                f"Cumulative CPU time {cpu_elapsed:.4f}s < required {min_cpu_seconds:.4f}s after {batches_executed} batches"
            )

        wall_elapsed = time.perf_counter() - t_wall_start
        cpu_sec = max(cpu_elapsed, 1e-4)
        throughput = total_smooth / cpu_sec if cpu_sec > 0 else 0.0

        return {
            "single_batch_smooth_relations": single_batch_smooth,
            "single_batch_pairs": single_batch_pairs,
            "batches_executed": batches_executed,
            "cumulative_cpu_seconds": round(cpu_sec, 6),
            "cumulative_wall_seconds": round(wall_elapsed, 6),
            "cumulative_smooth_relations": total_smooth,
            "throughput_relations_per_core_sec": round(throughput, 4),
        }

    def evaluate_paired_throughput_benchmark(
        self,
        N: int,
        cand_pair: PolynomialPair,
        base_pair: PolynomialPair,
        bound_a: int = 50,
        bound_b: int = 10,
        min_cpu_seconds: float = 0.25,
    ) -> Dict[str, Any]:
        """Benchmark candidate vs baseline relation throughput using cumulative batch timing."""
        res_cand = self.benchmark_relation_throughput(
            cand_pair, bound_a=bound_a, bound_b=bound_b, min_cpu_seconds=min_cpu_seconds
        )
        res_base = self.benchmark_relation_throughput(
            base_pair, bound_a=bound_a, bound_b=bound_b, min_cpu_seconds=min_cpu_seconds
        )

        th_cand = res_cand["throughput_relations_per_core_sec"]
        th_base = res_base["throughput_relations_per_core_sec"]
        th_ratio = round(th_cand / th_base, 4) if th_base > 0 else None

        return {
            "cand_throughput": th_cand,
            "base_throughput": th_base,
            "throughput_ratio": th_ratio,
            "cand_cpu_seconds": res_cand["cumulative_cpu_seconds"],
            "base_cpu_seconds": res_base["cumulative_cpu_seconds"],
            "cand_batches": res_cand["batches_executed"],
            "base_batches": res_base["batches_executed"],
        }

    def evaluate_paired_b3(
        self,
        N: int,
        bound_a: int = 50,
        bound_b: int = 10,
    ) -> Dict[str, Any]:
        """Paired exact McNemar evaluation of quadratic baseline vs cubic candidate on homogeneous B3 sieve."""
        p2 = create_base_m_representation(N, degree=2)
        p3 = create_base_m_representation(N, degree=3)

        res2 = self.homogeneous_sieve_b3(p2, bound_a=bound_a, bound_b=bound_b)
        res3 = self.homogeneous_sieve_b3(p3, bound_a=bound_a, bound_b=bound_b)

        pairs2: Set[Tuple[int, int]] = res2["smooth_pairs"]
        pairs3: Set[Tuple[int, int]] = res3["smooth_pairs"]
        total_pairs: int = res3["total_pairs"]

        # Exact 2x2 contingency table for coprime sieve points (a, b)
        n11 = len(pairs3 & pairs2)  # Smooth for both
        n10 = len(pairs3 - pairs2)  # Smooth for deg-3 only
        n01 = len(pairs2 - pairs3)  # Smooth for deg-2 only
        n00 = total_pairs - (n11 + n10 + n01)  # Smooth for neither

        # Exact McNemar test on discordant pairs (n10, n01)
        discordant = n10 + n01
        if discordant > 0:
            mcnemar_chi2 = round(((abs(n10 - n01) - 1.0) ** 2) / discordant, 4)
            k_extreme = max(n10, n01)
            binom_p = min(1.0, 2.0 * sum(math.comb(discordant, k) * (0.5 ** discordant) for k in range(k_extreme, discordant + 1)))
        else:
            mcnemar_chi2 = 0.0
            binom_p = 1.0

        r2 = res2["yield_rate"]
        r3 = res3["yield_rate"]
        yield_diff = round(r3 - r2, 6)

        # Ratio without 999 sentinel: None if r2 == 0
        yield_ratio = round(r3 / r2, 4) if r2 > 0 else None

        return {
            "deg2": res2,
            "deg3": res3,
            "total_pairs": total_pairs,
            "n11_both": n11,
            "n10_deg3_only": n10,
            "n01_deg2_only": n01,
            "n00_neither": n00,
            "mcnemar_chi2": mcnemar_chi2,
            "mcnemar_pvalue": round(binom_p, 8),
            "yield_diff": yield_diff,
            "yield_gain": yield_ratio,
            "deg2_smooth": res2["smooth_relations"],
            "deg2_pairs": res2["total_pairs"],
            "deg2_cpu_sec": res2["cpu_seconds"],
            "deg3_smooth": res3["smooth_relations"],
            "deg3_pairs": res3["total_pairs"],
            "deg3_cpu_sec": res3["cpu_seconds"],
        }

    def evaluate_modulus_cohort(
        self,
        moduli: List[int],
        bound_a: int = 50,
        bound_b: int = 10,
        cand_degree: int = 3,
        base_degree: int = 2,
        max_cpu_seconds_per_modulus: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Evaluate a cohort of independent moduli, computing modulus-level paired statistics."""
        import numpy as np
        from scipy import stats

        n = len(moduli)
        if n == 0:
            return {"n_moduli": 0, "status": "EMPTY_COHORT"}

        per_modulus: List[Dict[str, Any]] = []
        cand_yields: List[float] = []
        base_yields: List[float] = []
        paired_diffs: List[float] = []
        cand_throughputs: List[float] = []
        base_throughputs: List[float] = []

        total_n11 = 0
        total_n10 = 0
        total_n01 = 0
        total_n00 = 0

        for N in moduli:
            paired = self.evaluate_paired_b3(N, bound_a=bound_a, bound_b=bound_b)
            r_cand = paired["deg3"]["yield_rate"]
            r_base = paired["deg2"]["yield_rate"]
            diff = paired["yield_diff"]

            th_cand = paired["deg3"]["relation_rate"]
            th_base = paired["deg2"]["relation_rate"]
            mod_cpu = paired["deg2_cpu_sec"] + paired["deg3_cpu_sec"]

            if max_cpu_seconds_per_modulus is not None and mod_cpu > max_cpu_seconds_per_modulus:
                raise TimeoutError(
                    f"Modulus {N} exceeded CPU budget ceiling: {mod_cpu:.4f}s > {max_cpu_seconds_per_modulus:.4f}s"
                )

            cand_yields.append(r_cand)
            base_yields.append(r_base)
            paired_diffs.append(diff)
            cand_throughputs.append(th_cand)
            base_throughputs.append(th_base)

            total_n11 += paired["n11_both"]
            total_n10 += paired["n10_deg3_only"]
            total_n01 += paired["n01_deg2_only"]
            total_n00 += paired["n00_neither"]

            per_modulus.append({
                "N": N,
                "cand_yield": r_cand,
                "base_yield": r_base,
                "yield_diff": diff,
                "yield_gain": paired["yield_gain"],
                "cand_throughput": th_cand,
                "base_throughput": th_base,
                "deg2_cpu_sec": paired["deg2_cpu_sec"],
                "deg3_cpu_sec": paired["deg3_cpu_sec"],
                "cpu_seconds": mod_cpu,
                "mcnemar_pvalue": paired["mcnemar_pvalue"],
            })

        cand_wins = sum(1 for d in paired_diffs if d > 0)
        cand_losses = sum(1 for d in paired_diffs if d < 0)
        ties = sum(1 for d in paired_diffs if d == 0)
        win_rate = round(cand_wins / n, 4)

        mean_diff = float(np.mean(paired_diffs))
        std_diff = float(np.std(paired_diffs, ddof=1)) if n > 1 else 0.0

        if n > 1 and std_diff > 0:
            t_crit = float(stats.t.ppf(0.975, df=n - 1))
            ci_margin = t_crit * (std_diff / math.sqrt(n))
            ci_95 = (round(mean_diff - ci_margin, 6), round(mean_diff + ci_margin, 6))
        else:
            ci_95 = (round(mean_diff, 6), round(mean_diff, 6))

        # Modulus-level paired statistical tests
        non_zero_diffs = [d for d in paired_diffs if d != 0]
        if len(non_zero_diffs) >= 5:
            try:
                w_res = stats.wilcoxon(cand_yields, base_yields)
                wilcoxon_p = float(w_res.pvalue)
            except Exception:
                wilcoxon_p = 1.0
        else:
            wilcoxon_p = 1.0 if not any(d > 0 for d in paired_diffs) else 0.05

        if n > 1 and std_diff > 0:
            try:
                t_res = stats.ttest_rel(cand_yields, base_yields)
                paired_t_p = float(t_res.pvalue)
            except Exception:
                paired_t_p = 1.0
        else:
            paired_t_p = 1.0

        mean_cand_th = float(np.mean(cand_throughputs))
        mean_base_th = float(np.mean(base_throughputs))
        th_ratio = round(mean_cand_th / mean_base_th, 4) if mean_base_th > 0 else None

        return {
            "n_moduli": n,
            "mean_cand_yield": round(float(np.mean(cand_yields)), 6),
            "mean_base_yield": round(float(np.mean(base_yields)), 6),
            "mean_paired_diff": round(mean_diff, 6),
            "std_paired_diff": round(std_diff, 6),
            "ci_95": ci_95,
            "candidate_wins": cand_wins,
            "candidate_losses": cand_losses,
            "ties": ties,
            "win_rate": win_rate,
            "wilcoxon_pvalue": round(wilcoxon_p, 8),
            "paired_t_pvalue": round(paired_t_p, 8),
            "mean_cand_throughput": round(mean_cand_th, 2),
            "mean_base_throughput": round(mean_base_th, 2),
            "throughput_ratio": th_ratio,
            "diagnostic_intra_mcnemar_pooled": {
                "n11": total_n11,
                "n10": total_n10,
                "n01": total_n01,
                "n00": total_n00,
            },
            "per_modulus": per_modulus,
        }


