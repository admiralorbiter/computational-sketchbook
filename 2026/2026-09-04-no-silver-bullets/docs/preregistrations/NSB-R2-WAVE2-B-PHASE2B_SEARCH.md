# Preregistration Protocol: NSB-R2-WAVE2-B-PHASE2B

**Contract ID**: `NSB-R2-WAVE2-B-PHASE2B`  
**Protocol Version**: `1.3 (Resource-Only Amendment: Calibrated Ceilings from v002 Profiling, Fresh v004 Holdout Scope)`  
**Date**: 2026-09-04  
**Primary Track**: Track B (Evolved Algebraic Representations)  
**Execution Phase**: Phase 2B (Search & Polyselect Proxy on Fresh Out-of-Sample Holdout)  
**Status**: `PREREGISTERED / AWAITING v004 HOLDOUT GENERATION & EXECUTION AUTHORIZATION`  

---

## 1. Scientific Context & Core Research Question

Phase 2A established that canonical base-$m$ degree-3 polynomials achieve statistically overwhelming yield superiority over degree-2 at 32b ($93.3\%$ win rate, $p=7.67 \times 10^{-6}$) and 48b ($100.0\%$ win rate, $p=1.72 \times 10^{-6}$), but the fixed assay ($A=100, B=20, FB=250$) enters an event-starved sparse-relation regime at 64 bits ($23.3\%$ win rate, 22 ties out of 30 moduli), reaching a zero-yield measurement floor at 80b and 96b.

The core research question of Phase 2B is:
> **Can frozen representation search (translations and linear rotations) lift absolute relation density enough to escape the 64b–96b sparse-sieve floor on a fresh out-of-sample holdout corpus?**

---

## 2. Preregistered Claims & Hypotheses

### Target vs Supporting Bit Sizes
- **Primary Target Bit Sizes**: `[64, 80, 96]`. Global certification of Tier 2 or Tier 3 requires **ALL** target bit sizes to PASS.
- **Supporting Bit Sizes**: `[32, 48]`. Evaluated as baseline controls; passing 32b and/or 48b alone cannot confer global certification.

### Tier 2: Representation-Search Claim (`search_claim`)
- **Baseline**: Canonical base-$m$ degree 3.
- **Candidate**: `FrozenSearchOptimizer` degree 3 (deterministic systematic grid of 1 canonical + 10 translations + 24 linear rotations = 35 evaluations, capped by budget of 50).
- **Assay**: $A=100, B=20, FB=250$, candidate degree 3.
- **Primary Metric**: Modulus-paired smooth relation yield difference.
- **Statistical Direction**: One-sided (`alternative: "greater"`).
- **Preregistered Gates**:
  1. Mean paired yield gain $\ge 1.15\times$ over canonical base-$m$ (evaluated via raw unrounded comparison: $\text{mean\_cand\_yield} \ge 1.15 \times \text{mean\_base\_yield}$ if baseline $> 0$).
  2. Candidate win rate $\ge 70.0\%$ of independent moduli.
  3. Non-parametric Wilcoxon $p \le 0.01$ and parametric paired $t$-test $p \le 0.01$ (one-sided).
  4. Mean paired difference $> 0$.
  5. **Executable Log-Norm Gate**: Cohort mean paired B1 log-norm ratio ($\text{cand\_norm} / \text{base\_norm}$) $\le 0.95$.
  6. **Absolute Relation Floor Criterion**: At least $50\%$ of moduli in the cohort ($\ge 15/30$) must produce $\ge 1$ smooth relation for the candidate.
  7. **Target Zero Policy**: For target cohorts (`[64, 80, 96]`), remaining at 0-vs-0 yield is classified as a Tier-2 `FAIL` (relation floor $0.0\% < 50.0\%$), NOT an exempt non-evaluable floor.
- **Target Verdict**: `SEARCH_ADVANTAGE_CERTIFIED` (conferred only if ALL target cohorts [64, 80, 96] pass).

### Tier 3: In-House Polyselect Proxy Claim (`in_house_polyselect_proxy`)
- **Baseline**: Symmetrical in-house polyselect baseline (`select_in_house_murphy_e_baseline()`). Searches the identical 35-representation space (canonical + 10 translations $m \pm 5$ + 24 linear rotations $u, v \in [-2, 2]$) evaluating the identical B0-valid subset, maximizing Murphy-$E$.
- **Candidate**: `FrozenSearchOptimizer` candidate.
- **Statistical Direction**: One-sided (`alternative: "greater"`).
- **Preregistered Gates**:
  1. Modulus-level paired empirical yield Wilcoxon signed-rank test $p \le 0.01$ and strict positive mean difference ($\text{proxy\_yield\_diff} > 0.0$).
  2. Murphy-$E$ rating: raw mean candidate Murphy-$E \ge$ raw mean proxy Murphy-$E$ (prevents rounding artifacts such as 0.99996 rounding to 1.0000).
  3. Empirical throughput: raw cumulative candidate throughput $\ge$ raw cumulative proxy throughput.
  4. **Target Floor Independence**: If candidate and canonical produce zero relations but the proxy produces relations, Tier 3 is evaluable and fails.
  5. **Prohibition of SOTA Overclaim**: Explicitly forbids claiming CADO-NFS SOTA.
