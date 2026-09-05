import math
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from pydantic import BaseModel, Field, field_validator

from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.profiles import CadoParameterProfile


class CandidateInterventionLevel(str, Enum):
    """Categorization of candidate selection scope and cost accounting."""

    FULL_SELECTOR = "full_selector"
    STAGE1_GENERATOR = "stage1_generator"
    POST_ROPT_RANKER = "post_ropt_ranker"


class SearchBudget(BaseModel):
    """Execution constraints governing candidate search per modulus."""

    max_cpu_seconds: float
    max_wall_seconds: float = 600.0
    max_peak_rss_mb: float = 4096.0
    threads: int = 1
    allow_gpu: bool = False
    allow_network: bool = False

    @field_validator("threads")
    @classmethod
    def validate_threads(cls, v: int) -> int:
        if v != 1:
            raise ValueError(f"Candidate search budget strictly enforces threads=1 (received threads={v})")
        return v

    @field_validator("allow_gpu")
    @classmethod
    def validate_gpu(cls, v: bool) -> bool:
        if v is not False:
            raise ValueError("Candidate search budget strictly forbids GPU access (allow_gpu must be False)")
        return v

    @field_validator("allow_network")
    @classmethod
    def validate_network(cls, v: bool) -> bool:
        if v is not False:
            raise ValueError("Candidate search budget strictly forbids network access (allow_network must be False)")
        return v

    @field_validator("max_cpu_seconds")
    @classmethod
    def validate_max_cpu(cls, v: float) -> float:
        if not math.isfinite(v) or v <= 0:
            raise ValueError(f"Candidate search budget max_cpu_seconds must be finite and positive (received {v})")
        return v

    @field_validator("max_wall_seconds")
    @classmethod
    def validate_max_wall(cls, v: float) -> float:
        if not math.isfinite(v) or v <= 0:
            raise ValueError(f"Candidate search budget max_wall_seconds must be finite and positive (received {v})")
        return v

    @field_validator("max_peak_rss_mb")
    @classmethod
    def validate_max_rss(cls, v: float) -> float:
        if not math.isfinite(v) or v <= 0:
            raise ValueError(f"Candidate search budget max_peak_rss_mb must be finite and positive (received {v})")
        return v


class CandidateOutput(BaseModel):
    """Raw candidate submission returned from select(). Purely diagnostic."""

    selected_pair: Optional[NfsPolynomialPair] = None
    method_id: str
    version: str
    intervention_level: CandidateInterventionLevel
    seed: int
    candidates_generated: int = 0
    candidates_valid: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    search_trace_log: str = ""


class RunnerExecutionEvidence(BaseModel):
    """Authoritative supervisor-owned resource, timing, and artifact evidence."""

    actual_cpu_seconds: float
    actual_wall_seconds: float
    peak_rss_mb: float
    termination_status: str  # "COMPLETED", "BUDGET_EXCEEDED_REJECTED", "TIMEOUT", "ERROR"
    termination_reason: str
    cgroup_path: Optional[str] = None
    contained: bool = False
    worker_pid: Optional[int] = None
    overshoot_cpu_seconds: float = 0.0
    search_trace_hash: str = ""
    selected_pair_hash: str = ""
    stdout_path: Optional[str] = None
    stderr_path: Optional[str] = None
    stdout_hash: str = ""
    stderr_hash: str = ""

    @field_validator("actual_cpu_seconds", "actual_wall_seconds", "peak_rss_mb", "overshoot_cpu_seconds")
    @classmethod
    def validate_non_negative_finite(cls, v: float, info) -> float:
        if not math.isfinite(v) or v < 0:
            raise ValueError(f"RunnerExecutionEvidence metric {info.field_name} must be finite and non-negative (received {v})")
        return v


class CandidateExecutionRecord(BaseModel):
    """Authoritative immutable execution record binding candidate output and supervisor evidence."""

    instance_id: Optional[str] = None
    modulus_n: str
    digits: int
    profile_name: str
    profile: Dict[str, Any]
    budget: SearchBudget
    candidate_output: Optional[CandidateOutput] = None
    evidence: RunnerExecutionEvidence
    passed: bool
    rejection_reason: Optional[str] = None


class NfsCandidateSelector(Protocol):
    """Protocol for candidate polynomial selection algorithms."""

    method_id: str
    version: str
    intervention_level: CandidateInterventionLevel

    def select(
        self,
        N: int,
        profile: CadoParameterProfile,
        budget: SearchBudget,
        seed: int,
    ) -> CandidateOutput:
        """Execute candidate polynomial search given strictly N, profile, budget, and seed."""
        ...
