"""Research Director v0 (proposal-only mode)."""

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from nsb.core.identity import generate_experiment_id


class DirectorProposal(BaseModel):
    proposal_id: str
    parent_experiment: Optional[str]
    track: str
    hypothesis: str
    mechanism: str
    mutations: Dict[str, Any] = Field(default_factory=dict)
    expected_effect: str
    budget: Dict[str, Any]
    stopping_rule: str
    promotion_target: str
    novelty_reason: str


class ResearchDirector:
    """Proposes scientific experiments and mutations without truth access."""

    def __init__(self, mode: str = "proposal_only"):
        if mode != "proposal_only":
            raise ValueError(f"For R0 foundation, director mode must be 'proposal_only', got '{mode}'")
        self.mode = mode

    def propose_next_experiments(
        self,
        latest_metrics: Optional[Dict[str, Any]] = None,
    ) -> List[DirectorProposal]:
        """Generate one structured proposal per research track conforming to R0 protocol."""
        now = datetime.datetime.now(datetime.timezone.utc).date()
        proposals: List[DirectorProposal] = []

        # Inspect judgments if provided
        judge_verdicts = {}
        if latest_metrics:
            for k, v in latest_metrics.items():
                if hasattr(v, "verdict"):
                    judge_verdicts[k] = getattr(v.verdict, "value", str(v.verdict))
                elif isinstance(v, dict) and "verdict" in v:
                    judge_verdicts[k] = str(v["verdict"])

        # Track A proposal
        if judge_verdicts.get("A") == "INCONCLUSIVE":
            prop_a = DirectorProposal(
                proposal_id=generate_experiment_id("A", date=now, suffix="A00002"),
                parent_experiment="EXP-TRACK-A-PILOT-v0.1.0",
                track="A",
                hypothesis="Systematic grid over (factor_base_size x scale_c x candidate_budget) maps the relation collapse boundary on 20-32 bit moduli.",
                mechanism="Babai nearest plane relation yield collapsed at 32b; expanding factor base (25-40) and candidate budget (2000) tests whether relation yield recovers.",
                mutations={"scale_c_grid": [500, 1000, 2000], "factor_base_grid": [16, 25, 40], "candidate_budget": 2000},
                expected_effect="relation_discovery_rate > 0 at 32-bit and >= 1.5x gain over baseline",
                budget={"max_wall_seconds": 60.0, "max_cpu_seconds": 60.0, "max_rss_mb": 1024},
                stopping_rule="stop if 2000 candidates yield 0 relations across all grid points",
                promotion_target="Pilot A-P2",
                novelty_reason="Targeted calibration of relation collapse boundary revealed by PromotionJudge.",
            )
        else:
            prop_a = DirectorProposal(
                proposal_id=generate_experiment_id("A", date=now, suffix="A00001"),
                parent_experiment=None,
                track="A",
                hypothesis="Scaling parameter C=5000 in Schnorr lattice increases smooth relation yield by >= 1.5x at 48-64 bits.",
                mechanism="Higher logarithmic scaling improves balance between prime-base weights and modulus vector.",
                mutations={"scale_c": 5000, "factor_base_size": 25},
                expected_effect="unique_valid_relations / cpu_second >= 1.5 * baseline",
                budget={"max_wall_seconds": 30.0, "max_cpu_seconds": 30.0, "max_rss_mb": 1024},
                stopping_rule="stop if 500 candidates yield 0 relations",
                promotion_target="Pilot A-P1",
                novelty_reason="First exploration of scaling parameter mutation.",
            )
        proposals.append(prop_a)

        # Track B proposal
        if judge_verdicts.get("B") == "CANDIDATE":
            prop_b = DirectorProposal(
                proposal_id=generate_experiment_id("B", date=now, suffix="B00002"),
                parent_experiment="EXP-TRACK-B-PILOT-v0.1.0",
                track="B",
                hypothesis="B3 homogeneous sieving on cubic candidates yields >= 25% smooth relations over quadratic base-m on 32-64 bits.",
                mechanism="Cubic representation verified in B1 log-norm; Level B3 evaluates true downstream algebraic-sieve relation rate.",
                mutations={"eval_level": "B3", "bound_a": 50, "bound_b": 20, "factor_base_size": 32},
                expected_effect="smooth_relations_per_sec >= 1.25 * degree_2_yield",
                budget={"max_wall_seconds": 45.0, "max_cpu_seconds": 45.0, "max_rss_mb": 1024},
                stopping_rule="stop if B3 smooth relation yield is zero after 1000 pairs",
                promotion_target="Pilot B-P2",
                novelty_reason="Evaluating downstream B3 smooth yield per frozen protocol requirement.",
            )
        else:
            prop_b = DirectorProposal(
                proposal_id=generate_experiment_id("B", date=now, suffix="B00001"),
                parent_experiment=None,
                track="B",
                hypothesis="Degree-3 base-m representation achieves lower log-norm proxy score than degree-2 at 64 bits.",
                mechanism="Higher degree distributes N across smaller individual coefficients.",
                mutations={"degree": 3, "sample_bound": 500},
                expected_effect="proxy_log_norm_score <= 0.85 * degree_2_score",
                budget={"max_wall_seconds": 30.0, "max_cpu_seconds": 30.0, "max_rss_mb": 1024},
                stopping_rule="stop if Level B0 validity filter fails",
                promotion_target="Pilot B-P1",
                novelty_reason="Testing representation shift from quadratic to cubic base-m.",
            )
        proposals.append(prop_b)

        # Track C proposal
        if judge_verdicts.get("C") == "CALIBRATION_INCOMPLETE":
            prop_c = DirectorProposal(
                proposal_id=generate_experiment_id("C", date=now, suffix="C00002"),
                parent_experiment="EXP-TRACK-C-PILOT-v0.1.0",
                track="C",
                hypothesis="Fine-grained MSB calibration ladder (25%, 35%, 40%, 45%, 50%, 55%, 60%) establishes exact empirical recovery boundary.",
                mechanism="Testing genuine partial bit slices across 7 steps determines exact recovery cutoff and lattice dimension scaling limits.",
                mutations={"fractions": [0.25, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60], "lattice_dimension": 5},
                expected_effect="empirical_recovery_curve mapped across all 7 fractions without synthetic placeholders",
                budget={"max_wall_seconds": 60.0, "max_cpu_seconds": 60.0, "max_rss_mb": 1024},
                stopping_rule="stop if LLL basis reduction exceeds 60 seconds",
                promotion_target="Pilot C-P2",
                novelty_reason="Full-ladder calibration replacing synthetic negative control.",
            )
        else:
            prop_c = DirectorProposal(
                proposal_id=generate_experiment_id("C", date=now, suffix="C00001"),
                parent_experiment=None,
                track="C",
                hypothesis="Bivariate lattice root search lowers required known MSB fraction from 50% to 45% on 48-bit semiprimes.",
                mechanism="Adding dual-monomial polynomial relations extends Howgrave-Graham root bound.",
                mutations={"lattice_dimension": 4, "degree_m": 3},
                expected_effect="downstream_exact_recovery_rate >= 0.8 at fraction=0.45",
                budget={"max_wall_seconds": 60.0, "max_cpu_seconds": 60.0, "max_rss_mb": 1024},
                stopping_rule="stop if LLL basis reduction exceeds 60 seconds",
                promotion_target="Pilot C-P1",
                novelty_reason="Exploration of sub-50% MSB small-root recovery.",
            )
        proposals.append(prop_c)

        # Track D proposal
        if judge_verdicts.get("D") == "BASELINE_ESTABLISHED":
            prop_d = DirectorProposal(
                proposal_id=generate_experiment_id("D", date=now, suffix="D00002"),
                parent_experiment="EXP-TRACK-D-PILOT-v0.1.0",
                track="D",
                hypothesis="Carry-save adder tree encoding reduces CDCL SAT solve time by >= 2x over schoolbook baseline on 24-32 bit moduli.",
                mechanism="Carry-save tree reduces clause dependency chain depth from O(n^2) to O(n log n).",
                mutations={"encoding_family": "carry_save", "baseline_encoding": "schoolbook", "solver": "glucose4"},
                expected_effect="solve_time <= 0.50 * baseline_schoolbook_solve_time",
                budget={"max_wall_seconds": 45.0, "max_cpu_seconds": 45.0, "max_rss_mb": 1024},
                stopping_rule="stop if D-CANARY-1 semantic equivalence test fails",
                promotion_target="Pilot D-P2",
                novelty_reason="First paired encoding comparison against characterized schoolbook baseline.",
            )
        else:
            prop_d = DirectorProposal(
                proposal_id=generate_experiment_id("D", date=now, suffix="D00001"),
                parent_experiment=None,
                track="D",
                hypothesis="Carry-save adder tree encoding reduces SAT conflict count by >= 25% on 32-bit balanced semiprimes.",
                mechanism="Reduces clause dependency chain depth compared to ripple-carry adders.",
                mutations={"encoding_family": "carry_save", "solver": "cadical195"},
                expected_effect="conflicts <= 0.75 * baseline_schoolbook_conflicts",
                budget={"max_wall_seconds": 30.0, "max_cpu_seconds": 30.0, "max_rss_mb": 1024},
                stopping_rule="stop if D-CANARY-1 semantic equivalence test fails",
                promotion_target="Pilot D-P1",
                novelty_reason="First non-schoolbook arithmetic encoding mutation.",
            )
        proposals.append(prop_d)

        return proposals