- **Target Verdict**: `IN_HOUSE_POLYSELECT_PROXY_BEATEN` (conferred only if ALL target cohorts [64, 80, 96] pass).

### Zero-Denominator Semantics
- When baseline yield is zero, `yield_ratio = None`.
- When baseline throughput is zero, `throughput_ratio = None`.
- Synthetic sentinels (such as `999.0` or float infinities) are strictly forbidden across all statistical pipelines.

---

## 3. Fresh Holdout Corpus Specification
 
- **Target Corpus**: `v004_wave2/search_holdout`
- **Specification**: 150 balanced random semiprimes (Family R, 30 per cohort across 32, 48, 64, 80, 96 bits).
- **Master RNG Seed Derivation**: Dynamic derivation derived deterministically from the SHA of the final pre-holdout executable freeze commit:
  $$\text{seed} = \text{int}\left(\text{SHA256}(f\text{"}\{\text{freeze\_sha}\}\text{:NSB-R2-WAVE2-B-PHASE2B:v004"})\left[:16\right], 16\right) \ \& \ \text{0x7FFFFFFFFFFFFFFF}$$
- **Canonical Generator**: `corpus.generate_wave2_phase2b_holdout_v4(base_dir, freeze_sha)` frozen prior to corpus generation.
- **Integrity Requirements**: 300 strictly unique prime factors, verified pairwise coprimality $\gcd(N_i, N_j) = 1$ for all 11,175 pairs, untampered tripwire canary, and verified SHA-256 manifests.
- **Prior Corpus Retirement**: `v003_wave2/search_holdout` is officially designated `BURNED_RESOURCE_CALIBRATION / NO SCIENTIFIC VERDICT` and retired from confirmatory claims following the whole-pipeline ceiling timeout on modulus 1.
- **Execution Rule**: Generated ONLY after Phase 2B executable harness freeze commit is committed and pushed.
 
---
 
 ## 4. Fail-Closed Cumulative Timing & Counterbalanced Order
 
 - All throughput evaluations must use `benchmark_relation_throughput()` with cumulative multi-batch timing ($\ge 0.25\text{s}$ CPU per modulus).
 - If cumulative CPU $< 0.25\text{s}$ after `max_batch_repeats=2000`, the harness raises `TimingInvalidError` (fail-closed execution).
 - **Counterbalanced Execution Order**: AB/BA alternation by modulus index within each 30-modulus cohort (15 candidate-first, 15 proxy-first) to eliminate cache and warm-up bias.
 
 ---
 
 ## 5. Resource Ceilings & Stopping Rules (Calibrated via v002 Profiling)
 
 Resource limits were derived mechanically by profiling all 150 moduli of `v002_wave2/confirmatory` using the exact Phase 2B pipeline (`PROFILE_ONLY` mode, max modulus CPU observed = $8.94\text{s}$, max cohort wall = $197.05\text{s}$, total wall = $917.25\text{s}$, peak RSS = $32.9\text{ MB}$):
 - **Per-Modulus Whole-Pipeline CPU Ceiling**: $20.0$ seconds ($\lceil 2 \times 8.94 / 5 \rceil \times 5$). Covers candidate search (35 evals), proxy selection (35 evals), 3 B3 sieves, and 2 multi-batch throughput benchmarks. Aborts and invalidates canonical certification if exceeded.
 - **Per-Cohort Wall Time Ceiling**: $420.0$ seconds ($\lceil 2 \times 197.05 / 60 \rceil \times 60 = 7\text{ min}$).
 - **Total Experiment Wall Time Ceiling**: $2100.0$ seconds ($\lceil 2 \times 917.25 / 300 \rceil \times 300 = 35\text{ min}$).
 - **RSS Memory Limit**: $2048$ MB (observed peak = $32.9\text{ MB}$).
 - **All 5 Cohorts Mandatory**: Any truncated execution receives `PARTIAL_RUN_DIAGNOSTIC_ONLY`.
 - **Zero Imputation Prohibited**: Unobserved moduli cannot be imputed as zeroes.
