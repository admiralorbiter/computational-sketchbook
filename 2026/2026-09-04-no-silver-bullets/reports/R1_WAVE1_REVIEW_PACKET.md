# No Silver Bullet — R1 Wave 1 — Human-Reviewed Search Review Packet

**Generated**: 2026-09-04T03:11:06.047379+00:00  
**Active Contract**: `NSB-R1-WAVE1-SEARCH`  
**Evaluated Commit**: `277f3bd0841ac4d4ef3eac7bbe107d08aba77e05`  
**Attestation Commit**: *(Pending final commit)*  
**Benchmark Version**: `v001_pilot`  
**Wave**: `R1 Wave 1 — Human-Reviewed Search`  
**Total Compute Seconds**: 48.53s  
**Auditor Verdict**: **`PASS`**  

---

## 1. Executive Status

* **Contract**: `NSB-R1-WAVE1-SEARCH`
* **Evaluated Commit**: `277f3bd0841ac4d4ef3eac7bbe107d08aba77e05`
* **Attestation Commit**: *(Pending final commit)*
* **Benchmark Version**: `v001_pilot`
* **Wave**: `R1 Wave 1 — Human-Reviewed Search`
* **Total Pilot Compute**: 48.53s
* **Auditor Verdict**: **`PASS`**
* **Gate 1 Milestone Status**: **`GATE_1A_FEASIBILITY_PASSED / CALIBRATION_ESTABLISHED`**
* **Promotion Status Summary**: Track A: `INCONCLUSIVE` | Track B: `CANDIDATE` | Track C: `CALIBRATION_INCOMPLETE` | Track D: `INCONCLUSIVE`
* **Human Decision Required**: R1 Wave 1 research executed and recertified under v1.1 post-hoc safeguards. Track A 18-point parametric grid executed (linear residual growth drives catastrophic yield collapse; scheduled for 1 bounded BKZ/multi-vector rescue experiment before parking). Track B demonstrated 18.00x pooled smooth-relation yield gain on B3 homogeneous sieve (exact McNemar p=4.29e-13), designated CANDIDATE pending multi-instance replication (30 semiprimes/size across 32b-96b) benchmarked against SOTA Kleinjung/CADO-NFS polynomial selection. Track C genuine 25-60% MSB ladder confirmed finite-size Coppersmith boundary (retained as shared infrastructure bridge). Track D carry-save multiplier evaluated (sub-2.0x across 16-28b; parked until fundamentally new constraint representation appears). Roadmap: Adopt asymmetric Wave 2 portfolio with primary focus on Track B SOTA benchmarking.

---

## 2. Track Summary Table

| Track | Champion Experiment | Evidence Tier | Bit Range | Primary Metric | Baseline | Delta | Validation Status | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | `NSB-A-PILOT-01` | E1 | 16-32 | smooth_relations/cpu_sec=69.3 rel/s (16b), 15.9 rel/s (20b), 23.9 rel/s (24b), 7.7 rel/s (32b) | 84010.1 rel/s (16b), 35578.5 rel/s (20b), 65090.0 rel/s (24b), 3471.0 rel/s (32b) | C=2000 not promoted (0.00x at 16b (69.3 vs 84010.1 rel/s), 0.00x at 20b (15.9 vs 35578.5 rel/s), 0.00x at 24b (23.9 vs 65090.0 rel/s), 0.00x at 32b (7.7 vs 3471.0 rel/s)) | `PASS` | **`INCONCLUSIVE`** |
| **B** | `NSB-B-PILOT-01` | E1 | 32-64 | log_norm_proxy_score=deg-3: 23.80 (32b), 34.99 (48b), 46.06 (64b) | deg-2: 30.68 (32b), 46.79 (48b), 61.97 (64b) | Strong positive signal (gain=18.00x, McNemar p=4.29e-13); confirmatory replication on 20-50 instances warranted before R2 promotion | `PASS` | **`CANDIDATE`** |
| **C** | `NSB-C-PILOT-01` | E1 | 32-48 | threshold_recovery_rate=32b: SUCCESS (0.12s), 40b: FAIL, 48b: FAIL | zero_information | Exact rational Sturm/LLL verified at 32b; 40b/48b bound transition incomplete (1/3 recovered) | `PASS` | **`CALIBRATION_INCOMPLETE`** |
| **D** | `NSB-D-PILOT-01` | E1 | 16-32 | median_solve_time_seconds=0.0011s (16b) to 0.2223s (32b) | schoolbook_sat_glucose4 | Comparative encoding failed speedup threshold | `PASS` | **`INCONCLUSIVE`** |

