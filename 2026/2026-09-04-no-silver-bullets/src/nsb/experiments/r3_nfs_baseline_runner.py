"""Experiment runner and gate verifier for NSB-R3-B-NFS-BASELINE-FOUNDATION.

Implements and verifies:
- R3-G0: Dependency Foundation & Environment Gate.
- R3-G1: Discrete Binary Adapter Canaries (polyselect, ropt, score, las).
- R3-G2: Deterministic Rerun Canary (counterbalanced A1->B1->B2->A2 exact relation invariance).
"""

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from nsb.baselines.cado_nfs.adapter import CadoSubprocessAdapter
from nsb.baselines.cado_nfs.environment import CadoEnvironment
from nsb.baselines.cado_nfs.models import (
    CadoPolyselectResult,
    CadoScoreResult,
    CadoSieveResult,
    NfsPolynomialPair,
)
from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector
from nsb.baselines.cado_nfs.scorer import CadoScorer
from nsb.baselines.cado_nfs.sieve import CadoRelationCollector
from nsb.baselines.cado_nfs.verifier import (
    compute_sylvester_resultant,
    verify_nfs_polynomial_pair,
)
from nsb.baselines.cado_nfs.profiles import (
    CadoParameterProfile,
    CADO_PARAMS_C60,
    CANARY_PLUMBING_C60,
)

# Standard public 60-digit balanced semiprime: N = p * q
# p = 316227766016837933199889354447 (prime, 30 digits)
# q = 316227766016837933199889354591 (prime, 30 digits)
# N has no small prime factors (min factor > 3.16e29)
SMOKE_60_DIGIT_COMPOSITE = (
    100000000000000000000000000047894685265564092504022465716177
)  # 60 digits


# Verified mathematically valid degree-4 base-m polynomial (matching params.c60 degree 4)
# m = 562341325190349 = floor(N^(1/4))
# Satisfies: f1(m) == N, f2(m) == 0, Res(f1, f2) == N == 0 (mod N)
VERIFIED_C60_POLY = NfsPolynomialPair(
    f1_coeffs=[78987903916411, 14538431061421, 180837613225436, 0, 1],
    f2_coeffs=[-562341325190349, 1],
    N=SMOKE_60_DIGIT_COMPOSITE,
    m=562341325190349,
    skew=1.5,
    metadata={"origin": "verified_balanced_semiprime_c60_expansion"},
)


