# R3 Foundation Canary Execution Attestation (G0 → G1 → G2)

**Protocol**: `NSB-R3-B-NFS-BASELINE-FOUNDATION` (v1.1.3)  
**Evaluated Commit**: `a9c57b641463ab5946685bf87725e817b395a906`  
**Execution Timestamp**: 2026-09-04T12:49:17-05:00  
**Overall Verdict**: **`FAIL`** (G0 Environment Gate Fail-Closed)

---

## 1. Executive Summary

Canonical R3 canary execution was authorized and invoked via:
```powershell
PYTHONPATH=src python -m nsb.experiments.r3_nfs_baseline_runner --gate all --certify --out reports/R3_FOUNDATION_G0_G1_G2_CANARY.json
```

The experiment runner executed under strict fail-closed enforcement. **Gate R3-G0 rejected the execution environment** because the host platform is native Windows (`win32`) without an active Linux or WSL2 subsystem. Consequently, discrete binary adapter canaries (**R3-G1**) and paired-instrument invariance canaries (**R3-G2**) were blocked from execution, preserving strict protocol integrity.

---

## 2. Gate-by-Gate Results

| Gate | Gate Name | Result | Diagnostic Details |
| :--- | :--- | :---: | :--- |
| **R3-G0** | Environment & Dependency Foundation | **FAIL** | Canonical R3 execution requires Python runner executing inside native Linux / WSL2. Windows host execution is non-canonical. |
| **R3-G1** | Discrete Binary Adapter Canaries | **BLOCKED** | Blocked by G0 failure. Pinned binary execution halted. |
| **R3-G2** | Paired Invariance Canary ($A_1 \to B_1 \to B_2 \to A_2$) | **BLOCKED** | Blocked by G0 failure. Invariance testing halted. |

---

## 3. Environment Fingerprint

```json
{
  "platform": "win32",
  "is_linux": false,
  "is_windows": true,
  "python_version": "3.12.0",
  "cpu_architecture": "AMD64",
  "cpu_count": 16,
  "os_release": "11",
  "cado_root": "cado-nfs",
  "cado_root_exists": false,
  "pinned_git_commit": "73ca6b6847118b05b15eeec27c86f45cef82a19e",
  "detected_git_commit": null,
  "is_git_clean": false,
  "toolchain": {
    "gcc": "unavailable",
    "cmake": "unavailable",
    "git": "git version 2.50.0.windows.1"
  },
  "binaries_present": [],
  "missing_binaries": [
    "polyselect",
    "polyselect_ropt",
    "score",
    "makefb",
    "las",
    "check_rels"
  ],
  "binary_hashes": {}
}
```

---

## 4. Methodological Conclusion & Operational Status

1. **Protocol Guardrails Operating Correctly**:
   The automated harness successfully prevented invalid, uninstrumented, or cross-platform emulation execution. Per preregistered contract `NSB-R3-B-NFS-BASELINE-FOUNDATION`, Windows host execution cannot certify mature Linux CADO binaries.
2. **Program State**:
   Program state remains:
   $$\mathbf{\texttt{R3\_FOUNDATION\_V1.1.3\_SCAFFOLD\_IMPLEMENTED / REAL\_BINARY\_CANARIES\_PENDING\_LINUX\_CERTIFICATION / CALIBRATION\_ON\_HOLD}}$$
   Certification to `R3_FOUNDATION_EXECUTABLE_CERTIFIED` is **NOT** achieved.
3. **Standing Holds**:
   - **Baseline Calibration**: HOLD.
   - **Fresh Corpus Generation**: HOLD.
   - **Candidate Scientific Development**: HOLD.
