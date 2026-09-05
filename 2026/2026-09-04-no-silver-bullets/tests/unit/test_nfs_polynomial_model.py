"""Unit tests for NfsPolynomialPair, Sylvester resultant, and mathematical verification."""

import pytest
from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.parser import parse_cado_poly_file
from nsb.baselines.cado_nfs.verifier import (
    bareiss_determinant,
    compute_sylvester_resultant,
    verify_nfs_polynomial_pair,
)


def test_bareiss_determinant():
    # 2x2 matrix
    m2 = [[3, 8], [4, 6]]
    # 3*6 - 8*4 = 18 - 32 = -14
    assert bareiss_determinant(m2) == -14

    # 3x3 identity
    m3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert bareiss_determinant(m3) == 1

    # 4x4 known determinant
    m4 = [
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, -1, 0],
        [0, 1, 0, -1],
    ]
    assert bareiss_determinant(m4) == 4


def test_sylvester_resultant():
    # f1(x) = x^2 + 1 -> coeffs [1, 0, 1]
    # f2(x) = x^2 - 1 -> coeffs [-1, 0, 1]
    # Res(x^2 + 1, x^2 - 1) = 4
    res = compute_sylvester_resultant([1, 0, 1], [-1, 0, 1])
    assert res == 4

    # Linear f2(x) = x - 3 -> [-3, 1]
    # f1(x) = x^2 - 9 -> [-9, 0, 1]
    # Common root 3, so resultant must be 0
    res_common = compute_sylvester_resultant([-9, 0, 1], [-3, 1])
    assert res_common == 0


def test_nfs_polynomial_pair_evaluation():
    # f1(x) = 2 + 3x + 4x^2
    # f2(x) = -5 + x
    pair = NfsPolynomialPair(
        f1_coeffs=[2, 3, 4],
        f2_coeffs=[-5, 1],
        N=12345,
        m=5,
        skew=2.5,
    )
    assert pair.degree1 == 2
    assert pair.degree2 == 1
    assert pair.degree == 2

    # f1(2) = 2 + 6 + 16 = 24
    assert pair.eval_f1(2) == 24
    # f2(2) = -5 + 2 = -3
    assert pair.eval_f2(2) == -3

    # Homogeneous: F1(a, b) = 4 a^2 + 3 a b + 2 b^2
    # F1(2, 3) = 4*(4) + 3*(6) + 2*(9) = 16 + 18 + 18 = 52
    assert pair.eval_f1_homogeneous(2, 3) == 52

    # F2(a, b) = a - 5 b
    # F2(2, 3) = 2 - 15 = -13
    assert pair.eval_f2_homogeneous(2, 3) == -13


def test_cado_poly_file_io_roundtrip():
    original = NfsPolynomialPair(
        f1_coeffs=[-5832, 0, 0, 1],
        f2_coeffs=[-18, 1],
        N=5893,
        m=18,
        skew=1.875,
        metadata={"author": "NSB-Test", "test_id": "42"},
    )
    cado_str = original.to_cado_poly_string()
    assert "n: 5893" in cado_str
    assert "skew: 1.8750" in cado_str
    assert "c0: -5832" in cado_str
    assert "c3: 1" in cado_str
    assert "Y0: -18" in cado_str
    assert "Y1: 1" in cado_str

    # Parse back
    reconstructed = parse_cado_poly_file(cado_str)
    assert reconstructed.f1_coeffs == original.f1_coeffs
    assert reconstructed.f2_coeffs == original.f2_coeffs
    assert reconstructed.N == original.N
    assert reconstructed.m == original.m
    assert abs(reconstructed.skew - original.skew) < 1e-3


def test_verify_nfs_polynomial_pair_valid():
    # Modulus N = 5893, m = 18
    # f1(x) = x^3 - 5832
    # f2(x) = x - 18
    pair = NfsPolynomialPair(
        f1_coeffs=[-5832, 0, 0, 1],
        f2_coeffs=[-18, 1],
        N=5893,
        m=18,
    )
    valid, msg = verify_nfs_polynomial_pair(pair)
    assert valid is True
    assert msg == "Valid NFS polynomial pair"


def test_verify_nfs_polynomial_pair_invalid_degree():
    # Degree 0 polynomial
    pair = NfsPolynomialPair(
        f1_coeffs=[5],
        f2_coeffs=[-18, 1],
        N=5893,
    )
    valid, msg = verify_nfs_polynomial_pair(pair)
    assert valid is False
    assert "degree" in msg


def test_verify_nfs_polynomial_pair_zero_leading_coeff():
    # Leading coefficient 0
    pair = NfsPolynomialPair(
        f1_coeffs=[1, 2, 0],
        f2_coeffs=[-18, 1],
        N=5893,
    )
    valid, msg = verify_nfs_polynomial_pair(pair)
    assert valid is False
    assert "Leading coefficient" in msg


def test_verify_nfs_polynomial_pair_non_primitive():
    # Content > 1: gcd(2, 4, 6) = 2
    pair = NfsPolynomialPair(
        f1_coeffs=[2, 4, 6],
        f2_coeffs=[-18, 1],
        N=5893,
    )
    valid, msg = verify_nfs_polynomial_pair(pair)
    assert valid is False
    assert "not primitive" in msg


def test_verify_nfs_polynomial_pair_resultant_failure():
    # Resultant does not divide N
    pair = NfsPolynomialPair(
        f1_coeffs=[1, 0, 1],  # x^2 + 1
        f2_coeffs=[-1, 0, 1],  # x^2 - 1 -> Res = 4
        N=5893,  # 4 % 5893 != 0
    )
    valid, msg = verify_nfs_polynomial_pair(pair)
    assert valid is False
    assert "Resultant" in msg
