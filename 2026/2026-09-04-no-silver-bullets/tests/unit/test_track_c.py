"""Unit tests for Track C: LLL reduction and small-root finding."""

from fractions import Fraction
import pytest
from nsb.tracks.partial_information.lattice_root import lll_reduction, solve_univariate_small_root_linear


def test_lll_reduction_basic():
    # Standard 2x2 lattice basis
    basis = [
        [Fraction(1), Fraction(2)],
        [Fraction(3), Fraction(4)],
    ]
    reduced = lll_reduction(basis)
    assert len(reduced) == 2
    # Verify basis is not empty
    assert any(x != 0 for x in reduced[0])


def test_solve_univariate_small_root():
    # p = 10007, q = 10009 -> N = 100160063
    p = 10007
    q = 10009
    N = p * q

    # Known upper bits: p_bits = 14
    # Let known be upper 7 bits: shift = 7
    shift = 7
    msb_val = p >> shift
    P0 = msb_val << shift
    X = 1 << shift

    root = solve_univariate_small_root_linear(N, P0, X)
    assert root is not None
    assert (P0 + root in (p, q))
    assert N % (P0 + root) == 0

