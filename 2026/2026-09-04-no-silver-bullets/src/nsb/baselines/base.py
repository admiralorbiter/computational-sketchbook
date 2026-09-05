"""Abstract base class for classical factorization baselines."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaselineFactorResult:
    def __init__(
        self,
        success: bool,
        factors: Optional[List[int]] = None,
        steps: int = 0,
        wall_seconds: float = 0.0,
        cpu_seconds: float = 0.0,
        extra_metrics: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.factors = factors or []
        self.steps = steps
        self.wall_seconds = wall_seconds
        self.cpu_seconds = cpu_seconds
        self.extra_metrics = extra_metrics or {}


class BaselineSolver(ABC):
    """Abstract interface for classical factorization algorithms."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the algorithm."""
        pass

    @abstractmethod
    def factor(self, N: int, max_seconds: float = 10.0, max_steps: Optional[int] = None) -> BaselineFactorResult:
        """Attempt to factor N within budget.

        Args:
            N: Target integer modulus.
            max_seconds: Maximum wall-clock time in seconds.
            max_steps: Optional upper bound on iteration steps.

        Returns:
            BaselineFactorResult with success status and factors.
        """
        pass
