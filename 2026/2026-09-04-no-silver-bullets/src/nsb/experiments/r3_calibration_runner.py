"""R3-G3 Public Baseline Calibration Runner for CADO-NFS.

Executes baseline characterization across frozen public semiprimes (60, 70, 80, 90 digits)
under pinned parameter profiles (c60_pinned, c70_pinned, c80_pinned, c90_pinned).
Enforces:
1. G0 environment gate verification.
2. Frozen corpus verification via SHA-256 manifest.
3. q_start = profile.qmin, q_range = profile.qrange, threads = 1.
4. Complete profile capture (polyselect, scoring geometry, sieving).
5. All-or-nothing cohort completion (no partial results become baseline).
6. Linear percentile aggregation (p10, p50, p90, min, median, max, mean, std).
"""

import argparse
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from nsb.baselines.cado_nfs.adapter import CadoSubprocessAdapter
from nsb.baselines.cado_nfs.environment import CadoEnvironment
from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector
from nsb.baselines.cado_nfs.profiles import (
    CadoParameterProfile,
    get_cado_profile,
)
from nsb.baselines.cado_nfs.scorer import CadoScorer
from nsb.baselines.cado_nfs.sieve import CadoRelationCollector
from nsb.baselines.cado_nfs.verifier import verify_nfs_polynomial_pair
from nsb.core.hashing import hash_file

DEFAULT_CORPUS_MANIFEST = "benchmarks/public/v005_r3_calibration/public_calibration/manifest.json"
DEFAULT_CALIBRATION_OUTPUT = "config/baselines/cado_nfs_calibration.json"

SIZE_PROFILE_MAP = {
    60: "c60_pinned",
    70: "c70_pinned",
    80: "c80_pinned",
    90: "c90_pinned",
}


def compute_distribution_metrics(values: List[float], precision: Optional[int] = None) -> Dict[str, float]:
    """Compute standard summary metrics including linear p10, p50, p90."""
    if not values:
        return {}
    arr = np.array(values, dtype=float)
    p10, p50, p90 = np.percentile(arr, [10, 50, 90], method="linear")

    def _val(x: float) -> float:
        f = float(x)
        return round(f, precision) if precision is not None else f

    return {
        "count": len(values),
        "min": _val(np.min(arr)),
        "p10": _val(p10),
        "median": _val(p50),
        "p50": _val(p50),
        "p90": _val(p90),
        "max": _val(np.max(arr)),
        "mean": _val(np.mean(arr)),
        "std": _val(np.std(arr)),
    }


