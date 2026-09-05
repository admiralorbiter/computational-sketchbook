"""Tests verifying alignment of FrozenSearchOptimizer with criteria."""

import inspect
from nsb.tracks.algebraic_evolution.search import FrozenSearchOptimizer


def test_frozen_search_optimizer_signature_and_bounds():
    optimizer = FrozenSearchOptimizer(budget=50)

    # Verify optimize() does NOT accept seed
    sig = inspect.signature(optimizer.optimize)
    assert "seed" not in sig.parameters, "Seed parameter must be removed from optimize()"

    # Verify systematic evaluation runs
    N = 10403
    cand = optimizer.optimize(N, degree=3)
    assert cand.evaluations_run <= 50
    assert cand.evaluations_run > 1
