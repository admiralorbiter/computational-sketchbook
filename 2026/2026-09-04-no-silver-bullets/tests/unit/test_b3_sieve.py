"""Unit tests for Track B downstream B3 homogeneous sieve evaluation."""

import pytest
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator


def test_evaluate_paired_b3():
    evaluator = AlgebraicEvaluator(small_primes_bound=250)
    N = 3233  # 61 * 53
    res = evaluator.evaluate_paired_b3(N, bound_a=30, bound_b=5)

    assert "deg2" in res
    assert "deg3" in res
    assert "n11_both" in res
    assert "n10_deg3_only" in res
    assert "n01_deg2_only" in res
    assert "n00_neither" in res
    assert "mcnemar_chi2" in res
    assert "mcnemar_pvalue" in res
    assert "yield_diff" in res
    assert res["deg2_pairs"] > 0
    assert res["deg3_pairs"] > 0
    assert res["n11_both"] + res["n10_deg3_only"] + res["n01_deg2_only"] + res["n00_neither"] == res["total_pairs"]
    assert res["yield_gain"] != 999.0
