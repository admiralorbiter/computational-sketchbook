"""Unit tests for Track C calibration ladder."""

import pytest
from nsb.tracks.partial_information.calibration import (
    generate_oracle_slices,
    run_calibration_ladder,
)


def test_generate_oracle_slices():
    p = 10007  # 14-bit prime
    fractions = [0.25, 0.50, 0.60]
    slices = generate_oracle_slices(p, fractions)
    assert len(slices) == 3
    assert slices[0]["fraction"] == 0.25
    assert slices[1]["fraction"] == 0.50
    assert slices[2]["fraction"] == 0.60
    for s in slices:
        # Reconstruct high bits
        msb = s["msb_value"]
        shift = s["shift"]
        assert msb == (p >> shift)


def test_run_calibration_ladder():
    p = 10007
    q = 10009
    N = p * q
    bits = N.bit_length()
    slices = generate_oracle_slices(p, [0.25, 0.50])
    results = run_calibration_ladder(N, bits, slices)
    assert len(results) == 2
    assert results[0].is_synthetic is False
    assert results[1].is_synthetic is False
    assert results[1].fraction == 0.50
    assert results[1].success is True
