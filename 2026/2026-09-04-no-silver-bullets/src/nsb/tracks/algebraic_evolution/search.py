"""Frozen candidate search algorithm for Track B (Evolved Algebraic Representations).

Implements systematic translation and linear rotation search around canonical base-m:
- Translations: m' = m + k
- Rotations: f1(x) + (u*x + v)*(x - m)
- Selection objective: joint minimization of Level B1 logarithmic norm and Murphy alpha
- Fixed evaluation budget of 50 candidates per modulus
"""

import math
from typing import Any, Dict, List, Optional, Tuple
import gmpy2
from pydantic import BaseModel, Field

from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
    generate_systematic_representation_grid,
)
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator
from nsb.tracks.algebraic_evolution.murphy import compute_murphy_alpha


class SearchOptimizedCandidate(BaseModel):
    """Metadata for a search-optimized polynomial pair."""

    pair: PolynomialPair
    log_norm: float
    alpha: float
    score: float
    evaluations_run: int
    operation: str
    evaluated_operations: List[str] = Field(default_factory=list)


class FrozenSearchOptimizer:
    """Deterministic, preregistered polynomial candidate search optimizer."""

    def __init__(
        self,
        budget: int = 50,
        translation_radius: int = 5,
        rotation_u_bound: int = 2,
        rotation_v_bound: int = 2,
    ):
        self.budget = budget
        self.translation_radius = translation_radius
        self.rotation_u_bound = rotation_u_bound
        self.rotation_v_bound = rotation_v_bound
        self.evaluator = AlgebraicEvaluator(small_primes_bound=250)

    def optimize(
        self,
        N: int,
        degree: int = 3,
    ) -> SearchOptimizedCandidate:
        """Find the optimal degree-d polynomial pair for modulus N.

        Evaluates a deterministic systematic grid of up to 35 candidate pairs
        (1 canonical base-m + 10 translations + 24 linear rotations), capped
        by the evaluation budget.
        """
        grid = generate_systematic_representation_grid(
            N,
            degree=degree,
            translation_radius=self.translation_radius,
            rotation_u_bound=self.rotation_u_bound,
            rotation_v_bound=self.rotation_v_bound,
        )

        canonical_base, _ = grid[0]
        base_norm = self.evaluator.score_proxy_b1(canonical_base, sample_bound=50)
        base_alpha = compute_murphy_alpha(canonical_base.f1_coeffs, prime_bound=2000)
        base_score = base_norm + base_alpha

        best_pair = canonical_base
        best_norm = base_norm
        best_alpha = base_alpha
        best_score = base_score
        best_op = "canonical_base_m"

        evals_count = 0
        evaluated_ops: List[str] = []
        for cand, op_name in grid:
            if evals_count >= self.budget:
                break

            is_valid, _ = self.evaluator.validate_b0(cand, N)
            if not is_valid:
                continue

            evaluated_ops.append(op_name)
            norm = self.evaluator.score_proxy_b1(cand, sample_bound=50)
            alpha = compute_murphy_alpha(cand.f1_coeffs, prime_bound=2000)
            score = norm + alpha
            evals_count += 1

            if score < best_score:
                best_score = score
                best_norm = norm
                best_alpha = alpha
                best_pair = cand
                best_op = op_name

        return SearchOptimizedCandidate(
            pair=best_pair,
            log_norm=best_norm,
            alpha=best_alpha,
            score=round(best_score, 4),
            evaluations_run=evals_count,
            operation=best_op,
            evaluated_operations=evaluated_ops,
        )
