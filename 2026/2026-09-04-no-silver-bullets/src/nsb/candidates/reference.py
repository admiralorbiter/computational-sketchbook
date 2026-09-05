"""Reference implementation of NfsCandidateSelector wrapping standard CADO polyselection."""

from typing import Optional

from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector
from nsb.baselines.cado_nfs.profiles import CadoParameterProfile
from nsb.candidates.models import (
    CandidateInterventionLevel,
    CandidateOutput,
    NfsCandidateSelector,
    SearchBudget,
)


class CadoBaselineCandidateSelector:
    """Reference candidate selector executing standard CADO polyselect + ropt."""

    def __init__(self, selector: Optional[CadoPolynomialSelector] = None):
        self.method_id = "cado_baseline_reference"
        self.version = "1.0.0"
        self.intervention_level = CandidateInterventionLevel.FULL_SELECTOR
        self.selector = selector or CadoPolynomialSelector()

    def select(
        self,
        N: int,
        profile: CadoParameterProfile,
        budget: SearchBudget,
        seed: int,
    ) -> CandidateOutput:
        """Execute CADO baseline polynomial selection within budget."""
        res = self.selector.select_polynomial(
            n=N,
            degree=profile.degree,
            profile=profile,
            timeout_seconds=budget.max_wall_seconds,
        )

        trace_log = (
            f"CadoBaselineReference: selected pair for N={N}, degree={profile.degree}, "
            f"cpu={res.cpu_seconds:.4f}s, wall={res.wall_seconds:.4f}s"
        )

        return CandidateOutput(
            selected_pair=res.pair,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            candidates_generated=profile.nrkeep,
            candidates_valid=1,
            metadata={
                "selector_cpu": res.cpu_seconds,
                "selector_wall": res.wall_seconds,
            },
            search_trace_log=trace_log,
        )


class ReferenceDummyCandidateSelector:
    """Pre-computed deterministic reference candidate for testing worker module-import execution."""

    def __init__(self):
        self.method_id = "reference_dummy_selector"
        self.version = "1.0.0"
        self.intervention_level = CandidateInterventionLevel.FULL_SELECTOR

    def select(
        self,
        N: int,
        profile: CadoParameterProfile,
        budget: SearchBudget,
        seed: int,
    ) -> CandidateOutput:
        from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY
        return CandidateOutput(
            selected_pair=VERIFIED_C60_POLY,
            method_id=self.method_id,
            version=self.version,
            intervention_level=self.intervention_level,
            seed=seed,
            candidates_generated=1,
            candidates_valid=1,
            search_trace_log="reference dummy selector trace",
        )
