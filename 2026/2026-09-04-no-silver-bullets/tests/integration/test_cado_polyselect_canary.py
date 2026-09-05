"""Integration test for R3-G1 CADO polynomial selection canary.

Executes actual discrete polyselect binaries on a ~60-digit smoke composite
if CADO environment is available; skips gracefully if environment is not set up.
"""

import pytest
from nsb.baselines.cado_nfs.environment import CadoEnvironment
from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector
from nsb.baselines.cado_nfs.verifier import verify_nfs_polynomial_pair
from nsb.experiments.r3_nfs_baseline_runner import SMOKE_60_DIGIT_COMPOSITE

env = CadoEnvironment()
cado_available, cado_msg = env.validate_for_canonical_execution()


@pytest.mark.skipif(not cado_available, reason=f"CADO-NFS environment unavailable: {cado_msg}")
def test_cado_polyselect_canary():
    selector = CadoPolynomialSelector(run_ropt=True)
    res = selector.select_polynomial(
        n=SMOKE_60_DIGIT_COMPOSITE,
        degree=5,
        timeout_seconds=300.0,
    )
    assert res.pair.degree1 >= 4
    assert res.pair.degree2 >= 1
    assert res.cpu_seconds > 0.0

    valid, msg = verify_nfs_polynomial_pair(res.pair)
    assert valid is True, f"Polynomial verification failed: {msg}"
