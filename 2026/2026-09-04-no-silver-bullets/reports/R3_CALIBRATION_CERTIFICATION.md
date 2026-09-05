# R3-G3 Public Baseline Calibration Attestation

**Protocol**: `NSB-R3-B-NFS-BASELINE-FOUNDATION` (v1.3.0)  
**Evaluated Commit (Runner/Schema)**: `760df16398917370ceef8c22a8b900d42152f7ed`  
**Execution & Baseline Freeze Commit**: `edb62057a8b4c2844da5ce9fc4b5c4471b1713b1`  
**Execution Environment**: Native Linux (WSL2 Ubuntu 24.04 LTS, Python 3.12.3, GCC 13.3.0, CMake 3.28.3)  
**Overall Verdict**: **`PASS`** (R3-G3 Public Baseline Calibration Certified; Summary-Precision Erratum Applied)  
**Baseline Artifact**: `config/baselines/cado_nfs_calibration.json`  

---

## 1. Executive Summary

The empirical public baseline calibration for `NSB-R3-B-NFS-BASELINE-FOUNDATION` (R3-G3) has executed to 100% completion under strict fail-closed criteria in native Linux WSL2:
```bash
PYTHONPATH=src CADO_NFS_ROOT=/opt/cado-nfs python src/nsb/experiments/r3_calibration_runner.py --out config/baselines/cado_nfs_calibration.json
```

All 40 frozen public balanced semiprimes (10 per size: 60, 70, 80, 90 decimal digits) derived deterministically from master seed `NSB-R3-CALIBRATION-CORPUS-20260904-V001` were evaluated end-to-end through the discrete CADO-NFS toolchain (`polyselect` -> `polyselect_ropt` -> `score` -> `makefb` -> `las` -> `check_rels`).

### Key Validation Outcomes:
1. **Zero Failures / Zero Timeouts**: All 40 instances succeeded and executed well under the canonical per-stage timeout of 600.0s (the slowest observed instance recorded total wall time of 75.52s). Total cohort wall time was 1,117.26 seconds (~18.6 minutes).
2. **100% Mathematical Verification**: Every selected polynomial pair was independently verified for degree, leading coefficient, content coprimality, algebraic common root $m$, and Sylvester resultant modulo $N$ via Bareiss fraction-free algorithm (`verify_nfs_polynomial_pair`).
3. **100% Relation Correctness**: Every single relation file was independently checked and primality-verified via CADO's native `check_rels` binary (`checked_with_check_rels is True`).
4. **100% Relation Conservation**: Zero parser leakage; every parsed relation matched the raw las report line count (`conservation_checked is True`).
5. **Exact Profile Purity**: Each size class strictly executed its mechanically verified pinned profile (`c60_pinned`, `c70_pinned`, `c80_pinned`, `c90_pinned`) with single-threaded execution ($t=1$).
6. **Full Schema Completeness**: Every instance record includes full polynomial coefficients (`f1_coeffs`, `f2_coeffs`, $m$, degrees, skew), `polyselect` CPU & wall times, `score` Murphy-$E$, `sieving` throughput & wall time, and `timeout_seconds`.

---

## 2. Erratum: Murphy-E Summary Precision & Factual Clarifications

### Erratum A: High-Precision Summary Recomputation
The original runner function `compute_distribution_metrics()` rounded derived percentile metrics to six decimal places (`round(..., 6)`). While benign for CPU seconds, this precision truncation collapsed Murphy-$E$ percentiles around $10^{-6}$ (e.g. collapsing 80d percentiles to identical `3e-6` values despite raw observations ranging from $2.56 \times 10^{-6}$ to $4.04 \times 10^{-6}$).

In this results-only erratum:
- All 40 raw instance records remain 100% untouched and certified.
- Derived cohort aggregates in `config/baselines/cado_nfs_calibration.json` and `reports/R3_CALIBRATION_CERTIFICATION.json` were recomputed directly from the immutable raw instance records without 6-decimal rounding, preserving full floating-point precision.
- `compute_distribution_metrics()` in `src/nsb/experiments/r3_calibration_runner.py` was updated to default to full precision (`precision=None`).

### Erratum B: Commit SHA Typo & Wall Time Bounds
- **Commit SHA**: The evaluated runner commit is `760df16398917370ceef8c22a8b900d42152f7ed`, and the actual calibration-freeze commit is `edb62057a8b4c2844da5ce9fc4b5c4471b1713b1` (direct child of `760df16`).
- **Wall Time**: The maximum observed instance wall time across all 40 runs was 75.5249s (`R3-CALIB-D090-00008`), comfortably within the 600.0s threshold.
- **Timeout Policy**: The historical calibration policy enforced a 600.0s discrete stage timeout across each CADO binary invocation rather than a monolithic process timer.

---

## 3. High-Precision Cohort Performance Distributions

Distributions computed via `numpy.percentile(method='linear')` from raw per-instance records:

### 60-Digit Cohort (`c60_pinned`, ~196-200 bits, $N=10$)
- **Murphy-$E$**: $p_{10} = 7.876 \times 10^{-6}$, $p_{50} = 8.360 \times 10^{-6}$, $p_{90} = 8.988 \times 10^{-6}$ (min $7.840 \times 10^{-6}$, max $9.150 \times 10^{-6}$, mean $8.396 \times 10^{-6}$)
- **Polyselect CPU**: $p_{10} = 2.031\text{s}$, $p_{50} = 2.120\text{s}$, $p_{90} = 2.313\text{s}$ (mean $2.137\text{s}$)
- **Sieve CPU**: $p_{10} = 1.323\text{s}$, $p_{50} = 1.454\text{s}$, $p_{90} = 1.650\text{s}$ (mean $1.471\text{s}$)
- **Total CPU**: $p_{10} = 3.349\text{s}$, $p_{50} = 3.636\text{s}$, $p_{90} = 3.784\text{s}$ (mean $3.610\text{s}$)
- **Relations / CPU sec**: $p_{10} = 2,888.40$, $p_{50} = 3,177.47$, $p_{90} = 3,383.79$ (mean $3,152.46$)

