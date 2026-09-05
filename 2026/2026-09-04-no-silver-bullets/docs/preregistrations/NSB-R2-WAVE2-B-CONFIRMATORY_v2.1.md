# Preregistration Protocol Amendment v2.1: NSB-R2-WAVE2-B-CONFIRMATORY

**Contract ID**: `NSB-R2-WAVE2-B-CONFIRMATORY`  
**Protocol Version**: `2.1 (Amendment 1: Pre-Run Methodological Audit Amendments)`  
**Date**: 2026-09-04  
**Primary Track**: Track B (Evolved Algebraic Representations)  
**Status**: `FROZEN / SUPERSEDES v2.0 / ZERO COMPUTE SPENT`  

---

## 1. Audit Context & Amendment Rationale

Following the initial v2.0 preregistration, an independent pre-run methodological audit identified critical scientific vulnerabilities prior to compute allocation:
1. **Corpus Factor Collisions**: In the v2.0 generated corpus, independent prime sampling without global factor deduplication caused shared-factor collisions across moduli (`R-032-00001` & `R-032-00014` shared 59207; `R-032-00005` & `R-032-00010` shared 60703). This violated the independence of instances and rendered four moduli factorable via pairwise GCD.
2. **Unenforced Paired t-Test**: While both Wilcoxon and paired $t$-test thresholds were preregistered, `PromotionJudge` evaluated only Wilcoxon, leaving the parametric gate unverified.
3. **Unfrozen Candidate Search**: The evolved representation search algorithm, search budget, rotation operators, and Wave 2 runner were not committed prior to corpus exposure.
4. **SOTA Claim Inflation Risk**: Benchmarking against an in-house proxy cannot certify outperforming production CADO-NFS.
5. **Scaling Overclaim Risk**: Point-estimate slope $\hat{\beta} \ge 0$ across two bit sizes cannot certify asymptotic scaling.
6. **Synthetic Zero Imputation**: Imputing zeroes for unobserved instances manufactures synthetic data.

Amendment v2.1 completely resolves each of these vulnerabilities while preserving zero experimental compute spent.

---

## 2. 150-Modulus Benchmark Corpus Specification (v2.1)

- **Benchmark Version**: `v002_wave2`
- **Dataset Split**: `confirmatory`
- **Master Generation Seed**: `20260904`
- **Global Unique Prime Registry**: Primes $p, q$ are tracked in a global registry across all 150 instances. Any prime previously drawn is rejected.
- **Mechanical Pairwise Coprimality Assertion**: After generation, the corpus generation pipeline mechanically computes all $\binom{150}{2} = 11,175$ pairwise greatest common divisors and asserts:
  $$\forall i \ne j, \quad \gcd(N_i, N_j) = 1$$
- **Cohort Composition**: Exactly 30 pairwise-coprime balanced semiprimes (Family R) per bit size across 32, 48, 64, 80, and 96 bits (150 total moduli).
- **Isolation & Provenance**: Public instances and sealed ground truth stored with active tripwire canary and published SHA-256 digests.

---

## 3. Frozen Candidate Search Algorithm (`FrozenSearchOptimizer`)

