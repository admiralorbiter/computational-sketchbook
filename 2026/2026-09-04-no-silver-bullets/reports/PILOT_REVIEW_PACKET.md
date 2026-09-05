# No Silver Bullet — Gate 1 Pilot Review Packet

**Generated**: 2026-09-04T02:01:59.540812+00:00  
**Active Contract**: `NSB-R0-GATE1-PILOTS`  
**Evaluated Commit**: `c0d5ae5a6a4a77bfbb2c8197f430eb7df40d9541`  
**Attestation Commit**: *(Pending final commit)*  
**Benchmark Version**: `v001_pilot`  
**Wave**: `Gate 1A — Feasibility & Calibration`  
**Total Compute Seconds**: 18.17s  
**Auditor Verdict**: **`PASS`**  

---

## 1. Executive Status

* **Contract**: `NSB-R0-GATE1-PILOTS`
* **Evaluated Commit**: `c0d5ae5a6a4a77bfbb2c8197f430eb7df40d9541`
* **Attestation Commit**: *(Pending final commit)*
* **Benchmark Version**: `v001_pilot`
* **Wave**: `Gate 1A — Feasibility & Calibration`
* **Total Pilot Compute**: 18.17s
* **Auditor Verdict**: **`PASS`**
* **Gate 1 Milestone Status**: **`GATE_1A_FEASIBILITY_PASSED / CALIBRATION_ESTABLISHED`**
* **Promotion Status Summary**: Track A: `INCONCLUSIVE` | Track B: `CANDIDATE` | Track C: `CALIBRATION_INCOMPLETE` | Track D: `BASELINE_ESTABLISHED`
* **Human Decision Required**: Gate 1A feasibility and calibration established. Research tracks evaluated per PromotionJudge criteria: Track A relation collapse boundary needs parametric grid; Track B requires B3 homogeneous sieve yield measurement; Track C requires multi-fraction MSB calibration ladder; Track D characterized schoolbook baseline and is ready for carry-save adder tree comparison.

---

## 2. Track Summary Table

| Track | Champion Experiment | Evidence Tier | Bit Range | Primary Metric | Baseline | Delta | Validation Status | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | `NSB-A-PILOT-01` | E1 | 16-32 | smooth_relations/cpu_sec: 13.3 rel/s (16b), 1.5 rel/s (20b), 0.0 rel/s (32b) | 12.1 rel/s (16b), 3.8 rel/s (20b), 0.0 rel/s (32b) | C=2000 not promoted (1.09x at 16b (13.3 vs 12.1 rel/s), 0.39x at 20b (1.5 vs 3.8 rel/s), 1.00x at 32b (0.0 vs 0.0 rel/s)) | `VALIDATED` | **`INCONCLUSIVE`** |
| **B** | `NSB-B-PILOT-01` | E1 | 32-64 | log_norm_proxy_score: deg-3: 23.80 (32b), 34.99 (48b), 46.06 (64b) | deg-2: 30.68 (32b), 46.79 (48b), 61.97 (64b) | Cubic base-m shows genuine B1 signal; B3 relation yield not yet evaluated for promotion | `VALIDATED` | **`CANDIDATE`** |
| **C** | `NSB-C-PILOT-01` | E1 | 32-48 | threshold_recovery_rate: 32b: SUCCESS (0.13s), 40b: FAIL, 48b: FAIL | zero_information | Exact rational Sturm/LLL verified at 32b; 40b/48b bound transition incomplete (1/3 recovered) | `VALIDATED` | **`CALIBRATION_INCOMPLETE`** |
| **D** | `NSB-D-PILOT-01` | E1 | 16-32 | median_solve_time_seconds: 0.0012s (16b) to 0.2195s (32b) | schoolbook_sat_glucose4 | Schoolbook SAT baseline characterized; alternative carry-save encoding ready for comparison | `VALIDATED` | **`BASELINE_ESTABLISHED`** |

### Promotion Criteria Breakdown

