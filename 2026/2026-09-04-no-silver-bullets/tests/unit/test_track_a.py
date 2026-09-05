"""Unit tests for Track A: Schnorr lattice, sampler, and F2 linear dependencies."""

import pytest
from nsb.tracks.tensor_lattice.lattice import build_schnorr_lattice, get_factor_base
from nsb.tracks.tensor_lattice.sampler import check_smooth_and_factor
from nsb.tracks.tensor_lattice.relation import solve_f2_dependencies


def test_get_factor_base():
    fb = get_factor_base(5)
    assert fb == [2, 3, 5, 7, 11]


def test_build_schnorr_lattice():
    fb = [2, 3, 5]
    N = 77
    basis = build_schnorr_lattice(N, fb, scale_c=100)
    assert len(basis) == 3
    assert len(basis[0]) == 4



def test_check_smooth_and_factor():
    fb = [2, 3, 5]
    res = check_smooth_and_factor(18, fb)  # 18 = 2 * 3^2
    assert res == [1, 2, 0]

    assert check_smooth_and_factor(7, fb) is None


def test_solve_f2_dependencies():
    # 3 rows, 2 columns
    # row 0: [1, 0]
    # row 1: [0, 1]
    # row 2: [1, 1] -> row0 + row1 + row2 = [0, 0] mod 2
    matrix = [
        [1, 0],
        [0, 1],
        [1, 1],
    ]
    dependencies = solve_f2_dependencies(matrix)
    assert len(dependencies) >= 1
    # Check that sum of combo is indeed even
    for combo in dependencies:
        s0 = sum(matrix[idx][0] for idx in combo) % 2
        s1 = sum(matrix[idx][1] for idx in combo) % 2
        assert s0 == 0 and s1 == 0
