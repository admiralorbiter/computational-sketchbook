# 02 — System Architecture

## 1. Architectural Goal

The architecture must support thousands of failed experiments without turning the repository into an untraceable pile of scripts.

The core is a deterministic experiment engine wrapped by a bounded autonomous proposal loop.

---

## 2. Component Topology

```text
                           HUMAN
                             |
                     moonshot / limits
                             |
                      +--------------+
                      |   CONTRACT   |
                      +--------------+
                             |
                 +-----------------------+
                 |   RESEARCH DIRECTOR   |
                 | proposal + selection  |
                 +-----------------------+
                    |        |        |
                 proposal  proposal  proposal
                    v        v        v
               +---------------------------+
               | IMMUTABLE EXPERIMENT SPEC |
               +---------------------------+
                             |
                           RUNNER
                             |
              +--------------+--------------+
              |                             |
          TRACK CODE                    BASELINES
              |                             |
              +-------------+---------------+
                            |
                         ARTIFACTS
                            |
                         VERIFIER
                            |
                     CANONICAL METRICS
                            |
                          AUDITOR
                            |
              PASS / REJECT / ESCALATE
                            |
                   append-only ledger
```

---

## 3. Experiment Identity

Every experiment receives a unique identifier:
`NSB-<TRACK>-<YYYYMMDD>-<6char>` (e.g., `NSB-B-20260903-A17F2C`).

The immutable manifest includes:
* Experiment ID;
* Parent experiment ID;
* Track identifier;
* Hypothesis;
* Git commit hash;
* Config SHA-256 hash;
* Benchmark version & dataset split;
* Random seed(s);
* Environment fingerprint;
* Resource caps (wall time, CPU time, memory);
* Allowed inputs;
* Expected output schema;
* Stopping and promotion rules.

---

## 4. Execution State Machine

Operational runtime states:
`IDLE` $\to$ `READY` $\to$ `RUNNING` $\to$ `VERIFYING` $\to$ `AUDITING` $\to$ `COMPLETE` (or `FAILED` / `ESCALATED`).

Research verdicts are separate:
* `CANDIDATE`
* `PROMOTED`
* `REJECTED`
* `INCONCLUSIVE`
* `REVISED_CONTRACT_REQUIRED`
* `ESCALATED`

*Never overload runtime execution state with scientific verdict.*

---

## 5. Storage Model

SQLite stores searchable metadata (`state/experiments.sqlite`). Raw artifacts remain immutable files on disk.

### Tables
* `experiments`: Identity, parent link, track, contract, git commit, config hash, status, verdict, timestamps.
* `runs`: Individual instance execution (run ID, instance ID, seed, bit length, exit code, wall/CPU seconds, peak RSS, timeout, artifact paths).
* `metrics`: Canonical metrics (run ID, metric name, metric value, metric unit, metric version).
* `events`: Append-only tamper-evident event log (event ID, timestamp, actor, experiment ID, event type, payload JSON, previous hash, event hash).

---

## 6. Process Isolation & Sealed Boundary

Research-track code must not directly read:
* Hidden factor files (`sealed/`);
* Hidden holdout metadata;
* Verifier outputs for the current holdout run;
* Another track's secret benchmark answers.

The runner executes track code in isolated directories with explicit input allowlists.

---

## 7. Common Interface

Each track exposes:
* `prepare(instance, config) -> prepared_artifact`
* `run(prepared_artifact, budget) -> candidate_result`
* `summarize(candidate_result) -> track_metrics`

The verifier remains strictly separate:
* `verify(instance_truth, candidate_result) -> canonical_result`

---

## 8. Determinism & Resource Governor

* **Determinism**: Fix RNG seeds, pin library versions, record hardware fingerprint, record exact invocation command, and hash all inputs and outputs.
* **Governor**: Enforce wall time, CPU time, memory, candidate count, and retry caps. Kills that exceed caps are recorded cleanly as data.
