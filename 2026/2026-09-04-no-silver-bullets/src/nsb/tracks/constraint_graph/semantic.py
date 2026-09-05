"""Semantic equivalence verification for Track D constraint encodings."""

from typing import Dict, List, Set, Tuple
from pysat.solvers import Solver
from nsb.tracks.constraint_graph.encoder import SchoolbookSATEncoder


class SemanticEquivalenceResult:
    def __init__(self, equivalent: bool, models_found: int, valid_factor_pairs: Set[Tuple[int, int]], error: str = ""):
        self.equivalent = equivalent
        self.models_found = models_found
        self.valid_factor_pairs = valid_factor_pairs
        self.error = error


def verify_encoding_semantic_equivalence(
    encoder: SchoolbookSATEncoder,
    p_true: int,
    q_true: int,
    solver_name: str = "cadical195",
) -> SemanticEquivalenceResult:
    """Verify that an encoding generates all and only valid factor pairs for N = p_true * q_true.

    For small bit sizes (8 to 24 bits), enumerates all satisfying models.
    """
    if p_true > q_true:
        p_true, q_true = q_true, p_true
    N = p_true * q_true

    bp = p_true.bit_length()
    bq = q_true.bit_length()

    cnf, mapping = encoder.encode(N, bp=bp, bq=bq)

    recovered_pairs: Set[Tuple[int, int]] = set()
    models_count = 0

    with Solver(name=solver_name, bootstrap_with=cnf) as solver:
        for model in solver.enum_models():
            models_count += 1
            model_set = set(model)
            p_vars = mapping["p_vars"]
            q_vars = mapping["q_vars"]

            p_val = 0
            for i, var in enumerate(p_vars):
                if var in model_set:
                    p_val |= (1 << i)

            q_val = 0
            for j, var in enumerate(q_vars):
                if var in model_set:
                    q_val |= (1 << j)

            # Check that model represents a valid factor pair
            if p_val * q_val != N:
                return SemanticEquivalenceResult(
                    equivalent=False,
                    models_found=models_count,
                    valid_factor_pairs=recovered_pairs,
                    error=f"Model produced invalid product: {p_val} * {q_val} != {N}",
                )

            if p_val <= 1 or q_val <= 1:
                return SemanticEquivalenceResult(
                    equivalent=False,
                    models_found=models_count,
                    valid_factor_pairs=recovered_pairs,
                    error=f"Model produced trivial factor: p={p_val}, q={q_val}",
                )

            norm_pair = (p_val, q_val) if p_val <= q_val else (q_val, p_val)
            recovered_pairs.add(norm_pair)

    # Check that true factor pair is present
    expected_pair = (p_true, q_true)
    if expected_pair not in recovered_pairs:
        return SemanticEquivalenceResult(
            equivalent=False,
            models_found=models_count,
            valid_factor_pairs=recovered_pairs,
            error=f"Encoding failed to represent true factor pair: {expected_pair}",
        )

    return SemanticEquivalenceResult(
        equivalent=True,
        models_found=models_count,
        valid_factor_pairs=recovered_pairs,
    )
