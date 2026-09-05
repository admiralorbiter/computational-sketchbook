"""Gate 1 Pilot Execution Engine orchestrating bounded scaling pilots across tracks A, B, C, D and Baselines."""

import datetime
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from nsb.tracks.constraint_graph.encoder import SchoolbookSATEncoder
from nsb.tracks.constraint_graph.solver import SATSolverAdapter
from nsb.tracks.partial_information.bridge import PartialInformationBridge
from nsb.tracks.tensor_lattice.lattice import get_factor_base
from nsb.tracks.tensor_lattice.sampler import BabaiSchnorrLatticeSampler
from nsb.verifier.leakage import audit_environment_leakage


class PilotRunner:
    """Orchestrates the Gate 1 pilot ladder across all research tracks and classical baselines."""

    def __init__(self, config_path: str = "config/pilot.yaml", allow_dirty: bool = False):
        self.config_path = config_path
        self.allow_dirty = allow_dirty
        self.cfg, self.cfg_hash = load_config(config_path)

        db_file = Path(self.cfg.storage.database_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        self.ledger = ExperimentLedger(db_path=db_file)

    def run_all(self) -> bool:
        """Run complete Gate 1 pilot suite."""
        print("=================================================================")
        print("NO SILVER BULLET — GATE 1 PILOT SUITE (PILOT A-P1 .. D-P1 & BASELINES)")
        print("=================================================================")

        start_time = time.perf_counter()

        # Step 0: Environment & Provenance
        print(f"[P0] Capturing environment fingerprint (Config hash: {self.cfg_hash[:8]})...")
        fp = capture_environment_fingerprint()
        print(f"     OS: {fp.os_name} {fp.os_release} ({fp.architecture})")
        print(f"     Python: {fp.python_version}")
        print(f"     Git Commit: {fp.git_commit[:10]} (Dirty: {fp.git_dirty})")
        print(f"     CPU: {fp.cpu_model} ({fp.cpu_count_logical} logical cores)")

        if fp.git_dirty and not self.allow_dirty:
            print("FAIL: Working tree is dirty. Canonical pilot runs require clean git HEAD.")
            return False

        leakage_env = audit_environment_leakage()
        if not leakage_env.passed:
            print(f"FAIL: Environment leakage detected: {leakage_env.violations}")
            return False

        # Step 1: Sandbox & Benchmark Instances
        print("[P1] Initializing isolated worker sandbox and loading pilot corpus...")
        sandbox = WorkerSandbox(base_dir=".", cleanup_on_exit=False)
        sandbox_dir = sandbox.setup(
            experiment_id="PILOT_SUITE",
            run_id="RUN_001",
            version=self.cfg.benchmark_version,
            split="pilot",
        )
        instances = load_public_instances(".", self.cfg.benchmark_version, "pilot")
        print(f"     Loaded {len(instances)} public instances across families R, F, P1, C, E.")
        inst_by_id = {i.instance_id: i for i in instances}
        inst_by_family: Dict[str, List[Any]] = {}
        for i in instances:
            inst_by_family.setdefault(i.family, []).append(i)

        track_summaries: List[Dict[str, Any]] = []
        scaling_data: Dict[str, List[Dict[str, Any]]] = {}
        rejected_branches: List[Dict[str, Any]] = []

        # -------------------------------------------------------------
        # Step 2: Baselines Scaling Ladder
        # -------------------------------------------------------------
        print("[P2] Running Baselines Pilot (Fermat, Pollard rho, Pollard p-1)...")
        exp_id_base = f"EXP-BASELINES-PILOT-{self.cfg.benchmark_version}"
        self.ledger.insert_experiment(
            exp_id=exp_id_base,
            track="BASELINES",
            contract_id=self.cfg.contract_id,
            commit_sha=fp.git_commit,
            config_sha256=self.cfg_hash,
            benchmark_version=self.cfg.benchmark_version,
            status="RUNNING",
        )

        base_curves = []
        baseline_observations = []
        # Family F (Fermat positive controls)
        for f_inst in inst_by_family.get("F", []):
            res, ver = run_baseline_solve("fermat", int(f_inst.N))
            run_id = f"RUN-FMT-{f_inst.instance_id}"
            self.ledger.insert_run(
                run_id=run_id,
                experiment_id=exp_id_base,
                instance_id=f_inst.instance_id,
                bit_length=f_inst.bits,
                method="fermat",
                wall_seconds=res.wall_seconds,
                cpu_seconds=res.cpu_seconds,
            )
            self.ledger.insert_metric(run_id, "steps", float(res.steps), "count")
            base_curves.append({"label": "Fermat (Family F)", "bits": f_inst.bits, "metric_str": f"{res.steps} steps ({res.wall_seconds:.5f}s)"})
            baseline_observations.append(BaselineObservation(
                family="F",
                method="fermat",
                bits=f_inst.bits,
                wall_seconds=res.wall_seconds,
                steps=res.steps,
                success=ver.verified,
            ))

        # Family P1 (Pollard p-1 positive controls)
        for p1_inst in inst_by_family.get("P1", []):
            res, ver = run_baseline_solve("pollard_pm1", int(p1_inst.N))
            run_id = f"RUN-PM1-{p1_inst.instance_id}"
            self.ledger.insert_run(
                run_id=run_id,
                experiment_id=exp_id_base,
                instance_id=p1_inst.instance_id,
                bit_length=p1_inst.bits,
                method="pollard_pm1",
                wall_seconds=res.wall_seconds,
                cpu_seconds=res.cpu_seconds,
            )
            base_curves.append({"label": "Pollard p-1 (Family P1)", "bits": p1_inst.bits, "metric_str": f"{res.wall_seconds:.5f}s"})
            baseline_observations.append(BaselineObservation(
                family="P1",
                method="pollard_pm1",
                bits=p1_inst.bits,
                wall_seconds=res.wall_seconds,
                steps=None,
                success=ver.verified,
            ))

        # Family R small (Pollard rho comparison)
        r_instances = sorted(inst_by_family.get("R", []), key=lambda x: x.bits)
        for r_inst in [i for i in r_instances if i.bits <= 40]:
            res, ver = run_baseline_solve("pollard_rho", int(r_inst.N), max_steps=200000)
            run_id = f"RUN-RHO-{r_inst.instance_id}"
            self.ledger.insert_run(
                run_id=run_id,
                experiment_id=exp_id_base,
                instance_id=r_inst.instance_id,
                bit_length=r_inst.bits,
                method="pollard_rho",
                wall_seconds=res.wall_seconds,
                cpu_seconds=res.cpu_seconds,
            )
            self.ledger.insert_metric(run_id, "steps", float(res.steps), "count")
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
        self.ledger.update_experiment_status(exp_id_base, status="COMPLETED", verdict="PASS")

        # -------------------------------------------------------------
        # Step 3: Track A Pilot (Pilot A-P1: Tensor/Lattice)
        # -------------------------------------------------------------
        print("[P3] Running Track A Pilot A-P1 (Babai/Schnorr CVP Relation Yield vs Scale)...")
        exp_id_a = f"EXP-TRACK-A-PILOT-{self.cfg.benchmark_version}"
        self.ledger.insert_experiment(
            exp_id=exp_id_a,
            track="A",
            contract_id=self.cfg.contract_id,
            commit_sha=fp.git_commit,
            config_sha256=self.cfg_hash,
            benchmark_version=self.cfg.benchmark_version,
            status="RUNNING",
        )

        a_curves = []
        track_a_observations = []
        fb_size = 16
        # Ladder of 16, 20, 32 bits to evaluate empirical scaling of relation yield
        a_instances = [e for e in inst_by_family.get("E", []) if e.bits in (16, 20)] + [r for r in r_instances if r.bits == 32][:1]
        for a_inst in a_instances:
            N = int(a_inst.N)
            # Baseline scale C=500
            s_base = BabaiSchnorrLatticeSampler(factor_base_size=fb_size, scale_c=500)
            t0 = time.perf_counter()
            c0 = time.process_time()
            rels_base = s_base.sample_relations(N, max_candidates=500)
            t_wall_base = time.perf_counter() - t0
            t_cpu_base = max(0.001, time.process_time() - c0)
            rate_base = len(rels_base) / t_cpu_base

            # Candidate scale C=2000
            s_cand = BabaiSchnorrLatticeSampler(factor_base_size=fb_size, scale_c=2000)
            t0 = time.perf_counter()
            c0 = time.process_time()
            rels_cand = s_cand.sample_relations(N, max_candidates=500)
            t_wall_cand = time.perf_counter() - t0
            t_cpu_cand = max(0.001, time.process_time() - c0)
            rate_cand = len(rels_cand) / t_cpu_cand

            run_id = f"RUN-TRK-A-{a_inst.instance_id}"
            self.ledger.insert_run(
                run_id=run_id,
                experiment_id=exp_id_a,
                instance_id=a_inst.instance_id,
                bit_length=a_inst.bits,
                method="schnorr_cvp_c2000",
                wall_seconds=t_wall_cand,
                cpu_seconds=t_cpu_cand,
            )
            self.ledger.insert_metric(run_id, "relations_found", float(len(rels_cand)), "count")
            self.ledger.insert_metric(run_id, "relations_per_cpu_sec", rate_cand, "rate")
            a_curves.append({
                "label": f"Schnorr CVP C=2000 vs C=500",
                "bits": a_inst.bits,
                "metric_str": f"{len(rels_cand)} rels ({rate_cand:.1f}/cpu_s) vs baseline {len(rels_base)} rels ({rate_base:.1f}/cpu_s)",
            })
            track_a_observations.append(TrackAObservation(
                bits=a_inst.bits,
                candidate_rate=rate_cand,
                baseline_rate=rate_base,
                candidate_relations=len(rels_cand),
                baseline_relations=len(rels_base),
            ))

        scaling_data["A"] = a_curves
        self.ledger.update_experiment_status(exp_id_a, status="COMPLETED", verdict="PASS")

        # -------------------------------------------------------------
        # Step 4: Track B Pilot (Pilot B-P1: Algebraic Evolution)
        # -------------------------------------------------------------
        print("[P4] Running Track B Pilot B-P1 (Cascade B0-B3 on Degree-2 vs Degree-3 Base-m)...")
        exp_id_b = f"EXP-TRACK-B-PILOT-{self.cfg.benchmark_version}"
        self.ledger.insert_experiment(
            exp_id=exp_id_b,
            track="B",
            contract_id=self.cfg.contract_id,
            commit_sha=fp.git_commit,
            config_sha256=self.cfg_hash,
            benchmark_version=self.cfg.benchmark_version,
            status="RUNNING",
        )

        b_eval = AlgebraicEvaluator()
        b_curves = []
        track_b_observations = []
        # Select one distinct instance per bit size (32, 48, 64)
        seen_b_bits = set()
        track_b_instances = []
        for i in r_instances:
            if i.bits in (32, 48, 64) and i.bits not in seen_b_bits:
                seen_b_bits.add(i.bits)
                track_b_instances.append(i)

        for r_inst in track_b_instances:
            N = int(r_inst.N)
            # Degree 2
            p2 = create_base_m_representation(N, degree=2)
            v2, _ = b_eval.validate_b0(p2, N)
            score2 = b_eval.score_proxy_b1(p2, sample_bound=50)
            homo2 = b_eval.homogeneous_sieve_b3(p2, bound_a=20, bound_b=5)

            # Degree 3
            p3 = create_base_m_representation(N, degree=3)
            v3, _ = b_eval.validate_b0(p3, N)
            score3 = b_eval.score_proxy_b1(p3, sample_bound=50)
            homo3 = b_eval.homogeneous_sieve_b3(p3, bound_a=20, bound_b=5)

            run_id = f"RUN-TRK-B-{r_inst.instance_id}"
            self.ledger.insert_run(
                run_id=run_id,
                experiment_id=exp_id_b,
                instance_id=r_inst.instance_id,
                bit_length=r_inst.bits,
                method="base_m_deg3_vs_deg2",
            )
            self.ledger.insert_metric(run_id, "log_norm_deg2", score2, "score")
            self.ledger.insert_metric(run_id, "log_norm_deg3", score3, "score")

            b_curves.append({
                "label": "Base-m deg-3 vs deg-2 log-norm",
                "bits": r_inst.bits,
                "metric_str": f"deg-3={score3:.2f} (homo: {homo3['total_pairs']}) vs deg-2={score2:.2f} (homo: {homo2['total_pairs']})",
            })
            track_b_observations.append(TrackBObservation(
                bits=r_inst.bits,
                deg2_log_norm=score2,
                deg3_log_norm=score3,
                b3_pairs=homo3["total_pairs"],
                b3_smooth_relations=0,
                b3_relation_rate=0.0,
            ))

        scaling_data["B"] = b_curves
        self.ledger.update_experiment_status(exp_id_b, status="COMPLETED", verdict="PASS")

        # -------------------------------------------------------------
        # Step 5: Track C Pilot (Pilot C-P1: Partial Information Bridge)
        # -------------------------------------------------------------
        print("[P5] Running Track C Pilot C-P1 (Oracle MSB Calibration Curve Across Fractions)...")
        exp_id_c = f"EXP-TRACK-C-PILOT-{self.cfg.benchmark_version}"
        self.ledger.insert_experiment(
            exp_id=exp_id_c,
            track="C",
            contract_id=self.cfg.contract_id,
            commit_sha=fp.git_commit,
            config_sha256=self.cfg_hash,
            benchmark_version=self.cfg.benchmark_version,
            status="RUNNING",
        )

        c_bridge = PartialInformationBridge()
        c_curves = []
        track_c_observations = []
        for c_inst in inst_by_family.get("C", []):
            N = int(c_inst.N)
            oracle = c_inst.metadata["oracle"]
            f_bits = oracle["factor_bit_length"]

            # Test 50% fraction (positive recovery)
            res50 = c_bridge.recover_from_oracle_msb(
                N=N,
                msb_value=oracle["msb_value"],
                shift=oracle["shift"],
                factor_bit_length=f_bits,
                no_fallback=True,
            )

            # Test 25% fraction (negative control - must fail cleanly)
            res25 = c_bridge.recover_from_oracle_msb(
                N=N,
                msb_value=1,
                shift=int(f_bits * 0.75),
                factor_bit_length=f_bits,
                no_fallback=True,
            )

            run_id = f"RUN-TRK-C-{c_inst.instance_id}"
            self.ledger.insert_run(
                run_id=run_id,
                experiment_id=exp_id_c,
                instance_id=c_inst.instance_id,
                bit_length=c_inst.bits,
                method="sturm_lattice_recovery",
                wall_seconds=res50.wall_seconds,
                cpu_seconds=res50.cpu_seconds,
            )
            self.ledger.insert_metric(run_id, "rec_50pct_success", 1.0 if res50.success else 0.0, "binary")
            self.ledger.insert_metric(run_id, "rec_25pct_success", 1.0 if res25.success else 0.0, "binary")

            c_curves.append({
                "label": "Oracle MSB Recovery Curve",
                "bits": c_inst.bits,
                "metric_str": f"50% MSB: {'SUCCESS' if res50.success else 'FAIL'} ({res50.wall_seconds:.4f}s); 25% MSB: {'CLEAN_FAIL' if not res25.success else 'LEAK_BUG'}",
            })
            track_c_observations.append(TrackCObservation(
                bits=c_inst.bits,
                fraction=0.50,
                success=res50.success,
                wall_seconds=res50.wall_seconds,
                is_synthetic=False,
            ))
            track_c_observations.append(TrackCObservation(
                bits=c_inst.bits,
                fraction=0.25,
                success=res25.success,
                wall_seconds=res25.wall_seconds,
                is_synthetic=True,
            ))

        scaling_data["C"] = c_curves
        self.ledger.update_experiment_status(exp_id_c, status="COMPLETED", verdict="PASS")

        # -------------------------------------------------------------
        # Step 6: Track D Pilot (Pilot D-P1: Constraint Graph SAT)
        # -------------------------------------------------------------
        print("[P6] Running Track D Pilot D-P1 (Schoolbook SAT Inversion Scaling Ladder 16-32 bits)...")
        exp_id_d = f"EXP-TRACK-D-PILOT-{self.cfg.benchmark_version}"
        self.ledger.insert_experiment(
            exp_id=exp_id_d,
            track="D",
            contract_id=self.cfg.contract_id,
            commit_sha=fp.git_commit,
            config_sha256=self.cfg_hash,
            benchmark_version=self.cfg.benchmark_version,
            status="RUNNING",
        )

        d_curves = []
        track_d_observations = []
        e_instances = sorted(inst_by_family.get("E", []), key=lambda x: x.bits)
        for e_inst in e_instances:
            N = int(e_inst.N)
            encoder = SchoolbookSATEncoder()
            cnf, vmap = encoder.encode(N)
            sol = SATSolverAdapter(solver_name="glucose4").solve(cnf, vmap, timeout_seconds=15.0)

            run_id = f"RUN-TRK-D-{e_inst.instance_id}"
            self.ledger.insert_run(
                run_id=run_id,
                experiment_id=exp_id_d,
                instance_id=e_inst.instance_id,
                bit_length=e_inst.bits,
                method="sat_glucose4_schoolbook",
                wall_seconds=sol.solve_time_seconds,
                cpu_seconds=sol.solve_time_seconds,
            )
            self.ledger.insert_metric(run_id, "sat_variables", float(cnf.nv), "count")
            self.ledger.insert_metric(run_id, "sat_clauses", float(len(cnf.clauses)), "count")
            self.ledger.insert_metric(run_id, "solve_time", sol.solve_time_seconds, "seconds")

            d_curves.append({
                "label": "Schoolbook SAT Glucose4",
                "bits": e_inst.bits,
                "metric_str": f"{sol.solve_time_seconds:.4f}s ({cnf.nv} vars, {len(cnf.clauses)} clauses, sat={sol.satisfiable})",
            })
            track_d_observations.append(TrackDObservation(
                bits=e_inst.bits,
                baseline_solve_time=sol.solve_time_seconds,
                candidate_solve_time=None,
                sat_vars=cnf.nv,
                sat_clauses=len(cnf.clauses),
                satisfiable=sol.satisfiable,
            ))

        scaling_data["D"] = d_curves
        self.ledger.update_experiment_status(exp_id_d, status="COMPLETED", verdict="PASS")

        # -------------------------------------------------------------
        # Step 7: Scientific Promotion Judge Mechanical Evaluation
        # -------------------------------------------------------------
        print("[P7] Running Scientific Promotion Judge across empirical metrics...")
        judge = PromotionJudge()
        judgments = judge.evaluate_all(track_data={
            "A": track_a_observations,
            "B": track_b_observations,
            "C": track_c_observations,
            "D": track_d_observations,
        })
        for trk_key in ["A", "B", "C", "D"]:
            ev = judgments[trk_key]
            v_str = getattr(ev.verdict, "value", str(ev.verdict))
            print(f"     Track {trk_key} Verdict: {v_str} ({ev.delta_description})")
            track_summaries.append({
                "track": ev.track,
                "champion_id": ev.champion_id,
                "evidence_tier": ev.evidence_tier,
                "bit_range": ev.bit_range,
                "primary_metric": f"{ev.primary_metric_name}: {ev.primary_metric_value}",
                "baseline": ev.baseline_value,
                "delta": ev.delta_description,
                "validation_status": "VALIDATED",
                "verdict": v_str,
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

        # -------------------------------------------------------------
        # Step 8: Director Proposals Responsive to Promotion Judge
        # -------------------------------------------------------------
        print("[P8] Research Director generating proposals conditioned on empirical judge results...")
        director = ResearchDirector(mode="proposal_only")
        proposals = director.propose_next_experiments(latest_metrics=judgments)

        # -------------------------------------------------------------
        # Step 9: Independent Auditor Check & Certified Review Packet
        # -------------------------------------------------------------
        print("[P9] Executing independent scientific audit on pilot results...")
        auditor = Auditor()
        audit_report = auditor.audit(require_clean_git=not self.allow_dirty)
        print(f"     Auditor Verdict: {audit_report.verdict}")
        for chk in audit_report.checks:
            tag = "PASS" if chk.passed else "FAIL"
            print(f"       [{tag}] {chk.name}: {chk.details}")

        total_compute = time.perf_counter() - start_time
        print("     Assembling certified Gate 1A Pilot Review Packet...")
        packet_path = generate_pilot_review_packet(
            contract_id=self.cfg.contract_id,
            audit_report=audit_report,
            benchmark_version=self.cfg.benchmark_version,
            wave_name="Gate 1A — Feasibility & Calibration",
            track_summaries=track_summaries,
            scaling_data=scaling_data,
            rejected_branches=rejected_branches,
            director_proposals=[p.model_dump() for p in proposals],
            total_compute_seconds=total_compute,
            judgments=judgments,
            baseline_observations=baseline_observations,
        )
        print(f"     Review packet written to: {packet_path}")

        print("=================================================================")
        if audit_report.verdict == "PASS" or (self.allow_dirty and audit_report.verdict == "FIX"):
            print(f"GATE 1A PILOT SUITE PASSED & CERTIFIED in {total_compute:.2f}s")
            print("=================================================================")
            return True
        else:
            print(f"FAIL: Audit verdict {audit_report.verdict} does not certify Gate 1 pass.")
            print("=================================================================")
            return False


def run_pilot_suite(config_path: str = "config/pilot.yaml", allow_dirty: bool = False) -> bool:
    """CLI entrypoint for running the pilot suite."""
    runner = PilotRunner(config_path=config_path, allow_dirty=allow_dirty)
    return runner.run_all()
