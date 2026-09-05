"""Unit tests for classical factorization baselines: Fermat, Pollard p-1, and Pollard rho."""

import pytest
from nsb.baselines.fermat import FermatSolver
from nsb.baselines.pollard_pm1 import PollardPM1Solver
from nsb.baselines.pollard_rho import PollardRhoSolver
from nsb.baselines.portfolio import get_baseline_solver, run_baseline_solve


def test_fermat_solver_close_primes():
    solver = FermatSolver()
    p = 65537
    q = 65539
    N = p * q
    res = solver.factor(N, max_seconds=2.0)
    assert res.success is True
    assert set(res.factors) == {p, q}
    assert res.steps <= 5


def test_fermat_solver_timeout_or_limit():
    solver = FermatSolver()
    # distant primes
    p = 10007
    q = 104729
    N = p * q
    res = solver.factor(N, max_seconds=0.1, max_steps=50)
    assert res.success is False
    assert res.steps == 50


def test_pollard_pm1_solver():
    solver = PollardPM1Solver()
    # 196799 is prime, 196799 - 1 = 2 * 79 * 1245... smooth primes <= 500
    p = 196799
    q = 65537
    N = p * q
    res = solver.factor(N, max_seconds=2.0, b1_bound=1000)
    assert res.success is True
    assert p in res.factors or q in res.factors


def test_pollard_rho_solver():
    solver = PollardRhoSolver()
    p = 1009
    q = 1013
    N = p * q
    res = solver.factor(N, max_seconds=2.0)
    assert res.success is True
    assert set(res.factors) == {p, q}


def test_run_baseline_solve_pipeline():
    p = 65537
    q = 65539
    N = p * q
    factor_res, verif_res = run_baseline_solve("fermat", N)
    assert factor_res.success is True
    assert verif_res.verified is True
    assert verif_res.status == "SUCCESS"