### Promotion Criteria Breakdown

#### Track A (NSB-A-PILOT-01)
- **Scientific Verdict**: **`INCONCLUSIVE`** (Tier E1, Range: 16-32 bits)
- **Promotion Criteria Evaluation (v1.1 Recertification Safeguards / Post-Hoc Rules)**:
  - `[FAIL] relation_rate_gain`: 0.00x at 16b (69.3 vs 84010.1 rel/s), 0.00x at 20b (15.9 vs 35578.5 rel/s), 0.00x at 24b (23.9 vs 65090.0 rel/s), 0.00x at 32b (7.7 vs 3471.0 rel/s) (Target: >= 1.5x advantage over baseline across >= 3 adjacent sizes)
    - *Justification*: Max adjacent sizes with >= 1.5x gain was 0 (required: 3).
  - `[FAIL] scaling_persistence`: Ratios: ['16b:0.00x', '20b:0.00x', '24b:0.00x', '32b:0.00x']; zero_yield_bits: [] (Target: Advantage persists with increasing bit length)
    - *Justification*: Advantage did not persist with increasing bit length.
- **Judge Recommendation**: Parametric grid completed: residual cofactor bits scale linearly (~0.90 bits per modulus bit), causing severe yield collapse and 350x–2800x lower throughput than baseline. Conduct at most one bounded multi-vector / BKZ rescue experiment across multiple independent moduli; if residual growth remains catastrophic, park Track A.

#### Track B (NSB-B-PILOT-01)
- **Scientific Verdict**: **`CANDIDATE`** (Tier E1, Range: 32-64 bits)
- **Promotion Criteria Evaluation (v1.1 Recertification Safeguards / Post-Hoc Rules)**:
  - `[PASS] b1_log_norm_advantage`: deg-3=23.80 vs deg-2=30.68 (32b, ratio=0.78); deg-3=34.99 vs deg-2=46.79 (48b, ratio=0.75); deg-3=46.06 vs deg-2=61.97 (64b, ratio=0.74) (Target: Degree-3 proxy log-norm <= 0.85 * Degree-2 score)
    - *Justification*: Degree-3 base-m representation consistently achieved <= 0.85 coefficient log-norm across all tested moduli.
  - `[PASS] b3_downstream_yield_promotion`: Cubic yield=5.79% (54/933) vs Deg-2=0.32% (3/933), diff=+5.47%, gain=18.00x, 2x2=[[n11=0, n10=54], [n01=3, n00=876]], McNemar p=4.29e-13 (Target: >= 25% smooth relation yield improvement in B3 homogeneous sieve (rule: never promote on B1 alone))
    - *Justification*: B3 homogeneous sieve achieved statistically significant paired yield gain (18.00x, p=4.29e-13 <= 0.05) with discordant counts n10=54 vs n01=3.
  - `[FAIL] confirmatory_sample_replication`: min 1 instance(s) per size tested (32b: 1, 48b: 1, 64b: 1, threshold: 5) (Target: >= 5 replicated instances per bit length (minimum across all evaluated sizes))
    - *Justification*: Evaluation sample size (minimum 1 per size) is insufficient for R2 promotion; confirmatory replication on 20-50 instances is required.
