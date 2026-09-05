"""CADO-NFS Mature Baseline & Adapter Subsystem.

Provides integration with CADO-NFS development commit 73ca6b6847118b05b15eeec27c86f45cef82a19e
for realistic polynomial selection, neutral Murphy-E scoring, and lattice sieving.
"""

from nsb.baselines.cado_nfs.models import (
    NfsPolynomialPair,
    CadoPolyselectResult,
    CadoScoreResult,
    CadoSieveResult,
)
from nsb.baselines.cado_nfs.parser import (
    parse_cado_poly_file,
    parse_cado_score_output,
    parse_las_output,
)
from nsb.baselines.cado_nfs.verifier import verify_nfs_polynomial_pair
from nsb.baselines.cado_nfs.environment import CadoEnvironment
from nsb.baselines.cado_nfs.adapter import CadoSubprocessAdapter
from nsb.baselines.cado_nfs.scorer import CadoScorer
from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector, CandidatePolynomialSelector
from nsb.baselines.cado_nfs.sieve import CadoRelationCollector
from nsb.baselines.cado_nfs.profiles import (
    CadoParameterProfile,
    CADO_PARAMS_C60,
    CANARY_PLUMBING_C60,
    get_cado_profile,
)

__all__ = [
    "NfsPolynomialPair",
    "CadoPolyselectResult",
    "CadoScoreResult",
    "CadoSieveResult",
    "parse_cado_poly_file",
    "parse_cado_score_output",
    "parse_las_output",
    "verify_nfs_polynomial_pair",
    "CadoEnvironment",
    "CadoSubprocessAdapter",
    "CadoScorer",
    "CadoPolynomialSelector",
    "CandidatePolynomialSelector",
    "CadoRelationCollector",
    "CadoParameterProfile",
    "CADO_PARAMS_C60",
    "CANARY_PLUMBING_C60",
    "get_cado_profile",
]
