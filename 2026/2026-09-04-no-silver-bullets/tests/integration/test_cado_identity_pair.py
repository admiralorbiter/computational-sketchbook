"""Integration test for R3-G2 paired-instrument invariance canary.

Verifies that passing the identical polynomial pair through two evaluation passes
under counterbalanced order yields identical relation counts and identical behavior.
Skips gracefully if CADO environment is unavailable.
"""

import pytest
from nsb.baselines.cado_nfs.environment import CadoEnvironment
from nsb.experiments.r3_nfs_baseline_runner import R3BaselineRunner, VERIFIED_C60_POLY

env = CadoEnvironment()
cado_available, cado_msg = env.validate_for_canonical_execution()


@pytest.mark.skipif(not cado_available, reason=f"CADO-NFS environment unavailable: {cado_msg}")
def test_cado_identity_pair_invariance():
    runner = R3BaselineRunner()
    g2 = runner.run_g2_paired_identity_canary(
        pair=VERIFIED_C60_POLY,
        q_start=500_000,
        q_range=200,
        timeout_seconds=180.0,
    )
    assert g2["passed"] is True
    assert g2["invariance_verified"] is True
    assert g2["unique_relations"] > 0
    assert g2["relation_set_hash"] != "MISMATCH"
    # Exact relation-set SHA-256 matches across A1, B1, B2, A2
    h_a1 = g2["runs"]["A1"]["relations_hash"]
    h_b1 = g2["runs"]["B1"]["relations_hash"]
    h_b2 = g2["runs"]["B2"]["relations_hash"]
    h_a2 = g2["runs"]["A2"]["relations_hash"]
    assert h_a1 == h_b1 == h_b2 == h_a2 != ""
    assert all(r["checked_with_check_rels"] is True for r in g2["runs"].values())
