# 11 — Pilot, Long Run, Promotion, and Stopping

## 1. Gate 1 Pilot

After canary success, each track executes a bounded pilot to evaluate scaling trends across multiple bit lengths (e.g. 64 to 96/128 bits) with matched compute budgets.

---

## 2. Wave Execution Model

Long-running search is structured into discrete, immutable waves:
* **Wave 0**: Baselines and reproduction.
* **Wave 1**: Broad cheap variants across tracks.
* **Wave 2**: Replication and local mutation of promising lines.
* **Wave 3**: Bit-size ladder escalation for Pareto frontier only.
* **Wave 4**: Hidden holdout evaluation.
* **Wave 5**: Independent reproduction.

---

## 3. Early Stopping & Track Suspension

* **Candidate Killing**: Dominated by baseline, shrinking advantage across 3 sizes, or budget exhausted without valid candidate.
* **Track Suspension**: Suspend track when exploration budget yields no competitive branch or scaling worsens. Document conditions required to justify reopening.

---

## 4. Breakthrough Protocol

If a candidate unexpectedly factors a significantly larger balanced modulus:
1. Freeze process immediately;
2. Hash all artifacts and environment state;
3. Block director mutations;
4. Independently verify factors, products, and primality;
5. Repeat from clean process on unseen fresh moduli;
6. Audit for inadvertent leakage or benchmark contamination;
7. Only then prepare an escalation packet for human review.
