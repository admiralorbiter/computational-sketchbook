"""Track A Parametric Grid Runner: Relation-Collapse Surface Exploration.

Explores (factor_base_size x scale_c x candidate_budget) across multiple bit lengths
to characterize relation yield, Babai approximation distance, exponent vector norms,
smoothness residuals, candidate entropy, and baseline comparative advantage.
"""

from dataclasses import asdict, dataclass
import math
import time
from typing import Any, Dict, List, Optional
from nsb.tracks.tensor_lattice.sampler import (
    BabaiSchnorrLatticeSampler,
    SqrtNeighborhoodSmoothnessSampler,
)


@dataclass
class GridPointResult:
    bits: int
    N: int
    fb_size: int
    scale_c: int
    budget: int
    # Candidate metrics
    candidate_relations: int
    candidate_candidates_tested: int
    candidate_wall_seconds: float
    candidate_rel_per_sec: float
    mean_babai_distance: float
    mean_l1_norm: float
    mean_l2_norm: float
    max_linf_norm: int
    mean_diff_bits: float
    mean_residual_bits: float
    smooth_rate: float
    duplicate_rate: float
    candidate_entropy: float
    # Baseline comparison
    baseline_relations: int
    baseline_wall_seconds: float
    baseline_rel_per_sec: float
    advantage_ratio: float


def run_grid_point(
    N: int,
    bits: int,
    fb_size: int = 25,
    scale_c: int = 1000,
    budget: int = 500,
) -> GridPointResult:
    """Execute a single grid evaluation point with full diagnostics and baseline comparison."""
    # 1. Candidate: Babai Schnorr Lattice Sampler
    cand_sampler = BabaiSchnorrLatticeSampler(factor_base_size=fb_size, scale_c=scale_c)
    cand_relations, cand_diag = cand_sampler.sample_relations_with_diagnostics(N, max_candidates=budget)

    # 2. Baseline: Sqrt Neighborhood Control
    base_sampler = SqrtNeighborhoodSmoothnessSampler(factor_base_size=fb_size)
    t0 = time.perf_counter()
    base_relations = base_sampler.sample_relations(N, max_candidates=budget)
    base_wall = time.perf_counter() - t0
    base_rate = len(base_relations) / base_wall if base_wall > 0 else 0.0

    cand_rate = cand_diag["relation_rate"]
    if base_rate > 0:
        adv_ratio = cand_rate / base_rate
    elif cand_rate > 0:
        adv_ratio = 999.0
    else:
        adv_ratio = 1.0 if len(cand_relations) == len(base_relations) else 0.0

    return GridPointResult(
        bits=bits,
        N=N,
        fb_size=fb_size,
        scale_c=scale_c,
        budget=budget,
        candidate_relations=len(cand_relations),
        candidate_candidates_tested=cand_diag["candidates_tested"],
        candidate_wall_seconds=cand_diag["wall_seconds"],
        candidate_rel_per_sec=cand_rate,
        mean_babai_distance=cand_diag["mean_babai_distance"],
        mean_l1_norm=cand_diag["mean_l1_norm"],
        mean_l2_norm=cand_diag["mean_l2_norm"],
        max_linf_norm=cand_diag["max_linf_norm"],
        mean_diff_bits=cand_diag["mean_diff_bits"],
        mean_residual_bits=cand_diag["mean_residual_bits"],
        smooth_rate=cand_diag["smooth_rate"],
        duplicate_rate=cand_diag["duplicate_rate"],
        candidate_entropy=cand_diag["candidate_entropy"],
        baseline_relations=len(base_relations),
        baseline_wall_seconds=base_wall,
        baseline_rel_per_sec=base_rate,
        advantage_ratio=adv_ratio,
    )


def fit_residual_scaling_model(grid_results: List[GridPointResult]) -> Dict[str, Any]:
    """Fit empirical linear regression model: residual_bits ~ beta_0 + beta_1 * modulus_bits.

    Also computes empirical smooth probability vs residual bit size.
    """
    if not grid_results:
        return {}

    xs = [float(r.bits) for r in grid_results]
    ys = [float(r.mean_residual_bits) for r in grid_results]
    n = len(xs)

    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    ss_xx = sum((x - mean_x) ** 2 for x in xs)
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    ss_yy = sum((y - mean_y) ** 2 for y in ys)

    slope = ss_xy / ss_xx if ss_xx > 0 else 0.0
    intercept = mean_y - slope * mean_x
    r_squared = (ss_xy ** 2) / (ss_xx * ss_yy) if (ss_xx > 0 and ss_yy > 0) else 0.0

    mean_res_by_bits = {
        b: round(
            sum(r.mean_residual_bits for r in grid_results if r.bits == b)
            / sum(1 for r in grid_results if r.bits == b),
            2,
        )
        for b in sorted(set(r.bits for r in grid_results))
    }

    return {
        "slope_bits_per_modulus_bit": round(slope, 4),
        "intercept": round(intercept, 4),
        "r_squared": round(r_squared, 4),
        "model_equation": f"residual_bits = {slope:.2f} * modulus_bits + ({intercept:.2f}) [R^2 = {r_squared:.3f}]",
        "sample_points": len(grid_results),
        "mean_residual_by_bits": mean_res_by_bits,
    }


def run_track_a_grid(
    corpus_samples: List[Dict[str, Any]],
    fb_sizes: Optional[List[int]] = None,
    scales: Optional[List[int]] = None,
    budgets: Optional[List[int]] = None,
    scale_cs: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Run full parametric grid over instances."""
    fb_sizes = fb_sizes or [16, 25, 40]
    scales = scales or scale_cs or [500, 1000, 2000]
    budgets = budgets or [500, 2000]

    grid_results: List[GridPointResult] = []

    for item in corpus_samples:
        N = int(item.get("N", item.get("n")))
        bits = int(item["bits"])
        for fb in fb_sizes:
            for sc in scales:
                for bgt in budgets:
                    res = run_grid_point(N=N, bits=bits, fb_size=fb, scale_c=sc, budget=bgt)
                    grid_results.append(res)

    model = fit_residual_scaling_model(grid_results)

    return {
        "total_points": len(grid_results),
        "results": [asdict(r) for r in grid_results],
        "model": model,
    }

