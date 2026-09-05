"""Baseline portfolio runner and dispatcher."""

from typing import Any, Dict, List, Optional
from nsb.baselines.base import BaselineFactorResult, BaselineSolver
from nsb.baselines.fermat import FermatSolver
from nsb.baselines.pollard_pm1 import PollardPM1Solver
from nsb.baselines.pollard_rho import PollardRhoSolver
from nsb.verifier.factor import FactorVerificationResult, verify_factors

SOLVER_REGISTRY: Dict[str, BaselineSolver] = {
    "fermat": FermatSolver(),
    "pollard_pm1": PollardPM1Solver(),
    "pollard_rho": PollardRhoSolver(),
}


def get_baseline_solver(name: str) -> BaselineSolver:
    """Retrieve solver by name."""
    clean = name.lower().replace("-", "_")
    if clean in SOLVER_REGISTRY:
        return SOLVER_REGISTRY[clean]
    raise ValueError(f"Unknown baseline solver: '{name}'. Available: {list(SOLVER_REGISTRY.keys())}")


def run_baseline_solve(
    solver_name: str,
    N: int,
    max_seconds: float = 10.0,
    max_steps: Optional[int] = None,
) -> tuple[BaselineFactorResult, FactorVerificationResult]:
    """Execute a baseline solver and verify result through deterministic verifier."""
    solver = get_baseline_solver(solver_name)
    factor_res = solver.factor(N, max_seconds=max_seconds, max_steps=max_steps)

    if factor_res.success and len(factor_res.factors) >= 2:
        verif_res = verify_factors(N, factor_res.factors[0], factor_res.factors[1])
    else:
        verif_res = FactorVerificationResult(
            verified=False,
            status="FAILED",
            error_message="Baseline solver did not find factors within budget",
        )

    return factor_res, verif_res
