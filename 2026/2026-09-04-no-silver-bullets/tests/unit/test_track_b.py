"""Unit tests for Track B: algebraic polynomial representations and evaluation cascade."""

import pytest
from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
)
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator, is_smooth


def test_create_base_m_representation():
    N = 10007 * 10009
    pair = create_base_m_representation(N, degree=2)
    assert pair.degree >= 1
    assert pair.eval_f1(pair.m) == N
    assert pair.eval_f2(pair.m) == 0


def test_is_smooth():
    primes = [2, 3, 5, 7]
    assert is_smooth(1, primes) is True
    assert is_smooth(24, primes) is True  # 2^3 * 3
    assert is_smooth(11, primes) is False  # 11 is prime not in list


def test_algebraic_evaluator_valid_b0():
    N = 143
    pair = create_base_m_representation(N, degree=2)
    evaluator = AlgebraicEvaluator()
    valid, msg = evaluator.validate_b0(pair, N)
    assert valid is True
    assert msg == "VALID"


def test_algebraic_evaluator_proxy_b1():
    N = 143
    pair = create_base_m_representation(N, degree=2)
    evaluator = AlgebraicEvaluator()
    score = evaluator.score_proxy_b1(pair, sample_bound=50)
    assert score > 0.0


def test_algebraic_evaluator_homogeneous_b3():
    N = 143
    pair = create_base_m_representation(N, degree=2)
    evaluator = AlgebraicEvaluator(small_primes_bound=200)
    res = evaluator.homogeneous_sieve_b3(pair, bound_a=20, bound_b=5)
    assert res["total_pairs"] > 0
    assert "smooth_relations" in res
    assert "yield_rate" in res

