# R3 Foundation Canary Execution Attestation (G0 → G1 → G2)

**Protocol**: `NSB-R3-B-NFS-BASELINE-FOUNDATION` (v1.2.2)  
**Evaluated Commit**: `c3d69c6b1929680b3f22c43ae8ac716a3d058f4d`  
**Execution Timestamp**: 2026-09-04T14:39:57-05:00  
**Overall Verdict**: **`PASS`** (All Gates Certified: G0 PASS, G1 PASS, G2 PASS, Cross-Gate Invariance PASS)

---

## 1. Executive Summary

Canonical R3 canary execution was invoked inside the native Linux (WSL2 Ubuntu 24.04 LTS) environment under strict fail-closed enforcement:
```bash
PYTHONPATH=src CADO_NFS_ROOT=/opt/cado-nfs /home/admir/.venv-nsb/bin/python src/nsb/experiments/r3_nfs_baseline_runner.py --gate all --certify --out reports/R3_CANARY_CERTIFICATION.json
```

All three prerequisite gates and the cross-gate configuration parity check passed without warning or deviation:
1. **R3-G0 (Dependency & Provenance Gate)**: PASS. Native Linux execution verified, clean git working tree at evaluated commit `c3d69c6...`, CADO-NFS clean at pinned commit `73ca6b6...`, GCC 13.3.0 / CMake 3.28.3 / GMP 6.3.0 / MPFR 4.2.1 verified, Release `-O3 -DNDEBUG` build flags confirmed, deterministic Python package digest computed, and all 6 discrete binaries present with verified SHA-256 digests.
2. **R3-G1 (Discrete Binary Adapter Canaries)**: PASS. Valid algebraic polynomial selected and scored (degree 5, Murphy-$E = 1.53 \times 10^{-5}$), discrete factor base generated (`makefb`), lattice sieving completed (`las`) yielding 5,494 unique relations verified by `check_rels` with full relation conservation verified under profile `canary_plumbing_c60`.
3. **R3-G2 (Deterministic Rerun Canary & Parameter Parity)**: PASS. Counterbalanced 4-run execution sequence ($A_1 \to B_1 \to B_2 \to A_2$) executed under explicit profile `canary_plumbing_c60` yielded bit-for-bit identical normalized relation records (`e56879f8...`), bit-for-bit identical canonical $(a,b)$ pairs (`33c39da6...`), identical relation counts (5,494), 100% `check_rels` validity, and 100% relation conservation across all 4 runs.
4. **Cross-Gate Invariance Assertion**: PASS. When G1's certified polynomial was evaluated under the identical profile in G2, G1's `relations_hash` bit-for-bit matched every G2 run's hash (`cross_gate_hash_match is True`), closing the previous 5,494 vs 5,495 configuration difference.

---

## 2. Gate-by-Gate Results

| Gate | Gate Name | Result | Diagnostic Details |
| :--- | :--- | :---: | :--- |
| **R3-G0** | Dependency Foundation & Environment | **PASS** | Native Linux (Ubuntu 24.04 / WSL2), CADO-NFS pinned commit `73ca6b6...` (clean), NSB commit `c3d69c6...` (clean), 6/6 binaries verified. |
| **R3-G1** | Discrete Binary Adapter Canaries | **PASS** | Polyselect + ROPT valid; Murphy-$E = 1.53 \times 10^{-5} > 0$; makefb + las yielded 5,494 relations; check_rels verified; conservation checked; profile `canary_plumbing_c60`. |
| **R3-G2** | Deterministic Rerun Canary ($A_1 \to B_1 \to B_2 \to A_2$) | **PASS** | Complete relation record hash invariant across all 4 runs (`e56879f8...`); $(a,b)$ pairs invariant (`33c39da6...`); 5,494 unique relations; check_rels verified; conservation checked. |
| **Cross-Gate** | G1 $\leftrightarrow$ G2 Hash Equivalence | **PASS** | G1 `relations_hash` == G2 `relation_record_hash` across all 4 counterbalanced runs (`cross_gate_hash_match: true`). |

