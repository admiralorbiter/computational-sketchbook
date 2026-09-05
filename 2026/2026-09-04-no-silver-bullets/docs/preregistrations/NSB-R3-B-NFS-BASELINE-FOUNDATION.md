# Preregistered Protocol: NSB-R3-B-NFS-BASELINE-FOUNDATION
## Realistic NFS Polynomial Selection & Relation-Collection Baseline Foundation

**Protocol ID**: `NSB-R3-B-NFS-BASELINE-FOUNDATION`  
**Version**: `1.3.0`  
**Track**: `Track B (Algebraic Evolution & Realistic NFS Polynomial Selection)`  
**Baseline Framework**: `CADO-NFS` (Pinned Git Commit: `73ca6b6847118b05b15eeec27c86f45cef82a19e`)  
**Upstream Repository**: `https://gitlab.inria.fr/cado-nfs/cado-nfs.git` (Mirrored at `https://github.com/cado-nfs/cado-nfs.git`)  
**Execution Environment**: `Native Linux (or WSL2) only for canonical execution`

---

## 1. Scientific Objective & Paradigm Shift

Wave 2 demonstrated that systematic representation search over a local 35-slot degree-3 translation/rotation grid cannot lift algebraic relation density out of the dimensional sparsity floor at $\ge 64$ bits under an artificial micro-sieve proxy ($A=100, B=20, FB=250$).

`NSB-R3-B-NFS-BASELINE-FOUNDATION` executes Decision **D007**, abandoning the 32–96-bit micro-sieve toy problem and grounding Track B directly in state-of-the-art Number Field Sieve (NFS) machinery.

The central scientific question of Track B is redefined:
$$\mathbf{\text{“Can a novel representation-selection method produce reproducible improvements in actual NFS polynomial quality and downstream relation collection against a mature baseline?”}}$$

---

## 2. Pinned Development Baseline

CADO-NFS development commit `73ca6b6847118b05b15eeec27c86f45cef82a19e` is pinned as the authoritative reference implementation:
- **Language / Standards**: C++20, GCC $\ge 10$, CMake $\ge 3.18$, Python $\ge 3.8$, GMP $\ge 6.1$, MPFR $\ge 4.0$.
- **Operating System Requirement**: Linux (native Linux or WSL2 where Python runner executes in Linux).
- **Deterministic Build Directory**: `$CADO_ROOT/build/nsb-r3/`.
- **Binary Components**:
  - `polyselect`: Kleinjung size/norm search with real CADO parameter domain (`-P`, `-admin`, `-admax`, `-incr`, `-nq`).
  - `polyselect_ropt`: Root property optimization via `-inputpolys <file> -ropteffort <effort>`, selecting the global Murphy-E-best result among parsed candidate blocks.
  - `score`: Independent neutral evaluation via positional CLI `score --full -Bf <bf> -Bg <bg> -area <area> <target.poly>`.
  - `makefb`: Mandatory discrete factor base generation for side 0 and side 1.
  - `las`: Lattice siever for relation collection with parameter profiles (`-I`, `-lim[01]`, `-lpb[01]`, `-mfb[01]`, `-sqside`).
  - `check_rels`: Relation correctness and primality verifier (`build/nsb-r3/misc/check_rels`) invoked as `check_rels -poly <poly> -lpb0 <lpb0> -lpb1 <lpb1> -check_primality <rel_file>`, required in G0 and enforced in G1 and G2.

---

## 3. Narrow Experimental Intervention

The experimental harness enforces strict intervention isolation:
$$\text{Input Modulus } N \longrightarrow \text{Polynomial Selector} \longrightarrow \text{Canonical CADO } \texttt{.poly} \longrightarrow \text{Independent CADO Scoring} \longrightarrow \text{Identical CADO FB/LAS Sieving}$$

- Both CADO baseline and future research candidates output standard CADO `.poly` artifacts.
- Both are scored neutrally by CADO's own `score` binary.
- Both collect relations under identical parameter profiles, identical factor base bounds, identical sieve areas, identical thread counts, and identical special-$q$ intervals.

---

## 4. General Polynomial Model (`NfsPolynomialPair`)

The legacy constraint assuming degree 3 with a linear rational side ($f_2(x) = x - m$) is retired.
The new `NfsPolynomialPair` model supports:
- Arbitrary algebraic degree $d_1 \ge 1$ and rational/algebraic degree $d_2 \ge 1$ ($d_1 = 4, 5, 6+$).
- Arbitrary integer coefficient vectors on both sides: $f_1(x) = \sum_{i=0}^{d_1} a_i x^i$ and $f_2(x) = \sum_{j=0}^{d_2} b_j x^j$.
- Independent mathematical validity verification:
  - $\gcd(a_0, \dots, a_{d_1}) = 1$ and $\gcd(b_0, \dots, b_{d_2}) = 1$.
  - Leading coefficients $a_{d_1} \neq 0$ and $b_{d_2} \neq 0$.
  - Resultant condition: $\text{Res}(f_1, f_2) \equiv 0 \pmod N$ verified unconditionally via Bareiss fraction-free algorithm.
  - Common root condition: $f_1(m) \equiv f_2(m) \equiv 0 \pmod N$ when witness $m$ exists.