#### Track A (NSB-A-PILOT-01)
- **Scientific Verdict**: **`INCONCLUSIVE`** (Tier E1, Range: 16-32 bits)
- **Preregistered Promotion Criteria Evaluation**:
  - `[FAIL] relation_rate_gain`: 1.09x at 16b (13.3 vs 12.1 rel/s), 0.39x at 20b (1.5 vs 3.8 rel/s), 1.00x at 32b (0.0 vs 0.0 rel/s) (Target: >= 1.5x advantage over baseline across >= 3 adjacent sizes)
    - *Justification*: Advantage reversed or collapsed to 0 relations at [32]b.
  - `[FAIL] scaling_persistence`: Ratios: ['16b:1.09x', '20b:0.39x', '32b:1.00x']; zero_yield_bits: [32] (Target: Advantage persists with increasing bit length)
    - *Justification*: Complete yield drop-off to 0 relations observed at [32]b.
- **Judge Recommendation**: Map the relation collapse boundary via a parametric grid over (factor_base_size x scale_c x candidate_budget) before attempting larger moduli.

#### Track B (NSB-B-PILOT-01)
- **Scientific Verdict**: **`CANDIDATE`** (Tier E1, Range: 32-64 bits)
- **Preregistered Promotion Criteria Evaluation**:
  - `[PASS] b1_log_norm_advantage`: deg-3=23.80 vs deg-2=30.68 (32b, ratio=0.78); deg-3=34.99 vs deg-2=46.79 (48b, ratio=0.75); deg-3=46.06 vs deg-2=61.97 (64b, ratio=0.74) (Target: Degree-3 proxy log-norm <= 0.85 * Degree-2 score)
    - *Justification*: Degree-3 base-m representation consistently achieved <= 0.85 coefficient log-norm across all tested moduli.
  - `[NOT_ENOUGH_DATA] b3_downstream_yield_promotion`: 423 pairs sampled; smooth relations and B3 relation rate not evaluated for promotion (Target: >= 25% smooth relation yield improvement in B3 homogeneous sieve (rule: never promote on B1 alone))
    - *Justification*: Per frozen protocol docs/06_TRACK_B_ALGEBRAIC_EVOLUTION.md: 'The director never promotes on Level B1 alone.' Downstream B3 yield was not evaluated.
- **Judge Recommendation**: Execute B3 homogeneous sieving on top cubic candidates to measure actual smooth-relation rate through 64 bits.

#### Track C (NSB-C-PILOT-01)
- **Scientific Verdict**: **`CALIBRATION_INCOMPLETE`** (Tier E1, Range: 32-48 bits)
- **Preregistered Promotion Criteria Evaluation**:
  - `[FAIL] 50pct_msb_recovery_rate`: 1/3 recovered (32b: SUCCESS (0.13s), 40b: FAIL, 48b: FAIL) (Target: 100% exact recovery at 50% known MSB across pilot ladder)
    - *Justification*: Exact Sturm/LLL small-root solver succeeded on 1/3 instances at 50% MSB.
  - `[NOT_ENOUGH_DATA] calibration_ladder_completeness`: Only [0.5] tested with valid data; negative control used synthetic placeholder (Target: Calibrated across 25%, 35%, 45%, 50% true MSB fractions)
    - *Justification*: Genuine calibration surface requires testing true partial factor bit slices across 25%, 35%, 40%, 45%, 50%, 55%, 60%.
- **Judge Recommendation**: Construct a multi-fraction calibration corpus (25% to 60%) to empirically map the exact univariate root recovery boundary.

#### Track D (NSB-D-PILOT-01)
- **Scientific Verdict**: **`BASELINE_ESTABLISHED`** (Tier E1, Range: 16-32 bits)
- **Preregistered Promotion Criteria Evaluation**:
  - `[PASS] baseline_characterization`: 0.0012s (16b) -> 0.0027s (20b) -> 0.0146s (24b) -> 0.0402s (28b) -> 0.2195s (32b) (Target: Establish clean empirical solve-time scaling curve for Schoolbook SAT)
    - *Justification*: Clean, reproducible CDCL SAT scaling curve established across 5 consecutive bit lengths with zero semantic errors.
  - `[NOT_ENOUGH_DATA] comparative_encoding_advantage`: No alternative encoding evaluated in pilot run (schoolbook-only) (Target: >= 2.0x solve time improvement over schoolbook across >= 3 adjacent sizes)
    - *Justification*: Promotion requires comparing an alternative arithmetic encoding (e.g. carry-save adder tree) against the schoolbook baseline.
