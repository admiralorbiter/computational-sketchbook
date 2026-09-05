# 14 — Review Packet Specification

## 1. Purpose

After a smoke test, pilot run, or wave, the project generates a self-contained review packet enabling human review without requiring inspection of terminal logs or conversational history.

---

## 2. Required Packet Sections

1. **Executive Status**: Active contract, commit, benchmark version, wave number, total compute consumed, audit verdict (`PASS`/`FIX`/`ESCALATE`), flag indicating if human decision is required.
2. **Track Summary Table**:
   * Track identifier;
   * Champion experiment ID;
   * Evidence tier ($E_0 \dots E_5$);
   * Bit-length range tested;
   * Primary metric vs baseline;
   * Validation status and scientific verdict.
3. **New Findings**: Only claims directly supported by immutable experiment IDs.
4. **Failure Analysis**: Infrastructure errors, timeouts (recorded as data), leakage tripwires, or anomalies.
5. **Scaling Curves**: Fitted empirical models, residuals, and scaling exponents across tested bit lengths.
6. **Frontier & Rejected Branches**: Pareto frontier candidates preserved; rejected branches summarized with failure mechanisms.
7. **Research Director Log**: Proposals generated, compute allocated, contract boundaries respected.
8. **Reproduction Commands**: Exact, copy-pasteable commands to reproduce champion results from scratch.
