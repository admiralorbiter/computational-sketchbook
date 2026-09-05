"""NSB Baselines: Fermat, Pollard p-1, Pollard rho, and portfolio dispatchers."""

from nsb.baselines.base import BaselineFactorResult, BaselineSolver
from nsb.baselines.fermat import FermatSolver
from nsb.baselines.pollard_pm1 import PollardPM1Solver
from nsb.baselines.pollard_rho import PollardRhoSolver
from nsb.baselines.portfolio import (
    SOLVER_REGISTRY,
    get_baseline_solver,
    run_baseline_solve,
)

__all__ = [
    "BaselineFactorResult",
    "BaselineSolver",
    "FermatSolver",
    "PollardPM1Solver",
    "PollardRhoSolver",
    "SOLVER_REGISTRY",
    "get_baseline_solver",
    "run_baseline_solve",
]