- **Judge Recommendation**: Implement carry-save adder tree encoding and execute the first paired encoding-vs-encoding scaling comparison.


---

## 3. New Findings

1. **Baselines Ladder (Fermat, Pollard rho, Pollard p-1)**:
   - Fermat cleanly factored balanced Family F (48b in 1 steps (0.00008s), 64b in 1 steps (0.00003s)).
   - Pollard p-1 solved smooth-order Family P1 (48b in 0.00018s, 64b in 0.00036s).
   - Pollard rho factored Family R (32b in 255 steps (0.0001s), 32b in 127 steps (0.0001s), 40b in 511 steps (0.0002s), 40b in 1791 steps (0.0006s)), establishing the classical comparison curve.
2. **Track A (Tensor / Lattice Relation Discovery — `INCONCLUSIVE`)**:
   - Track A evaluated across 3 bit lengths (16-32 bits).
   - Observed scaling ratios: 1.09x at 16b (13.3 vs 12.1 rel/s), 0.39x at 20b (1.5 vs 3.8 rel/s), 1.00x at 32b (0.0 vs 0.0 rel/s).
   - Sharp relation-yield collapse observed at [32]b with 0 smooth relations found.
   - **Recommended Next Step**: Map the relation collapse boundary via a parametric grid over (factor_base_size x scale_c x candidate_budget) before attempting larger moduli.
3. **Track B (Evolved Algebraic Representations — `CANDIDATE`)**:
   - Multi-fidelity cascade B0-B3 verified algebraic representations across 32-64 bit moduli.
   - Degree-3 base-m representation measured log-norms: 23.80 (32b), 34.99 (48b), 46.06 (64b) vs deg-2 baseline: 30.68 (32b), 46.79 (48b), 61.97 (64b).
   - Promotion to E2 requires measuring actual smooth-relation yield in homogeneous sieving, which remains unevaluated.
   - **Recommended Next Step**: Execute B3 homogeneous sieving on top cubic candidates to measure actual smooth-relation rate through 64 bits.
4. **Track C (Partial Information Bridge — `CALIBRATION_INCOMPLETE`)**:
   - Exact rational Sturm chain root isolation operates with zero IEEE-754 precision loss and recovers exact factors with no fallback.
   - Observed 50% MSB success rate was 1/3 (32b: SUCCESS (0.13s), 40b: FAIL, 48b: FAIL).
   - Negative control at 25% used a synthetic placeholder rather than genuine factor MSBs.
   - **Recommended Next Step**: Construct a multi-fraction calibration corpus (25% to 60%) to empirically map the exact univariate root recovery boundary.
5. **Track D (Constraint Graph Inversion — `BASELINE_ESTABLISHED`)**:
   - Schoolbook SAT encoding successfully inverted across 16-32 bits with 100% factor recovery.
   - Empirical CDCL solve time exhibits clean scaling (0.0012s (16b) to 0.2195s (32b)).
   - Track D is not promoted because no paired alternative encoding was tested in this feasibility pilot.
   - **Recommended Next Step**: Implement carry-save adder tree encoding and execute the first paired encoding-vs-encoding scaling comparison.

---

## 4. Auditor Checks & Integrity Verification

- **[PASS] git_provenance_cleanliness**: Clean git state at c0d5ae5a6a4a77bfbb2c8197f430eb7df40d9541
- **[PASS] public_sha_pilot**: Calculated 1f447eea... vs Expected 1f447eea...
- **[PASS] sealed_sha_pilot**: Calculated 5bef83e1... vs Expected 5bef83e1...
- **[PASS] public_sha_smoke**: Calculated a0d734bd... vs Expected a0d734bd...
- **[PASS] sealed_sha_smoke**: Calculated 8373b701... vs Expected 8373b701...
- **[PASS] tripwire_pilot**: Tripwire intact and untampered
- **[PASS] tripwire_smoke**: Tripwire intact and untampered
- **[PASS] sandbox_leakage**: Verified 2 active sandbox(es); zero sealed leakage detected