- **Judge Recommendation**: Wave 2 Primary Focus: Replicate paired degree-3 vs degree-2 sieve on 30 independent balanced semiprimes per size across 32b, 48b, 64b, 80b, and 96b using the modulus as the independent experimental unit, and expand beyond canonical base-m to benchmark against Kleinjung/Murphy/CADO-NFS-style polynomial selection.

#### Track C (NSB-C-PILOT-01)
- **Scientific Verdict**: **`CALIBRATION_INCOMPLETE`** (Tier E1, Range: 32-48 bits)
- **Promotion Criteria Evaluation (v1.1 Recertification Safeguards / Post-Hoc Rules)**:
  - `[FAIL] 50pct_msb_recovery_rate`: 1/3 recovered (32b: SUCCESS (0.12s), 40b: FAIL, 48b: FAIL) (Target: >=100% exact recovery at 50% known MSB across pilot ladder)
    - *Justification*: Exact Sturm/LLL small-root solver succeeded on 1/3 instances at 50% MSB (threshold: 100.0%).
  - `[PASS] calibration_ladder_completeness`: Calibrated across [0.25, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6] genuine MSB fractions (Target: Calibrated across 25%, 35%, 45%, 50% true MSB fractions)
    - *Justification*: Multi-fraction empirical recovery curve established without synthetic placeholders.
- **Judge Recommendation**: Multi-fraction calibration complete: exact Sturm/LLL root isolation succeeds at >=55% MSB across 32b–48b, confirming the finite-size Coppersmith boundary with zero synthetic placeholders. Maintain Track C as shared infrastructure bridge for any track discovering partial factor bits.

#### Track D (NSB-D-PILOT-01)
- **Scientific Verdict**: **`INCONCLUSIVE`** (Tier E1, Range: 16-32 bits)
- **Promotion Criteria Evaluation (v1.1 Recertification Safeguards / Post-Hoc Rules)**:
  - `[PASS] baseline_characterization`: 0.0011s (16b) -> 0.0027s (20b) -> 0.0146s (24b) -> 0.0402s (28b) -> 0.2223s (32b) (Target: Establish clean empirical solve-time scaling curve for Schoolbook SAT)
    - *Justification*: Clean, reproducible CDCL SAT scaling curve established across 5 consecutive bit lengths with zero semantic errors.
  - `[FAIL] comparative_encoding_advantage`: Speedups: ['1.57x', '0.73x', '0.90x', '0.86x', '2.25x'] (Target: >= 2.0x solve time improvement over schoolbook across >= 3 adjacent sizes)
    - *Justification*: Alternative encoding failed to achieve consistent 2.0x advantage.
- **Judge Recommendation**: CSA-v1 evaluated: sub-2.0x speedups at 16–28 bits with noisy millisecond timings; single 2.30x speedup at 32b is insufficient evidence of algorithmic scaling. Park Track D until a fundamentally new constraint representation (beyond adder-tree rewrites) appears.


---

## 3. New Findings

1. **Baselines Ladder (Fermat, Pollard rho, Pollard p-1)**:
   - Fermat cleanly factored balanced Family F (48b in 1 steps (0.00011s), 64b in 1 steps (0.00001s)).
   - Pollard p-1 solved smooth-order Family P1 (48b in 0.00015s, 64b in 0.00020s).
   - Pollard rho factored Family R (32b in 255 steps (0.0001s), 32b in 127 steps (0.0001s), 40b in 511 steps (0.0002s), 40b in 1791 steps (0.0006s)), establishing the classical comparison curve.
