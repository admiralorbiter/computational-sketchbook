# Origin: No Silver Bullets (`no-silver-bullets`)

- **Original Repository:** `https://github.com/admiralorbiter/no-silver-bullets`
- **Active Research Window:** September 2026
- **Consolidated into Sketchbook:** 2026-09-04
- **Tech Stack:** Python 3.12, CADO-NFS (C/C++ binaries: `polyselect`, `polyselect_ropt`, `makefb`, `freerel`, `las`), Linux cgroups v2, unshare (`CLONE_NEWNET`), Pytest
- **Final Clean Commit on Main:** `ff87335d5eafc3c17904678037940f7a722c6f86`

---

## 1. Key Commit Lineage

| Commit SHA | Description / Gate Milestone |
| :--- | :--- |
| [`7d83282`](https://github.com/admiralorbiter/no-silver-bullets/commit/7d83282) | Freeze R3-G4 candidate interface and search budget contract |
| [`1ba7f8e`](https://github.com/admiralorbiter/no-silver-bullets/commit/1ba7f8e) | Enforce cgroup worker containment, supervisor watchdog, and strict judge validation |
| [`8e2efd3`](https://github.com/admiralorbiter/no-silver-bullets/commit/8e2efd3) | Harden worker module imports, fail-closed attachment, partial-intervention pipelines |
| [`453b541`](https://github.com/admiralorbiter/no-silver-bullets/commit/453b541) | Resolve attribute shadowing, complete boundary accounting, pool validation, deep holdouts |
| [`f5f5328`](https://github.com/admiralorbiter/no-silver-bullets/commit/f5f5328) | Enforce active helper containment, irreversible failure gating, guaranteed sandbox cleanup |
| [`6bcd412`](https://github.com/admiralorbiter/no-silver-bullets/commit/6bcd412) | Helper attachment barrier, cumulative cgroup snapshots, fail-closed unreadable CPU, file-backed IPC |
| [`ff87335`](https://github.com/admiralorbiter/no-silver-bullets/commit/ff87335) | Isolate helper environment and network namespace, fail-closed on initial CPU read |

---

## 2. Preserved Assets & Lineage Value

Even though external candidate reranking demonstrated no advantage within the budget, several assets remain directly reusable:

1. **CADO-NFS Pipeline Integration (`src/nsb/baselines/cado_nfs/`):**
   - Self-contained, robust Python interfaces wrapping CADO's polynomial selection and relation sieving.
   - Pinned parameters extracted from production CADO parameter tables (`c60` through `c90`).
2. **Mathematical Verification Suite (`verifier.py`):**
   - Independent validation of common roots $\pmod N$, coefficient norm parity, and relation conservation laws.
3. **Robust Linux Containment & Accounting Subsystem (`src/nsb/runners/`):**
   - Multi-process cgroup v2 accounting supervisor that accurately tracks subprocess trees and guarantees fail-closed termination.
4. **Empirical Case Study Dataset (`scratch/hindsight_oracle_results.json`):**
   - Complete 12-instance per-candidate evaluation data for archival study and teaching.
