"""Configuration data models and YAML loader for NSB laboratory."""

from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
from pydantic import BaseModel, Field
from nsb.core.hashing import hash_file


class StorageConfig(BaseModel):
    database_path: str = "state/experiments.sqlite"
    manifests_dir: str = "experiments/manifests"
    results_dir: str = "experiments/results"
    artifacts_dir: str = "experiments/artifacts"
    reports_dir: str = "reports"
    public_benchmarks_dir: str = "benchmarks/public"
    sealed_benchmarks_dir: str = "benchmarks/sealed"


class ResourceGovernorConfig(BaseModel):
    default_max_wall_seconds: float = 60.0
    default_max_cpu_seconds: float = 60.0
    default_max_rss_mb: int = 2048
    kill_grace_period_seconds: float = 2.0


class DirectorConfig(BaseModel):
    mode: str = "proposal_only"
    max_active_experiments: int = 8
    max_children_per_parent: int = 3
    portfolio_allocation: Dict[str, float] = Field(
        default_factory=lambda: {"exploit": 0.70, "explore_far": 0.20, "replicate": 0.10}
    )


class AuditorConfig(BaseModel):
    enforce_clean_git: bool = True
    enable_poison_tripwires: bool = True


class NSBConfig(BaseModel):
    contract_id: str = "NSB-R0-FOUNDATION"
    benchmark_version: str = "v001"
    storage: StorageConfig = Field(default_factory=StorageConfig)
    resource_governor: ResourceGovernorConfig = Field(default_factory=ResourceGovernorConfig)
    director: DirectorConfig = Field(default_factory=DirectorConfig)
    auditor: AuditorConfig = Field(default_factory=AuditorConfig)


def load_config(path: Union[str, Path]) -> tuple[NSBConfig, str]:
    """Load configuration from a YAML file.

    Returns:
        tuple[NSBConfig, str]: Parsed configuration and its SHA-256 hash.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Configuration file not found: {p}")

    config_hash = hash_file(p)
    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    config = NSBConfig(**data)
    return config, config_hash
