# 04 — Common Experiment Protocol

## 1. Experiment Lifecycle

1. **Hypothesis**: Formulate a single, falsifiable claim predicting a measurable outcome.
2. **Immutable Manifest**: Freeze method, parameters, benchmark split, canonical metrics, budget, stopping rules, and promotion rules.
3. **Canary (Gate 0)**: Run minimal cases to prove plumbing, schema validity, and positive/negative controls.
4. **Pilot (Gate 1)**: Run comparative experiments across multiple sizes and seeds against baseline.
5. **Canonical Verification**: Compute deterministic metrics; no track-specific code judges scientific truth.
6. **Audit**: Verify absence of leakage, benchmark integrity, timeout accounting, and absence of cherry-picking.
7. **Verdict**: Assign `PROMOTED`, `REJECTED`, `INCONCLUSIVE`, or `ESCALATED`.

---

## 2. Required Baselines

Every experiment must declare an explicit baseline:
* **Track A**: Babai-only or published neighborhood sampler.
* **Track B**: Conventional polynomial-selection baseline or prior champion generator.
* **Track C**: Zero-information baseline plus calibrated oracle controls.
* **Track D**: Schoolbook multiplication SAT encoding with a pinned solver.

---

## 3. Metrics Hierarchy

* **Primary**: Track-specific metric declared prior to execution.
* **Secondary**: Performance and mechanistic diagnostics.
* **Final**: Exact factor recovery and empirical scaling.

*A candidate cannot be promoted solely on proxy metrics if downstream metrics degrade.*

---

## 4. Scaling Analysis & Timeouts

* Fit multiple empirical models (log-linear, polynomial, exponential) across the bit-size range.
* Report uncertainty intervals, residuals, and sensitivity to small sizes.
* Use precise terminology: *“empirical scaling over tested range”*, never claiming unproved asymptotic complexity.
* **Timeouts are data**: Retain all censored runtimes and partial progress; never drop timeouts from analysis.

---

## 5. Promotion Rule Template

Promote only if all conditions hold:
1. Canary passed;
2. No leakage or audit violations;
3. Primary metric exceeds baseline by preregistered margin;
4. Improvement reproduces on validation data, not merely development;
5. Downstream success does not degrade;
6. Effect persists across multiple adjacent bit sizes;
7. Resource costs remain within declared caps.

---

## 6. Exact Factor Verification

When factor candidates $p', q'$ are returned:
* Normalize order ($p' \le q'$);
* Verify integer domain ($p', q' \in \mathbb{Z}$);
* Verify exact product: $p' \cdot q' == N$;
* Verify non-triviality: $1 < p', q' < N$;
* Verify primality where required.
