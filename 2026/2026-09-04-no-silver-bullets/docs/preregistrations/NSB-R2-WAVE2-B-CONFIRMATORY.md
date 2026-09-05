# Preregistration Protocol: NSB-R2-WAVE2-B-CONFIRMATORY

**Contract ID**: `NSB-R2-WAVE2-B-CONFIRMATORY`  
**Protocol Version**: `2.0 (Frozen Preregistration)`  
**Date**: 2026-09-04  
**Primary Track**: Track B (Evolved Algebraic Representations)  
**Status**: `FROZEN / READY FOR CONFIRMATORY EXECUTION`  

---

## 1. Scientific Context & Motivation

In R1 Wave 1 research (`NSB-R1-WAVE1-SEARCH`), Track B demonstrated a large downstream sieve yield advantage when evaluating a degree-3 base-$m$ polynomial representation against a degree-2 baseline ($52/311$ vs $3/311$ smooth relations on a 32-bit modulus, $17.33\times$ gain, pooled sieve-point McNemar $p = 4.29 \times 10^{-13}$).

However, external methodological audit identified critical scientific vulnerabilities:
1. **Under-Replication**: The R1 pilot was evaluated on only 1 modulus per bit size. A single modulus cannot establish that an algebraic advantage generalizes across the general distribution of balanced semiprimes.
2. **Unit of Analysis**: The extremely low $p$-value was computed across pseudo-replicated sieve points $(a, b)$ on the same modulus. The true independent experimental unit is the **integer modulus $N_i$**.
3. **Baseline Ambiguity**: Canonical base-$m$ degree-2 is a minimal baseline. Conventional Number Field Sieve implementations (e.g. Kleinjung, Murphy, CADO-NFS) employ sophisticated polynomial selection optimizing Murphy's $\alpha$, root properties, and optimal skew.
4. **Risk of Claim Inflation**: Without a strict hierarchy of claims, evidence supporting basic degree replication could be conflated with a claim of outperforming state-of-the-art polynomial selection or asymptotic scaling.

This preregistration protocol eliminates these vulnerabilities by freezing the 150-modulus corpus, the modulus-level paired statistical framework, and a 4-tier anti-inflation claim hierarchy prior to executing the confirmatory sieve.

---

## 2. 150-Modulus Benchmark Corpus Specification

- **Benchmark Version**: `v002_wave2`
- **Dataset Split**: `confirmatory`
- **Master Generation Seed**: `20260904`
- **Instance Generator**: Deterministic Family R (balanced random semiprime generator):
  - Balanced primes: $p \in [2^{b/2 - 1}, 2^{b/2}]$, $q \in [2^{b - b/2 - 1}, 2^{b - b/2}]$ with $p < q$.
  - Minimum factor separation: $q - p > 2^{b/2 - 10}$ to exclude Fermat-trivial moduli.
  - Verification: $\text{bit\_length}(p \cdot q) == b$ and Miller-Rabin primality test (25 rounds).
- **Cohort Composition**: Exactly 30 independent instances for each of 5 bit sizes (150 instances total):
  - 32 bits: `R-032-00001` through `R-032-00030`
  - 48 bits: `R-048-00001` through `R-048-00030`
  - 64 bits: `R-064-00001` through `R-064-00030`
  - 80 bits: `R-080-00001` through `R-080-00030`
  - 96 bits: `R-096-00001` through `R-096-00030`
- **Provenance Safeguards**:
  - Sealed truth containing $(p, q)$ stored in `benchmarks/sealed/v002_wave2/confirmatory/` behind an active tripwire canary file (`TRIPWIRE_DO_NOT_READ.txt`).
  - Public instances stored in `benchmarks/public/v002_wave2/confirmatory/instances.jsonl`.
  - Manifest file recording canonical SHA-256 digests.

---

## 3. Hierarchy of Claims & Anti-Inflation Gates

`PromotionJudge` evaluates four distinct claim tiers in strict sequence. Evidence at lower tiers cannot certify higher-tier claims.

