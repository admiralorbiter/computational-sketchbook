"""Integration test for R3-G1 discrete CADO LAS sieving canary.

Executes actual discrete las binary on a known polynomial system if CADO is available;
skips gracefully if environment is not set up.
"""

import pytest
from nsb.baselines.cado_nfs.environment import CadoEnvironment
from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.sieve import CadoRelationCollector
from nsb.experiments.r3_nfs_baseline_runner import SMOKE_60_DIGIT_COMPOSITE, VERIFIED_C60_POLY
from nsb.baselines.cado_nfs.verifier import verify_nfs_polynomial_pair

env = CadoEnvironment()
cado_available, cado_msg = env.validate_for_canonical_execution()


@pytest.mark.skipif(not cado_available, reason=f"CADO-NFS environment unavailable: {cado_msg}")
def test_cado_las_canary():
    # Verify the polynomial mathematically before executing LAS
    valid, msg = verify_nfs_polynomial_pair(VERIFIED_C60_POLY)
    assert valid is True, f"C60 polynomial verification failed: {msg}"

    collector = CadoRelationCollector(threads=1)
    res = collector.collect_relations(
        poly=VERIFIED_C60_POLY,
        q_start=500_000,
        q_range=200,
        i_param=11,
        lim0=500_000,
        lim1=1_000_000,
        lpb0=22,
        lpb1=22,
        run_makefb=True,
        validate_with_check_rels=True,
        timeout_seconds=120.0,
    )
    assert res.unique_relations > 0, "Canary must produce >0 relations"
    assert res.cpu_seconds > 0.0
    assert res.relations_hash != "", "Relations hash must be non-empty"
    assert res.checked_with_check_rels is True, "Canary relations must be verified with check_rels"
