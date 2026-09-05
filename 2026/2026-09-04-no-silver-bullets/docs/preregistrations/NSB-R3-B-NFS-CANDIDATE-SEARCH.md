# Preregistered Protocol: NSB-R3-B-NFS-CANDIDATE-SEARCH
## Track B Candidate Interface, Search Budget, and Promotion Governance

**Protocol ID**: `NSB-R3-B-NFS-CANDIDATE-SEARCH`  
**Version**: `1.0.0`  
**Track**: `Track B (Algebraic Evolution & Realistic NFS Polynomial Selection)`  
**Baseline Reference**: `NSB-R3-B-NFS-BASELINE-FOUNDATION` (v1.3.0 Certified)  
**Baseline Framework**: `CADO-NFS` (Pinned Commit: `73ca6b6847118b05b15eeec27c86f45cef82a19e`)  
**Execution Environment**: `Native Linux (WSL2 Ubuntu 24.04 LTS) only`  

---

## 1. Scientific Objective & Scope

With `NSB-R3-B-NFS-BASELINE-FOUNDATION` certified across G0, G1, G2, and G3, the baseline is immutable.
Protocol `NSB-R3-B-NFS-CANDIDATE-SEARCH` governs the transition to candidate research under strict intervention isolation:
$$\text{Can a novel representation-selection candidate achieve reproducible yield and efficiency advantages against CADO under identical compute budgets?}$$

---

## 2. Candidate Interface Protocol

The candidate algorithm implements the `NfsCandidateSelector` protocol:
```python
def select(
    N: int,
    profile: CadoParameterProfile,
    budget: SearchBudget,
    seed: int,
) -> CandidateOutput:
    ...
```

### Input Isolation
The candidate receives strictly:
1. Composite integer $N$.
2. Target pinned parameter profile (`profile`).
3. Execution search budget (`budget`).
4. Master pseudo-random seed (`seed`).

The candidate is strictly prohibited from receiving:
- The baseline polynomial for that modulus.
- Baseline Murphy-$E$ score or relation yield.
- Factors $p$ or $q$.
- Holdout evaluation data.
- Downstream LAS sieving feedback during claim-bearing search.

### Output Constraints
The returned `NfsPolynomialPair` must satisfy:
1. $pair.N == N$ (exact modulus match).
2. $pair.degree1 == profile.degree$ (algebraic degree match).
3. $pair.degree2 == 1$ (linear rational side).
4. Content coprimality on both sides.
5. $f_1(m) \equiv f_2(m) \equiv 0 \pmod N$ and $\text{Res}(f_1, f_2) \equiv 0 \pmod N$ verified independently via Bareiss algorithm.

---

## 3. Intervention Levels & Cost Accounting

Candidates declare one of three intervention levels:
1. `full_selector`: Candidate performs the entire polynomial search pipeline. Charged for full candidate search CPU.
2. `stage1_generator`: Candidate generates a raw candidate pool; fixed CADO `polyselect_ropt` is executed by the test harness. Charged: $T_{\text{total}} = T_{\text{candidate\_generator}} + T_{\text{harness\_ropt}}$.
3. `post_ropt_ranker`: Fixed CADO stage 1 + ropt generates candidate pool; candidate reranks them. Charged: $T_{\text{total}} = T_{\text{harness\_pool\_gen}} + T_{\text{candidate\_ranker}}$.

---

## 4. Kernel-Level cgroup v2 Budget Enforcement

Execution is contained in a dedicated cgroup v2 (`/sys/fs/cgroup/nsb/<run_id>`):
- **Budget Rule**: $\text{Budget} = 1.00 \times \text{baseline selection CPU}$ for the paired modulus and profile.
- **Cumulative CPU Accounting**: Read directly from kernel `cpu.stat` (`usage_usec`), capturing all processes and short-lived child forks.
- **Atomic Termination**: If cumulative CPU exceeds the budget or wall time exceeds 600s, `cgroup.kill` terminates the entire tree immediately.
- **Overshoot Enforcement**: Final CPU is sampled post-termination. Any execution whose final CPU exceeds the budget is rejected with `BUDGET_EXCEEDED_REJECTED`.
- **Resource Constraints**:
  - Memory: `memory.max = 4096 MB`.
  - Concurrency: `taskset -c 0` (strictly 1 CPU core).
  - Network: Linux network namespace (`unshare -n`).
  - GPU: Stripped environment (`CUDA_VISIBLE_DEVICES=""`).

---

## 5. Promotion Hierarchy & Executable Criteria

Evaluation requires paired comparison over frozen holdout moduli.

### Tier 1: Polynomial Quality Advantage
- **Primary Estimand**: Paired unique valid relation count ratio $R_i = \frac{Y_C(N_i)}{Y_B(N_i)}$ on identical special-$q$ interval $[q_{\min}, q_{\min} + q_{\text{range}}]$.
- **Threshold 1A**: Sample geometric mean ratio $\ge 1.10$ ($+10\%$ yield).
- **Threshold 1B**: Paired 95% bootstrap confidence interval lower bound $> 1.00$ (`scipy.stats.bootstrap(method='percentile', n_resamples=10000, random_state=42)`).
- **Threshold 1C**: Positive median paired difference $(Y_C - Y_B > 0)$ within **each** size cohort (evaluated separately at 95d and 100d).

### Tier 2: System Efficiency Advantage
- **Metric**: Total core-seconds per valid relation:
  $$\text{Cost} = \frac{T_{\text{selection}} + T_{\text{setup}} + T_{\text{sieve}}}{\text{unique valid relations}}$$
- **Threshold 2A**: Paired cost reduction $\ge 5\%$ (mean cost ratio $\le 0.95$).
- **Threshold 2B**: Paired 95% bootstrap confidence interval upper bound $< 1.00$.

### Decision Rules
- `R3_CANDIDATE_PROMOTED`: Passes both Tier 1 and Tier 2.
- `QUALITY_ADVANTAGE_ONLY`: Passes Tier 1 only.
- `SYSTEM_ADVANTAGE_ONLY`: Passes Tier 2 only.
- `PROMOTION_REJECTED`: Fails both tiers.
- **Penalty Rule**: Any failed or timed-out run receives $Y_C = 0$ and $\text{Cost}_C = 100 \times \text{Cost}_B$.

---

## 6. Future Holdout Protocol Specification (SPEC ONLY)

- **Ladder**: 95 decimal digits (~315 bits, profile `c95_pinned`) and 100 decimal digits (~332 bits, profile `c100_pinned`).
- **Sample Size**: 10 moduli per size (20 instances total).
- **Deterministic Master Seed Derivation**:
  $$\text{master\_seed} = \texttt{"NSB-R3-HOLDOUT-"} + \text{SHA256}(\text{candidate\_freeze\_commit\_sha})[:16].\text{upper}()$$
- **Status**: **`STRICT HOLD`**. Zero holdout numbers will be generated until candidate code and weights are frozen and committed.
- **Candidate Registry**: Every candidate evaluated on holdout is recorded to prevent selective reporting.