### Tier 1: Replication Claim
- **Hypothesis**: The cubic base-$m$ downstream sieve yield advantage over quadratic base-$m$ generalizes across independent moduli.
- **Candidate**: Canonical base-$m$ ($d=3$).
- **Baseline**: Canonical base-$m$ ($d=2$).
- **Primary Adjudication Statistic**: Modulus-level paired yield difference $\Delta_i = Y_3(N_i) - Y_2(N_i)$.
- **Preregistered Thresholds**:
  - Sample size: $n = 30$ independent moduli per bit size.
  - Mean paired effect: $\bar{\Delta} > 0$.
  - Modulus win rate: $W = \frac{1}{30} \sum \mathbb{I}(\Delta_i > 0) \ge 0.70$ (at least 21 of 30 moduli).
  - Wilcoxon signed-rank test across moduli: $p_{\text{wilcoxon}} < 0.01$.
  - Paired Student-$t$ test across moduli: $p_t < 0.01$.
  - Within-modulus McNemar contingency table reported strictly as an intra-modulus diagnostic.

### Tier 2: Representation-Search Claim
- **Hypothesis**: Evolved or search-selected representations outperform unoptimized canonical base-$m$ at the same degree.
- **Candidate**: Search-optimized polynomial pair ($d=3$, rotation/translation/skew).
- **Baseline**: Canonical base-$m$ ($d=3$).
- **Preregistered Thresholds**:
  - Modulus-level paired yield gain $\ge 1.15\times$ ($15\%$ advantage over unoptimized base-$m$).
  - Modulus-level Wilcoxon signed-rank test $p < 0.01$.
  - Logarithmic norm ratio $\le 0.95$.

### Tier 3: SOTA Benchmark Claim
- **Hypothesis**: Candidate representations outperform standard Number Field Sieve polynomial selection.
- **Baseline Definition (Kleinjung/Murphy/CADO-NFS Standard)**:
  - Polynomial pair maximizing Murphy's $E(f_1, f_2)$ rating.
  - Optimal skew $s = \sqrt{\frac{\|f_1\|_2}{\|f_2\|_2}}$.
  - Root property optimization: Murphy's $\alpha(f) = \sum_{p \le B} (\frac{1}{p-1} - \frac{n_p}{p+1}) \frac{\log p}{p}$ with prime bound $B = 2000$.
  - Translation and coefficient rotation search around base-$m$.
- **Candidate**: Search-optimized polynomial pair.
- **Preregistered Thresholds**:
  - Murphy's $E$ rating ratio: $E_{\text{cand}} / E_{\text{SOTA}} \ge 1.00$.
  - Empirical relation throughput ratio: $\Theta_{\text{cand}} / \Theta_{\text{SOTA}} \ge 1.00$ relations per core-second.
  - Modulus-level Wilcoxon signed-rank test $p < 0.01$.

### Tier 4: Asymptotic Scaling Claim
- **Hypothesis**: The empirical advantage does not decay as modulus bit length increases.
- **Preregistered Thresholds**:
  - Evaluated across all bit sizes with non-zero relation yield (at least 2 sizes required).
  - Ordinary least squares regression of mean paired yield ratio vs modulus bit length: slope $\beta_{\text{bits}} \ge 0.0$.

---

## 4. Experimental Sieve Parameters & Search Space

- **Polynomial Degrees**: $d \in \{2, 3, 4, 5, 6\}$.
- **Homogeneous Sieve Region**: Coprime integer pairs $(a, b)$ with $a \in [-100, 100]$, $b \in [1, 20]$, $\gcd(|a|, b) = 1$ ($\approx 2550$ test points per modulus).
- **Factor Base**: Primes $p \le 250$ (53 primes).
- **Murphy $\alpha$ Prime Bound**: Primes $p \le 2000$ (303 primes).

---

## 5. Compute Budget & Stopping Rules

- **Per-Modulus Timeout**: 5.0 seconds CPU time per representation.
- **Per-Cohort Timeout**: 300.0 seconds total per 30-modulus bit-size cohort.
- **Total Wave Wall-Clock Ceiling**: 1800.0 seconds (30 minutes).
- **Memory Ceiling**: 2048 MB RSS.
- **Zero-Yield Stopping Rule**: If 10 consecutive moduli at bit size $K$ produce 0 smooth relations for both baseline and candidate, the remainder of size $K$ is recorded as zero-yield floor to conserve compute.
