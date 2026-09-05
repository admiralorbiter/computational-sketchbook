"""Executable statistical promotion judge for Track B candidate evaluations."""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set, Union

import numpy as np
from scipy import stats


@dataclass
class PairedEvaluationRecord:
    """Paired baseline vs. candidate evaluation for a single modulus."""

    instance_id: str
    digits: int
    baseline_passed: bool
    candidate_passed: bool
    baseline_yield: int
    candidate_yield: int
    baseline_total_cpu: float
    candidate_total_cpu: float


@dataclass
class Tier1QualityResult:
    """Outcome of Tier 1 (Polynomial Quality) evaluation."""

    passed: bool
    sample_geometric_mean_ratio: float
    ci_lower: float
    ci_upper: float
    median_diff_by_digit: Dict[int, float]
    details: Dict[str, Any]


@dataclass
class Tier2SystemResult:
    """Outcome of Tier 2 (System Efficiency) evaluation."""

    passed: bool
    sample_cost_ratio: float
    ci_lower: float
    ci_upper: float
    details: Dict[str, Any]


@dataclass
class PromotionVerdict:
    """Formal decision rendered by PromotionJudge."""

    verdict: str  # R3_CANDIDATE_PROMOTED, QUALITY_ADVANTAGE_ONLY, SYSTEM_ADVANTAGE_ONLY, PROMOTION_REJECTED
    tier1_quality: Tier1QualityResult
    tier2_system: Tier2SystemResult
    total_moduli: int
    candidate_failures: int