### 70-Digit Cohort (`c70_pinned`, ~230-233 bits, $N=10$)
- **Murphy-$E$**: $p_{10} = 1.380 \times 10^{-5}$, $p_{50} = 1.520 \times 10^{-5}$, $p_{90} = 1.656 \times 10^{-5}$ (min $1.380 \times 10^{-5}$, max $1.710 \times 10^{-5}$, mean $1.517 \times 10^{-5}$)
- **Polyselect CPU**: $p_{10} = 5.109\text{s}$, $p_{50} = 5.335\text{s}$, $p_{90} = 5.597\text{s}$ (mean $5.350\text{s}$)
- **Sieve CPU**: $p_{10} = 2.656\text{s}$, $p_{50} = 2.918\text{s}$, $p_{90} = 3.323\text{s}$ (mean $2.929\text{s}$)
- **Total CPU**: $p_{10} = 7.795\text{s}$, $p_{50} = 8.465\text{s}$, $p_{90} = 8.635\text{s}$ (mean $8.281\text{s}$)
- **Relations / CPU sec**: $p_{10} = 3,400.24$, $p_{50} = 3,641.35$, $p_{90} = 3,918.78$ (mean $3,658.46$)

### 80-Digit Cohort (`c80_pinned`, ~263-266 bits, $N=10$)
- **Murphy-$E$**: $p_{10} = 2.713 \times 10^{-6}$, $p_{50} = 2.995 \times 10^{-6}$, $p_{90} = 3.455 \times 10^{-6}$ (min $2.560 \times 10^{-6}$, max $4.040 \times 10^{-6}$, mean $3.062 \times 10^{-6}$)
- **Polyselect CPU**: $p_{10} = 10.779\text{s}$, $p_{50} = 11.190\text{s}$, $p_{90} = 11.570\text{s}$ (mean $11.183\text{s}$)
- **Sieve CPU**: $p_{10} = 14.545\text{s}$, $p_{50} = 15.696\text{s}$, $p_{90} = 18.408\text{s}$ (mean $16.224\text{s}$)
- **Total CPU**: $p_{10} = 25.740\text{s}$, $p_{50} = 26.848\text{s}$, $p_{90} = 29.351\text{s}$ (mean $27.409\text{s}$)
- **Relations / CPU sec**: $p_{10} = 1,153.67$, $p_{50} = 1,271.43$, $p_{90} = 1,385.46$ (mean $1,260.13$)

### 90-Digit Cohort (`c90_pinned`, ~296-299 bits, $N=10$)
- **Murphy-$E$**: $p_{10} = 3.971 \times 10^{-6}$, $p_{50} = 4.215 \times 10^{-6}$, $p_{90} = 4.619 \times 10^{-6}$ (min $3.800 \times 10^{-6}$, max $4.970 \times 10^{-6}$, mean $4.251 \times 10^{-6}$)
- **Polyselect CPU**: $p_{10} = 31.797\text{s}$, $p_{50} = 32.045\text{s}$, $p_{90} = 32.699\text{s}$ (mean $32.202\text{s}$)
- **Sieve CPU**: $p_{10} = 33.201\text{s}$, $p_{50} = 35.571\text{s}$, $p_{90} = 38.439\text{s}$ (mean $35.882\text{s}$)
- **Total CPU**: $p_{10} = 65.316\text{s}$, $p_{50} = 67.769\text{s}$, $p_{90} = 70.334\text{s}$ (mean $68.086\text{s}$)
- **Relations / CPU sec**: $p_{10} = 1,151.31$, $p_{50} = 1,239.70$, $p_{90} = 1,297.56$ (mean $1,224.80$)

---

## 4. Provenance & Toolchain Binding

- **NSB Git Commit**: `760df16398917370ceef8c22a8b900d42152f7ed` (Clean working tree)
- **CADO Pinned Git Commit**: `73ca6b6847118b05b15eeec27c86f45cef82a19e` (Clean working tree)
- **Public Corpus Manifest SHA-256**: `93154f75bd2f00c9ec2377686e801c5795e1d84619a7b75ab872bb38e90535ba`
- **Public Instances SHA-256**: `9d32b59bccb88b6b56ec90c6600d8c80a3189504457b118240510a1f1b8b177c`
- **Python Version**: `3.12.3` (GCC 13.3.0)
- **Toolchain**: GCC `13.3.0`, CMake `3.28.3`, Git `2.43.0`, GMP `6.3.0`, MPFR `4.2.1`
- **Compiler Flags**: `-O3 -DNDEBUG` (Release build)
- **Host CPU**: AMD Ryzen 7 5800X 8-Core Processor (16 threads)
- **OS Kernel**: Linux `6.18.33.2-microsoft-standard-WSL2`

---

## 5. Operational Gate Status

| Gate | Name | Status |
| :--- | :--- | :---: |
| **R3-G0** | Dependency & Provenance Foundation | **CERTIFIED PASS** |
| **R3-G1** | Discrete Binary Adapter Canaries | **CERTIFIED PASS** |
| **R3-G2** | Deterministic Rerun & Cross-Gate Parity | **CERTIFIED PASS** |
| **R3-G3** | Public Baseline Calibration | **CERTIFIED PASS** |
| — | Out-of-Sample Holdout (>90 digits) Generation | **STRICT HOLD** |
| — | Candidate Representation Evolution / Claims | **STRICT HOLD** |
