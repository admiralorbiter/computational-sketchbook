"""Pollard's rho factorization baseline with Brent cycle detection and batched GCD."""

import time
from typing import Optional
import gmpy2
from nsb.baselines.base import BaselineFactorResult, BaselineSolver


class PollardRhoSolver(BaselineSolver):
    """Pollard's rho algorithm using Brent's cycle-finding variant."""

    @property
    def name(self) -> str:
        return "pollard_rho"

    def factor(
        self,
        N: int,
        max_seconds: float = 10.0,
        max_steps: Optional[int] = None,
        c: int = 1,
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

        n_mpz = gmpy2.mpz(N)
        c_mpz = gmpy2.mpz(c)

        y = gmpy2.mpz(2)
        c_val = c_mpz
        m = 128
        g = gmpy2.mpz(1)
        r = 1
        q = gmpy2.mpz(1)
        steps = 0
        limit_steps = max_steps or 2_000_000

        while g == 1 and steps < limit_steps:
            x = y
            for _ in range(r):
                y = (y * y + c_val) % n_mpz

            k = 0
            while k < r and g == 1 and steps < limit_steps:
                ys = y
                batch_limit = min(m, r - k)
                for _ in range(batch_limit):
                    y = (y * y + c_val) % n_mpz
                    q = (q * abs(x - y)) % n_mpz
                    steps += 1
                g = gmpy2.gcd(q, n_mpz)
                k += batch_limit

                if (steps & 0x3FF) == 0:
                    if (time.perf_counter() - start_wall) > max_seconds:
                        break

            r *= 2

        if g == n_mpz:
            # Backtrack
            while True:
                ys = (ys * ys + c_val) % n_mpz
                g = gmpy2.gcd(abs(x - ys), n_mpz)
                if g > 1:
                    break

        if 1 < g < n_mpz:
            p = int(g)
            q_val = N // p
            return BaselineFactorResult(
                success=True,
                factors=[p, q_val] if p <= q_val else [q_val, p],
                steps=steps,
                wall_seconds=time.perf_counter() - start_wall,
                cpu_seconds=time.process_time() - start_cpu,
            )

        return BaselineFactorResult(
            success=False,
            factors=None,
            steps=steps,
            wall_seconds=time.perf_counter() - start_wall,
            cpu_seconds=time.process_time() - start_cpu,
        )
