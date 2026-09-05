# 09 — Research Director

## 1. Purpose & Authority Split

The Research Director reduces human project management load while preserving scientific control. It is a bounded experiment manager, not an authority on truth.

* **Human**: Moonshot, frozen contracts, security/scope, max compute spend, major promotion rules, external claims.
* **Director**: Proposals, parameter mutations, branch scheduling, small-budget exploration, branch kills, wave summaries, promotion nominations.
* **Verifier**: Exact arithmetic correctness, primality, canonical metrics.
* **Auditor**: Protocol integrity, leakage detection, benchmark integrity, provenance, promotion compliance.

---

## 2. Director Proposal Schema

All director proposals must be machine-readable:
```yaml
proposal_id: "PROP-D-20260903-001"
parent_experiment: "NSB-D-20260903-A01B02"
track: "D"
hypothesis: "Carry-save adder tree reduces solver conflicts by 30% on 32-bit instances"
mechanism: "Localized carry graph limits propagation depth"
mutations:
  encoding_family: "carry_save"
expected_effect: "solve_cpu_seconds <= 0.7 * baseline"
budget:
  max_wall_seconds: 60
  max_cpu_seconds: 60
  max_rss_mb: 1024
stopping_rule: "fail if canary equivalence test fails"
promotion_target: "Pilot D-P1"
novelty_reason: "First test of redundant carry representation"
```

---

## 3. Branching, Exploration & Kill Rules

* **Branch Budget**: Max 8 active experiments; max 3 children from one parent per wave.
* **Portfolio**: 70% exploit/explore-near, 20% explore-far/novel, 10% replication.
* **Kill Rules**: Auto-kill if validity failure $> 20\%$, canary fails, performance is dominated by baseline, or proxy improves while canonical metric degrades.
* **Escalation**: Escalate to human if hidden holdout crosses promotion threshold, contract change is requested, or verifier/auditor disagree.
