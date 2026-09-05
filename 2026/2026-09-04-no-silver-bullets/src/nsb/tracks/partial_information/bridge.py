"""Partial-Information Bridge: maps partial factor constraints to exact factors via lattice recovery."""

import time
from typing import Any, Dict, List, Optional
from nsb.tracks.partial_information.lattice_root import (
    direct_residual_search_baseline,
    solve_univariate_small_root_linear,
)
from nsb.verifier.factor import FactorVerificationResult, verify_factors
from nsb.verifier.partial import PartialConstraint


class BridgeRecoveryResult:
    def __init__(
        self,
        success: bool,
        factors: Optional[List[int]] = None,
        wall_seconds: float = 0.0,
        cpu_seconds: float = 0.0,
        verification: Optional[FactorVerificationResult] = None,
        used_fallback: bool = False,
        error: str = "",
    ):
        self.success = success
        self.factors = factors or []
        self.wall_seconds = wall_seconds
        self.cpu_seconds = cpu_seconds
        self.verification = verification
        self.used_fallback = used_fallback
        self.error = error


class PartialInformationBridge:
    """Consumes constraints on factor p and executes small-root recovery to factor N."""

    def recover_from_oracle_msb(
        self,
        N: int,
        msb_value: int,
        shift: int,
        factor_bit_length: int,
        max_seconds: float = 10.0,
        no_fallback: bool = True,
    ) -> BridgeRecoveryResult:
        """Recover factor p given its upper bits.

        Args:
            N: Modulus.
            msb_value: Value of known high bits.
            shift: Bit shift (number of unknown low bits).
            factor_bit_length: Total bit length of factor p.
            max_seconds: Time budget.
            no_fallback: If True, strictly requires lattice recovery without exhaustive fallback.
        """
        start_wall = time.perf_counter()
        start_cpu = time.process_time()

        P0 = msb_value << shift
        X = 1 << shift

        if shift > (factor_bit_length * 0.75):
            elapsed_wall = time.perf_counter() - start_wall
            elapsed_cpu = time.process_time() - start_cpu
            return BridgeRecoveryResult(
                success=False,
                wall_seconds=round(elapsed_wall, 4),
                cpu_seconds=round(elapsed_cpu, 4),
                error=f"Insufficient information: shift {shift} > 75% of bit length {factor_bit_length}",
            )

        root = solve_univariate_small_root_linear(
            N, P0, X, max_seconds=max_seconds, no_fallback=no_fallback
        )

        elapsed_wall = time.perf_counter() - start_wall
        elapsed_cpu = time.process_time() - start_cpu

        if root is not None:
            p_cand = P0 + root
            if p_cand > 1 and N % p_cand == 0:
                q_cand = N // p_cand
                verif = verify_factors(N, p_cand, q_cand)
                if verif.verified:
                    return BridgeRecoveryResult(
                        success=True,
                        factors=[p_cand, q_cand] if p_cand <= q_cand else [q_cand, p_cand],
                        wall_seconds=round(elapsed_wall, 4),
                        cpu_seconds=round(elapsed_cpu, 4),
                        verification=verif,
                        used_fallback=False,
                    )

        err = (
            f"Time limit of {max_seconds}s exceeded during lattice recovery"
            if elapsed_wall >= max_seconds
            else "Root finding did not produce a dividing factor within bound"
        )
        return BridgeRecoveryResult(
            success=False,
            wall_seconds=round(elapsed_wall, 4),
            cpu_seconds=round(elapsed_cpu, 4),
            error=err,
        )
