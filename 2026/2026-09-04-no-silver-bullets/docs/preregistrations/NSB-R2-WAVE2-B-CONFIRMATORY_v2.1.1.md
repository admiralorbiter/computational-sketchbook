# Preregistration Protocol Amendment v2.1.1: NSB-R2-WAVE2-B-CONFIRMATORY

**Contract ID**: `NSB-R2-WAVE2-B-CONFIRMATORY`  
**Protocol Version**: `2.1.1 (Amendment 2: Execution-Integrity Hardening)`  
**Date**: 2026-09-04  
**Primary Track**: Track B (Evolved Algebraic Representations)  
**Execution Phase**: Phase 2A (Replication & Canonical Scaling Persistence)  
**Status**: `FROZEN / SUPERSEDES v2.1 / ZERO COMPUTE SPENT`  

---

## 1. Audit Context & Amendment Rationale

The pre-run execution review verified that the prior six methodological defects (including the corpus factor collision and unenforced paired $t$-test) were resolved. However, the execution harness review identified critical integration requirements prior to launching compute:
1. **Corpus Scope Separation**: `v002_wave2/confirmatory` was already public before `FrozenSearchOptimizer` was implemented. Attempting to certify candidate search optimization on an already-exposed dataset risks post-exposure tuning. Therefore, `v002_wave2/confirmatory` is strictly scoped to **Tier 1 (Replication Claim)** and **Tier 4 (Canonical Scaling Persistence)**. Tier 2 (Search Advantage) and Tier 3 (In-House Polyselect Proxy) are formally deferred to Phase 2B on a fresh out-of-sample split `v003_wave2/search_holdout` generated with a new seed.
2. **Partial Run Prevention**: Partial runs (`max_sizes < 5`) must be mechanically incapable of issuing canonical certification. If any of the five required bit sizes ($32, 48, 64, 80, 96$) is missing, the Judge will issue `PARTIAL_RUN_DIAGNOSTIC_ONLY`.
3. **Enforced Resource Ceilings**: Resource limits in YAML are wired to active runtime enforcement in `Wave2ConfirmatoryRunner`: 5.0s CPU process time per modulus, 300.0s per cohort, 1800.0s total wall time, and 2048 MB RSS memory.
4. **CPU Accounting Integrity**: Fixed `evaluate_paired_b3()` to return `res["cpu_seconds"]` rather than `wall_seconds` for `deg2_cpu_sec` and `deg3_cpu_sec`.
5. **Search Specification Alignment**: In `search.py`, aligned `prime_bound=2000` with the contract, removed the unused `seed` claim, and documented the exact 35-candidate systematic search grid.

---

## 2. Two-Phase Wave 2 Architecture

```
[Phase 2A: This Run]
  Corpus: v002_wave2/confirmatory (150 pairwise-coprime moduli across 32b, 48b, 64b, 80b, 96b)
  Target Claims:
    - Tier 1: Replication Claim (Canonical d=3 vs d=2) -> REPLICATION_CERTIFIED
    - Tier 4: Canonical Scaling Persistence (32b -> 96b) -> SCALING_PERSISTENCE_CERTIFIED
  Harness: Requires all 5 cohorts; active resource ceilings; zero imputation.

[Phase 2B: Subsequent Out-of-Sample Evaluation]
  Corpus: v003_wave2/search_holdout (Freshly generated with new deterministic seed)
  Target Claims:
    - Tier 2: Representation-Search Claim (FrozenSearchOptimizer vs canonical base-m)
    - Tier 3: In-House Polyselect Proxy Claim (Candidate vs in-house polyselect baseline)
```

---

## 3. Operational Resource Ceilings & Stopping Rules (Phase 2A)

- **Per-Modulus CPU Limit**: 5.0 CPU seconds (`time.process_time()`). If exceeded, the modulus evaluation is interrupted and marked `TIMEOUT`.
- **Per-Cohort Wall Limit**: 300.0 seconds.
- **Total Wall Time Limit**: 1800.0 seconds (30 minutes).
- **RSS Memory Limit**: 2048 MB.
- **Full Cohort Requirement**: All 30 moduli in each of the 5 bit sizes must be executed. Truncated runs (`max_sizes < 5`) receive `PARTIAL_RUN_DIAGNOSTIC_ONLY`.
- **Zero Imputation Prohibited**: If a cohort yields 0 smooth relations across all 30 moduli, it is recorded as `ZERO_YIELD_FLOOR` without artificial numbers.
