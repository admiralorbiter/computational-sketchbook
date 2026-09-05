"""Track D: Constraint-Graph Inversion and SAT/CSP Multiplier Encodings."""

from nsb.tracks.constraint_graph.encoder import (
    CarrySaveAdderSATEncoder,
    SchoolbookSATEncoder,
    VarManager,
)
from nsb.tracks.constraint_graph.solver import SATSolverAdapter, SATSolverResult
from nsb.tracks.constraint_graph.semantic import (
    SemanticEquivalenceResult,
    verify_encoding_semantic_equivalence,
)

__all__ = [
    "CarrySaveAdderSATEncoder",
    "SchoolbookSATEncoder",
    "VarManager",
    "SATSolverAdapter",
    "SATSolverResult",
    "SemanticEquivalenceResult",
    "verify_encoding_semantic_equivalence",
]