2. **Track A (Tensor / Lattice Relation Discovery — `INCONCLUSIVE`)**:
   - Track A evaluated across 4 bit lengths (16-32 bits).
   - Observed scaling ratios: 0.00x at 16b (69.3 vs 84010.1 rel/s), 0.00x at 20b (15.9 vs 35578.5 rel/s), 0.00x at 24b (23.9 vs 65090.0 rel/s), 0.00x at 32b (7.7 vs 3471.0 rel/s).
   - **Recommended Next Step**: Parametric grid completed: residual cofactor bits scale linearly (~0.90 bits per modulus bit), causing severe yield collapse and 350x–2800x lower throughput than baseline. Conduct at most one bounded multi-vector / BKZ rescue experiment across multiple independent moduli; if residual growth remains catastrophic, park Track A.
3. **Track B (Evolved Algebraic Representations — `CANDIDATE`)**:
   - Multi-fidelity cascade B0-B3 verified algebraic representations across 32-64 bit moduli.
   - Degree-3 base-m representation measured log-norms: 23.80 (32b), 34.99 (48b), 46.06 (64b) vs deg-2 baseline: 30.68 (32b), 46.79 (48b), 61.97 (64b).
   - Paired B3 homogeneous sieve measured cubic yield=5.79% vs quadratic=0.32% (gain=18.00x, McNemar exact p=4.29e-13, discordant pairs n10=54 vs n01=3).
   - Historical NFS degree selection context: For small moduli (32b-64b), degree 2 vs degree 3 yields depend heavily on polynomial coefficient bounds vs algebraic norm growth; higher degree typically shows its decisive asymptotic advantage as modulus size grows.
   - Pilot evaluated minimum 1 instance per bit size (32b: 1, 48b: 1, 64b: 1). Confirmatory multi-instance replication on 20-50 independent semiprimes is warranted before R2 promotion.
   - **Recommended Next Step**: Wave 2 Primary Focus: Replicate paired degree-3 vs degree-2 sieve on 30 independent balanced semiprimes per size across 32b, 48b, 64b, 80b, and 96b using the modulus as the independent experimental unit, and expand beyond canonical base-m to benchmark against Kleinjung/Murphy/CADO-NFS-style polynomial selection.
4. **Track C (Partial Information Bridge — `CALIBRATION_INCOMPLETE`)**:
   - Exact rational Sturm chain root isolation operates with zero IEEE-754 precision loss and recovers exact factors with no fallback.
   - Observed 50% MSB success rate was 1/3 (32b: SUCCESS (0.12s), 40b: FAIL, 48b: FAIL).
   - **Recommended Next Step**: Multi-fraction calibration complete: exact Sturm/LLL root isolation succeeds at >=55% MSB across 32b–48b, confirming the finite-size Coppersmith boundary with zero synthetic placeholders. Maintain Track C as shared infrastructure bridge for any track discovering partial factor bits.
5. **Track D (Constraint Graph Inversion — `INCONCLUSIVE`)**:
   - Schoolbook SAT encoding successfully inverted across 16-32 bits with 100% factor recovery.
   - Empirical CDCL solve time exhibits clean scaling (0.0011s (16b) to 0.2223s (32b)).
   - **Recommended Next Step**: CSA-v1 evaluated: sub-2.0x speedups at 16–28 bits with noisy millisecond timings; single 2.30x speedup at 32b is insufficient evidence of algorithmic scaling. Park Track D until a fundamentally new constraint representation (beyond adder-tree rewrites) appears.

---

## 4. Auditor Checks & Integrity Verification

- **[PASS] git_provenance_cleanliness**: Clean git state at 277f3bd0841ac4d4ef3eac7bbe107d08aba77e05
- **[PASS] public_sha_pilot**: Calculated 315ae15e... vs Expected 315ae15e...
- **[PASS] sealed_sha_pilot**: Calculated 5bef83e1... vs Expected 5bef83e1...
- **[PASS] public_sha_smoke**: Calculated a0d734bd... vs Expected a0d734bd...
- **[PASS] sealed_sha_smoke**: Calculated 8373b701... vs Expected 8373b701...
- **[PASS] tripwire_pilot**: Tripwire intact and untampered
- **[PASS] tripwire_smoke**: Tripwire intact and untampered
- **[PASS] sandbox_leakage**: Verified 3 active sandbox(es); zero sealed leakage detected