To eliminate researcher degrees of freedom after corpus exposure, the candidate search algorithm is frozen in [`src/nsb/tracks/algebraic_evolution/search.py`](file:///c:/Users/admir/Github/no-silver-bullets/src/nsb/tracks/algebraic_evolution/search.py):
- **Base Expansion**: Canonical base-$m$ expansion of $N$ at degree $d=3$.
- **Translation Neighborhood**: $m' = m + k$ for $k \in \{-5, \dots, 5\}$.
- **Linear Rotation Neighborhood**:
  $$f_1(x) \to f_1(x) + (u \cdot x + v)(x - m)$$
  with $(u, v) \in \{-2, \dots, 2\}^2$.
- **Invariants**: $f_1(m) \equiv 0 \pmod N$, $f_2(x) = x - m$, $f_1$ primitive.
- **Selection Objective**: Joint minimization of Level B1 logarithmic norm and Murphy $\alpha$.
- **Evaluation Budget**: Fixed 50 candidate pairs per modulus.
- **RNG Seed**: Modulus-derived deterministic seed `(hash(N) ^ 20260904) & 0xFFFFFFFF`.

---

## 4. Hierarchy of Claims & Anti-Inflation Promotion Gates (v2.1)

PromotionJudge evaluates four distinct claim tiers in strict sequence:

### Tier 1: Replication Claim
- **Hypothesis**: The cubic base-$m$ sieve yield advantage over quadratic base-$m$ generalizes across independent moduli.
- **Candidate**: Canonical base-$m$ ($d=3$).
- **Baseline**: Canonical base-$m$ ($d=2$).
- **Preregistered Gates** (Mechanically Enforced):
  - $n = 30$ independent moduli per bit size.
  - Mean paired yield difference $\bar{\Delta} > 0$.
  - Modulus win rate $W \ge 0.70$ (at least 21 of 30 moduli).
  - **Wilcoxon signed-rank test**: $p_{\text{wilcoxon}} \le 0.01$.
  - **Paired Student-$t$ test**: $p_t \le 0.01$.
- **Target Verdict**: **`REPLICATION_CERTIFIED`** (confers replication status only).

### Tier 2: Representation-Search Claim
- **Hypothesis**: `FrozenSearchOptimizer` representations outperform unoptimized canonical base-$m$ at the same degree.
- **Candidate**: `FrozenSearchOptimizer` candidate ($d=3$).
- **Baseline**: Canonical base-$m$ ($d=3$).
- **Preregistered Gates**:
  - Paired yield gain $\ge 1.15\times$ ($15\%$ advantage over unoptimized base-$m$).
  - Modulus-level Wilcoxon signed-rank test $p \le 0.01$.
  - Logarithmic norm ratio $\le 0.95$.
- **Target Verdict**: **`SEARCH_ADVANTAGE_CERTIFIED`**.

### Tier 3: In-House Polyselect Proxy Claim
- **Hypothesis**: Candidate representations outperform in-house size/root-optimized polynomial selection.
- **Baseline**: Deterministic in-house rotation/translation/skew optimizer scored by Murphy $E$.
- **Explicit Scoping**: Beating this in-house proxy **does NOT certify beating CADO-NFS or state-of-the-art**.
- **Preregistered Gates**:
  - Murphy $E$ score ratio $\ge 1.00$.
  - Core throughput ratio $\ge 1.00$ relations per core-second.
  - Wilcoxon signed-rank test $p \le 0.01$.
- **Target Verdict**: **`IN_HOUSE_POLYSELECT_PROXY_BEATEN`** (Claiming SOTA is forbidden).

### Tier 4: Scaling Persistence Claim
- **Hypothesis**: The empirical advantage does not decay as modulus bit length increases from 32b to 96b.
- **Explicit Scoping**: Finite bit sizes cannot certify asymptotic complexity.
- **Preregistered Gates**:
  - Evaluated on at least 4 of 5 bit sizes ($\ge 4$ sizes required).
  - Ordinary least squares regression of mean paired yield ratio vs modulus bit size.
  - One-sided non-inferiority: 95% Student-$t$ confidence interval lower bound on slope $\beta_{\text{lower}} \ge 0.0$.
- **Target Verdict**: **`SCALING_PERSISTENCE_CERTIFIED`**.

---

## 5. Execution Integrity & Throughput Accounting

- **True Core-Seconds**: Throughput is measured using process CPU time via `time.process_time()`, computing relations per core-second ($\Theta = k / t_{\text{cpu}}$) to eliminate wall-clock scheduling jitter.
- **No Manufactured Zeroes**: All 30 moduli per cohort are executed in full. If a cohort yields 0 smooth relations across all 30 moduli, it is recorded as `ZERO_YIELD_FLOOR` without artificial imputation.
- **Timeouts**: 5.0 seconds CPU time per representation per modulus; 300.0 seconds per 30-modulus cohort; 1800.0 seconds total wall time ceiling.
