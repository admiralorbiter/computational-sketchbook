# Operational Boundaries & Agent Research Contract

> **Core Principle:** Agents optimize research inquiry and investigative depth against the frozen
> evidence contract. Agents do not alter, forge, or embellish collected evidence.
>
> *Every factual claim in a generated analysis must resolve to one or more deterministic `artifact_id`s in the corpus.*

---

## 1. Trust Hierarchy & Epistemic Layers

This repository strictly separates observation from inference:

```
[Level 1: Immutable Ground Truth]
data/raw/                     <- Immutable raw API / HTTP response payloads
data/media/                   <- Hashed media files (exact binary preserves)

[Level 2: Normalized Evidence Corpus]
data/normalized/*.parquet     <- Deterministically transformed artifacts (sha256 IDs)

[Level 3: Attributed Annotations]
data/derived/annotations.parquet <- Model inferences (transcripts, topic tags, stance)
                                    Tagged with model, version, timestamp, prompt_hash

[Level 4: Synthesized Claims & Reports]
runs/<run-id>/report.md       <- Human-readable syntheses (all claims cite artifact_id)
```

**Rule of Invariant:**
- No LLM summary, transcript analysis, or synthesis may contradict or fabricate Level 1 or Level 2 evidence.
- An artifact's text, metrics, and timestamps are immutable source facts.
- Model inferences (stance, framing, topic) must reside exclusively in Level 3 annotations.

---

## 2. Agent Autonomy Boundaries

### What Agents May Do Autonomously:
1. **Query Planning:** Expand search vocabularies, alternate place names, synonyms, and relevant hashtags.
2. **Investigation Depth:** Follow promising leads, fetch full threads/conversations, and retrieve media transcripts.
3. **Corpus Querying:** Formulate and execute DuckDB SQL queries over Parquet data to calculate distributions, view counts, and time progressions.
4. **Counter-Searching (Skeptic Mode):** Actively search for contradictory evidence, disconfirming sources, or missing local perspectives.
5. **Report Drafting:** Synthesize findings into structured viewpoint maps with strict artifact citations.

### What Must Be Escalated to the Human Researcher:
1. **Scope Alteration:** Redefining the core question, time bounds, or geographic universe of a frozen inquiry.
2. **Corpus Mutation:** Modifying, deleting, or overwriting existing Parquet files or raw data.
3. **Threshold Reopening:** Reopening or altering finalized runs marked as `frozen` or `audited`.
4. **Person Identification:** Never attempt cross-platform person matching or deanonymization.

---

## 3. Evidence Citation Contract

When generating any synthesis, report, or summary:
- Every specific event claim, quote, or metric must be hyperlinked or footnoted with its canonical URL and `artifact_id`.
- Example:
  > *"Local news coverage noted business optimism along Main Street ([KMBC 9](https://www.youtube.com/watch?v=ANzs1GDiC-M), artifact `65922a46...`)."*

---

## 4. Verification Gates

Before declaring any inquiry run or research phase complete, verify:
1. `uv run ruff check .` passes with 0 lint errors.
2. `uv run pytest tests/ -v` passes with 0 failures.
3. `runs/<run-id>/manifest.json` is generated with `status: completed`.
4. Every cited artifact in `RUN_SUMMARY.md` exists in `data/normalized/artifacts.parquet`.
