"""Fermat difference-of-squares factorization baseline."""

import time
from typing import Optional
import gmpy2
from nsb.baselines.base import BaselineFactorResult, BaselineSolver


class FermatSolver(BaselineSolver):
    """Fermat factorization baseline: checks a^2 - N = b^2 starting from ceil(sqrt(N))."""

    @property
    def name(self) -> str:
        return "fermat"

    def factor(self, N: int, max_seconds: float = 10.0, max_steps: Optional[int] = None) -> BaselineFactorResult:
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

        a, rem = gmpy2.isqrt_rem(N)
        if rem != 0:
            a += 1
        else:
            # N is a perfect square
            return BaselineFactorResult(
                success=True,
                factors=[int(a), int(a)],
                steps=1,
                wall_seconds=time.perf_counter() - start_wall,
                cpu_seconds=time.process_time() - start_cpu,
            )

        steps = 0
        limit_steps = max_steps or 10_000_000

        while steps < limit_steps:
            steps += 1
            if (steps & 0x3FFF) == 0:
                if (time.perf_counter() - start_wall) > max_seconds:
                    break

            b2 = a * a - N
            if gmpy2.is_square(b2):
                b = gmpy2.isqrt(b2)
                p = int(a - b)
                q = int(a + b)
                if p > 1 and q > 1 and p * q == N:
                    return BaselineFactorResult(
                        success=True,
                        factors=[p, q] if p <= q else [q, p],
                        steps=steps,
                        wall_seconds=time.perf_counter() - start_wall,
                        cpu_seconds=time.process_time() - start_cpu,
                    )
            a += 1

        return BaselineFactorResult(
            success=False,
            factors=None,
            steps=steps,
            wall_seconds=time.perf_counter() - start_wall,
            cpu_seconds=time.process_time() - start_cpu,
        )
