"""Unit tests for Track D: SAT multiplier encoding and solving."""

import pytest
from nsb.tracks.constraint_graph.encoder import SchoolbookSATEncoder
from nsb.tracks.constraint_graph.solver import SATSolverAdapter
from nsb.verifier.factor import verify_factors


def test_sat_encoder_toy():
    encoder = SchoolbookSATEncoder(symmetry_breaking=True)
    # N = 77 (7 * 11)
    cnf, mapping = encoder.encode(77, bp=3, bq=4)
    assert len(cnf.clauses) > 0
    assert len(mapping["p_vars"]) == 3
    assert len(mapping["q_vars"]) == 4

    solver = SATSolverAdapter(solver_name="cadical195")
    res = solver.solve(cnf, mapping)
    assert res.satisfiable is True
    assert res.factors == [7, 11]

    verif = verify_factors(77, res.factors[0], res.factors[1])
    assert verif.verified is True


def test_sat_encoder_odd_check():
    encoder = SchoolbookSATEncoder()
    with pytest.raises(ValueError):
        encoder.encode(20)  # Even numbers rejected


def test_sat_solver_timeout():
    encoder = SchoolbookSATEncoder()
    # 48-bit semiprime with bp=24, bq=24 will not solve in 0.05s
    cnf, mapping = encoder.encode(281476922870851)
    solver = SATSolverAdapter(solver_name="glucose4")
    res = solver.solve(cnf, mapping, timeout_seconds=0.05)
    assert res.timed_out is True
    assert res.satisfiable is None
    assert res.factors == []

