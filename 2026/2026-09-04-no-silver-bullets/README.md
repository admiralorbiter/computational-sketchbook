# No Silver Bullets (NFS Candidate Search & Selection)

**Final Status:** Parked / Archived. *"Unresolved; no demonstrated advantage within budget."*

---

## 1. The Core Research Question

> **Does the CADO-NFS polynomial candidate pool contain enough overlooked quality to make an external candidate selection rule worth developing within the baseline CPU search budget?**

In the Number Field Sieve (NFS) for integer factorization, polynomial selection has a major impact on sieving yield. CADO-NFS selects polynomials by optimizing size and root properties via `polyselect` and `polyselect_ropt`. This project investigated whether machine-learning or heuristic rerankers could discover higher-yielding polynomials within CADO's candidate pool under a paired compute budget ($1.00\times$ baseline polyselect CPU).

---

## 2. What Was Built

- **CADO-NFS Baseline Harness (`src/nsb/baselines/cado_nfs/`):**
  - Full programmatic wrapper for CADO-NFS binaries (`polyselect`, `polyselect_ropt`, `makefb`, `freerel`, `las`).
  - Pinned parameter profiles for 60d, 70d, 80d, and 90d moduli based on production CADO params.
  - Strict mathematical verifiers ensuring algebraic norms, common roots, and relation conservation.
- **Sandboxed Execution & Resource Accounting (`src/nsb/runners/`):**
  - Robust supervisor isolating candidate workers via Linux cgroups v2 (`cpu.stat`, `memory.current`).
  - Linux namespace isolation (`CLONE_NEWNET`, separate IPC and process groups) to eliminate credential leakage.
  - Fail-closed initial CPU read accounting and watchdog process-group termination.
- **Calibrated Corpus & Benchmark Manifest (`benchmarks/public/`):**
  - 40 RSA-style composite integers across 60d, 70d, 80d, and 90d cohorts with frozen baseline execution records.
- **Hindsight Oracle Study (`scratch/run_hindsight_study.py`, `scratch/hindsight_oracle_results.json`):**
  - Evaluated every surviving polynomial candidate in the pool for 12 public calibration instances across 60d–90d using identical standardized test sieves.

---

## 3. What Was Learned & Methodological Lessons

This project provides a textbook specimen in experimental computer science and empirical methodology:

1. **Passing Tests $\neq$ Measuring the Phenomenon $\neq$ Supporting the Conclusion:**
   - A preliminary candidate selection rule passed all 204 unit and integration tests and reported a $+7.10\%$ throughput advantage over "CADO default".
   - Upon forensic review, the script had assigned `cado_default = pool[0]`, assuming `pool[0]` was CADO's selection. In reality, `generate_stage1_pool` returned candidates in arbitrary stdout order.
   - CADO's true baseline already selects the maximum Murphy-$E$ candidate (`is_best`). When evaluated against the actual baseline, the "pure Murphy-$E$" advantage was exactly $+0.00\%$.
2. **Throughput Oracles Are Not Relation-Count Ceilings:**
   - Defining the hindsight oracle as maximizing instantaneous sieving rate ($\text{rel}/\text{s}$) led to selecting polynomials that processed fewer total relations over the fixed test interval ($+3.86\%$ average relation delta).
   - Evaluating a true **Maximum-Relation Oracle** directly from the raw pool reveals a $+13.32\%$ mean relation-count headroom (with instances reaching $+40.20\%$ at 60d and $+48.76\%$ at 90d).
3. **Contractual Full-Pipeline Accounting:**
   - Sieve-only CPU per relation (e.g. $1{,}013.6\ \mu\text{s}/\text{rel}$) drastically underestimates true cost if selection CPU is omitted. On short calibration slices, selection CPU ($32.13\text{ s}$) accounts for over $90\%$ of total CPU ($10{,}366.8\ \mu\text{s}/\text{rel}$ total).
   - Measuring true efficiency requires amortizing selection cost over full-scale sieving runs.
4. **Zero-Tolerance Budget Contraction:**
   - Under a strict $1.00\times$ paired CPU budget with zero tolerance margin, ordinary inter-run Linux process and hypervisor scheduling jitter caused pool generation alone to fail budget compliance ($102\%\text{--}108\%$ of paired budget at 70d–90d).

---

## 4. Withdrawn Claims & Unresolved Discrepancies

- **Withdrawn:** The preliminary claim of $+7.10\%$ gain from a Murphy-$E$ reranker is withdrawn (artifact of unranked `pool[0]` comparison).
- **Withdrawn:** The claim of an unconditional $+13.06\%$ throughput headroom over baseline is withdrawn; true throughput headroom over the verified baseline is $+5.68\%$.
- **Unresolved:** The exact full-pipeline relation yield and efficiency curve across complete, non-truncated sieve intervals remains unmeasured.
- **Unresolved:** Whether an alternative candidate generator can produce a viable multi-candidate pool strictly under $1.00\times$ CPU without violating budget margins remains unproven.

---

## 5. Why Work Stopped & Reopening Criteria

- **Stopping Rationale:** No advantage within the contractual search budget was demonstrated. Continuing to tweak post-ropt heuristics or debug execution jitter without a grounded mathematical hypothesis would consume research hours without yielding a factoring breakthrough.
- **Reopening Criteria:** Reopen only if:
  1. A specific new mathematical hypothesis regarding size-search parameter interaction is formulated.
  2. A concrete downstream need emerges to reuse the hardened CADO runner and cgroup supervisor in another factoring project.