class R3BaselineRunner:
    """Orchestrator for R3 NFS baseline foundation and canaries."""

    def __init__(
        self,
        environment: Optional[CadoEnvironment] = None,
        adapter: Optional[CadoSubprocessAdapter] = None,
    ):
        self.env = environment or CadoEnvironment()
        self.adapter = adapter or CadoSubprocessAdapter(environment=self.env)
        self.scorer = CadoScorer(adapter=self.adapter)
        self.selector = CadoPolynomialSelector(adapter=self.adapter)
        self.collector = CadoRelationCollector(adapter=self.adapter)

    def run_g0_environment_gate(self) -> Dict[str, Any]:
        """Execute R3-G0 environment verification gate."""
        fp = self.env.fingerprint()
        is_valid, msg = self.env.validate_for_canonical_execution()
        return {
            "gate": "R3-G0",
            "passed": is_valid,
            "message": msg,
            "fingerprint": fp,
        }

    def run_g1_canary(
        self,
        n: int = SMOKE_60_DIGIT_COMPOSITE,
        degree: int = 5,
        q_start: int = 500_000,
        q_range: int = 200,
        profile: Optional[CadoParameterProfile] = None,
        timeout_seconds: float = 180.0,
    ) -> Dict[str, Any]:
        """Execute R3-G1 discrete binary adapter canaries with mandatory makefb and >0 relations."""
        active_profile = profile or CANARY_PLUMBING_C60

        g0 = self.run_g0_environment_gate()
        if not g0["passed"]:
            return {
                "gate": "R3-G1",
                "passed": False,
                "error": f"Cannot run G1: G0 failed: {g0['message']}",
                "environment_gate": g0,
            }

        t_start = time.time()
        # 1. Polyselect (+ ropt)
        poly_res = self.selector.select_polynomial(
            n=n,
            degree=degree,
            profile=active_profile,
            timeout_seconds=timeout_seconds,
        )

        # 2. Independent mathematical verification (Sylvester resultant + root)
        is_valid, v_msg = verify_nfs_polynomial_pair(poly_res.pair)
        if not is_valid:
            return {
                "gate": "R3-G1",
                "passed": False,
                "error": f"Mathematical verification failed: {v_msg}",
            }

        # 3. Native scoring with geometry tied to active profile
        score_res = self.scorer.score(
            poly_res.pair,
            bf=active_profile.bf,
            bg=active_profile.bg,
            area=active_profile.area,
            timeout_seconds=timeout_seconds,
        )

        # 4. Discrete lattice sieving (mandatory makefb + las + check_rels)
        sieve_res = self.collector.collect_relations(
            poly=poly_res.pair,
            q_start=q_start,
            q_range=q_range,
            profile=active_profile,
            run_makefb=True,
            validate_with_check_rels=True,
            timeout_seconds=timeout_seconds,
        )

        total_wall = time.time() - t_start
        total_cpu = (
            poly_res.cpu_seconds
            + score_res.cpu_seconds
            + sieve_res.cpu_seconds
        )

        # Strict relation requirement: must produce >0 relations, non-empty hash, check_rels == True, and conservation_checked == True
        relations_valid = (
            sieve_res.unique_relations > 0
            and bool(sieve_res.relations_hash)
            and sieve_res.checked_with_check_rels is True
            and sieve_res.conservation_checked is True
        )
        passed = (
            poly_res.pair.degree1 >= 1
            and score_res.murphy_e > 0.0
            and relations_valid
        )

        return {
            "gate": "R3-G1",
            "passed": passed,
            "modulus_n": str(n),
            "digit_count": len(str(n)),
            "profile_name": active_profile.name,
            "sieve_profile": active_profile.to_sieve_dict(),
            "certified_pair": poly_res.pair,
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
                "skew": score_res.skew,
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
                "cpu_seconds": sieve_res.cpu_seconds,
                "relations_per_cpu_second": sieve_res.relations_per_cpu_second,
            },
            "total_cpu_seconds": round(total_cpu, 4),
            "total_wall_seconds": round(total_wall, 4),
        }

    def run_g2_deterministic_rerun_canary(
        self,
        pair: Optional[NfsPolynomialPair] = None,
        q_start: int = 500_000,
        q_range: int = 200,
        profile: Optional[CadoParameterProfile] = None,
        expected_relations_hash: Optional[str] = None,
        timeout_seconds: float = 180.0,
    ) -> Dict[str, Any]:
        """Execute R3-G2 deterministic rerun / repeatability canary with 4-run A1 -> B1 -> B2 -> A2 counterbalanced order.

        Tests that repeated execution through the fixed CADO instrument produces bit-for-bit identical
        normalized relation records and (a, b) pairs. (A/B instrument fairness testing deferred to future gate
        once an actual candidate execution path exists).
        """
        active_profile = profile or CANARY_PLUMBING_C60

        g0 = self.run_g0_environment_gate()
        if not g0["passed"]:
            return {
                "gate": "R3-G2",
                "gate_name": "R3-G2 Deterministic Rerun Canary",
                "passed": False,
                "error": f"Cannot run G2: G0 failed: {g0['message']}",
            }

        target_pair = pair or VERIFIED_C60_POLY
        is_valid, v_msg = verify_nfs_polynomial_pair(target_pair)
        if not is_valid:
            return {
                "gate": "R3-G2",
                "gate_name": "R3-G2 Deterministic Rerun Canary",
                "passed": False,
                "error": f"G2 target polynomial failed verification: {v_msg}",
            }

        # 4-run counterbalanced execution: A1 -> B1 -> B2 -> A2
        runs = {}
        for run_name in ["A1", "B1", "B2", "A2"]:
            res = self.collector.collect_relations(
                poly=target_pair,
                q_start=q_start,
                q_range=q_range,
                profile=active_profile,
                run_makefb=True,
                validate_with_check_rels=True,
                timeout_seconds=timeout_seconds,
            )
            runs[run_name] = res

        # Invariance assertions:
        # 1. Complete normalized relation records SHA-256 hashes match across all 4 runs
        # 2. Canonical (a, b) pairs invariant hashes match across all 4 runs
        # 3. Relation counts match
        # 4. All runs validated with check_rels
        hashes = [r.relations_hash for r in runs.values()]
        ab_hashes = [r.ab_pairs_hash for r in runs.values()]
        unique_counts = [r.unique_relations for r in runs.values()]
        total_counts = [r.total_relations for r in runs.values()]
        all_checked_rels = all(r.checked_with_check_rels is True for r in runs.values())
        all_conserved = all(r.conservation_checked is True for r in runs.values())

        exact_hash_match = len(set(hashes)) == 1 and bool(hashes[0])
        exact_ab_match = len(set(ab_hashes)) == 1 and bool(ab_hashes[0])
        exact_unique_match = len(set(unique_counts)) == 1 and unique_counts[0] > 0
        exact_total_match = len(set(total_counts)) == 1

        cross_gate_match = True
        if expected_relations_hash is not None:
            cross_gate_match = (hashes[0] == expected_relations_hash) if exact_hash_match else False

        passed = (
            exact_hash_match
            and exact_ab_match
            and exact_unique_match
            and exact_total_match
            and all_checked_rels
            and all_conserved
            and cross_gate_match
        )

        return {
            "gate": "R3-G2",
            "gate_name": "R3-G2 Deterministic Rerun Canary",
            "passed": passed,
            "profile_name": active_profile.name,
            "sieve_profile": active_profile.to_sieve_dict(),
            "q_start": q_start,
            "q_range": q_range,
            "counterbalanced_order": ["A1", "B1", "B2", "A2"],
            "relation_record_hash": hashes[0] if exact_hash_match else "MISMATCH",
            "relation_set_hash": hashes[0] if exact_hash_match else "MISMATCH",  # backward compatibility
            "ab_pairs_hash": ab_hashes[0] if exact_ab_match else "MISMATCH",
            "unique_relations": unique_counts[0],
            "expected_relations_hash": expected_relations_hash,
            "cross_gate_hash_match": cross_gate_match if expected_relations_hash is not None else None,
            "runs": {
                name: {
                    "unique_relations": r.unique_relations,
                    "total_relations": r.total_relations,
                    "relations_hash": r.relations_hash,
                    "ab_pairs_hash": r.ab_pairs_hash,
                    "checked_with_check_rels": r.checked_with_check_rels,
                    "conservation_checked": r.conservation_checked,
                    "cpu_seconds": r.cpu_seconds,
                }
                for name, r in runs.items()
            },
            "deterministic_rerun_verified": passed,
            "invariance_verified": passed,  # backward compatibility
        }

    # Backward compatibility alias
    run_g2_paired_identity_canary = run_g2_deterministic_rerun_canary