class R3CalibrationRunner:
    """Orchestrator for R3-G3 public baseline calibration across frozen 40-instance corpus."""

    def __init__(
        self,
        environment: Optional[CadoEnvironment] = None,
        adapter: Optional[CadoSubprocessAdapter] = None,
        repo_root: Optional[Path] = None,
    ):
        self.repo_root = repo_root or Path(".").resolve()
        self.env = environment or CadoEnvironment()
        self.adapter = adapter or CadoSubprocessAdapter(environment=self.env)
        self.scorer = CadoScorer(adapter=self.adapter)
        self.selector = CadoPolynomialSelector(adapter=self.adapter)
        self.collector = CadoRelationCollector(adapter=self.adapter, threads=1)

    def verify_corpus_manifest(self, manifest_path: Optional[Path] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Verify calibration corpus manifest and public instances file."""
        m_path = manifest_path or (self.repo_root / DEFAULT_CORPUS_MANIFEST)
        if not m_path.is_file():
            return False, f"Manifest not found: {m_path}", {}

        try:
            manifest = json.loads(m_path.read_text(encoding="utf-8"))
            pub_file = self.repo_root / manifest["public_file"]
            if not pub_file.is_file():
                return False, f"Instances file not found: {pub_file}", manifest

            calc_sha = hash_file(pub_file)
            if calc_sha != manifest["public_sha256"]:
                return False, f"Public instances SHA mismatch: {calc_sha} != {manifest['public_sha256']}", manifest

            return True, "Corpus manifest verified", manifest
        except Exception as e:
            return False, f"Manifest verification failed: {e}", {}

    def load_instances(self, manifest: Dict[str, Any], target_digit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load and filter instances from manifest."""
        pub_file = self.repo_root / manifest["public_file"]
        instances: List[Dict[str, Any]] = []
        with open(pub_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    inst = json.loads(line)
                    if target_digit is None or inst.get("digits") == target_digit:
                        instances.append(inst)
        return instances

    def run_single_instance(
        self,
        instance: Dict[str, Any],
        timeout_seconds: float = 600.0,
    ) -> Dict[str, Any]:
        """Execute discrete CADO baseline pipeline on a single modulus."""
        digits = instance["digits"]
        inst_id = instance["instance_id"]
        N = int(instance["N"])

        profile_name = SIZE_PROFILE_MAP[digits]
        profile = get_cado_profile(profile_name)

        t_start = time.time()

        # 1. Polyselect (+ ROPT)
        poly_res = self.selector.select_polynomial(
            n=N,
            degree=profile.degree,
            profile=profile,
            timeout_seconds=timeout_seconds,
        )

        # 2. Independent mathematical verification
        is_valid, v_msg = verify_nfs_polynomial_pair(poly_res.pair)
        if not is_valid:
            raise ValueError(f"Polynomial verification failed for {inst_id}: {v_msg}")

        # 3. Independent scoring
        score_res = self.scorer.score(
            poly_res.pair,
            bf=profile.bf,
            bg=profile.bg,
            area=profile.area,
            timeout_seconds=timeout_seconds,
        )

        # 4. Discrete lattice sieving (makefb + las + check_rels)
        sieve_res = self.collector.collect_relations(
            poly=poly_res.pair,
            q_start=profile.qmin,
            q_range=profile.qrange,
            profile=profile,
            run_makefb=True,
            validate_with_check_rels=True,
            timeout_seconds=timeout_seconds,
        )

        total_wall = time.time() - t_start
        total_cpu = poly_res.cpu_seconds + score_res.cpu_seconds + sieve_res.cpu_seconds

        # Verification check
        valid = (
            score_res.murphy_e > 0.0
            and sieve_res.unique_relations > 0
            and sieve_res.checked_with_check_rels is True
            and sieve_res.conservation_checked is True
        )

        if not valid:
            raise RuntimeError(
                f"Instance {inst_id} failed validity criteria: "
                f"murphy_e={score_res.murphy_e}, unique_relations={sieve_res.unique_relations}, "
                f"check_rels={sieve_res.checked_with_check_rels}, conservation={sieve_res.conservation_checked}"
            )

        return {
            "instance_id": inst_id,
            "digits": digits,
            "N": str(N),
            "profile_name": profile_name,
            "profile": profile.to_full_dict(),
            "polynomial": {
                "f1_coeffs": poly_res.pair.f1_coeffs,
                "f2_coeffs": poly_res.pair.f2_coeffs,
                "m": poly_res.pair.m,
                "degree1": poly_res.pair.degree1,
                "degree2": poly_res.pair.degree2,
                "skew": poly_res.pair.skew,
            },
            "polyselect": {
                "degree1": poly_res.pair.degree1,
                "degree2": poly_res.pair.degree2,
                "skew": poly_res.pair.skew,
                "cpu_seconds": poly_res.cpu_seconds,
                "wall_seconds": poly_res.wall_seconds,
            },
            "scoring": {
                "murphy_e": score_res.murphy_e,
                "lognorm": score_res.lognorm,
                "exp_e": score_res.exp_e,
                "rroots": score_res.rroots,
                "cpu_seconds": score_res.cpu_seconds,
            },
            "sieving": {
                "q_start": sieve_res.q_start,
                "q_range": sieve_res.q_range,
                "unique_relations": sieve_res.unique_relations,
                "total_relations": sieve_res.total_relations,
                "relations_hash": sieve_res.relations_hash,
                "checked_with_check_rels": sieve_res.checked_with_check_rels,
                "conservation_checked": sieve_res.conservation_checked,
                "wall_seconds": sieve_res.wall_seconds,
                "cpu_seconds": sieve_res.cpu_seconds,
                "relations_per_cpu_second": sieve_res.relations_per_cpu_second,
            },
            "total_cpu_seconds": round(total_cpu, 4),
            "total_wall_seconds": round(total_wall, 4),
            "timeout_seconds": timeout_seconds,
            "passed": True,
        }

    def run_calibration(
        self,
        target_digit: Optional[int] = None,
        dry_run: bool = False,
        timeout_seconds: float = 600.0,
    ) -> Dict[str, Any]:
        """Execute full calibration cohort across verified instances."""
        # 1. G0 check
        fp = self.env.fingerprint()
        is_g0, g0_msg = self.env.validate_for_canonical_execution(require_clean_nsb=not dry_run)
        if not is_g0:
            return {
                "status": "FAIL",
                "gate": "R3-G3",
                "error": f"G0 Environment check failed: {g0_msg}",
                "fingerprint": fp,
            }

        # 2. Manifest check
        is_corpus, corpus_msg, manifest = self.verify_corpus_manifest()
        if not is_corpus:
            return {
                "status": "FAIL",
                "gate": "R3-G3",
                "error": f"Corpus check failed: {corpus_msg}",
                "fingerprint": fp,
            }

        instances = self.load_instances(manifest, target_digit=target_digit)
        expected_count = 10 if target_digit else 40
        if len(instances) != expected_count:
            return {
                "status": "FAIL",
                "gate": "R3-G3",
                "error": f"Instance count mismatch: expected {expected_count}, got {len(instances)}",
                "fingerprint": fp,
            }

        if dry_run:
            # Validate parameter profile mappings without execution
            validation_records = []
            for inst in instances:
                p_name = SIZE_PROFILE_MAP[inst["digits"]]
                prof = get_cado_profile(p_name)
                validation_records.append({
                    "instance_id": inst["instance_id"],
                    "digits": inst["digits"],
                    "profile_name": p_name,
                    "qmin": prof.qmin,
                    "qrange": prof.qrange,
                    "expected_area": prof.expected_area,
                    "area_matches": abs(prof.area - prof.expected_area) < 1e-3,
                    "bf_matches": prof.bf == prof.expected_bf,
                    "bg_matches": prof.bg == prof.expected_bg,
                })
            return {
                "status": "DRY_RUN_PASS",
                "gate": "R3-G3",
                "environment_g0": "PASS",
                "corpus_manifest": manifest,
                "instance_count": len(instances),
                "timeout_seconds": timeout_seconds,
                "validation_records": validation_records,
                "fingerprint": fp,
            }

        # 3. Execution (fail closed if any instance fails)
        results_by_digit: Dict[int, List[Dict[str, Any]]] = {60: [], 70: [], 80: [], 90: []}
        all_instances_results: List[Dict[str, Any]] = []

        t_cohort_start = time.time()
        for idx, inst in enumerate(instances, 1):
            inst_id = inst["instance_id"]
            digits = inst["digits"]
            print(f"[{idx}/{len(instances)}] Executing {inst_id} ({digits} digits)...")
            try:
                rec = self.run_single_instance(inst, timeout_seconds=timeout_seconds)
                results_by_digit[digits].append(rec)
                all_instances_results.append(rec)
            except Exception as e:
                return {
                    "status": "FAIL",
                    "gate": "R3-G3",
                    "error": f"Calibration failed on instance {inst_id}: {e}",
                    "failed_instance": inst_id,
                    "completed_count": len(all_instances_results),
                    "fingerprint": fp,
                }

        cohort_wall = time.time() - t_cohort_start

        # 4. Distribution aggregations
        cohort_summary = {}
        for d, recs in results_by_digit.items():
            if not recs:
                continue
            murphy_e_vals = [r["scoring"]["murphy_e"] for r in recs]
            poly_cpu_vals = [r["polyselect"]["cpu_seconds"] for r in recs]
            sieve_cpu_vals = [r["sieving"]["cpu_seconds"] for r in recs]
            total_cpu_vals = [r["total_cpu_seconds"] for r in recs]
            rels_per_cpu_vals = [r["sieving"]["relations_per_cpu_second"] for r in recs]

            cohort_summary[f"d{d}"] = {
                "digits": d,
                "profile_name": SIZE_PROFILE_MAP[d],
                "instances_evaluated": len(recs),
                "murphy_e": compute_distribution_metrics(murphy_e_vals),
                "polyselect_cpu_seconds": compute_distribution_metrics(poly_cpu_vals),
                "sieve_cpu_seconds": compute_distribution_metrics(sieve_cpu_vals),
                "total_cpu_seconds": compute_distribution_metrics(total_cpu_vals),
                "relations_per_cpu_second": compute_distribution_metrics(rels_per_cpu_vals),
            }

        return {
            "status": "PASS",
            "gate": "R3-G3",
            "benchmark_version": manifest["benchmark_version"],
            "master_seed": manifest["master_seed"],
            "public_manifest_sha256": hash_file(self.repo_root / DEFAULT_CORPUS_MANIFEST),
            "total_instances_evaluated": len(all_instances_results),
            "total_cohort_wall_seconds": round(cohort_wall, 2),
            "timeout_seconds": timeout_seconds,
            "percentile_algorithm": "numpy.percentile(method='linear')",
            "summary_by_digit": cohort_summary,
            "instances": all_instances_results,
            "fingerprint": fp,
        }


def main():
    parser = argparse.ArgumentParser(description="R3-G3 Public Baseline Calibration Runner")
    parser.add_argument("--digits", type=int, choices=[60, 70, 80, 90], default=None, help="Target digit size (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Validate G0, corpus, and profiles without sieving")
    parser.add_argument("--out", type=str, default=DEFAULT_CALIBRATION_OUTPUT, help="Path to save calibration output JSON")
    parser.add_argument("--timeout", type=float, default=600.0, help="Per-instance timeout seconds")
    args = parser.parse_args()

    runner = R3CalibrationRunner()
    result = runner.run_calibration(target_digit=args.digits, dry_run=args.dry_run, timeout_seconds=args.timeout)

    print(f"R3-G3 Calibration Result: {result['status']}")
    if result["status"] != "PASS" and result["status"] != "DRY_RUN_PASS":
        print(f"  Error: {result.get('error')}")
        sys.exit(1)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