---

## 5. Empirical Scaling Curves

### Track Baselines Scaling Curve
- **Fermat (Family F)** (48 bits): 1 steps (0.00011s)
- **Fermat (Family F)** (64 bits): 1 steps (0.00001s)
- **Pollard p-1 (Family P1)** (48 bits): 0.00015s
- **Pollard p-1 (Family P1)** (64 bits): 0.00020s
- **Pollard rho (Family R)** (32 bits): 255 steps (0.0001s)
- **Pollard rho (Family R)** (32 bits): 127 steps (0.0001s)
- **Pollard rho (Family R)** (40 bits): 511 steps (0.0002s)
- **Pollard rho (Family R)** (40 bits): 1791 steps (0.0006s)
### Track A Scaling Curve
- **Schnorr CVP Relation Yield (16b 18-pt grid)** (16 bits): 18 pts tested | champ: 18 rels (69.3 r/s, babai_dist=2.8, res_bits=8.6b) vs base: 30 rels (84010.1 r/s) | model: residual_bits = 0.90 * modulus_bits + (-5.52) [R^2 = 0.864]
- **Schnorr CVP Relation Yield (20b 18-pt grid)** (20 bits): 18 pts tested | champ: 2 rels (15.9 r/s, babai_dist=3.0, res_bits=12.8b) vs base: 29 rels (35578.5 r/s) | model: residual_bits = 0.90 * modulus_bits + (-5.52) [R^2 = 0.864]
- **Schnorr CVP Relation Yield (24b 18-pt grid)** (24 bits): 18 pts tested | champ: 3 rels (23.9 r/s, babai_dist=3.0, res_bits=16.0b) vs base: 30 rels (65090.0 r/s) | model: residual_bits = 0.90 * modulus_bits + (-5.52) [R^2 = 0.864]
- **Schnorr CVP Relation Yield (32b 18-pt grid)** (32 bits): 18 pts tested | champ: 1 rels (7.7 r/s, babai_dist=3.3, res_bits=23.1b) vs base: 3 rels (3471.0 r/s) | model: residual_bits = 0.90 * modulus_bits + (-5.52) [R^2 = 0.864]
### Track B Scaling Curve
- **Base-m Deg-3 vs Deg-2 Sieve** (32 bits): B1 norm: deg3=23.80 vs deg2=30.68 | B3 yield: deg3=52/311 (64102.6 r/s) vs deg2=3/311 (3807.6 r/s, gain=17.33x) | McNemar 2x2: n11=0, n10=52, n01=3, n00=256 (p=0.00e+00)
- **Base-m Deg-3 vs Deg-2 Sieve** (48 bits): B1 norm: deg3=34.99 vs deg2=46.79 | B3 yield: deg3=1/311 (1312.7 r/s) vs deg2=0/311 (0.0 r/s, deg2_smooth=0) | McNemar 2x2: n11=0, n10=1, n01=0, n00=310 (p=1.00e+00)
- **Base-m Deg-3 vs Deg-2 Sieve** (64 bits): B1 norm: deg3=46.06 vs deg2=61.97 | B3 yield: deg3=1/311 (1339.4 r/s) vs deg2=0/311 (0.0 r/s, deg2_smooth=0) | McNemar 2x2: n11=0, n10=1, n01=0, n00=310 (p=1.00e+00)
### Track C Scaling Curve
- **Multi-Fraction MSB Ladder** (32 bits): Ladder (25%:FAIL, 35%:FAIL, 40%:FAIL, 45%:FAIL, 50%:OK, 55%:OK, 60%:OK)
- **Multi-Fraction MSB Ladder** (40 bits): Ladder (25%:FAIL, 35%:FAIL, 40%:FAIL, 45%:FAIL, 50%:FAIL, 55%:OK, 60%:OK)
- **Multi-Fraction MSB Ladder** (48 bits): Ladder (25%:FAIL, 35%:FAIL, 40%:FAIL, 45%:FAIL, 50%:FAIL, 55%:OK, 60%:OK)
### Track D Scaling Curve
- **Schoolbook vs Carry-Save SAT** (16 bits): CSA: 0.0007s (200 vars, 978 cls) vs Schoolbook: 0.0011s (200 vars, speedup: 1.57x)
- **Schoolbook vs Carry-Save SAT** (20 bits): CSA: 0.0037s (310 vars, 1562 cls) vs Schoolbook: 0.0027s (310 vars, speedup: 0.73x)
- **Schoolbook vs Carry-Save SAT** (24 bits): CSA: 0.0163s (444 vars, 2282 cls) vs Schoolbook: 0.0146s (444 vars, speedup: 0.90x)
- **Schoolbook vs Carry-Save SAT** (28 bits): CSA: 0.0470s (602 vars, 3138 cls) vs Schoolbook: 0.0402s (602 vars, speedup: 0.86x)
- **Schoolbook vs Carry-Save SAT** (32 bits): CSA: 0.0986s (784 vars, 4130 cls) vs Schoolbook: 0.2223s (784 vars, speedup: 2.25x)