---

## 5. Empirical Scaling Curves

### Track Baselines Scaling Curve
- **Fermat (Family F)** (48 bits): 1 steps (0.00008s)
- **Fermat (Family F)** (64 bits): 1 steps (0.00003s)
- **Pollard p-1 (Family P1)** (48 bits): 0.00018s
- **Pollard p-1 (Family P1)** (64 bits): 0.00036s
- **Pollard rho (Family R)** (32 bits): 255 steps (0.0001s)
- **Pollard rho (Family R)** (32 bits): 127 steps (0.0001s)
- **Pollard rho (Family R)** (40 bits): 511 steps (0.0002s)
- **Pollard rho (Family R)** (40 bits): 1791 steps (0.0006s)
### Track A Scaling Curve
- **Schnorr CVP C=2000 vs C=500** (16 bits): 35 rels (13.3/cpu_s) vs baseline 32 rels (12.1/cpu_s)
- **Schnorr CVP C=2000 vs C=500** (20 bits): 4 rels (1.5/cpu_s) vs baseline 10 rels (3.8/cpu_s)
- **Schnorr CVP C=2000 vs C=500** (32 bits): 0 rels (0.0/cpu_s) vs baseline 0 rels (0.0/cpu_s)
### Track B Scaling Curve
- **Base-m deg-3 vs deg-2 log-norm** (32 bits): deg-3=23.80 (homo: 141) vs deg-2=30.68 (homo: 141)
- **Base-m deg-3 vs deg-2 log-norm** (48 bits): deg-3=34.99 (homo: 141) vs deg-2=46.79 (homo: 141)
- **Base-m deg-3 vs deg-2 log-norm** (64 bits): deg-3=46.06 (homo: 141) vs deg-2=61.97 (homo: 141)
### Track C Scaling Curve
- **Oracle MSB Recovery Curve** (32 bits): 50% MSB: SUCCESS (0.1295s); 25% MSB: CLEAN_FAIL
- **Oracle MSB Recovery Curve** (40 bits): 50% MSB: FAIL (0.2076s); 25% MSB: CLEAN_FAIL
- **Oracle MSB Recovery Curve** (48 bits): 50% MSB: FAIL (0.4109s); 25% MSB: CLEAN_FAIL
### Track D Scaling Curve
- **Schoolbook SAT Glucose4** (16 bits): 0.0012s (200 vars, 978 clauses, sat=True)
- **Schoolbook SAT Glucose4** (20 bits): 0.0027s (310 vars, 1562 clauses, sat=True)
- **Schoolbook SAT Glucose4** (24 bits): 0.0146s (444 vars, 2282 clauses, sat=True)
- **Schoolbook SAT Glucose4** (28 bits): 0.0402s (602 vars, 3138 clauses, sat=True)
- **Schoolbook SAT Glucose4** (32 bits): 0.2195s (784 vars, 4130 clauses, sat=True)

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

### Track D — NSB-D-20260904-D00002
- **Hypothesis**: Carry-save adder tree encoding reduces CDCL SAT solve time by >= 2x over schoolbook baseline on 24-32 bit moduli.
- **Mechanism**: Carry-save tree reduces clause dependency chain depth from O(n^2) to O(n log n).
- **Mutations**: {"encoding_family": "carry_save", "baseline_encoding": "schoolbook", "solver": "glucose4"}
- **Expected Effect**: solve_time <= 0.50 * baseline_schoolbook_solve_time
- **Promotion Target**: Pilot D-P2


---

## 8. Exact Reproduction Command

```powershell
.venv\Scripts\python.exe -m nsb.cli pilot --config config/pilot.yaml
```
