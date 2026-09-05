"""Track A: Tensor/Lattice Relation Discovery and Schnorr-Style Factoring."""

from nsb.tracks.tensor_lattice.lattice import (
    build_schnorr_lattice,
    get_factor_base,
)
from nsb.tracks.tensor_lattice.sampler import (
    BabaiSchnorrLatticeSampler,
    SqrtNeighborhoodSmoothnessSampler,
    check_smooth_and_factor,
)
from nsb.tracks.tensor_lattice.relation import (
    extract_factors_from_relations,
    solve_f2_dependencies,
)

__all__ = [
    "build_schnorr_lattice",
    "get_factor_base",
    "BabaiSchnorrLatticeSampler",
    "SqrtNeighborhoodSmoothnessSampler",
    "check_smooth_and_factor",
    "extract_factors_from_relations",
    "solve_f2_dependencies",
]