---

## 5. Cumulative Observed Process-Tree Accounting

To eliminate process-exit undercounting inherent in sampling child process trees of sequential controllers, the R3 harness uses cumulative observed process-tree accounting: measuring CPU core-seconds (`user + system` time via `psutil` polled at 50ms intervals across cumulative observed PIDs) for each discrete binary execution:
$$\text{Total CPU} = t_{\text{polyselect}} + t_{\text{polyselect\_ropt}} + t_{\text{score}} + t_{\text{makefb}} + t_{\text{las}} (+ t_{\text{check\_rels}})$$
Process streams (stdout/stderr) are streamed directly to disk files to prevent OS pipe deadlocks.

---

## 6. Metric Hierarchy & Evaluation Views

### Metric Hierarchy:
1. **Level 1 (Diagnostic / Mechanistic)**: CADO Murphy-$E$, logarithmic norm, $\exp(E)$, skewness, real root count (`rroots`).
2. **Level 2 (Primary Experimental Outcome)**: Unique valid relations per core-second ($> 0$), relations per special-$q$ range, productive special-$q$ ratio.
3. **Level 3 (System Efficiency)**: Total core-seconds (selection + setup + sieving) to reach a fixed relation target.

### Dual Evaluation Views:
- **Quality View**: Given each method's prescribed search, which polynomial yields superior downstream relations under identical LAS settings?
- **System View**: When charged for polynomial-selection CPU, which method reaches a fixed relation target in fewer total core-seconds?

---

## 7. Staged Implementation Gates

- **R3-G0 — Dependency & Comprehensive Provenance Foundation**: Lockfile, bootstrap script, comprehensive environment fingerprinting (CPU model, total/available RAM, kernel version, Python dependency lock digest and installed packages freeze hash, CMake effective compiler/build flags, CMake cache hash), exact full 40-char SHA check (`73ca6b6...`), clean CADO git tree assertion, clean NSB git tree assertion, enforced toolchain version locks (GCC $\ge 10$, CMake $\ge 3.18$, Python $\ge 3.8$, GMP $\ge 6.1$, MPFR $\ge 4.0$), deterministic fresh build directory `$CADO_ROOT/build/nsb-r3/`, and Linux/WSL fail-closed checks. Status: **CERTIFIED PASS**.
- **R3-G1 — Adapter Canaries & Fail-Closed Parser Conservation**: Polyselection, root optimization, multi-block parsing of `.polys`, independent resultant/root verification, `score`, mandatory side-specific `makefb`, bounded `las`, fail-closed parser conservation checking (missing summary count line or count mismatch raises error; `sieve_res.conservation_checked is True` required), and `check_rels` verification yielding $>0$ unique relations on public ~60-digit balanced semiprime under profile `canary_plumbing_c60`. Status: **CERTIFIED PASS**.
- **R3-G2 — Deterministic Rerun Canary & Parameter Parity**: 4-run counterbalanced execution ($A_1 \to B_1 \to B_2 \to A_2$) on identical polynomial and special-$q$ interval through the fixed CADO relation collector under explicit profile `canary_plumbing_c60`. Asserts identical unique relation counts (5,494), identical normalized complete relation record SHA-256 hashes (`relations_hash`), identical $(a, b)$ pair hashes (`ab_pairs_hash`), cross-gate hash matching with G1 (`cross_gate_hash_match is True`), and fail-closed conservation checks. Status: **CERTIFIED PASS**.
- **R3-G3 — Public Baseline Calibration (Strictly Separated from Holdout)**: Empirical profiling across 40 frozen balanced semiprimes (10 per size: 60, 70, 80, 90 decimal digits) from deterministic master seed `NSB-R3-CALIBRATION-CORPUS-20260904-V001` (`manifest.json` public SHA: `9d32b59b...`, sealed SHA: `da5cae95...`). Executed with single thread, $q_{\text{start}}=q_{\min}$, $q_{\text{range}}=\text{qrange}$, and full profile capture under pinned CADO profiles (`c60_pinned`, `c70_pinned`, `c80_pinned`, `c90_pinned`). Canonical discrete stage execution timeout is frozen at 600.0 seconds per binary; exceeding timeout is a fail-closed calibration failure, not an operator tunable. Fail-closed cohort policy: any single instance failure invalidates the cohort; no partial results become baseline. Establishes the historical performance distribution anchor ($p_{10}, p_{50}, p_{90}$ via linear interpolation, plus raw observations, min, median, max, mean, std) frozen in `config/baselines/cado_nfs_calibration.json`. Operational Status: **CERTIFIED PASS**.
- **Candidate Evaluation Contamination Rule**: Candidate comparison claims strictly require an out-of-sample fresh preregistered holdout corpus with at least one larger size ($>90$ digits) not used during calibration. Status: **HOLD**.