---

## 3. Environment & Toolchain Fingerprint

```json
{
  "platform": "linux",
  "is_linux": true,
  "nsb_git_commit": "c3d69c6ba75c92c85e2b02bb7d0a28f8045610ec",
  "nsb_git_dirty": false,
  "python_version": "3.12.3",
  "python_compiler": "GCC 13.3.0",
  "installed_python_packages_hash": "9ec3edbe8a9812667b5839b315d45ca29818ba93717a1b085dab663ae53156c5",
  "cpu_architecture": "x86_64",
  "cpu_model": "AMD Ryzen 7 5800X 8-Core Processor",
  "cpu_count": 16,
  "os_system": "Linux",
  "os_release": "6.18.33.2-microsoft-standard-WSL2",
  "cado_root": "/opt/cado-nfs",
  "pinned_git_commit": "73ca6b6847118b05b15eeec27c86f45cef82a19e",
  "detected_git_commit": "73ca6b6847118b05b15eeec27c86f45cef82a19e",
  "is_git_clean": true,
  "toolchain": {
    "gcc": "13.3.0",
    "cmake": "cmake version 3.28.3",
    "git": "git version 2.43.0"
  },
  "gmp_mpfr": {
    "gmp": "6.3.0",
    "mpfr": "4.2.1"
  },
  "cmake_cache": {
    "effective_cmake_flags": {
      "CMAKE_BUILD_TYPE": "Release",
      "CMAKE_CXX_COMPILER": "/usr/bin/c++",
      "CMAKE_CXX_FLAGS_RELEASE": "-O3 -DNDEBUG",
      "CMAKE_C_COMPILER": "/usr/bin/cc",
      "CMAKE_C_FLAGS_RELEASE": "-O3 -DNDEBUG",
      "CMAKE_GENERATOR": "Unix Makefiles"
    }
  },
  "binaries_present": [
    "polyselect",
    "polyselect_ropt",
    "score",
    "makefb",
    "las",
    "check_rels"
  ],
  "binary_hashes": {
    "polyselect": "7ebc096f5e7830663acd43d7e83e973f4132ea4971c035b8ec70d1e106d5fbdb",
    "polyselect_ropt": "4e8f00182ea7ac8912183b9d2c002a2f5c30d634a562e18165412ca1d8b9d273",
    "score": "49bcf15da4c9103f063c152720cc14c0d30450685c7f2fb2f4b4eaa46620d428",
    "makefb": "327f56b89dae2aaa50b37bfbce84d1561ccb438171a144664272e5944f4a0d76",
    "las": "7207656efc4e89748c499bda821d63be027a69811035a3413aadcc9f56da87f9",
    "check_rels": "234cd00682adf30ed4b6e9669224ec14b7397e19ee28633162889598cf792d3d"
  }
}
```

---

## 4. Discrete Binary Adapter Canary Details (R3-G1)

- **Modulus $N$**: `100000000000000000000000000047894685265564092504022465716177` (60 digits)
- **Profile**: `canary_plumbing_c60`
- **Polyselect**: Selected degree-5 polynomial ($c_5 = -720$, skew = 133.443) in 14.13 CPU seconds (14.14 wall seconds).
- **Scoring**:
  - Murphy $E$: $1.53 \times 10^{-5} > 0$
  - LogNorm: 18.47
  - Exp $E$: 13.67
  - Real roots: 3
- **Lattice Sieving**:
  - Special-$q$ range: $[500000, 500200]$
  - Unique relations: 5,494
  - Total relations: 5,494
  - Relations SHA-256 hash: `e56879f8b1ab44749c9236aa5f30686b5359abbd05ef23aea2b0912a2cfd7955`
  - `check_rels` verification: **PASS**
  - LAS conservation check: **PASS** (`conservation_checked == true`)
  - Sieve CPU time: 1.23 CPU seconds (4,458.33 relations/CPU s)