def main():
    parser = argparse.ArgumentParser(description="NSB R3 Baseline Runner")
    parser.add_argument("--gate", choices=["G0", "G1", "G2", "G3", "all"], default="G0")
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--certify", action="store_true", help="Fail closed if any gate fails or is skipped")
    parser.add_argument("--dry-run", action="store_true", help="Dry run for calibration (G3 only)")
    args = parser.parse_args()

    runner = R3BaselineRunner()
    results = {}
    certified_pair: Optional[NfsPolynomialPair] = None
    g1_relations_hash: Optional[str] = None
    all_passed = True

    if args.gate in ["G0", "all"]:
        results["G0"] = runner.run_g0_environment_gate()
        passed = results["G0"]["passed"]
        all_passed = all_passed and passed
        print(f"R3-G0 Environment Gate: {'PASS' if passed else 'FAIL'}")
        print(f"  Details: {results['G0']['message']}")

    if args.gate in ["G1", "all"]:
        results["G1"] = runner.run_g1_canary()
        passed = results["G1"].get("passed", False)
        all_passed = all_passed and passed
        print(f"R3-G1 Adapter Canary: {'PASS' if passed else 'FAIL'}")
        if passed and "certified_pair" in results["G1"]:
            certified_pair = results["G1"]["certified_pair"]
            g1_relations_hash = results["G1"].get("sieving", {}).get("relations_hash")

    if args.gate in ["G2", "all"]:
        results["G2"] = runner.run_g2_deterministic_rerun_canary(
            pair=certified_pair,
            expected_relations_hash=g1_relations_hash if certified_pair is not None else None,
        )
        passed = results["G2"].get("passed", False)
        all_passed = all_passed and passed
        print(f"R3-G2 Deterministic Rerun Canary: {'PASS' if passed else 'FAIL'}")
        if results["G2"].get("cross_gate_hash_match") is not None:
            cg_status = "PASS" if results["G2"]["cross_gate_hash_match"] else "FAIL"
            print(f"  Cross-Gate Invariance (G1 relations_hash == G2 relations_hash): {cg_status}")

    if args.gate == "G3":
        from nsb.experiments.r3_calibration_runner import R3CalibrationRunner
        calib_runner = R3CalibrationRunner(environment=runner.env, adapter=runner.adapter)
        results["G3"] = calib_runner.run_calibration(dry_run=args.dry_run)
        passed = results["G3"]["status"] in ["PASS", "DRY_RUN_PASS"]
        all_passed = all_passed and passed
        print(f"R3-G3 Baseline Calibration: {results['G3']['status']}")

    if args.out:
        # Convert pairs to strings for clean JSON serialization
        serializable_results = {}
        for k, v in results.items():
            if isinstance(v, dict):
                v_copy = dict(v)
                if "certified_pair" in v_copy and isinstance(v_copy["certified_pair"], NfsPolynomialPair):
                    v_copy["certified_pair"] = v_copy["certified_pair"].to_cado_poly_string()
                serializable_results[k] = v_copy
            else:
                serializable_results[k] = v

        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(serializable_results, indent=2), encoding="utf-8")
        print(f"Wrote report to {out_path}")

    if args.certify and not all_passed:
        print("CERTIFICATION FAILED: One or more gates did not pass.")
        sys.exit(1)


if __name__ == "__main__":
    main()
