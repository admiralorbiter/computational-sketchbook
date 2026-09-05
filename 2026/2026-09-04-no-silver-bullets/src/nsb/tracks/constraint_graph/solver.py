"""SAT solver adapter executing CNF factoring instances and extracting integer factors."""

import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from pysat.formula import CNF
from pysat.solvers import Solver


class SATSolverResult:
    def __init__(
        self,
        satisfiable: Optional[bool],
        factors: Optional[List[int]] = None,
        solve_time_seconds: float = 0.0,
        num_variables: int = 0,
        num_clauses: int = 0,
        conflicts: Optional[int] = None,
        decisions: Optional[int] = None,
        timed_out: bool = False,
    ):
        self.satisfiable = satisfiable
        self.factors = factors or []
        self.solve_time_seconds = solve_time_seconds
        self.num_variables = num_variables
        self.num_clauses = num_clauses
        self.conflicts = conflicts
        self.decisions = decisions
        self.timed_out = timed_out


class SATSolverAdapter:
    """Invokes modern CDCL SAT solvers via PySAT."""

    def __init__(self, solver_name: str = "glucose4"):
        self.solver_name = solver_name

    def solve(
        self,
        cnf: CNF,
        mapping: Dict[str, List[int]],
        timeout_seconds: Optional[float] = None,
    ) -> SATSolverResult:
        """Solve CNF formula and decode factor bits."""
        num_vars = len(set(abs(lit) for clause in cnf.clauses for lit in clause))
        num_clauses = len(cnf.clauses)

        start_time = time.perf_counter()
        sat: Optional[bool] = False
        model = None
        conflicts = None
        decisions = None
        timed_out = False

        with Solver(name=self.solver_name, bootstrap_with=cnf) as solver:
            if timeout_seconds is not None and timeout_seconds > 0:
                timed_out_box = [False]

                def interrupt_solver():
                    timed_out_box[0] = True
                    try:
                        solver.interrupt()
                    except (NotImplementedError, AttributeError):
                        pass

                timer = threading.Timer(timeout_seconds, interrupt_solver)
                timer.daemon = True
                timer.start()
                try:
                    res = solver.solve_limited(expect_interrupt=True)
                    if res is None or timed_out_box[0]:
                        sat = None
                        timed_out = True
                    else:
                        sat = bool(res)
                except NotImplementedError:
                    # Solver does not support limited solve
                    sat = solver.solve()
                finally:
                    timer.cancel()
            else:
                sat = solver.solve()

            solve_time = time.perf_counter() - start_time

            if sat is True:
                model = solver.get_model()

            # Attempt to gather stats if available from solver
            accum_stats = solver.accum_stats() if hasattr(solver, "accum_stats") else {}
            conflicts = accum_stats.get("conflicts", None)
            decisions = accum_stats.get("decisions", None)

        factors = None
        if sat is True and model is not None:
            # Model is a list where index corresponds to literal polarity
            model_set = set(model)
            p_vars = mapping["p_vars"]
            q_vars = mapping["q_vars"]

            p_val = 0
            for i, var in enumerate(p_vars):
                if var in model_set:
                    p_val |= (1 << i)

            q_val = 0
            for j, var in enumerate(q_vars):
                if var in model_set:
                    q_val |= (1 << j)

            factors = [p_val, q_val] if p_val <= q_val else [q_val, p_val]

        return SATSolverResult(
            satisfiable=sat,
            factors=factors,
            solve_time_seconds=round(solve_time, 4),
            num_variables=num_vars,
            num_clauses=num_clauses,
            conflicts=conflicts,
            decisions=decisions,
            timed_out=timed_out,
        )

