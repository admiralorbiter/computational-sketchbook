"""R2 Wave 2 Phase 2B Research Execution Engine.

Executes Track B Phase 2B (Representation Search & In-House Polyselect Proxy)
on the fresh out-of-sample holdout corpus (v003_wave2/search_holdout).

Evaluates:
- Tier 2: Representation-Search Claim (FrozenSearchOptimizer d=3 vs Canonical base-m d=3)
- Tier 3: In-House Polyselect Proxy Claim (Candidate vs Symmetrical Murphy-E Baseline)

Adjudicated mechanically by PromotionJudge using config/contracts/r2_wave2_phase2b_criteria.yaml.
"""

import datetime
import math
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import numpy as np
from scipy import stats
import yaml

from nsb.auditor.engine import Auditor
from nsb.auditor.judge import PromotionJudge, Wave2Phase2BCohortObservation
from nsb.benchmarks.corpus import load_public_instances
from nsb.tracks.algebraic_evolution.evaluator import (
    AlgebraicEvaluator,
    TimingInvalidError,
)
from nsb.tracks.algebraic_evolution.murphy import (
    compute_murphy_e,
    select_in_house_murphy_e_baseline,
)
from nsb.tracks.algebraic_evolution.representation import (
    PolynomialPair,
    create_base_m_representation,
)
from nsb.tracks.algebraic_evolution.search import FrozenSearchOptimizer


