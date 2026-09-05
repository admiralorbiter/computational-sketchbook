# No Silver Bullet — R2 Wave 2 Phase 2B Review Packet
## Representation Search & In-House Polyselect Proxy Evaluation

**Generated**: 2026-09-04T14:57:28.452412+00:00  
**Active Contract**: `NSB-R2-WAVE2-B-PHASE2B` (Criteria v1.3)  
**Evaluated Commit**: `8152a9f1ef34c9ce6245f51759a03366081514c1`  
**Attestation Commit**: [`c6dd6dd2089c8025b6e7ecf0faef5d107330e92c`](https://github.com/admiralorbiter/no-silver-bullets/commit/c6dd6dd2089c8025b6e7ecf0faef5d107330e92c)  
**Benchmark Version**: `v004_wave2` (split: `search_holdout`, derived seed: `3138178080747748033`)  
**Wave**: `R2 Wave 2 Phase 2B — Representation Search & In-House Polyselect Proxy`  
**Total Elapsed Seconds**: 897.29s  
**Overall Adjudicated Verdict**: **`SEARCH_ADVANTAGE_FAILED`**  

> [!NOTE]
> **Provenance & Attestation Erratum**: The initial generation of this review packet left `attestation_commit: null` while awaiting execution completion and git commit creation. The true enclosing Git attestation commit certifying the raw execution results and this review packet in Git history is [`c6dd6dd2089c8025b6e7ecf0faef5d107330e92c`](https://github.com/admiralorbiter/no-silver-bullets/commit/c6dd6dd2089c8025b6e7ecf0faef5d107330e92c). The dual-commit provenance chain is: Evaluated Commit `8152a9f1...` → Attestation Commit `c6dd6dd2...`.

---

## 1. Executive Status

* **Contract**: `NSB-R2-WAVE2-B-PHASE2B`
* **Evaluated Commit**: `8152a9f1ef34c9ce6245f51759a03366081514c1` (clean working tree during execution)
* **Benchmark**: `v004_wave2/search_holdout` (150 balanced semiprimes, 30 per cohort across 32, 48, 64, 80, 96 bits)
* **Overall Adjudicated Verdict**: **`SEARCH_ADVANTAGE_FAILED`**
* **Primary Target Bit Sizes**: `[64, 80, 96]` (strict global gate)
* **Supporting Bit Sizes**: `[32, 48]` (calibration & sanity controls)
* **Tier 2 Status (Representation Search vs Canonical base-m d=3)**: **`FAIL`**
* **Tier 3 Status (Candidate vs Symmetrical Murphy-E Proxy)**: **`FAIL`**
* **Anti-Inflation Guardrail**: Confirmed. Supporting cohorts [32, 48] cannot confer promotion; zero-yield target cohorts evaluated as relation floor failure; raw unrounded comparisons enforced; CADO-NFS SOTA claims strictly forbidden.

---

## 2. Cohort Evaluation Table (v004_wave2 / search_holdout)

| Bit Size | Moduli | Cand Yield | Base Yield | Paired Diff | 95% CI | Win Rate | Wilcoxon p | Paired-t p | Floor % | Log-Norm R | Murphy-E R | Throughput R | Proxy Yield Diff | Proxy Wilcoxon p | Tier 2 Verdict | Tier 3 Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **32b** | 30 | 0.041043 | 0.026891 | +0.014152 | [0.007688, 0.020617] | 76.7% (23/30) | 1.42e-04 | 5.41e-05 | 100.0% | 0.9363 | 0.9617x | 0.9838x | +-0.000160 | 3.80e-01 | **`PASS`** | **`FAIL`** |
| **48b** | 30 | 0.004975 | 0.003415 | +0.001561 | [0.000362, 0.002760] | 46.7% (14/30) | 8.88e-03 | 6.26e-03 | 100.0% | 0.9553 | 0.9215x | 2.2242x | +0.002708 | 7.34e-05 | **`FAIL`** | **`FAIL`** |
| **64b** | 30 | 0.000293 | 0.000173 | +0.000120 | [-0.000038, 0.000278] | 26.7% (8/30) | 5.54e-02 | 6.52e-02 | 43.3% | 0.9796 | 0.9494x | 0.9417x | +-0.000013 | 5.82e-01 | **`FAIL`** | **`FAIL`** |
| **80b** | 30 | 0.000013 | 0.000000 | +0.000013 | [-0.000014, 0.000041] | 3.3% (1/30) | 5.00e-01 | 1.63e-01 | 3.3% | 0.9851 | 0.9549x | 0.9412x | +0.000000 | 1.00e+00 | **`FAIL`** | **`FAIL`** |
| **96b** | 30 | 0.000000 | 0.000000 | +0.000000 | [0.000000, 0.000000] | 0.0% (0/30) | 1.00e+00 | 1.00e+00 | 0.0% | 0.9838 | 0.9624x | N/A | +0.000000 | 1.00e+00 | **`FAIL`** | **`FAIL`** |

---

## 3. Tier-by-Tier Findings

### Tier 2: Representation-Search Claim (`tier2_search`)
- **Tier Verdict**: **`FAIL`**
- 32b: PASS. Mean diff +0.014152, gain=1.53x, win rate 76.7%, floor=100.0% (30/30), log-norm ratio=0.9363 <= 0.95, Wilcoxon p=1.42e-04, paired-t p=5.41e-05.
- 48b: FAIL. log-norm ratio failed (0.9553 > 0.95); stats failed (diff=0.001561, win=46.7%, wilcoxon_p=8.88e-03, paired_t_p=6.26e-03).
- 64b: FAIL. relation floor failed (43.3% < 50.0%); log-norm ratio failed (0.9796 > 0.95); stats failed (diff=0.000120, win=26.7%, wilcoxon_p=5.54e-02, paired_t_p=6.52e-02).
- 80b: FAIL. relation floor failed (3.3% < 50.0%); log-norm ratio failed (0.9851 > 0.95); stats failed (diff=0.000013, win=3.3%, wilcoxon_p=5.00e-01, paired_t_p=1.63e-01).
- 96b: FAIL. Relation floor failed (0.0% < 50.0%: zero-yield floor reached on primary target size).

### Tier 3: In-House Polyselect Proxy Claim (`tier3_proxy`)
- **Tier Verdict**: **`FAIL`**
- 32b: FAIL. Murphy-E raw gate failed (cand=1.310259e-01 < req=1.0x proxy=1.362431e-01); throughput raw gate failed (cand=16326.40 < req=1.0x proxy=16595.33); empirical yield test failed (diff=-0.000160 <= 0.0 or Wilcoxon p=3.80e-01 > 0.01).
- 48b: FAIL. Murphy-E raw gate failed (cand=5.546872e-02 < req=1.0x proxy=6.019692e-02).
- 64b: FAIL. Murphy-E raw gate failed (cand=8.741595e-02 < req=1.0x proxy=9.207823e-02); throughput raw gate failed (cand=109.87 < req=1.0x proxy=116.67); empirical yield test failed (diff=-0.000013 <= 0.0 or Wilcoxon p=5.82e-01 > 0.01).
- 80b: FAIL. Murphy-E raw gate failed (cand=2.270984e-02 < req=1.0x proxy=2.378170e-02); throughput raw gate failed (cand=4.27 < req=1.0x proxy=4.53); empirical yield test failed (diff=0.000000 <= 0.0 or Wilcoxon p=1.00e+00 > 0.01).
- 96b: FAIL. Murphy-E raw gate failed (cand=2.074711e-03 < req=1.0x proxy=2.155718e-03); throughput raw gate failed (cand=0.00 < req=1.0x proxy=0.00); empirical yield test failed (diff=0.000000 <= 0.0 or Wilcoxon p=1.00e+00 > 0.01).

---

## 4. Auditor Checks & Integrity Verification

- **[PASS] public_sha_pilot**: Calculated 315ae15e... vs Expected 315ae15e...
- **[PASS] sealed_sha_pilot**: Calculated 5bef83e1... vs Expected 5bef83e1...
- **[PASS] public_sha_smoke**: Calculated a0d734bd... vs Expected a0d734bd...
- **[PASS] sealed_sha_smoke**: Calculated 8373b701... vs Expected 8373b701...
- **[PASS] public_sha_confirmatory**: Calculated 4c934876... vs Expected 4c934876...
- **[PASS] sealed_sha_confirmatory**: Calculated db0981a7... vs Expected db0981a7...
- **[PASS] public_sha_search_holdout**: Calculated cacc42ae... vs Expected cacc42ae...
- **[PASS] sealed_sha_search_holdout**: Calculated 0cdaf7a8... vs Expected 0cdaf7a8...
- **[PASS] public_sha_search_holdout**: Calculated 5c5b117c... vs Expected 5c5b117c...
- **[PASS] sealed_sha_search_holdout**: Calculated 0f7b0ad5... vs Expected 0f7b0ad5...
- **[PASS] tripwire_pilot**: Tripwire intact and untampered
- **[PASS] tripwire_smoke**: Tripwire intact and untampered
- **[PASS] tripwire_confirmatory**: Tripwire intact and untampered
- **[PASS] tripwire_search_holdout**: Tripwire intact and untampered
- **[PASS] tripwire_search_holdout**: Tripwire intact and untampered

---

## 5. Scientific Summary & Analysis

1. **Target Bit Size Performance ([64, 80, 96] bits)**:
   - **64-bit Cohort**: The search candidate remains directionally superior on mean yield—approximately $1.69\text{x}$ canonical base-$m$ ($0.000293$ vs $0.000173$, $+0.000120$ paired difference). However, only 8 of 30 moduli produced candidate wins, while 18 were ties ($0$ vs $0$) and 4 were losses ($26.7\%$ win rate). The $95\%$ confidence interval crosses zero ($[-0.000038, 0.000278]$), both directional inferential tests miss the preregistered threshold (Wilcoxon $p = 0.0554$, paired-$t$ $p = 0.0652$), the log-norm ratio is $0.9796$, and only 13 of 30 moduli ($43.3\%$) yield any relations at all, failing the mandatory $\ge 50\%$ absolute relation floor gate.
   - **80-bit Cohort**: Effectively one smooth relation occurred in the entire 30-modulus candidate cohort versus zero canonical (candidate yield $0.000013$ vs $0.000000$). With 29 of 30 moduli tied at $0$ vs $0$, the non-zero modulus ratio is $3.3\%$ ($1/30$), failing the relation floor gate ($3.3\% < 50\%$) and significance testing ($p = 0.50$).
   - **96-bit Cohort**: Complete zero-yield floor reached across all 30 moduli ($0.000000$ relations across all representations). Under Criteria v1.3 zero-target policy, this is adjudicated as a definitive relation-floor failure.
   - **Absolute Event Density Collapse**: Across the 74,970 total sieve points per cohort ($30 \text{ moduli} \times 2499 \text{ points}$), total relation counts for candidate versus canonical base-$m$ are:
     - **32b**: $\sim 3,077$ vs $2,016$ relations
     - **48b**: $\sim 373$ vs $256$ relations
     - **64b**: $22$ vs $13$ relations
     - **80b**: $1$ vs $0$ relations
     - **96b**: $0$ vs $0$ relations
     The core scientific problem is absolute relation density: the favorable direction survives at 64b, but events become far too sparse and concentrated to satisfy the confirmatory claim.

2. **Progression of B1 Norm Advantage**:
   - The cohort-averaged B1 log-norm ratio (candidate / base-$m$) progressively degrades as bit size grows:
     $$\mathbf{0.9363} \text{ (32b)} \longrightarrow \mathbf{0.9553} \text{ (48b)} \longrightarrow \mathbf{0.9796} \text{ (64b)} \longrightarrow \mathbf{0.9851} \text{ (80b)} \longrightarrow \mathbf{0.9838} \text{ (96b)}$$
   - This geometric pattern is highly revealing: the small translation/rotation neighborhood ($\pm 5$ translation, $[-2, 2]$ linear rotation) can find meaningfully smaller-norm representations at 32b, but by 64b and above it barely moves the B1 geometry away from canonical base-$m$. This directly explains the empirical outcome: a small relative yield gain remains, but nowhere near enough to alter the scaling regime.

3. **In-House Polyselect Proxy Comparison (Tier 3)**:
   - The mechanical Tier 3 `FAIL` reflects the strict multi-metric dominance requirement of the preregistration. Because the proxy searches the exact same 35-representation set and explicitly maximizes Murphy-$E$, the ratio $\frac{\text{candidate Murphy-}E}{\text{proxy Murphy-}E}$ is mathematically constrained to be $\le 1.00$ unless the candidate happens to select an $E$-maximizing tie.
   - Importantly, the empirical results reveal that Murphy-$E$ selection does **not** empirically dominate B1+$\alpha$ selection:
     - At **48b**, despite possessing only $0.9215\text{x}$ of the proxy's Murphy-$E$, the B1+$\alpha$ candidate decisively beats the Murphy-$E$-selected representation on empirical yield ($+0.002708$ paired difference, $80\%$ win rate, Wilcoxon $p = 7.34 \times 10^{-5}$) and delivers $2.224\text{x}$ throughput.
     - At **32b**, the candidate/proxy yield difference is tiny and statistically indistinguishable ($-0.000160$, $p = 0.380$).
     - At **64b**, the proxy's slight empirical edge is also statistically indistinguishable ($-0.000013$, $p = 0.582$).
     - At **80b** and **96b**, both selectors are pinned by the sparse relation floor.
   - A plausible mechanistic hypothesis for this disconnect is rectangular sampling geometry: the in-house Murphy-$E$ approximation samples an $A=50, B=10$ rectangle, whereas Phase 2B's empirical B3 assay sieves over $A=100, B=20$.

4. **Program Verdict & Scientific Conclusion**:
   - **Hypothesis Verdict**: The preregistered hypothesis—that a 35-candidate local translation/rotation search coupled with a B1/$\alpha$ selector rescues the fixed $A=100, B=20, FB=250$ sparse floor at $64\text{--}96$ bits—is **`REJECTED`**.
   - **Configuration Status**: Current local-search configuration is **`PARKED`**.
   - **Track B Status**: Broader Track B remains open. Polynomial and representation selection remains an active theoretical lever; this specific 35-candidate local neighborhood and selector did not overcome the dimensional sparsity of the micro-sieve assay.
