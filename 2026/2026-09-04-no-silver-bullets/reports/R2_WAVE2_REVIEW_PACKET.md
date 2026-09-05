# No Silver Bullet — R2 Wave 2 Phase 2A — Confirmatory Replication & Scaling Review Packet

**Generated**: 2026-09-04T04:15:27.230080+00:00  
**Active Contract**: `NSB-R2-WAVE2-B-CONFIRMATORY`  
**Evaluated Commit**: `9c81c54b5f4113c9cec68ad3f805e618c93b1861`  
**Attestation Commit**: `9373fc53f79302643d501a992245f0b8f28bc48d`  
**Benchmark Version**: `v002_wave2`  
**Wave**: `R2 Wave 2 Phase 2A — Confirmatory Replication & Scaling`  
**Total Compute Seconds**: 2.85s  
**Auditor Verdict**: **`PASS`**  

> [!NOTE]
> **Provenance & Attestation Erratum**: The initial draft of this packet recorded an intermediate pre-amendment hash (`5150cd09...`). The true, enclosing Git attestation commit certifying the raw execution results and this review packet in Git history is [`9373fc53f79302643d501a992245f0b8f28bc48d`](https://github.com/admiralorbiter/no-silver-bullets/commit/9373fc53f79302643d501a992245f0b8f28bc48d). The dual-commit provenance chain is: Evaluated Commit `9c81c54b...` → Attestation Commit `9373fc53...`.

---

## 1. Executive Status

* **Contract**: `NSB-R2-WAVE2-B-CONFIRMATORY`
* **Evaluated Commit**: `9c81c54b5f4113c9cec68ad3f805e618c93b1861` (clean working tree when experiment started)
* **Attestation Commit**: `9373fc53f79302643d501a992245f0b8f28bc48d` (enclosing Git certification)
* **Benchmark Version**: `v002_wave2` (confirmatory split, Family R, 150 pairwise-coprime balanced semiprimes)
* **Wave**: `R2 Wave 2 Phase 2A — Confirmatory Replication & Scaling`
* **Total Compute Time**: 2.85s (zero resource overruns; all moduli <= 5.0s CPU limit)
* **Auditor Verdict**: **`PASS`** (11/11 checks verified clean on attestation commit)
* **Confirmatory Scientific Verdict**: **`REPLICATION_FAILED`**
* **Executive Summary**: Phase 2A confirmatory evaluation executed across all 150 independent balanced semiprimes (30 per cohort: 32b, 48b, 64b, 80b, 96b) with zero experimental overruns or CPU timeouts. The replication hypothesis (canonical base-$m$ degree 3 vs degree 2) confirmed strong statistical superiority at 32b (win rate 93.3%, p=7.67e-06) and 48b (win rate 100.0%, p=1.72e-06). However, the fixed $A=100, B=20, FB=250$ assay enters a sparse-relation regime around 64 bits, where candidate win rate dropped to 23.3% (7 wins, 1 loss, 22 ties, p=0.0337 > 0.01), failing the preregistered >= 70% win rate threshold. At 80b and 96b, the assay reached its measurement floor (0 vs 0). In accordance with the preregistered criteria, PromotionJudge mechanically issued **`REPLICATION_FAILED`**.

---

## 2. Four-Tier Claim Hierarchy Breakdown

### Tier 1: Confirmatory Replication Claim (`replication_claim`)
- **Tier Status**: **`FAIL`**
- **Summary**: Replication hypothesis failed to achieve required win rate or significance across evaluated sizes.
- **Per-Cohort Verdicts & Findings**:
  - 32b: PASS. Mean paired diff +0.015486, win rate 93.3% (28/30), Wilcoxon p=7.67e-06, paired t p=1.66e-06.
  - 48b: PASS. Mean paired diff +0.002454, win rate 100.0% (30/30), Wilcoxon p=1.72e-06, paired t p=3.00e-08.
  - 64b: FAIL. Mean paired diff +0.000120, win rate 23.3% (7 wins, 1 loss, 22 ties), Wilcoxon p=3.37e-02, paired t p=3.66e-02.
  - 80b: ZERO_YIELD_FLOOR. Zero yield observed across all 30 moduli (sieve floor reached).
  - 96b: ZERO_YIELD_FLOOR. Zero yield observed across all 30 moduli (sieve floor reached).

#### Modulus Cohort Statistics (Family R, Balanced Semiprimes)
| Bit Size | Moduli Evaluated | Candidate Mean Yield | Baseline Mean Yield | Mean Paired Diff | 95% CI | Candidate Wins | Losses | Ties | Win Rate | Wilcoxon p-value | Paired-t p-value | Throughput Ratio* | Cohort Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **32b** | 30 | 0.027718 | 0.012232 | +0.015486 | [0.010194, 0.020779] | 28 | 2 | 0 | 93.3% | 7.67e-06 | 1.66e-06 | 1.78x | **`PASS`** |
| **48b** | 30 | 0.002694 | 0.000240 | +0.002454 | [0.001782, 0.003127] | 30 | 0 | 0 | 100.0% | 1.72e-06 | 3.00e-08 | 9.71x | **`PASS`** |
| **64b** | 30 | 0.000133 | 0.000013 | +0.000120 | [0.000008, 0.000232] | 7 | 1 | 22 | 23.3% | 3.37e-02 | 3.66e-02 | 78130x* | **`FAIL`** |
| **80b** | 30 | 0.000000 | 0.000000 | +0.000000 | [0.000000, 0.000000] | 0 | 0 | 30 | 0.0% | 1.00e+00 | 1.00e+00 | N/A | **`ZERO_YIELD_FLOOR`** |
| **96b** | 30 | 0.000000 | 0.000000 | +0.000000 | [0.000000, 0.000000] | 0 | 0 | 30 | 0.0% | 1.00e+00 | 1.00e+00 | N/A | **`ZERO_YIELD_FLOOR`** |

*\*Note on Throughput Column: The 78,130x throughput ratio at 64b is a timer-resolution artifact caused by per-modulus process time hitting the 15.6ms Windows timer tick floor (or 1e-6s clamp). Throughput was not a promotion gate in Phase 2A and did not affect the REPLICATION_FAILED verdict. A multi-batch aggregate timing procedure is mandated for Phase 2B.*

---

### Tier 2: Representation-Search Claim (`search_claim`)
- **Tier Status**: **`NOT_ENOUGH_DATA`**
- No representation-search candidate evaluated in this run.
- *Provenance Note*: Per Preregistration Amendment v2.1.1, Tier 2 is disabled on `v002_wave2/confirmatory` and strictly deferred to Phase 2B on the out-of-sample holdout corpus `v003_wave2/search_holdout`.

### Tier 3: In-House Polyselect Proxy Claim (`in_house_polyselect_proxy`)
- **Tier Status**: **`NOT_ENOUGH_DATA`**
- No in-house polyselect proxy comparison evaluated in this run.
- *Provenance Note*: Per Preregistration Amendment v2.1.1, Tier 3 is disabled on `v002_wave2/confirmatory` and strictly deferred to Phase 2B on the out-of-sample holdout corpus `v003_wave2/search_holdout`.

### Tier 4: Canonical Scaling Persistence Claim (`scaling_persistence`)
- **Tier Status**: **`NOT_ENOUGH_DATA`**
- Only 3 non-zero bit sizes available; at least 4 required to certify scaling persistence.
- *Criterion Requirement*: Evaluates whether empirical yield advantage does not decay across bit lengths. Requires at least 4 non-zero evaluable bit sizes to fit OLS regression and determine 95% CI slope lower bound $\beta_{\text{lower}} \ge 0.0$. Sieve floor was reached at 80b and 96b (only 3 non-zero sizes observed: 32b, 48b, 64b).

---

## 3. Auditor Checks & Integrity Verification

### Post-Attestation Provenance Audit (Commit `9373fc53f79302643d501a992245f0b8f28bc48d`)
- **[PASS] git_provenance_cleanliness**: Clean git state at 9373fc53f79302643d501a992245f0b8f28bc48d (CLEAN, git_dirty: False)
- **[PASS] public_sha_pilot**: Calculated 315ae15e... vs Expected 315ae15e...
- **[PASS] sealed_sha_pilot**: Calculated 5bef83e1... vs Expected 5bef83e1...
- **[PASS] public_sha_smoke**: Calculated a0d734bd... vs Expected a0d734bd...
- **[PASS] sealed_sha_smoke**: Calculated 8373b701... vs Expected 8373b701...
- **[PASS] public_sha_confirmatory**: Calculated 4c934876... vs Expected 4c934876...
- **[PASS] sealed_sha_confirmatory**: Calculated db0981a7... vs Expected db0981a7...
- **[PASS] tripwire_pilot**: Tripwire intact and untampered
- **[PASS] tripwire_smoke**: Tripwire intact and untampered
- **[PASS] tripwire_confirmatory**: Tripwire intact and untampered
- **[PASS] sandbox_leakage**: Verified 3 active sandbox(es); zero sealed leakage detected
- **Post-Attestation Audit Summary**: Audit verdict: PASS. Checks passed: 11/11. Git SHA: 9373fc53f79302643d501a992245f0b8f28bc48d (CLEAN).

### Pre-Attestation Execution Integrity Check (Commit `9c81c54b5f4113c9cec68ad3f805e618c93b1861`)
- Verified all benchmark manifests and tripwires untampered immediately upon raw output generation (working tree dirty solely due to newly generated `WAVE2_CONFIRMATORY_RAW.json`).

---

## 4. Scientific Synthesis & Next Actions

1. **Confirmation of Low-Bit Yield Advantage**: Replicated robustly on 30 independent balanced semiprimes at 32-bit (win rate 93.3%, p=7.67e-06) and 48-bit (win rate 100%, p=1.72e-06). Canonical base-$m$ degree-3 polynomials yield significantly more smooth relations than degree-2 in small factor-base sieves at <=48 bits.
2. **Sparse-Relation Regime at 64-Bit**: The fixed $A=100, B=20, FB=250$ assay enters a sparse-relation regime around 64 bits. The cubic representation no longer meets confirmatory cross-modulus replication requirements, despite retaining a directionally positive aggregate yield signal (7 wins, 1 loss, 22 ties; mean paired diff $+0.000120$, 95% CI $[0.000008, 0.000232]$, pooled smooth points 10 candidate vs 1 baseline). At 80–96 bits the assay itself reaches its measurement floor (0 vs 0).
3. **Event Starvation vs Advantage Disappearance**: The mean yield ratios remain directionally favorable (~2.3x at 32b, ~11.2x at 48b, ~10.2x at 64b). What collapses is the absolute relation density under fixed sieve bounds, causing 22 of 30 moduli to register zero relations for both representations.
4. **Mechanical Anti-Inflation Adjudication**: Because the preregistered replication criterion properly treats zero-yield ties as non-wins ($23.3\% < 70\%$), PromotionJudge refused promotion and issued `REPLICATION_FAILED`.
5. **Phase 2B Research Focus**: Can frozen representation search (translations/rotations) lift absolute relation density enough to escape the 64b–96b sparse-sieve floor on a fresh out-of-sample holdout corpus (`v003_wave2/search_holdout`), evaluated with cumulative batch timing and an absolute non-zero relation floor criterion?
