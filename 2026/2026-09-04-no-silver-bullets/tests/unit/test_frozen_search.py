"""Tests for FrozenSearchOptimizer candidate generation and deterministic behavior."""

from nsb.tracks.algebraic_evolution.search import FrozenSearchOptimizer
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator


def test_frozen_search_optimizer_validity():
    optimizer = FrozenSearchOptimizer(budget=50)
    evaluator = AlgebraicEvaluator()
    N = 10403  # 101 * 103

    candidate = optimizer.optimize(N, degree=3)

    assert candidate.evaluations_run <= 50
    assert candidate.pair.degree == 3

    # Mathematical validity B0
    is_valid, msg = evaluator.validate_b0(candidate.pair, N)
    assert is_valid, f"Candidate failed B0 validity: {msg}"

    # Log norm score
    assert candidate.log_norm > 0.0
    assert candidate.score is not None


def test_frozen_search_optimizer_determinism():
    optimizer = FrozenSearchOptimizer(budget=50)
    N = 11849  # 79 * 150 (Wait, 11849)

    res1 = optimizer.optimize(N, degree=3)
    res2 = optimizer.optimize(N, degree=3)

    assert res1.pair.f1_coeffs == res2.pair.f1_coeffs
    assert res1.pair.m == res2.pair.m
    assert res1.score == res2.score
    assert res1.operation == res2.operation
