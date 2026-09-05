"""Canary tests for Track A: A-CANARY-1, A-CANARY-2, and A-CANARY-3."""

from pathlib import Path
import pytest
from nsb.tracks.tensor_lattice.lattice import get_factor_base
from nsb.tracks.tensor_lattice.sampler import (
    BabaiSchnorrLatticeSampler,
    SqrtNeighborhoodSmoothnessSampler,
)
from nsb.tracks.tensor_lattice.relation import extract_factors_from_relations
from nsb.verifier.factor import verify_factors
from nsb.verifier.leakage import audit_path_access


def test_a_canary_1_deterministic_relation():
    """A-CANARY-1: Handcrafted tiny modulus yielding at least one verified valid Schnorr CVP relation."""
    N = 143  # 11 * 13
    sampler = BabaiSchnorrLatticeSampler(factor_base_size=8, scale_c=3)
    relations = sampler.sample_relations(N, max_candidates=100)

    assert len(relations) >= 1
    # Check that u = +/- diff mod N
    for r in relations:
        u = r["u"]
        diff = r["diff"]
        sign = r["sign"]
        expected_diff = (u if sign == 0 else -u) % N
        assert (diff % N == expected_diff) or ((-diff) % N == expected_diff)


def test_a_canary_2_baseline_factor_extraction():
    """A-CANARY-2: CVP relation extraction reaches exact factor on non-close balanced semiprime without near-square bias."""
    # Positive control: 20-bit non-close balanced semiprime (641 * 1061 = 680101, delta = 420 >> N^0.25)
    p_true = 641
    q_true = 1061
    N = p_true * q_true
    fb = get_factor_base(18)

    sampler = BabaiSchnorrLatticeSampler(factor_base_size=18, scale_c=4)
    relations = sampler.sample_relations(N, max_candidates=3000)

    assert len(relations) >= len(fb) + 2, f"Insufficient relations collected: {len(relations)}"

    # Extract exact factors deterministically via GF(2) linear dependency solver
    success, factors, verif = extract_factors_from_relations(relations, N, fb)
    assert success is True, "Failed to extract factors from Schnorr CVP relations"
    assert factors is not None
    assert set(factors) == {p_true, q_true}
    assert verif is not None
    assert verif.verified is True



def test_a_canary_3_no_leak():
    """A-CANARY-3: Sealed truth access fails audit."""
    sealed_dir = Path("benchmarks/sealed/v001_smoke/smoke")
    secret_path = sealed_dir / "truth.jsonl"
    audit_res = audit_path_access([secret_path], sealed_dir)
    assert audit_res.passed is False
    assert len(audit_res.violations) == 1
