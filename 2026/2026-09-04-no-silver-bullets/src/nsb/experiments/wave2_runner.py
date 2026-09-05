"""R2 Wave 2 Confirmatory Research Execution Engine.

Executes Track B Confirmatory Replication & Multi-Tier Claim Verification on the 150-modulus
pairwise-coprime benchmark corpus (v002_wave2/confirmatory).

Tiers evaluated:
1. Tier 1: Replication Claim (Canonical base-m d=3 vs d=2 across 30 moduli per size)
2. Tier 2: Representation-Search Claim (FrozenSearchOptimizer vs canonical base-m)
3. Tier 3: In-House Polyselect Proxy Claim (Candidate vs in-house size/root-optimized baseline)
4. Tier 4: Scaling Persistence Claim (Non-inferiority of yield advantage across 32b-96b)

Adjudicated mechanically by PromotionJudge using config/contracts/r2_wave2_criteria.yaml.
"""

import datetime
import json
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import yaml

from nsb.auditor.engine import Auditor
from nsb.auditor.judge import PromotionJudge, Wave2CohortObservation
from nsb.benchmarks.corpus import load_public_instances
from nsb.core.fingerprint import capture_environment_fingerprint
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator
from nsb.tracks.algebraic_evolution.murphy import (
    compute_murphy_e,
    select_kleinjung_murphy_baseline,
)
from nsb.tracks.algebraic_evolution.search import FrozenSearchOptimizer


