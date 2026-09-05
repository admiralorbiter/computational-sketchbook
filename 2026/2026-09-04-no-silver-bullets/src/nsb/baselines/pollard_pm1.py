"""Pollard's p-1 algorithm baseline."""

import math
import time
from typing import Optional
import gmpy2
from nsb.baselines.base import BaselineFactorResult, BaselineSolver


class PollardPM1Solver(BaselineSolver):
    """Pollard's p-1 factorization baseline using smoothness bounds."""

    @property
    def name(self) -> str:
        return "pollard_p_minus_1"

    def factor(
        self,
        N: int,
        max_seconds: float = 10.0,
        max_steps: Optional[int] = None,
        b1_bound: int = 50_000,
    ) -> BaselineFactorResult:
        start_wall = time.perf_counter()
        start_cpu = time.process_time()

        if N % 2 == 0:
            return BaselineFactorResult(
                success=True,
                factors=[2, N // 2],
                steps=1,
                wall_seconds=time.perf_counter() - start_wall,
                cpu_seconds=time.process_time() - start_cpu,
            )

        a = gmpy2.mpz(2)
        n_mpz = gmpy2.mpz(N)
        steps = 0
        limit_steps = max_steps or b1_bound

        # Pre-sieve small primes up to b1_bound
        prime_cand = 2
        while prime_cand <= b1_bound and steps < limit_steps:
            steps += 1
            if (steps & 0xFF) == 0:
                if (time.perf_counter() - start_wall) > max_seconds:
                    break

            if gmpy2.is_prime(prime_cand):
                # Multiply exponent by prime power q^k <= b1_bound
                pk = prime_cand
                while pk * prime_cand <= b1_bound:
                    pk *= prime_cand
                a = gmpy2.powmod(a, pk, n_mpz)

                g = gmpy2.gcd(a - 1, n_mpz)
                if 1 < g < n_mpz:
                    p = int(g)
                    q = N // p
                    return BaselineFactorResult(
                        success=True,
                        factors=[p, q] if p <= q else [q, p],
                        steps=steps,
                        wall_seconds=time.perf_counter() - start_wall,
                        cpu_seconds=time.process_time() - start_cpu,
                        extra_metrics={"b1_reached": prime_cand},
                    )
                elif g == n_mpz:
                    # Trivial factor; failure with this base
                    break

            prime_cand = int(gmpy2.next_prime(prime_cand))

        return BaselineFactorResult(
            success=False,
            factors=None,
            steps=steps,
            wall_seconds=time.perf_counter() - start_wall,
            cpu_seconds=time.process_time() - start_cpu,
        )
