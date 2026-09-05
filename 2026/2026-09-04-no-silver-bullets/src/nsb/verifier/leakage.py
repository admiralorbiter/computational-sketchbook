"""Leakage detection and tripwire audit checks."""

import os
from pathlib import Path
from typing import List, Optional, Union
from pydantic import BaseModel, Field

SENTINEL_ENV_VARS = ["NSB_SEALED_TRUTH", "NSB_LEAK_SECRET", "NSB_BENCHMARK_TRUTH"]


class LeakageAuditResult(BaseModel):
    passed: bool
    violations: List[str] = Field(default_factory=list)


def audit_environment_leakage() -> LeakageAuditResult:
    """Check that no forbidden truth-leaking environment variables are set."""
    violations: List[str] = []
    for var in SENTINEL_ENV_VARS:
        if var in os.environ:
            violations.append(f"Forbidden sentinel environment variable '{var}' detected in process space")

    return LeakageAuditResult(
        passed=len(violations) == 0,
        violations=violations,
    )


def audit_path_access(accessed_paths: List[Union[str, Path]], sealed_base_dir: Union[str, Path]) -> LeakageAuditResult:
    """Audit a list of paths accessed by research code to ensure none touch sealed storage."""
    violations: List[str] = []
    sealed_p = Path(sealed_base_dir).resolve()

    for p in accessed_paths:
        resolved = Path(p).resolve()
        try:
            resolved.relative_to(sealed_p)
            # If relative_to succeeds, the path is inside sealed directory!
            violations.append(f"Unauthorized path access to sealed storage: {resolved}")
        except ValueError:
            # Path is not inside sealed directory
            pass

    return LeakageAuditResult(
        passed=len(violations) == 0,
        violations=violations,
    )