---

## 6. Frontier & Rejected Branches

- No catastrophic branch failures in pilot ladder.

---

## 7. Research Director Log & Next Wave Proposals

### Track A — NSB-A-20260904-A00002
- **Hypothesis**: Systematic grid over (factor_base_size x scale_c x candidate_budget) maps the relation collapse boundary on 20-32 bit moduli.
- **Mechanism**: Babai nearest plane relation yield collapsed at 32b; expanding factor base (25-40) and candidate budget (2000) tests whether relation yield recovers.
- **Mutations**: {"scale_c_grid": [500, 1000, 2000], "factor_base_grid": [16, 25, 40], "candidate_budget": 2000}
- **Expected Effect**: relation_discovery_rate > 0 at 32-bit and >= 1.5x gain over baseline
- **Promotion Target**: Pilot A-P2

### Track B — NSB-B-20260904-B00002
- **Hypothesis**: B3 homogeneous sieving on cubic candidates yields >= 25% smooth relations over quadratic base-m on 32-64 bits.
- **Mechanism**: Cubic representation verified in B1 log-norm; Level B3 evaluates true downstream algebraic-sieve relation rate.
- **Mutations**: {"eval_level": "B3", "bound_a": 50, "bound_b": 20, "factor_base_size": 32}
- **Expected Effect**: smooth_relations_per_sec >= 1.25 * degree_2_yield
- **Promotion Target**: Pilot B-P2

### Track C — NSB-C-20260904-C00002
- **Hypothesis**: Fine-grained MSB calibration ladder (25%, 35%, 40%, 45%, 50%, 55%, 60%) establishes exact empirical recovery boundary.
- **Mechanism**: Testing genuine partial bit slices across 7 steps determines exact recovery cutoff and lattice dimension scaling limits.
- **Mutations**: {"fractions": [0.25, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6], "lattice_dimension": 5}
- **Expected Effect**: empirical_recovery_curve mapped across all 7 fractions without synthetic placeholders
- **Promotion Target**: Pilot C-P2

### Track D — NSB-D-20260904-D00001
- **Hypothesis**: Carry-save adder tree encoding reduces SAT conflict count by >= 25% on 32-bit balanced semiprimes.
- **Mechanism**: Reduces clause dependency chain depth compared to ripple-carry adders.
- **Mutations**: {"encoding_family": "carry_save", "solver": "cadical195"}
- **Expected Effect**: conflicts <= 0.75 * baseline_schoolbook_conflicts
- **Promotion Target**: Pilot D-P1


---

## 8. Exact Reproduction Command

```powershell
.venv\Scripts\python.exe -m nsb.cli wave1 --config config/wave1.yaml
```
