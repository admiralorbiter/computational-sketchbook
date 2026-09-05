# 00 — Program Charter

## 1. Research Thesis

Factoring research has repeatedly advanced by changing the representation of the problem rather than by making blind divisor search faster. This program therefore explores representation changes and search over representations.

The central hypothesis is deliberately broad:

> *Modern computational techniques may make previously impractical mathematical representations useful, or may allow automated discovery of representations and heuristics that human-designed pipelines have not searched densely.*

The program is agnostic about which mechanism succeeds.

---

## 2. Four Independent Hypotheses

* **H-A — Tensor/Lattice**: A Schnorr-style lattice construction may produce useful factoring relations at a better practical rate if the “find nearby/low-energy candidates” stage is replaced or augmented by modern structured sampling.
* **H-B — Algebraic Evolution**: For a fixed semiprime $N$, automated search may discover algebraic representations whose smoothness yield or downstream relation rate exceeds conventional hand-designed selection heuristics enough to matter.
* **H-C — Partial Information**: There may exist efficiently computable features of $N$ that do not directly reveal a factor but constrain one factor strongly enough that lattice/small-root methods can finish.
* **H-D — Constraint Graph**: The hardness of direct SAT/CSP inversion may be dominated by a poor encoding of multiplication. Alternative arithmetic representations may reduce effective dependency width enough to produce a different empirical scaling curve.

---

## 3. What Counts as Evidence

Evidence is tiered:

* **Tier E0 — Plumbing**: The code runs and produces schema-valid output.
* **Tier E1 — Exact Local Success**: A method factors or recovers a known small synthetic case under sealed conditions.
* **Tier E2 — Comparative Improvement**: Across a preregistered distribution of inputs, the method improves a canonical metric relative to its baseline.
* **Tier E3 — Scaling Improvement**: The improvement persists across increasing bit sizes and is visible in the fitted scaling model, not merely at one size.
* **Tier E4 — Independent Replication**: A clean environment reproduces the result from the frozen commit and manifest.
* **Tier E5 — External Claim**: Reserved for results strong enough to communicate publicly. Requires human review and independent verification.

---

## 4. Design Principle: Hidden Truth, Visible Metrics

Every synthetic modulus is generated from hidden primes $p$ and $q$.

Research-track code receives only:
* $N$;
* Public benchmark metadata that is explicitly allowed;
* Its own configuration.

The evaluator/verifier may access $p$ and $q$ only after the candidate output is frozen. This enables scoring partial-information methods without leaking the answer into the search process.

---

## 5. Primary Scientific Metrics

The project records raw outcomes and derives:
* Factorization success rate;
* Wall-clock and CPU time;
* Peak memory;
* Candidate evaluations;
* Useful relation yield and unique relation yield;
* Smoothness probability;
* Solver conflicts/decisions where applicable;
* Lattice dimensions and reduction effort;
* Tensor contraction/sampling effort where applicable;
* Partial-information accuracy and information gain;
* Downstream recovery success;
* Empirical scaling parameters.

*No track may substitute its preferred proxy for the program-level success metric.*

---

## 6. Benchmark Principle

Every “promising” result must survive:
1. Development set;
2. Seeded validation set;
3. Hidden holdout set.

The Research Director can see development metrics. It cannot see hidden factors or hidden holdout answers.

---

## 7. Research Strategy

The program intentionally uses a scattershot $\to$ feedback $\to$ selection cycle:
1. Generate many cheap variants;
2. Reject aggressively;
3. Promote a small frontier;
4. Spend meaningful compute only on the frontier;
5. Periodically inject fresh random variants to avoid premature convergence.

This is more appropriate than one long sequential idea-review loop because most hypotheses are expected to fail.

---

## 8. Program-Level Stopping Rules

Pause the entire program if:
* Verifier integrity fails;
* Benchmark leakage is detected;
* Repeated “improvements” disappear on hidden holdout;
* Resource accounting becomes unreliable;
* The AI director modifies frozen scientific contracts;
* A long run cannot be resumed deterministically.

*The appropriate response to a negative result is documentation, not goalpost movement.*
