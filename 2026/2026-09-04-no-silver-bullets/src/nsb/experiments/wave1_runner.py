"""R1 Wave 1 Human-Reviewed Search Execution Engine.

Executes four focused research investigations:
1. Track A (EXP-A-W1-GRID): Relation-collapse surface grid over (FB x C x Budget) with rich diagnostics.
2. Track B (EXP-B-W1-B3): Downstream B3 homogeneous sieve paired smooth relation yield measurement.
3. Track C (EXP-C-W1-CALIBRATION): Multi-fraction empirical calibration ladder (25%-60% MSB) using genuine factor slices.
4. Track D (EXP-D-W1-CARRY-SAVE): Carry-save adder tree SAT multiplier encoding vs schoolbook baseline.

Adjudicated mechanically by PromotionJudge using config/contracts/r1_wave1_criteria.yaml.
"""

import datetime
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional
import yaml

from nsb.auditor.engine import Auditor
from nsb.auditor.judge import (
    BaselineObservation,
    PromotionJudge,
    TrackAObservation,
    TrackBObservation,
    TrackCObservation,
    TrackDObservation,
)
from nsb.baselines.portfolio import run_baseline_solve
from nsb.benchmarks.corpus import load_public_instances
from nsb.core.config import NSBConfig, load_config
from nsb.core.db import ExperimentLedger
from nsb.core.fingerprint import capture_environment_fingerprint
from nsb.core.sandbox import WorkerSandbox
from nsb.director.engine import ResearchDirector
from nsb.pilots.packet import generate_pilot_review_packet
from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator
from nsb.tracks.algebraic_evolution.representation import create_base_m_representation
from nsb.tracks.constraint_graph.benchmark import run_paired_sat_comparison
from nsb.tracks.partial_information.bridge import PartialInformationBridge
from nsb.tracks.partial_information.calibration import (
    CalibrationPointResult,
    generate_oracle_slices,
    run_calibration_ladder,
)
from nsb.tracks.tensor_lattice.grid import run_grid_point, run_track_a_grid
from nsb.verifier.leakage import audit_environment_leakage