class PromotionJudge:
    """Multi-tier statistical adjudicator enforcing preregistered promotion thresholds."""

    def __init__(
        self,
        quality_ratio_threshold: float = 1.10,
        system_reduction_threshold: float = 0.05,
        confidence_level: float = 0.95,
        n_resamples: int = 10000,
        random_seed: int = 42,
        expected_digits: Optional[List[int]] = None,
        expected_count_per_cohort: Optional[int] = 10,
        require_manifest: bool = True,
        manifest_path: Optional[Union[str, Path]] = None,
        expected_instance_ids: Optional[List[str]] = None,
    ):
        self.quality_ratio_threshold = quality_ratio_threshold
        self.system_reduction_threshold = system_reduction_threshold
        self.confidence_level = confidence_level
        self.n_resamples = n_resamples
        self.random_seed = random_seed
        self.expected_digits = expected_digits if expected_digits is not None else [95, 100]
        self.expected_count_per_cohort = expected_count_per_cohort
        self.require_manifest = require_manifest
        self.manifest_path = Path(manifest_path) if manifest_path else None
        self.expected_instance_ids = expected_instance_ids

    @staticmethod
    def _load_manifest_instance_ids(manifest_path: Path) -> List[str]:
        """Extract instance IDs from a manifest or instances file."""
        import json
        if not manifest_path.is_file():
            raise ValueError(f"Manifest file not found: {manifest_path}")
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                if "instances" in data:
                    return [item.get("instance_id", item) for item in data["instances"]]
                if "public_file" in data:
                    inst_file = manifest_path.parent / Path(data["public_file"]).name
                    if not inst_file.is_file():
                        inst_file = Path(data["public_file"])
                    if inst_file.is_file():
                        ids = []
                        for line in inst_file.read_text(encoding="utf-8").splitlines():
                            if line.strip():
                                rec = json.loads(line)
                                ids.append(rec["instance_id"])
                        return ids
            elif isinstance(data, list):
                return [item.get("instance_id", item) if isinstance(item, dict) else str(item) for item in data]
        except Exception as e:
            raise ValueError(f"Failed parsing manifest {manifest_path}: {e}")
        raise ValueError(f"Unable to extract instance IDs from manifest {manifest_path}")

    def validate_cohort_records(
        self,
        records: List[PairedEvaluationRecord],
        expected_instance_ids: Optional[List[str]] = None,
    ) -> None:
        """Strictly validate evaluation records before statistical adjudication."""
        if not records:
            raise ValueError("Adjudication rejected: evaluation records list is empty")

        # 1. Manifest / instance ID requirement
        target_expected_ids = expected_instance_ids
        if target_expected_ids is None:
            if self.expected_instance_ids is not None:
                target_expected_ids = self.expected_instance_ids
            elif self.manifest_path is not None:
                target_expected_ids = self._load_manifest_instance_ids(self.manifest_path)
            elif self.require_manifest:
                raise ValueError("Adjudication rejected: formal promotion requires expected_instance_ids or a frozen manifest")

        # 2. Unique instance IDs (no duplicates allowed)
        instance_ids = [r.instance_id for r in records]
        if len(instance_ids) != len(set(instance_ids)):
            duplicates = [x for x in set(instance_ids) if instance_ids.count(x) > 1]
            raise ValueError(f"Adjudication rejected: duplicate instance IDs detected: {duplicates}")

        # 3. Check against expected manifest instance IDs if provided/required
        if target_expected_ids is not None:
            expected_set = set(target_expected_ids)
            actual_set = set(instance_ids)
            if actual_set != expected_set:
                missing = expected_set - actual_set
                unauthorized = actual_set - expected_set
                raise ValueError(
                    f"Adjudication rejected: instance IDs do not match expected manifest. "
                    f"Missing: {missing}, Unauthorized: {unauthorized}"
                )

        # 4. Check required digit cohorts (e.g. 95d and 100d)
        records_by_digit: Dict[int, List[PairedEvaluationRecord]] = {}
        for r in records:
            records_by_digit.setdefault(r.digits, []).append(r)

        actual_digits = sorted(records_by_digit.keys())
        if actual_digits != sorted(self.expected_digits):
            raise ValueError(
                f"Adjudication rejected: record digit cohorts {actual_digits} do not match "
                f"required promotion cohorts {sorted(self.expected_digits)}"
            )

        # 5. Check instance count per cohort
        if self.expected_count_per_cohort is not None:
            for d, recs in records_by_digit.items():
                if len(recs) != self.expected_count_per_cohort:
                    raise ValueError(
                        f"Adjudication rejected: cohort {d}d contains {len(recs)} instances, "
                        f"expected exactly {self.expected_count_per_cohort}"
                    )

        # 6. Baseline integrity & numerical validity of measured values
        failed_baselines = [r.instance_id for r in records if not r.baseline_passed]
        if failed_baselines:
            raise ValueError(
                f"Adjudication rejected: baseline failed on {len(failed_baselines)} instances: {failed_baselines}. "
                "Cannot adjudicate candidate advantage against failed baselines."
            )

        for r in records:
            # Yield validity
            if not isinstance(r.baseline_yield, (int, np.integer)) or r.baseline_yield < 0:
                raise ValueError(f"Adjudication rejected on {r.instance_id}: baseline_yield must be non-negative integer")
            if not isinstance(r.candidate_yield, (int, np.integer)) or r.candidate_yield < 0:
                raise ValueError(f"Adjudication rejected on {r.instance_id}: candidate_yield must be non-negative integer")

            # Baseline passed validation (non-zero yield and finite positive CPU)
            if r.baseline_passed:
                if not math.isfinite(r.baseline_total_cpu) or r.baseline_total_cpu <= 0:
                    raise ValueError(f"Adjudication rejected on {r.instance_id}: passed baseline must have finite positive CPU")
                if r.baseline_yield <= 0:
                    raise ValueError(f"Adjudication rejected on {r.instance_id}: passed baseline must have strictly positive yield")

            # Candidate resource validation (finite and non-negative)
            if not math.isfinite(r.candidate_total_cpu) or r.candidate_total_cpu < 0:
                raise ValueError(
                    f"Adjudication rejected on {r.instance_id}: candidate_total_cpu must be finite and non-negative "
                    f"(received {r.candidate_total_cpu})"
                )

    def evaluate_tier1_quality(
        self,
        records: List[PairedEvaluationRecord],
    ) -> Tier1QualityResult:
        """Evaluate Tier 1: Polynomial Quality Advantage."""
        if not records:
            return Tier1QualityResult(
                passed=False,
                sample_geometric_mean_ratio=0.0,
                ci_lower=0.0,
                ci_upper=0.0,
                median_diff_by_digit={},
                details={"error": "Empty records"},
            )

        # Build paired yield arrays
        by_digit: Dict[int, List[float]] = {}
        ratios: List[float] = []
        any_candidate_zero = False

        for r in records:
            by_digit.setdefault(r.digits, [])
            y_base = r.baseline_yield
            y_cand = r.candidate_yield if r.candidate_passed else 0

            diff = float(y_cand - y_base)
            by_digit[r.digits].append(diff)

            if y_cand <= 0:
                any_candidate_zero = True
                ratios.append(0.0)
            else:
                ratios.append(float(y_cand) / float(y_base))

        # Check positive median difference within each digit cohort
        median_diffs = {}
        all_medians_positive = True
        for d, diffs in by_digit.items():
            med = float(np.median(diffs))
            median_diffs[d] = med
            if med <= 0:
                all_medians_positive = False

        # True zero geometric mean: if any candidate yield is 0, geometric mean is strictly 0.0
        if any_candidate_zero:
            return Tier1QualityResult(
                passed=False,
                sample_geometric_mean_ratio=0.0,
                ci_lower=0.0,
                ci_upper=0.0,
                median_diff_by_digit={k: round(v, 2) for k, v in median_diffs.items()},
                details={
                    "all_medians_positive": all_medians_positive,
                    "meets_threshold": False,
                    "ci_excludes_1": False,
                    "reason": "Candidate produced zero valid relations or failed on one or more instances",
                },
            )

        # All candidate yields > 0: compute geometric mean and bootstrap CI
        log_ratios = np.log(np.array(ratios, dtype=float))
        sample_geom_mean = float(np.exp(np.mean(log_ratios)))

        rng = np.random.default_rng(self.random_seed)
        try:
            boot_res = stats.bootstrap(
                (log_ratios,),
                statistic=lambda x: np.exp(np.mean(x)),
                confidence_level=self.confidence_level,
                n_resamples=self.n_resamples,
                method="percentile",
                random_state=rng,
            )
            ci_lower = float(boot_res.confidence_interval.low)
            ci_upper = float(boot_res.confidence_interval.high)
        except Exception:
            ci_lower = 0.0
            ci_upper = 0.0

        passed = (
            sample_geom_mean >= self.quality_ratio_threshold
            and ci_lower > 1.00
            and all_medians_positive
        )

        return Tier1QualityResult(
            passed=passed,
            sample_geometric_mean_ratio=round(sample_geom_mean, 4),
            ci_lower=round(ci_lower, 4),
            ci_upper=round(ci_upper, 4),
            median_diff_by_digit={k: round(v, 2) for k, v in median_diffs.items()},
            details={
                "all_medians_positive": all_medians_positive,
                "meets_threshold": sample_geom_mean >= self.quality_ratio_threshold,
                "ci_excludes_1": ci_lower > 1.00,
            },
        )

    def evaluate_tier2_system(
        self,
        records: List[PairedEvaluationRecord],
    ) -> Tier2SystemResult:
        """Evaluate Tier 2: System Efficiency Advantage (Total CPU / valid relation)."""
        if not records:
            return Tier2SystemResult(
                passed=False,
                sample_cost_ratio=float("inf"),
                ci_lower=float("inf"),
                ci_upper=float("inf"),
                details={"error": "Empty records"},
            )

        cost_ratios = []

        for r in records:
            # Baseline cost per valid relation (safeguarded against division by zero)
            y_base = float(r.baseline_yield)
            if y_base <= 0 or not math.isfinite(r.baseline_total_cpu) or r.baseline_total_cpu <= 0:
                c_base = 1e-12
            else:
                c_base = r.baseline_total_cpu / y_base

            # Candidate cost per valid relation (failure penalty: 100x baseline cost)
            y_cand = float(r.candidate_yield)
            if not r.candidate_passed or y_cand <= 0 or not math.isfinite(r.candidate_total_cpu) or r.candidate_total_cpu < 0:
                c_cand = c_base * 100.0
            else:
                c_cand = r.candidate_total_cpu / y_cand

            cost_ratios.append(c_cand / c_base if c_base > 0 else 100.0)

        cost_ratios_arr = np.array(cost_ratios, dtype=float)
        sample_cost_ratio = float(np.mean(cost_ratios_arr))

        # Bootstrap confidence interval on mean cost ratio
        rng = np.random.default_rng(self.random_seed)
        try:
            boot_res = stats.bootstrap(
                (cost_ratios_arr,),
                statistic=np.mean,
                confidence_level=self.confidence_level,
                n_resamples=self.n_resamples,
                method="percentile",
                random_state=rng,
            )
            ci_lower = float(boot_res.confidence_interval.low)
            ci_upper = float(boot_res.confidence_interval.high)
        except Exception:
            ci_lower = float("inf")
            ci_upper = float("inf")

        # Required: at least 5% cost reduction (ratio <= 0.95) and CI upper < 1.00
        target_ratio = 1.0 - self.system_reduction_threshold
        passed = sample_cost_ratio <= target_ratio and ci_upper < 1.00

        return Tier2SystemResult(
            passed=passed,
            sample_cost_ratio=round(sample_cost_ratio, 4),
            ci_lower=round(ci_lower, 4),
            ci_upper=round(ci_upper, 4),
            details={
                "target_ratio": target_ratio,
                "meets_reduction": sample_cost_ratio <= target_ratio,
                "ci_excludes_1": ci_upper < 1.00,
            },
        )

    def judge(
        self,
        records: List[PairedEvaluationRecord],
        expected_instance_ids: Optional[List[str]] = None,
    ) -> PromotionVerdict:
        """Render formal multi-tier promotion verdict after strict input validation."""
        # Enforce validation on inputs fail-closed
        self.validate_cohort_records(records, expected_instance_ids=expected_instance_ids)

        t1 = self.evaluate_tier1_quality(records)
        t2 = self.evaluate_tier2_system(records)

        cand_failures = sum(1 for r in records if not r.candidate_passed)

        if t1.passed and t2.passed:
            verdict = "R3_CANDIDATE_PROMOTED"
        elif t1.passed and not t2.passed:
            verdict = "QUALITY_ADVANTAGE_ONLY"
        elif not t1.passed and t2.passed:
            verdict = "SYSTEM_ADVANTAGE_ONLY"
        else:
            verdict = "PROMOTION_REJECTED"

        return PromotionVerdict(
            verdict=verdict,
            tier1_quality=t1,
            tier2_system=t2,
            total_moduli=len(records),
            candidate_failures=cand_failures,
        )
