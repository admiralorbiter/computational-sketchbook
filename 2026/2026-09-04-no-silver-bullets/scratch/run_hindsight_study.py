"""Stage 1 Hindsight Oracle Ceiling Study.

Evaluates 12 public calibration instances (3 each of 60d, 70d, 80d, 90d).
Measures:
1. Complete CADO candidate pools.
2. Standardized sieve relation yield across all candidates in each pool.
3. Hindsight oracle headroom (difference between best available polynomial and CADO default).
4. Feature correlation (Murphy-E vs actual relation yield).
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector
from nsb.baselines.cado_nfs.sieve import CadoRelationCollector
from nsb.baselines.cado_nfs.profiles import (
    CADO_PARAMS_C60,
    CADO_PARAMS_C70,
    CADO_PARAMS_C80,
    CADO_PARAMS_C90,
)

PROFILES_BY_DIGITS = {
    60: CADO_PARAMS_C60,
    70: CADO_PARAMS_C70,
    80: CADO_PARAMS_C80,
    90: CADO_PARAMS_C90,
}

# Select 3 instances per digit size (indices 1, 2, 3 of each digit cohort)
SELECTED_INSTANCE_IDS = [
    # 60d
    "R3-CALIB-D060-00001",
    "R3-CALIB-D060-00002",
    "R3-CALIB-D060-00003",
    # 70d
    "R3-CALIB-D070-00001",
    "R3-CALIB-D070-00002",
    "R3-CALIB-D070-00003",
    # 80d
    "R3-CALIB-D080-00001",
    "R3-CALIB-D080-00002",
    "R3-CALIB-D080-00003",
    # 90d
    "R3-CALIB-D090-00001",
    "R3-CALIB-D090-00002",
    "R3-CALIB-D090-00003",
]

def load_selected_instances() -> List[Dict[str, Any]]:
    instances_file = Path("benchmarks/public/v005_r3_calibration/public_calibration/instances.jsonl")
    selected = []
    with open(instances_file) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("instance_id") in SELECTED_INSTANCE_IDS:
                selected.append(rec)
    return selected

def main():
    instances = load_selected_instances()
    print(f"Loaded {len(instances)} selected instances across 60d, 70d, 80d, 90d.")
    
    selector = CadoPolynomialSelector()
    collector = CadoRelationCollector()
    
    output_dir = Path("reports/candidates/hindsight_study")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    study_results = []
    
    t_study_start = time.time()
    
    for inst_idx, inst in enumerate(instances):
        inst_id = inst["instance_id"]
        digits = int(inst["digits"])
        N = int(inst["N"])
        profile = PROFILES_BY_DIGITS[digits]
        
        print(f"\n=======================================================")
        print(f"[{inst_idx+1}/12] Evaluating {inst_id} ({digits}d, N={str(N)[:8]}...{str(N)[-8:]})")
        print(f"Profile: {profile.name} (degree={profile.degree}, p_val={profile.p_val})")
        print(f"=======================================================")
        
        t0_pool = time.time()
        pool, pool_cpu, pool_wall = selector.generate_stage1_pool(
            n=N,
            profile=profile,
            timeout_seconds=300.0,
            run_ropt_on_candidates=True,
        )
        t_pool_wall = time.time() - t0_pool
        print(f"Pool size: {len(pool)} candidates generated in {t_pool_wall:.2f}s wall, {pool_cpu:.2f}s CPU.")
        
        # Standardized special-q range for identical evaluation
        # Use min(profile.qrange, 1000) for fast high-precision comparison
        q_eval_range = min(profile.qrange, 1000)
        
        poly_evaluations = []
        
        for p_idx, poly in enumerate(pool):
            murphy_e = float(poly.metadata.get("murphy_e", 0.0) or 0.0)
            alpha = float(poly.metadata.get("alpha", 0.0) or 0.0)
            exp_e = float(poly.metadata.get("exp_e", 0.0) or 0.0)
            
            t0_sieve = time.time()
            sieve_res = collector.collect_relations(
                poly=poly,
                q_start=profile.qmin,
                q_range=q_eval_range,
                profile=profile,
                run_makefb=True,
                validate_with_check_rels=False,
                timeout_seconds=120.0,
            )
            t_sieve_wall = time.time() - t0_sieve
            
            p_data = {
                "index": p_idx,
                "is_cado_default": (p_idx == 0),
                "murphy_e": murphy_e,
                "alpha": alpha,
                "exp_e": exp_e,
                "skew": poly.skew,
                "degree1": poly.degree1,
                "degree2": poly.degree2,
                "total_relations": sieve_res.total_relations,
                "unique_relations": sieve_res.unique_relations,
                "sieve_cpu_seconds": sieve_res.cpu_seconds,
                "relations_per_cpu_sec": sieve_res.relations_per_cpu_second,
            }
            poly_evaluations.append(p_data)
            print(
                f"  Cand {p_idx:02d} {'[CADO]' if p_idx == 0 else '      '}: "
                f"E={murphy_e:.3e} | alpha={alpha:.2f} | "
                f"rels={sieve_res.total_relations:4d} | "
                f"cpu={sieve_res.cpu_seconds:5.2f}s | "
                f"yield={sieve_res.relations_per_cpu_second:7.1f} rel/s"
            )
            
        # Analysis for this instance
        cado_default = poly_evaluations[0]
        oracle_yield_best = max(poly_evaluations, key=lambda p: p["relations_per_cpu_sec"])
        oracle_rels_best = max(poly_evaluations, key=lambda p: p["total_relations"])
        
        c_yield = cado_default["relations_per_cpu_sec"]
        o_yield = oracle_yield_best["relations_per_cpu_sec"]
        yield_headroom_pct = ((o_yield - c_yield) / c_yield * 100.0) if c_yield > 0 else 0.0
        
        c_rels = cado_default["total_relations"]
        o_rels = oracle_rels_best["total_relations"]
        rels_headroom_pct = ((o_rels - c_rels) / c_rels * 100.0) if c_rels > 0 else 0.0
        
        # Rank of CADO default by actual yield (1 = best)
        sorted_by_yield = sorted(poly_evaluations, key=lambda p: p["relations_per_cpu_sec"], reverse=True)
        cado_yield_rank = [p["index"] for p in sorted_by_yield].index(0) + 1
        
        # Correlation between Murphy-E and actual yield
        e_vals = [p["murphy_e"] for p in poly_evaluations]
        y_vals = [p["relations_per_cpu_sec"] for p in poly_evaluations]
        corr_e_yield = float(np.corrcoef(e_vals, y_vals)[0, 1]) if len(e_vals) > 1 and np.std(e_vals) > 0 and np.std(y_vals) > 0 else 0.0
        
        inst_summary = {
            "instance_id": inst_id,
            "digits": digits,
            "N": str(N),
            "profile_name": profile.name,
            "pool_size": len(pool),
            "pool_cpu_seconds": pool_cpu,
            "pool_wall_seconds": pool_wall,
            "cado_default": {
                "murphy_e": cado_default["murphy_e"],
                "total_relations": c_rels,
                "relations_per_cpu_sec": c_yield,
                "rank_in_pool": cado_yield_rank,
            },
            "oracle_best": {
                "index": oracle_yield_best["index"],
                "murphy_e": oracle_yield_best["murphy_e"],
                "total_relations": oracle_yield_best["total_relations"],
                "relations_per_cpu_sec": o_yield,
            },
            "yield_headroom_pct": yield_headroom_pct,
            "relations_headroom_pct": rels_headroom_pct,
            "murphy_e_yield_correlation": corr_e_yield,
            "candidates": poly_evaluations,
        }
        study_results.append(inst_summary)
        
        print(f"\n>> Instance {inst_id} Summary:")
        print(f"   CADO Default Yield : {c_yield:.1f} rel/s (Rank {cado_yield_rank}/{len(pool)})")
        print(f"   Oracle Best Yield  : {o_yield:.1f} rel/s (Cand {oracle_yield_best['index']})")
        print(f"   Yield Headroom     : +{yield_headroom_pct:.2f}%")
        print(f"   Relations Headroom : +{rels_headroom_pct:.2f}%")
        print(f"   Murphy-E / Yield r : {corr_e_yield:.3f}")
        
    # Global Study Synthesis
    print("\n" + "=" * 60)
    print("GLOBAL HINDSIGHT ORACLE STUDY RESULTS")
    print("=" * 60)
    
    by_digit = {}
    for res in study_results:
        d = res["digits"]
        by_digit.setdefault(d, []).append(res)
        
    cohort_summaries = {}
    all_headrooms = [r["yield_headroom_pct"] for r in study_results]
    all_rels_headrooms = [r["relations_headroom_pct"] for r in study_results]
    all_ranks = [r["cado_default"]["rank_in_pool"] for r in study_results]
    all_corrs = [r["murphy_e_yield_correlation"] for r in study_results]
    
    print("\n| Digit | Instances | Mean Headroom | Max Headroom | Mean CADO Rank | Mean Murphy-E r |")
    print("| :---: | :-------: | :-----------: | :----------: | :------------: | :-------------: |")
    
    for d, d_results in sorted(by_digit.items()):
        h_vals = [r["yield_headroom_pct"] for r in d_results]
        r_vals = [r["cado_default"]["rank_in_pool"] for r in d_results]
        c_vals = [r["murphy_e_yield_correlation"] for r in d_results]
        
        m_headroom = float(np.mean(h_vals))
        max_headroom = float(np.max(h_vals))
        m_rank = float(np.mean(r_vals))
        m_corr = float(np.mean(c_vals))
        
        cohort_summaries[f"d{d}"] = {
            "digits": d,
            "instances": len(d_results),
            "mean_yield_headroom_pct": m_headroom,
            "max_yield_headroom_pct": max_headroom,
            "mean_cado_rank": m_rank,
            "mean_murphy_e_corr": m_corr,
        }
        print(f"| {d}d | {len(d_results)} | +{m_headroom:.2f}% | +{max_headroom:.2f}% | {m_rank:.1f} | {m_corr:.3f} |")
        
    overall_mean_headroom = float(np.mean(all_headrooms))
    overall_max_headroom = float(np.max(all_headrooms))
    overall_mean_rank = float(np.mean(all_ranks))
    overall_mean_corr = float(np.mean(all_corrs))
    
    print("-" * 60)
    print(f"OVERALL MEAN HEADROOM: +{overall_mean_headroom:.2f}% (Max: +{overall_max_headroom:.2f}%)")
    print(f"OVERALL MEAN CADO RANK: {overall_mean_rank:.1f}")
    print(f"OVERALL MEAN CORRELATION (Murphy-E vs Yield): {overall_mean_corr:.3f}")
    print(f"Total Study Time: {time.time() - t_study_start:.2f}s")
    
    final_output = {
        "benchmark_version": "v005_r3_calibration",
        "study": "hindsight_oracle_ceiling",
        "total_instances": len(study_results),
        "overall_mean_yield_headroom_pct": overall_mean_headroom,
        "overall_max_yield_headroom_pct": overall_max_headroom,
        "overall_mean_cado_rank": overall_mean_rank,
        "overall_mean_murphy_e_corr": overall_mean_corr,
        "cohort_summaries": cohort_summaries,
        "instances": study_results,
    }
    
    out_file = output_dir / "hindsight_oracle_results.json"
    with open(out_file, "w") as f:
        json.dump(final_output, f, indent=2)
    print(f"\nComplete study saved to {out_file}")

if __name__ == "__main__":
    main()
