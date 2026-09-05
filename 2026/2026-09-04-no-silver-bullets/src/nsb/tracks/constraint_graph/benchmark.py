"""Comparative scaling benchmark for Track D: Schoolbook vs Carry-Save Adder SAT Encodings."""

from dataclasses import asdict, dataclass
import time
from typing import Any, Dict, List, Optional
from nsb.tracks.constraint_graph.encoder import CarrySaveAdderSATEncoder, SchoolbookSATEncoder
from nsb.tracks.constraint_graph.solver import SATSolverAdapter


@dataclass
class TrackDComparisonResult:
    bits: int
    N: int
    schoolbook_time: float
    csa_time: float
    speedup: float
    schoolbook_vars: int
    csa_vars: int
    schoolbook_clauses: int
    csa_clauses: int
    schoolbook_conflicts: Optional[int]
    csa_conflicts: Optional[int]
    satisfiable: bool
    factors_recovered: List[int]


def run_paired_sat_comparison(
    N: int,
    bits: int,
    timeout_seconds: float = 10.0,
    solver_name: str = "glucose4",
) -> TrackDComparisonResult:
    """Run paired comparative benchmark on a single modulus: Schoolbook vs Carry-Save Tree."""
    adapter = SATSolverAdapter(solver_name=solver_name)

    # 1. Baseline: Schoolbook encoding
    sch_encoder = SchoolbookSATEncoder()
    cnf_sch, map_sch = sch_encoder.encode(N)
    res_sch = adapter.solve(cnf_sch, map_sch, timeout_seconds=timeout_seconds)

    # 2. Candidate: Carry-Save Adder tree encoding
    csa_encoder = CarrySaveAdderSATEncoder()
    cnf_csa, map_csa = csa_encoder.encode(N)
    res_csa = adapter.solve(cnf_csa, map_csa, timeout_seconds=timeout_seconds)

    t_sch = max(0.0001, res_sch.solve_time_seconds)
    t_csa = max(0.0001, res_csa.solve_time_seconds)
    speedup = t_sch / t_csa

    sat_status = bool(res_sch.satisfiable and res_csa.satisfiable)
    factors = res_csa.factors if res_csa.factors else res_sch.factors

    return TrackDComparisonResult(
        bits=bits,
        N=N,
        schoolbook_time=round(t_sch, 6),
        csa_time=round(t_csa, 6),
        speedup=round(speedup, 4),
        schoolbook_vars=res_sch.num_variables,
        csa_vars=res_csa.num_variables,
        schoolbook_clauses=res_sch.num_clauses,
        csa_clauses=res_csa.num_clauses,
        schoolbook_conflicts=res_sch.conflicts,
        csa_conflicts=res_csa.conflicts,
        satisfiable=sat_status,
        factors_recovered=factors,
    )


def run_track_d_scaling(
    instances: List[Dict[str, Any]],
    timeout_seconds: float = 10.0,
    solver_name: str = "glucose4",
) -> List[TrackDComparisonResult]:
    """Execute paired comparative scaling across multiple bit sizes."""
    results: List[TrackDComparisonResult] = []
    for item in instances:
        N = int(item["n"])
        bits = int(item["bits"])
        res = run_paired_sat_comparison(
            N=N,
            bits=bits,
            timeout_seconds=timeout_seconds,
            solver_name=solver_name,
        )
        results.append(res)
    return results