class Wave2Phase2BRunner:
    """Canonical runner for Wave 2 Track B Phase 2B evaluation."""

    def __init__(
        self,
        config_path: str = "config/wave2_phase2b.yaml",
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

        self.contract_id = self.raw_cfg.get("contract_id", "NSB-R2-WAVE2-B-PHASE2B")
        self.benchmark_version = self.raw_cfg.get("benchmark_version", "v003_wave2")
        self.benchmark_split = self.raw_cfg.get("benchmark_split", "search_holdout")
        self.criteria_path = self.raw_cfg.get(
            "criteria_contract_path", "config/contracts/r2_wave2_phase2b_criteria.yaml"
        )

        self.auditor = Auditor(".")
        self.judge = PromotionJudge(criteria_path=self.criteria_path)
        self.evaluator = AlgebraicEvaluator(small_primes_bound=250)
        self.search_optimizer = FrozenSearchOptimizer(budget=50)

    def evaluate_cohort(
        self,
        moduli: List[int],
        bound_a: int = 100,
        bound_b: int = 20,
        per_modulus_cpu_limit: float = 5.0,
    ) -> Dict[str, Any]:
        """Evaluate a single cohort of moduli across candidate, canonical base-m, and proxy baseline."""
        per_mod_records = []
        n_moduli = len(moduli)

        cand_yields = []
        base_yields = []
        proxy_yields = []
        paired_diffs_base = []
        paired_diffs_proxy = []

        cand_murphy_es = []
        proxy_murphy_es = []

        cand_throughputs = []
        proxy_throughputs = []

        moduli_with_cand_relations = 0
        paired_log_norm_ratios = []

        for i, N in enumerate(moduli):
            t_mod_cpu_start = time.process_time()

            # 1. Candidate representation (Level B1 + Murphy alpha optimization)
            cand_res = self.search_optimizer.optimize(N, degree=3)
            cand_pair = cand_res.pair

            # 2. Canonical base-m degree-3 baseline (Tier 2 baseline)
            base_pair = create_base_m_representation(N, degree=3)
            base_norm = self.evaluator.score_proxy_b1(base_pair, sample_bound=50)
            log_norm_ratio = cand_res.log_norm / base_norm if base_norm > 0 else 1.0
            paired_log_norm_ratios.append(log_norm_ratio)

            # 3. Symmetrical Murphy-E proxy baseline (Tier 3 baseline)
            proxy_pair, proxy_stats = select_in_house_murphy_e_baseline(
                N,
                degree=3,
                translation_radius=5,
                rotation_u_bound=2,
                rotation_v_bound=2,
                budget=50,
            )

            # 4. Homogeneous B3 sieving for all three representations
            sieve_cand = self.evaluator.homogeneous_sieve_b3(cand_pair, bound_a=bound_a, bound_b=bound_b)
            sieve_base = self.evaluator.homogeneous_sieve_b3(base_pair, bound_a=bound_a, bound_b=bound_b)
            sieve_proxy = self.evaluator.homogeneous_sieve_b3(proxy_pair, bound_a=bound_a, bound_b=bound_b)

            y_cand = sieve_cand["yield_rate"]
            y_base = sieve_base["yield_rate"]
            y_proxy = sieve_proxy["yield_rate"]

            cand_yields.append(y_cand)
            base_yields.append(y_base)
            proxy_yields.append(y_proxy)

            diff_base = y_cand - y_base
            diff_proxy = y_cand - y_proxy
            paired_diffs_base.append(diff_base)
            paired_diffs_proxy.append(diff_proxy)

            if sieve_cand["smooth_relations"] >= 1:
                moduli_with_cand_relations += 1

            # 5. Murphy-E ratings
            cand_e_res = compute_murphy_e(cand_pair)
            cand_e = cand_e_res["murphy_e"]
            proxy_e = proxy_stats["murphy_e"]
            cand_murphy_es.append(cand_e)
            proxy_murphy_es.append(proxy_e)

            # 6. Cumulative multi-batch relation throughput benchmarks (>= 0.25s CPU)
            # Counterbalanced AB/BA order: 15 candidate-first, 15 proxy-first per 30-modulus cohort
            if i % 2 == 0:
                bm_cand = self.evaluator.benchmark_relation_throughput(
                    cand_pair, bound_a=bound_a, bound_b=bound_b, min_cpu_seconds=0.25
                )
                bm_proxy = self.evaluator.benchmark_relation_throughput(
                    proxy_pair, bound_a=bound_a, bound_b=bound_b, min_cpu_seconds=0.25
                )
                timing_order = "cand_then_proxy"
            else:
                bm_proxy = self.evaluator.benchmark_relation_throughput(
                    proxy_pair, bound_a=bound_a, bound_b=bound_b, min_cpu_seconds=0.25
                )
                bm_cand = self.evaluator.benchmark_relation_throughput(
                    cand_pair, bound_a=bound_a, bound_b=bound_b, min_cpu_seconds=0.25
                )
                timing_order = "proxy_then_cand"

            th_cand = bm_cand["throughput_relations_per_core_sec"]
            th_proxy = bm_proxy["throughput_relations_per_core_sec"]
            cand_throughputs.append(th_cand)
            proxy_throughputs.append(th_proxy)

            # Check whole-modulus pipeline CPU ceiling
            mod_cpu = time.process_time() - t_mod_cpu_start
            if mod_cpu > per_modulus_cpu_limit:
                raise TimeoutError(
                    f"Modulus {N} exceeded whole-pipeline CPU ceiling: {mod_cpu:.4f}s > {per_modulus_cpu_limit:.4f}s"
                )

            per_mod_records.append({
                "N": N,
                "cand_yield": round(y_cand, 6),
                "base_yield": round(y_base, 6),
                "proxy_yield": round(y_proxy, 6),
                "cand_smooth": sieve_cand["smooth_relations"],
                "cand_op": cand_res.operation,
                "proxy_op": proxy_stats.get("operation", "unknown"),
                "cand_log_norm": round(cand_res.log_norm, 4),
                "base_log_norm": round(base_norm, 4),
                "log_norm_ratio": round(log_norm_ratio, 4),
                "cand_murphy_e": cand_e,
                "proxy_murphy_e": proxy_e,
                "cand_throughput": th_cand,
                "proxy_throughput": th_proxy,
                "timing_order": timing_order,
                "mod_cpu_seconds": round(mod_cpu, 4),
            })

        # Statistics Tier 2 (vs Canonical base-m)
        mean_cand_y = float(np.mean(cand_yields)) if cand_yields else 0.0
        mean_base_y = float(np.mean(base_yields)) if base_yields else 0.0
        mean_p_diff = float(np.mean(paired_diffs_base)) if paired_diffs_base else 0.0
        std_p_diff = float(np.std(paired_diffs_base, ddof=1)) if len(paired_diffs_base) > 1 else 0.0
        mean_log_norm_r = float(np.mean(paired_log_norm_ratios)) if paired_log_norm_ratios else 1.0

        wins = sum(1 for d in paired_diffs_base if d > 1e-12)
        losses = sum(1 for d in paired_diffs_base if d < -1e-12)
        ties = n_moduli - (wins + losses)
        win_rate = wins / n_moduli if n_moduli > 0 else 0.0

        # One-sided paired t-test (alternative="greater")
        if std_p_diff > 0 and n_moduli > 1:
            t_stat = mean_p_diff / (std_p_diff / math.sqrt(n_moduli))
            paired_t_p = float(stats.t.sf(t_stat, df=n_moduli - 1))
            ci_half = float(stats.t.ppf(0.975, df=n_moduli - 1) * (std_p_diff / math.sqrt(n_moduli)))
            ci_95 = (round(mean_p_diff - ci_half, 6), round(mean_p_diff + ci_half, 6))
        else:
            paired_t_p = 1.0
            ci_95 = (round(mean_p_diff, 6), round(mean_p_diff, 6))

        # One-sided Wilcoxon signed-rank test (alternative="greater")
        diff_arr = np.array(paired_diffs_base)
        non_zero = diff_arr[diff_arr != 0]
        if len(non_zero) >= 5:
            try:
                res_w = stats.wilcoxon(non_zero, alternative="greater")
                wilcoxon_p = float(res_w.pvalue)
            except Exception:
                wilcoxon_p = 1.0
        elif len(non_zero) > 0 and all(x > 0 for x in non_zero):
            wilcoxon_p = float(0.5 ** len(non_zero))
        else:
            wilcoxon_p = 1.0

        # Yield gain (None if base is zero)
        yield_gain = round(mean_cand_y / mean_base_y, 4) if mean_base_y > 0 else None
        relation_floor_ratio = moduli_with_cand_relations / n_moduli if n_moduli > 0 else 0.0

        # Statistics Tier 3 (vs Symmetrical Proxy Baseline)
        mean_cand_e = float(np.mean(cand_murphy_es)) if cand_murphy_es else 0.0
        mean_proxy_e = float(np.mean(proxy_murphy_es)) if proxy_murphy_es else 0.0
        murphy_e_ratio = round(mean_cand_e / mean_proxy_e, 4) if mean_proxy_e > 0 else None

        cum_cand_th = float(np.mean(cand_throughputs)) if cand_throughputs else 0.0
        cum_proxy_th = float(np.mean(proxy_throughputs)) if proxy_throughputs else 0.0
        th_ratio = round(cum_cand_th / cum_proxy_th, 4) if cum_proxy_th > 0 else None

        proxy_p_diff = float(np.mean(paired_diffs_proxy)) if paired_diffs_proxy else 0.0
        std_proxy_diff = float(np.std(paired_diffs_proxy, ddof=1)) if len(paired_diffs_proxy) > 1 else 0.0

        proxy_wins = sum(1 for d in paired_diffs_proxy if d > 1e-12)
        proxy_win_rate = proxy_wins / n_moduli if n_moduli > 0 else 0.0

        # Proxy empirical yield Wilcoxon (alternative="greater")
        proxy_non_zero = np.array(paired_diffs_proxy)[np.array(paired_diffs_proxy) != 0]
        if len(proxy_non_zero) >= 5:
            try:
                res_pw = stats.wilcoxon(proxy_non_zero, alternative="greater")
                proxy_wilcoxon_p = float(res_pw.pvalue)
            except Exception:
                proxy_wilcoxon_p = 1.0
        elif len(proxy_non_zero) > 0 and all(x > 0 for x in proxy_non_zero):
            proxy_wilcoxon_p = float(0.5 ** len(proxy_non_zero))
        else:
            proxy_wilcoxon_p = 1.0

        if std_proxy_diff > 0 and n_moduli > 1:
            t_stat_p = proxy_p_diff / (std_proxy_diff / math.sqrt(n_moduli))
            proxy_paired_t_p = float(stats.t.sf(t_stat_p, df=n_moduli - 1))
        else:
            proxy_paired_t_p = 1.0

        return {
            "n_moduli": n_moduli,
            "mean_cand_yield": round(mean_cand_y, 6),
            "mean_base_yield": round(mean_base_y, 6),
            "mean_paired_diff": round(mean_p_diff, 6),
            "candidate_wins": wins,
            "candidate_losses": losses,
            "ties": ties,
            "win_rate": round(win_rate, 4),
            "wilcoxon_pvalue": wilcoxon_p,
            "paired_t_pvalue": paired_t_p,
            "yield_gain": yield_gain,
            "moduli_with_relations_cand": moduli_with_cand_relations,
            "relation_floor_ratio": round(relation_floor_ratio, 4),
            "mean_log_norm_ratio": round(mean_log_norm_r, 4),
            "ci_95": ci_95,
            "mean_cand_murphy_e": round(mean_cand_e, 6),
            "mean_proxy_murphy_e": round(mean_proxy_e, 6),
            "murphy_e_ratio": murphy_e_ratio,
            "cumulative_cand_throughput": round(cum_cand_th, 4),
            "cumulative_proxy_throughput": round(cum_proxy_th, 4),
            "throughput_ratio": th_ratio,
            "proxy_yield_diff": round(proxy_p_diff, 6),
            "proxy_wilcoxon_pvalue": proxy_wilcoxon_p,
            "proxy_paired_t_pvalue": proxy_paired_t_p,
            "proxy_win_rate": round(proxy_win_rate, 4),
            "raw_mean_cand_yield": mean_cand_y,
            "raw_mean_base_yield": mean_base_y,
            "raw_mean_cand_murphy_e": mean_cand_e,
            "raw_mean_proxy_murphy_e": mean_proxy_e,
            "raw_cum_cand_throughput": cum_cand_th,
            "raw_cum_proxy_throughput": cum_proxy_th,
            "raw_mean_log_norm_ratio": mean_log_norm_r,
            "per_modulus": per_mod_records,
        }

    def run(self, max_sizes: Optional[int] = None) -> Dict[str, Any]:
        """Execute Phase 2B evaluation across holdout moduli."""
        start_time = time.time()

        # Audit git state
        git_sha, git_dirty, git_details = self.auditor.check_git_status()
        if git_dirty and not self.allow_dirty:
            raise RuntimeError(
                f"Phase 2B execution rejected: dirty working tree ({git_details}). "
                "Commit all changes before running Phase 2B experiment."
            )

        # Audit manifests & tripwires
        manifest_checks = self.auditor.check_manifest_integrity()
        tripwire_checks = self.auditor.check_tripwires()
        failed_checks = [c for c in manifest_checks + tripwire_checks if not c.passed]
        if failed_checks:
            raise RuntimeError(f"Auditor integrity checks failed: {failed_checks}")

        # Resource limits from criteria
        limits = self.judge.criteria_config.get("resource_limits", {})
        per_modulus_cpu_limit = limits.get("per_modulus_timeout_cpu_seconds", 5.0)
        per_cohort_wall_limit = limits.get("per_cohort_timeout_seconds", 300.0)
        max_total_wall_limit = limits.get("max_total_wall_seconds", 1800.0)
        max_rss_mb = limits.get("max_rss_mb", 2048)

        # Load holdout instances
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

        cohort_results: Dict[int, Wave2Phase2BCohortObservation] = {}
        per_size_details: Dict[int, Dict[str, Any]] = {}

        import psutil
        process = psutil.Process()

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
            cohort_data = self.evaluate_cohort(
                moduli=moduli,
                bound_a=100,
                bound_b=20,
                per_modulus_cpu_limit=per_modulus_cpu_limit,
            )

            cohort_elapsed = time.time() - cohort_start
            if cohort_elapsed > per_cohort_wall_limit:
                raise TimeoutError(
                    f"Cohort {bits}b wall time limit exceeded: {cohort_elapsed:.1f}s > {per_cohort_wall_limit}s"
                )

            per_size_details[bits] = cohort_data

            obs = Wave2Phase2BCohortObservation(
                bits=bits,
                n_moduli=cohort_data["n_moduli"],
                mean_cand_yield=cohort_data["mean_cand_yield"],
                mean_base_yield=cohort_data["mean_base_yield"],
                mean_paired_diff=cohort_data["mean_paired_diff"],
                candidate_wins=cohort_data["candidate_wins"],
                win_rate=cohort_data["win_rate"],
                wilcoxon_pvalue=cohort_data["wilcoxon_pvalue"],
                paired_t_pvalue=cohort_data["paired_t_pvalue"],
                yield_gain=cohort_data["yield_gain"],
                moduli_with_relations_cand=cohort_data["moduli_with_relations_cand"],
                relation_floor_ratio=cohort_data["relation_floor_ratio"],
                mean_log_norm_ratio=cohort_data["mean_log_norm_ratio"],
                ci_95=cohort_data["ci_95"],
                mean_cand_murphy_e=cohort_data["mean_cand_murphy_e"],
                mean_proxy_murphy_e=cohort_data["mean_proxy_murphy_e"],
                murphy_e_ratio=cohort_data["murphy_e_ratio"],
                cumulative_cand_throughput=cohort_data["cumulative_cand_throughput"],
                cumulative_proxy_throughput=cohort_data["cumulative_proxy_throughput"],
                throughput_ratio=cohort_data["throughput_ratio"],
                proxy_yield_diff=cohort_data["proxy_yield_diff"],
                proxy_wilcoxon_pvalue=cohort_data["proxy_wilcoxon_pvalue"],
                proxy_paired_t_pvalue=cohort_data["proxy_paired_t_pvalue"],
                proxy_win_rate=cohort_data["proxy_win_rate"],
                raw_mean_cand_yield=cohort_data.get("raw_mean_cand_yield"),
                raw_mean_base_yield=cohort_data.get("raw_mean_base_yield"),
                raw_mean_cand_murphy_e=cohort_data.get("raw_mean_cand_murphy_e"),
                raw_mean_proxy_murphy_e=cohort_data.get("raw_mean_proxy_murphy_e"),
                raw_cum_cand_throughput=cohort_data.get("raw_cum_cand_throughput"),
                raw_cum_proxy_throughput=cohort_data.get("raw_cum_proxy_throughput"),
                raw_mean_log_norm_ratio=cohort_data.get("raw_mean_log_norm_ratio"),
                per_modulus=cohort_data["per_modulus"],
            )
            cohort_results[bits] = obs

        # Mechanical adjudication via PromotionJudge
        evaluation_result = self.judge.evaluate_wave2_b_phase2b(
            cohort_results=cohort_results,
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