---

## 5. Deterministic Rerun Canary Details (R3-G2)

Four counterbalanced runs ($A_1 \to B_1 \to B_2 \to A_2$) were executed on the certified polynomial pair across special-$q \in [500000, 500200]$ under explicit profile `canary_plumbing_c60`:

| Run | Unique Rels | Total Rels | Full Record Hash (`relations_hash`) | $(a,b)$ Pairs Hash (`ab_pairs_hash`) | check_rels | Conservation | Sieve CPU (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A1** | 5,494 | 5,494 | `e56879f8b1ab44749c9236aa5f30686b5359abbd05ef23aea2b0912a2cfd7955` | `33c39da676d594ae9d3f94c041e1633fab35aca099a67de52275b7bdfd50d72e` | PASS | PASS | 1.8325 |
| **B1** | 5,494 | 5,494 | `e56879f8b1ab44749c9236aa5f30686b5359abbd05ef23aea2b0912a2cfd7955` | `33c39da676d594ae9d3f94c041e1633fab35aca099a67de52275b7bdfd50d72e` | PASS | PASS | 1.8525 |
| **B2** | 5,494 | 5,494 | `e56879f8b1ab44749c9236aa5f30686b5359abbd05ef23aea2b0912a2cfd7955` | `33c39da676d594ae9d3f94c041e1633fab35aca099a67de52275b7bdfd50d72e` | PASS | PASS | 1.8625 |
| **A2** | 5,494 | 5,494 | `e56879f8b1ab44749c9236aa5f30686b5359abbd05ef23aea2b0912a2cfd7955` | `33c39da676d594ae9d3f94c041e1633fab35aca099a67de52275b7bdfd50d72e` | PASS | PASS | 1.8725 |

**Invariance Verification**:
- Full Normalized Relation Records: **Bit-for-bit identical across all 4 runs** (`e56879f8...`)
- Canonical $(a,b)$ Pairs: **Bit-for-bit identical across all 4 runs** (`33c39da6...`)
- Unique Relation Count: **Exactly 5,494 in all 4 runs**
- Relation Conservation: **100% verified in all 4 runs**
- `check_rels` Verification: **100% valid in all 4 runs**
- Cross-Gate Invariance: **`cross_gate_hash_match: true`** (G1 hash == G2 hash bit-for-bit)

---

## 6. Program State & Scientific Governance

1. **Certification Status**:
   $$\mathbf{\texttt{R3\_FOUNDATION\_EXECUTABLE\_CERTIFIED / CALIBRATION\_READINESS\_PATCHED}}$$
   - G0: PASS
   - G1: PASS
   - G2 repeatability: PASS
   - G1 $\leftrightarrow$ G2 parameter parity & cross-gate invariance: PASS
   - Pinned per-size profiles frozen: `c60_pinned`, `c70_pinned`, `c80_pinned`, `c90_pinned`
   - R3-G3 public baseline calibration design preregistered in `ACTIVE_CONTRACT.md`
2. **Standing Holds (Strictly Maintained)**:
   - **Baseline Calibration Execution** (60/70/80/90-digit runs): **HOLD PENDING CALIBRATION REVIEW**.
   - **Fresh Out-of-Sample Holdout Generation**: **HOLD**.
   - **Candidate Scientific Development / Claims**: **HOLD**.

---

## 7. Erratum

- **Evaluated Commit SHA Referent**: In the initial draft of this markdown report, the evaluated commit SHA was typographically reported as `c3d69c6ba75c92c85e2b02bb7d0a28f8045610ec`. The authoritative machine-generated JSON report ([`R3_CANARY_CERTIFICATION.json`](R3_CANARY_CERTIFICATION.json)) correctly recorded the true git commit hash `c3d69c6b1929680b3f22c43ae8ac716a3d058f4d`. The markdown header and body referents have been corrected to match the true commit hash without altering any experimental data.
