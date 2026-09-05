"""Tests verifying CPU process time accounting in evaluator."""

from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator


def test_evaluate_paired_b3_cpu_seconds_accounting():
    evaluator = AlgebraicEvaluator(small_primes_bound=50)
    N = 10403  # 101 * 103

    res = evaluator.evaluate_paired_b3(N, bound_a=20, bound_b=5)

    assert "deg2_cpu_sec" in res
    assert "deg3_cpu_sec" in res
    assert res["deg2_cpu_sec"] > 0.0
    assert res["deg3_cpu_sec"] > 0.0

    # Verify they match the cpu_seconds reported by each representation's sieve
    assert res["deg2_cpu_sec"] == res["deg2"]["cpu_seconds"]
    assert res["deg3_cpu_sec"] == res["deg3"]["cpu_seconds"]
