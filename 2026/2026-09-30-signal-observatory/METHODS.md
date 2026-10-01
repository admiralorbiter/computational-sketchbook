# Methods & Epistemic Standards for Digital Trace Research

> **Guiding Principle:** Digital trace data provides invaluable contemporaneous insight into public discourse,
> but platform samples are **never representative of the general population**. Research claims must be
> rigorously bounded to the observed data.

---

## 1. Computational Grounded Theory

This observatory adopts Laura Nelson's three-step **Computational Grounded Theory** methodology:

```
[Phase 1: Computational Pattern Detection]
  - Broad keyword/hashtag harvesting across public platforms
  - Topic clustering, frequency counts, burst detection, co-occurrence analysis

[Phase 2: Interpretive Deep Dive]
  - Reading representative artifacts, analyzing video transcripts
  - Identifying recurring narrative frames, moral foundations, and vocabulary

[Phase 3: Computational Confirmation]
  - Verifying identified frames across the full corpus using DuckDB SQL
  - Measuring frame prevalence, temporal trajectory, and platform differences
```

---

## 2. Epistemic Ground Rules

### Rule 1: No False Claims of Public Representation
- Do **not** write: *"Kansas City residents oppose the streetcar extension."*
- **Do write:** *"Among 42 collected online videos and posts observing the streetcar project between Jan–Sep 2026, discussion concentrated on construction disruptions and business access."*

### Rule 2: Non-Comparable Platform Metrics
- Never equate 100 YouTube views to 100 Reddit upvotes or 100 Bluesky likes.
- Each platform has distinct algorithmic affordances, user demographics, and visibility mechanics.
- Analyze platform trends independently before making cross-platform comparisons.

### Rule 3: Missing or Non-Reporting is NOT Zero
- If a community or topic does not appear in a search sample, do not conclude it does not exist.
- Always document search parameters, pagination limits, and query blind spots in the run manifest.

### Rule 4: Separation of Observation from Interpretation
- Source text, metrics, and timestamps belong in `artifacts.parquet`.
- Analytical interpretations (e.g. `stance: supportive`, `frame: economic development`) belong in `annotations.parquet` with the model, prompt, and date stamped.

### Rule 5: Privacy and De-identification
- Do not build or run automated facial recognition or cross-platform identity linking.
- Research focuses on public narrative frames, themes, and evidence circulation, not individual private profiling.