class Wave2ConfirmatoryRunner:
    """Canonical runner for Wave 2 Track B confirmatory evaluation."""

    def __init__(
        self,
        config_path: str = "config/wave2_confirmatory.yaml",
        allow_dirty: bool = False,
    ):
        self.config_path = config_path
        self.allow_dirty = allow_dirty
        self.cfg_path = Path(config_path)

        if self.cfg_path.exists():
            with open(self.cfg_path, "r", encoding="utf-8") as f:
                self.raw_cfg = yaml.safe_load(f) or {}
        else:
            self.raw_cfg = {}

        self.contract_id = self.raw_cfg.get("contract_id", "NSB-R2-WAVE2-B-CONFIRMATORY")
        self.benchmark_version = self.raw_cfg.get("benchmark_version", "v002_wave2")
        self.benchmark_split = self.raw_cfg.get("benchmark_split", "confirmatory")
        self.criteria_path = self.raw_cfg.get(
            "criteria_contract_path", "config/contracts/r2_wave2_criteria.yaml"
        )

        self.auditor = Auditor(".")
        self.judge = PromotionJudge(criteria_path=self.criteria_path)
        self.evaluator = AlgebraicEvaluator(small_primes_bound=250)
        self.search_optimizer = FrozenSearchOptimizer(budget=50)

    def run(self, max_sizes: Optional[int] = None) -> Dict[str, Any]:
        """Execute the Wave 2 confirmatory protocol across all 150 independent moduli."""
        start_time = time.time()

        # Audit git state
        git_sha, git_dirty, git_details = self.auditor.check_git_status()
        if git_dirty and not self.allow_dirty:
            raise RuntimeError(
                f"Wave 2 execution rejected: dirty working tree ({git_details}). "
                "Commit all changes before running confirmatory experiment."
            )

        # Audit manifests & tripwires
        manifest_checks = self.auditor.check_manifest_integrity()
        tripwire_checks = self.auditor.check_tripwires()
        failed_checks = [c for c in manifest_checks + tripwire_checks if not c.passed]
        if failed_checks:
            raise RuntimeError(f"Auditor integrity checks failed: {failed_checks}")

        # Load resource limits from contract
        limits = self.judge.criteria_config.get("resource_limits", {})
        per_modulus_cpu_limit = limits.get("per_modulus_timeout_cpu_seconds", 5.0)
        per_cohort_wall_limit = limits.get("per_cohort_timeout_seconds", 300.0)
        max_total_wall_limit = limits.get("max_total_wall_seconds", 1800.0)
        max_rss_mb = limits.get("max_rss_mb", 2048)

        # Load 150-modulus public corpus
        instances = load_public_instances(".", self.benchmark_version, self.benchmark_split)
        instances_by_size: Dict[int, List[int]] = {}
        for inst in instances:
            instances_by_size.setdefault(inst.bits, []).append(int(inst.N))

        required_sizes = self.judge.criteria_config.get("corpus", {}).get("bit_sizes", [32, 48, 64, 80, 96])
        sorted_sizes = sorted(instances_by_size.keys())
        is_canonical = True

        if max_sizes is not None and max_sizes < len(required_sizes):
            sorted_sizes = sorted_sizes[:max_sizes]
            is_canonical = False

        cohort_results: Dict[int, Wave2CohortObservation] = {}
        per_size_details: Dict[int, Dict[str, Any]] = {}

        import psutil
        process = psutil.Process()

        # Tier 1 Evaluation: 30 independent moduli per size
        for bits in sorted_sizes:
            # Check total wall ceiling
            elapsed_total = time.time() - start_time
            if elapsed_total > max_total_wall_limit:
                raise TimeoutError(
                    f"Total wall time limit exceeded: {elapsed_total:.1f}s > {max_total_wall_limit}s"
                )

            # Check RSS memory ceiling
            rss_mb = process.memory_info().rss / (1024 * 1024)
            if rss_mb > max_rss_mb:
                raise MemoryError(
                    f"Process RSS memory limit exceeded: {rss_mb:.1f}MB > {max_rss_mb}MB"
                )

            cohort_start = time.time()
            moduli = instances_by_size[bits]
            cohort_data = self.evaluator.evaluate_modulus_cohort(
                moduli=moduli,
                bound_a=100,
                bound_b=20,
                cand_degree=3,
                base_degree=2,
                max_cpu_seconds_per_modulus=per_modulus_cpu_limit,
            )

            # Enforce per-modulus CPU budget retrospectively across all evaluated moduli
            for mod_entry in cohort_data.get("per_modulus", []):
                mod_cpu = mod_entry.get("cpu_seconds", 0.0)
                if mod_cpu > per_modulus_cpu_limit:
                    raise TimeoutError(
                        f"Modulus {mod_entry.get('N')} exceeded CPU budget ceiling: {mod_cpu:.4f}s > {per_modulus_cpu_limit:.4f}s"
                    )

            cohort_elapsed = time.time() - cohort_start
            if cohort_elapsed > per_cohort_wall_limit:
                raise TimeoutError(
                    f"Cohort {bits}b wall time limit exceeded: {cohort_elapsed:.1f}s > {per_cohort_wall_limit}s"
                )

            per_size_details[bits] = cohort_data

            obs = Wave2CohortObservation(
                bits=bits,
                n_moduli=cohort_data["n_moduli"],
                mean_cand_yield=cohort_data["mean_cand_yield"],
                mean_base_yield=cohort_data["mean_base_yield"],
                mean_paired_diff=cohort_data["mean_paired_diff"],
                candidate_wins=cohort_data["candidate_wins"],
                win_rate=cohort_data["win_rate"],
                wilcoxon_pvalue=cohort_data["wilcoxon_pvalue"],
                paired_t_pvalue=cohort_data["paired_t_pvalue"],
                mean_cand_throughput=cohort_data["mean_cand_throughput"],
                mean_base_throughput=cohort_data["mean_base_throughput"],
                throughput_ratio=cohort_data["throughput_ratio"],
                ci_95=cohort_data["ci_95"],
                per_modulus=cohort_data["per_modulus"],
            )
            cohort_results[bits] = obs

        # Mechanical adjudication via PromotionJudge
        evaluation_result = self.judge.evaluate_wave2_b_confirmatory(
            cohort_results=cohort_results,
            search_comparison=None,
            sota_comparison=None,
            is_canonical=is_canonical,
        )

        total_elapsed = time.time() - start_time
        summary = {
            "contract_id": self.contract_id,
            "benchmark_version": self.benchmark_version,
            "benchmark_split": self.benchmark_split,
            "git_sha": git_sha,
            "is_canonical": is_canonical,
            "verdict": evaluation_result["verdict"],
            "total_elapsed_seconds": round(total_elapsed, 2),
            "bit_sizes_evaluated": sorted_sizes,
            "claims": evaluation_result["claims"],
            "per_size_details": per_size_details,
        }

        return summary

