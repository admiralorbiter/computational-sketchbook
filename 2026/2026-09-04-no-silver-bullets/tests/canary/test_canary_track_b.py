"""Canary tests for Track B: B-CANARY-1, B-CANARY-2, and B-CANARY-3."""

import pytest
from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
)
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator


def test_b_canary_1_invalid_representation_rejected():
    """B-CANARY-1: Feed known-invalid candidate; rejected deterministically at Level B0."""
    N = 143  # 11 * 13
    evaluator = AlgebraicEvaluator()

    # Invalid: common root does not satisfy f1(m) == 0 mod N
    invalid_pair = PolynomialPair(
        f1_coeffs=[1, 2, 3],  # 3x^2 + 2x + 1
        f2_coeffs=[-5, 1],    # x - 5
        m=5,
        degree=2,
        name="invalid_root",
    )
    # 3*(25) + 10 + 1 = 86 != 0 mod 143
    valid, msg = evaluator.validate_b0(invalid_pair, N)
    assert valid is False
    assert "f1(m) != 0 mod N" in msg

    # Invalid: non-primitive (all coefficients divisible by 2)
    non_prim_pair = PolynomialPair(
        f1_coeffs=[286, 0, 2],  # content gcd = 2
        f2_coeffs=[-11, 1],
        m=11,
        degree=2,
        name="non_primitive",
    )
    valid2, msg2 = evaluator.validate_b0(non_prim_pair, N)
    assert valid2 is False
    assert "not primitive" in msg2


def test_b_canary_2_known_valid_representation_accepted():
    """B-CANARY-2: Known valid representation accepted and scored consistently at B0 and B1."""
    N = 3201165293  # 32-bit semiprime from smoke corpus R-032-00001
    evaluator = AlgebraicEvaluator()

    pair = create_base_m_representation(N, degree=2)
    valid, msg = evaluator.validate_b0(pair, N)
    assert valid is True
    assert msg == "VALID"

    score_1 = evaluator.score_proxy_b1(pair, sample_bound=50)
    score_2 = evaluator.score_proxy_b1(pair, sample_bound=50)
    assert score_1 == score_2  # Deterministic score
    assert score_1 > 0.0


def test_b_canary_3_proxy_yield_plumbing():
    """B-CANARY-3: Small synthetic N, deterministic ranking and raw micro-sieve data retention."""
    N = 33233  # 16-bit semiprime (167 * 199) from smoke corpus E-016-00001
    evaluator = AlgebraicEvaluator(small_primes_bound=100)

    pair_d1 = create_base_m_representation(N, degree=1)
    pair_d2 = create_base_m_representation(N, degree=2)

    sieve_d1 = evaluator.micro_sieve_b2(pair_d1, sample_bound=100)
    sieve_d2 = evaluator.micro_sieve_b2(pair_d2, sample_bound=100)

    assert "smooth_relations" in sieve_d1
    assert "yield_rate" in sieve_d1
    assert sieve_d1["total_evals"] == 200
    assert sieve_d2["total_evals"] == 200
    # Data is deterministically produced
    assert isinstance(sieve_d1["yield_rate"], float)
    assert isinstance(sieve_d2["yield_rate"], float)
