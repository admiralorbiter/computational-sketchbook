"""Unit tests for Track A Parametric Grid runner and diagnostics."""

import pytest
from nsb.tracks.tensor_lattice.sampler import BabaiSchnorrLatticeSampler
from nsb.tracks.tensor_lattice.grid import run_grid_point, run_track_a_grid


def test_babai_schnorr_diagnostics():
    """Verify that sample_relations_with_diagnostics populates all required metrics."""
    sampler = BabaiSchnorrLatticeSampler(factor_base_size=15, scale_c=1000)
    N = 3233  # 61 * 53 (12-bit)
    relations, diag = sampler.sample_relations_with_diagnostics(N, max_candidates=50)

    assert "candidates_tested" in diag
    assert "mean_babai_distance" in diag
    assert "mean_l1_norm" in diag
    assert "mean_l2_norm" in diag
    assert "mean_diff_bits" in diag
    assert "mean_residual_bits" in diag
    assert "candidate_entropy" in diag
    assert "duplicate_rate" in diag

    assert diag["candidates_tested"] > 0
    assert diag["mean_babai_distance"] >= 0.0
    assert diag["mean_l1_norm"] >= 0.0
    assert diag["candidate_entropy"] >= 0.0


def test_run_grid_point():
    """Verify run_grid_point executes candidate and baseline comparisons."""
    N = 3233
    bits = 12
    res = run_grid_point(N=N, bits=bits, fb_size=10, scale_c=500, budget=40)
    assert res.bits == 12
    assert res.N == 3233
    assert res.candidate_candidates_tested > 0
    assert res.advantage_ratio >= 0.0
