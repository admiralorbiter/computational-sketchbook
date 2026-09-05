"""Canary tests for Track C: C-CANARY-1, C-CANARY-2, and C-CANARY-3."""

from pathlib import Path
import pytest
from nsb.tracks.partial_information.bridge import PartialInformationBridge
from nsb.benchmarks.corpus import load_public_instances
from nsb.verifier.leakage import audit_path_access


def test_c_canary_1_oracle_msb_recovery():
    """C-CANARY-1: Oracle MSB with sufficient information (50%) recovers exact factor."""
    instances = load_public_instances(".", "v001_smoke", "smoke")
    c_inst = next((i for i in instances if i.family == "C"), None)
    assert c_inst is not None

    N = int(c_inst.N)
    oracle = c_inst.metadata["oracle"]
    msb_val = oracle["msb_value"]
    shift = oracle["shift"]
    factor_bits = oracle["factor_bit_length"]

    bridge = PartialInformationBridge()
    res = bridge.recover_from_oracle_msb(
        N=N,
        msb_value=msb_val,
        shift=shift,
        factor_bit_length=factor_bits,
        no_fallback=True,
    )

    assert res.success is True
    assert res.verification is not None
    assert res.verification.verified is True
    assert len(res.factors) == 2



def test_c_canary_2_insufficient_information_fails_cleanly():
    """C-CANARY-2: Insufficient information cleanly reports failure rather than hallucinating."""
    instances = load_public_instances(".", "v001_smoke", "smoke")
    c_inst = next((i for i in instances if i.family == "C"), None)
    assert c_inst is not None

    N = int(c_inst.N)
    oracle = c_inst.metadata["oracle"]
    factor_bits = oracle["factor_bit_length"]

    # Provide only 1 bit of information (shift = factor_bits - 1)
    fake_msb = 1
    shift = factor_bits - 1

    bridge = PartialInformationBridge()
    res = bridge.recover_from_oracle_msb(
        N=N,
        msb_value=fake_msb,
        shift=shift,
        factor_bit_length=factor_bits,
    )

    assert res.success is False
    assert res.verification is None
    assert "Insufficient information" in res.error or "Root finding did not produce" in res.error


def test_c_canary_3_sealed_boundary_leakage_audit():
    """C-CANARY-3: Attempt to access sealed truth fails audit."""
    sealed_dir = Path("benchmarks/sealed/v001_smoke/smoke")
    unauthorized_path = sealed_dir / "truth.jsonl"

    audit_res = audit_path_access([unauthorized_path], sealed_dir)
    assert audit_res.passed is False
    assert len(audit_res.violations) == 1
    assert "Unauthorized path access to sealed storage" in audit_res.violations[0]