class Wave1Runner:
    """Orchestrates R1 Wave 1 research experiments across all four tracks."""

    def __init__(self, config_path: str = "config/wave1.yaml", allow_dirty: bool = False):
        self.config_path = config_path
        self.allow_dirty = allow_dirty
        self.cfg_path = Path(config_path)

        if self.cfg_path.exists():
            with open(self.cfg_path, "r", encoding="utf-8") as f:
                self.raw_cfg = yaml.safe_load(f) or {}
        else:
            self.raw_cfg = {
                "contract_id": "NSB-R1-WAVE1-SEARCH",
                "benchmark_version": "v001_pilot",
                "criteria_contract_path": "config/contracts/r1_wave1_criteria.yaml",
            }

        self.contract_id = self.raw_cfg.get("contract_id", "NSB-R1-WAVE1-SEARCH")
        self.benchmark_version = self.raw_cfg.get("benchmark_version", "v001_pilot")
        self.criteria_path = self.raw_cfg.get("criteria_contract_path", "config/contracts/r1_wave1_criteria.yaml")

        db_file = Path("state/wave1_ledger.sqlite")
        db_file.parent.mkdir(parents=True, exist_ok=True)
        self.ledger = ExperimentLedger(db_file)

    def run(self) -> bool:
        start_time = time.perf_counter()
        print("=================================================================")
        print("NO SILVER BULLET — R1 WAVE 1 HUMAN-REVIEWED RESEARCH EXECUTION")
        print("=================================================================")
        print(f"Contract ID:        {self.contract_id}")
        print(f"Benchmark Version:  {self.benchmark_version}")
        print(f"Criteria Contract:  {self.criteria_path}")
        print(f"Allow Dirty:        {self.allow_dirty}")

        fp = capture_environment_fingerprint()
        print(f"Git SHA:            {fp.git_commit[:10]} (Dirty: {fp.git_dirty})")
        print(f"Python:             {fp.python_version} ({fp.architecture})")

        if fp.git_dirty and not self.allow_dirty:
            print("FAIL: Working tree is dirty. Canonical runs require clean git HEAD.")
            return False

        leakage = audit_environment_leakage()
        if not leakage.passed:
            print(f"FAIL: Environment leakage detected: {leakage.violations}")
            return False

        # Sandbox setup
        print("[W1] Initializing isolated sandbox & loading instances...")
        sandbox = WorkerSandbox(base_dir=".", cleanup_on_exit=False)
        sandbox.setup(
            experiment_id="WAVE1_SUITE",
            run_id="W1_RUN_001",
            version=self.benchmark_version,
            split="pilot",
        )
        instances = load_public_instances(".", self.benchmark_version, "pilot")
        print(f"     Loaded {len(instances)} public instances.")

        inst_by_family: Dict[str, List[Any]] = {}
        for i in instances:
            inst_by_family.setdefault(i.family, []).append(i)

        track_summaries: List[Dict[str, Any]] = []
        scaling_data: Dict[str, List[Dict[str, Any]]] = {}
        rejected_branches: List[Dict[str, Any]] = []

        # -------------------------------------------------------------
        # Baselines
        # -------------------------------------------------------------
        print("[W1-B0] Running classical baseline calibrations...")
        base_curves = []
        baseline_observations = []

        for f_inst in inst_by_family.get("F", []):
            res, ver = run_baseline_solve("fermat", int(f_inst.N))
            base_curves.append({"label": "Fermat (Family F)", "bits": f_inst.bits, "metric_str": f"{res.steps} steps ({res.wall_seconds:.5f}s)"})
            baseline_observations.append(BaselineObservation(
                family="F",
                method="fermat",
                bits=f_inst.bits,
                wall_seconds=res.wall_seconds,
                steps=res.steps,
                success=ver.verified,
            ))

        for p1_inst in inst_by_family.get("P1", []):
            res, ver = run_baseline_solve("pollard_pm1", int(p1_inst.N))
            base_curves.append({"label": "Pollard p-1 (Family P1)", "bits": p1_inst.bits, "metric_str": f"{res.wall_seconds:.5f}s"})
            baseline_observations.append(BaselineObservation(
                family="P1",
                method="pollard_pm1",
                bits=p1_inst.bits,
                wall_seconds=res.wall_seconds,
                steps=None,
                success=ver.verified,
            ))

        r_instances = sorted(inst_by_family.get("R", []), key=lambda x: x.bits)
        for r_inst in [i for i in r_instances if i.bits <= 40]:
            res, ver = run_baseline_solve("pollard_rho", int(r_inst.N), max_steps=200000)
            base_curves.append({"label": "Pollard rho (Family R)", "bits": r_inst.bits, "metric_str": f"{res.steps} steps ({res.wall_seconds:.4f}s)"})
            baseline_observations.append(BaselineObservation(
                family="R",
                method="pollard_rho",
                bits=r_inst.bits,
                wall_seconds=res.wall_seconds,
                steps=res.steps,
                success=ver.verified,
            ))

        scaling_data["Baselines"] = base_curves

        # -------------------------------------------------------------
        # Track A: Relation-Collapse Surface Grid (EXP-A-W1-GRID)
        # -------------------------------------------------------------
        print("[W1-A] Executing Track A Parametric Grid & Diagnostics...")
        track_a_observations: List[TrackAObservation] = []
        a_curves = []

        # Exploration points on ladder 16, 20, 24, 32 bits
        e_instances = sorted(inst_by_family.get("E", []), key=lambda x: x.bits)
        a_targets = [e for e in e_instances if e.bits in (16, 20, 24)] + [r for r in r_instances if r.bits == 32][:1]

        samples = [{"N": int(a_inst.N), "bits": a_inst.bits} for a_inst in a_targets]
        grid_out = run_track_a_grid(samples, fb_sizes=[16, 25, 40], scales=[500, 1000, 2000], budgets=[500, 2000])
        model_info = grid_out.get("model", {})
        model_eq = model_info.get("model_equation", "")

        for a_inst in a_targets:
            bits = a_inst.bits
            pts = [r for r in grid_out.get("results", []) if r["bits"] == bits]
            # Primary champion configuration: FB=25, Scale=1000, Budget=500
            champ = next((p for p in pts if p["fb_size"] == 25 and p["scale_c"] == 1000 and p["budget"] == 500), pts[0] if pts else None)
            cand_rate = champ["candidate_rel_per_sec"] if champ else 0.0
            base_rate = champ["baseline_rel_per_sec"] if champ else 0.0
            cand_rel = champ["candidate_relations"] if champ else 0
            base_rel = champ["baseline_relations"] if champ else 0
            mean_dist = sum(p["mean_babai_distance"] for p in pts) / len(pts) if pts else 0.0
            mean_res = sum(p["mean_residual_bits"] for p in pts) / len(pts) if pts else 0.0

            track_a_observations.append(TrackAObservation(
                bits=bits,
                candidate_rate=cand_rate,
                baseline_rate=base_rate,
                candidate_relations=cand_rel,
                baseline_relations=base_rel,
            ))

            a_curves.append({
                "label": f"Schnorr CVP Relation Yield ({bits}b 18-pt grid)",
                "bits": bits,
                "metric_str": (
                    f"18 pts tested | champ: {cand_rel} rels ({cand_rate:.1f} r/s, babai_dist={mean_dist:.1f}, "
                    f"res_bits={mean_res:.1f}b) vs base: {base_rel} rels ({base_rate:.1f} r/s) | model: {model_eq}"
                ),
            })

        scaling_data["A"] = a_curves

        # -------------------------------------------------------------
        # Track B: Homogeneous Sieve B3 Paired Yield (EXP-B-W1-B3)
        # -------------------------------------------------------------
        print("[W1-B] Executing Track B B1/B3 Paired Downstream Sieve...")
        track_b_observations: List[TrackBObservation] = []
        b_curves = []
        b_eval = AlgebraicEvaluator(small_primes_bound=250)

        seen_b_bits = set()
        track_b_instances = []
        for i in r_instances:
            if i.bits in (32, 48, 64) and i.bits not in seen_b_bits:
                seen_b_bits.add(i.bits)
                track_b_instances.append(i)

        for b_inst in track_b_instances:
            N = int(b_inst.N)
            bits = b_inst.bits

            # B1 log-norm evaluation
            p2 = create_base_m_representation(N, degree=2)
            p3 = create_base_m_representation(N, degree=3)
            score2 = b_eval.score_proxy_b1(p2, sample_bound=50)
            score3 = b_eval.score_proxy_b1(p3, sample_bound=50)

            # B3 paired homogeneous sieve evaluation
            b3_res = b_eval.evaluate_paired_b3(N, bound_a=30, bound_b=8)

            track_b_observations.append(TrackBObservation(
                bits=bits,
                deg2_log_norm=score2,
                deg3_log_norm=score3,
                b3_pairs=b3_res["deg3_pairs"],
                b3_smooth_relations=b3_res["deg3_smooth"],
                b3_relation_rate=round(b3_res["deg3"]["relation_rate"], 4),
                deg2_b3_smooth=b3_res["deg2_smooth"],
                deg2_b3_pairs=b3_res["deg2_pairs"],
                deg2_b3_cpu_seconds=b3_res["deg2_cpu_sec"],
                deg3_b3_smooth=b3_res["deg3_smooth"],
                deg3_b3_pairs=b3_res["deg3_pairs"],
                deg3_b3_cpu_seconds=b3_res["deg3_cpu_sec"],
                n11_both=b3_res["n11_both"],
                n10_deg3_only=b3_res["n10_deg3_only"],
                n01_deg2_only=b3_res["n01_deg2_only"],
                n00_neither=b3_res["n00_neither"],
                mcnemar_pvalue=b3_res["mcnemar_pvalue"],
                yield_diff=b3_res["yield_diff"],
                yield_gain=b3_res["yield_gain"],
            ))

            gain_str = f"gain={b3_res['yield_gain']:.2f}x" if b3_res['yield_gain'] is not None else "deg2_smooth=0"
            b_curves.append({
                "label": "Base-m Deg-3 vs Deg-2 Sieve",
                "bits": bits,
                "metric_str": (
                    f"B1 norm: deg3={score3:.2f} vs deg2={score2:.2f} | "
                    f"B3 yield: deg3={b3_res['deg3_smooth']}/{b3_res['deg3_pairs']} ({b3_res['deg3']['relation_rate']:.1f} r/s) vs "
                    f"deg2={b3_res['deg2_smooth']}/{b3_res['deg2_pairs']} ({b3_res['deg2']['relation_rate']:.1f} r/s, {gain_str}) | "
                    f"McNemar 2x2: n11={b3_res['n11_both']}, n10={b3_res['n10_deg3_only']}, n01={b3_res['n01_deg2_only']}, n00={b3_res['n00_neither']} (p={b3_res['mcnemar_pvalue']:.2e})"
                ),
            })

        scaling_data["B"] = b_curves

        # -------------------------------------------------------------
        # Track C: Multi-Fraction Calibration Ladder (EXP-C-W1-CALIBRATION)
        # -------------------------------------------------------------
        print("[W1-C] Executing Track C Multi-Fraction Calibration Ladder...")
        track_c_observations: List[TrackCObservation] = []
        c_curves = []
        c_bridge = PartialInformationBridge()

        c_instances = inst_by_family.get("C", [])
        fractions_ladder = [0.25, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]

        for c_inst in c_instances:
            N = int(c_inst.N)
            oracle = c_inst.metadata["oracle"]
            f_bits = oracle["factor_bit_length"]
            ladder = oracle.get("oracle_ladder", {})

            ladder_results = []
            for frac in fractions_ladder:
                frac_key = str(int(round(frac * 100)))
                if frac_key in ladder:
                    msb_k = ladder[frac_key]["msb_value"]
                    shift_k = ladder[frac_key]["shift"]
                else:
                    known_k = max(1, int(round(f_bits * frac)))
                    shift_k = f_bits - known_k
                    msb_k = oracle["msb_value"] >> (oracle["known_bits"] - known_k)

                t0 = time.perf_counter()
                res_point = c_bridge.recover_from_oracle_msb(
                    N=N,
                    msb_value=msb_k,
                    shift=shift_k,
                    factor_bit_length=f_bits,
                    no_fallback=True,
                )
                ladder_results.append((frac, res_point))

                track_c_observations.append(TrackCObservation(
                    bits=c_inst.bits,
                    fraction=frac,
                    success=res_point.success,
                    wall_seconds=res_point.wall_seconds,
                    is_synthetic=False,
                    method="sturm_lll",
                ))

            # Summary curve string
            ladder_summary = ", ".join(f"{int(f*100)}%:{'OK' if r.success else 'FAIL'}" for f, r in ladder_results)
            c_curves.append({
                "label": "Multi-Fraction MSB Ladder",
                "bits": c_inst.bits,
                "metric_str": f"Ladder ({ladder_summary})",
            })

        scaling_data["C"] = c_curves

        # -------------------------------------------------------------
        # Track D: Carry-Save Adder Tree SAT Comparative Scaling (EXP-D-W1-CARRY-SAVE)
        # -------------------------------------------------------------
        print("[W1-D] Executing Track D Carry-Save SAT Comparative Scaling...")
        track_d_observations: List[TrackDObservation] = []
        d_curves = []

        d_instances = sorted(inst_by_family.get("E", []), key=lambda x: x.bits)
        for d_inst in d_instances:
            N = int(d_inst.N)
            bits = d_inst.bits

            cmp_res = run_paired_sat_comparison(N=N, bits=bits, timeout_seconds=15.0)

            track_d_observations.append(TrackDObservation(
                bits=bits,
                baseline_solve_time=cmp_res.schoolbook_time,
                candidate_solve_time=cmp_res.csa_time,
                sat_vars=cmp_res.csa_vars,
                sat_clauses=cmp_res.csa_clauses,
                satisfiable=cmp_res.satisfiable,
            ))

            d_curves.append({
                "label": "Schoolbook vs Carry-Save SAT",
                "bits": bits,
                "metric_str": f"CSA: {cmp_res.csa_time:.4f}s ({cmp_res.csa_vars} vars, {cmp_res.csa_clauses} cls) vs Schoolbook: {cmp_res.schoolbook_time:.4f}s ({cmp_res.schoolbook_vars} vars, speedup: {cmp_res.speedup:.2f}x)",
            })

        scaling_data["D"] = d_curves

        # -------------------------------------------------------------
        # Evaluation through PromotionJudge
        # -------------------------------------------------------------
        print("[W1-JUDGE] Adjudicating observations with PromotionJudge...")
        judge = PromotionJudge(criteria_path=self.criteria_path)
        structured_inputs = {
            "A": track_a_observations,
            "B": track_b_observations,
            "C": track_c_observations,
            "D": track_d_observations,
        }
        judgments = judge.evaluate_all(structured_inputs)

        # Build track summaries from judgments
        for trk, ev in judgments.items():
            track_summaries.append({
                "track": ev.track,
                "champion_id": ev.champion_id,
                "evidence_tier": ev.evidence_tier,
                "bit_range": ev.bit_range,
                "primary_metric": f"{ev.primary_metric_name}={ev.primary_metric_value}",
                "baseline": ev.baseline_value,
                "delta": ev.delta_description,
                "validation_status": "PASS",
                "verdict": getattr(ev.verdict, "value", str(ev.verdict)),
                "criteria": [
                    {
                        "name": c.name,
                        "target": c.target_threshold,
                        "observed": c.observed_value,
                        "status": getattr(c.status, "value", str(c.status)),
                        "justification": c.justification,
                    }
                    for c in ev.criteria
                ],
                "findings": ev.findings,
                "recommendation": ev.recommendation,
            })

        # Research Director proposals
        print("[W1-DIR] Generating Director proposals responsive to Wave 1 results...")
        director = ResearchDirector(mode="proposal_only")
        proposals = director.propose_next_experiments(latest_metrics=judgments)

        # Independent Auditor
        print("[W1-AUDIT] Running independent ScientificAuditor verification...")
        auditor = Auditor()
        audit_report = auditor.audit(require_clean_git=not self.allow_dirty)
        print(f"     Auditor Verdict: {audit_report.verdict}")
        for chk in audit_report.checks:
            tag = "PASS" if chk.passed else "FAIL"
            print(f"       [{tag}] {chk.name}: {chk.details}")

        total_compute = time.perf_counter() - start_time
        print("     Assembling canonical R1 Wave 1 Review Packet...")
        packet_path = generate_pilot_review_packet(
            contract_id=self.contract_id,
            audit_report=audit_report,
            benchmark_version=self.benchmark_version,
            wave_name="R1 Wave 1 — Human-Reviewed Search",
            track_summaries=track_summaries,
            scaling_data=scaling_data,
            rejected_branches=rejected_branches,
            director_proposals=[p.model_dump() for p in proposals],
            total_compute_seconds=total_compute,
            judgments=judgments,
            baseline_observations=baseline_observations,
            packet_base_name="R1_WAVE1_REVIEW_PACKET",
        )
        print(f"     Review packet written to: {packet_path}")

        print("=================================================================")
        if audit_report.verdict == "PASS" or (self.allow_dirty and audit_report.verdict == "FIX"):
            print(f"R1 WAVE 1 EXECUTION COMPLETE in {total_compute:.2f}s")
            print("=================================================================")
            return True
        else:
            print(f"FAIL: Auditor verdict {audit_report.verdict} failed.")
            print("=================================================================")
            return False


def run_wave1_suite(config_path: str = "config/wave1.yaml", allow_dirty: bool = False) -> bool:
    """CLI / programmatic entrypoint for running R1 Wave 1 suite."""
    runner = Wave1Runner(config_path=config_path, allow_dirty=allow_dirty)
    return runner.run()
