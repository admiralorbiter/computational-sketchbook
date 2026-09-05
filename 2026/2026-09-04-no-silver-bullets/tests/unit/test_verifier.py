"""Unit tests for exact factor verifier and partial information evaluator."""

import pytest
from nsb.verifier.factor import verify_factors
from nsb.verifier.partial import PartialConstraint, evaluate_partial_constraints


def test_verify_factors_success():
    p = 65537
    q = 65539  # 65539 is prime
    N = p * q
    res = verify_factors(N, p, q)
    assert res.verified is True
    assert res.status == "SUCCESS"
    assert res.factors == [str(p), str(q)]

    # Single factor test
    res2 = verify_factors(N, p)
    assert res2.verified is True
    assert res2.status == "SUCCESS"


def test_verify_factors_trivial():
    res = verify_factors(15, 1, 15)
    assert res.verified is False
    assert res.status == "TRIVIAL"


def test_verify_factors_invalid_product():
    res = verify_factors(100, 7, 13)
    assert res.verified is False
    assert res.status == "INVALID_PRODUCT"


def test_verify_factors_composite():
    # 4 * 9 = 36, composite factors
    res = verify_factors(36, 4, 9, require_prime=True)
    assert res.verified is False
    assert res.status == "COMPOSITE_FACTOR"

    # With require_prime=False
    res_nonprime = verify_factors(36, 4, 9, require_prime=False)
    assert res_nonprime.verified is True


def test_evaluate_partial_constraints():
    p = 1009
    q = 1013

    constraints = [
        # Correct bit block
        PartialConstraint(
            constraint_type="bit_block",
            target="p",
            params={"start": 0, "end": 4, "value": p & 0xF},
        ),
        # Wrong bit block
        PartialConstraint(
            constraint_type="bit_block",
            target="p",
            params={"start": 0, "end": 4, "value": (p & 0xF) ^ 1},
        ),
        # Correct interval
        PartialConstraint(
            constraint_type="interval",
            target="p",
            params={"lower": 1000, "upper": 1020},
        ),
        # Correct congruence
        PartialConstraint(
            constraint_type="congruence",
            target="p",
            params={"modulus": 10, "residue": p % 10},
        ),
    ]

    score = evaluate_partial_constraints(constraints, p, q)
    assert score.total_constraints == 4
    assert score.valid_constraints == 3
    assert score.false_constraints == 1
    assert score.accuracy == 0.75
    assert score.information_gain_bits > 0.0
