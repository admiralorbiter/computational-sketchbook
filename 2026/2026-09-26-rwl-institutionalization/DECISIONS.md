# Methodological Decisions & Guardrails: RWL Institutionalization Study

This document preserves foundational methodological decisions established during Task 001 and Task 002. Future research agents and analysts **must not unknowingly reverse** these rules.

---

## 1. Direct Kauffman Grant Expiration = December 31, 2024
- **Rule**: Direct disbursements from the Ewing Marion Kauffman Foundation to Consolidated School District No. 4 terminated on **December 31, 2024**.
- **Rationale**: Empirically verified across IRS Form 990-PF records (Schedule of Grants, grant IDs 201904-6368, 202007-8824, 202307-14162). Total direct funding: $640,435 across 3 grants. The right-hand edge is empirically bounded; do not treat the grant end date as an open question.

## 2. Terminology: Use `post_direct_grant`, NOT `post_grant`
- **Rule**: Classify the period from January 1, 2025 onward as `post_direct_grant` (or `post-direct-Kauffman-grant`), never `post_grant`.
- **Rationale**: External philanthropic and federal-contractor investments continue in Grandview post-2024 (e.g., $125,000 KCNSC/Honeywell grant to Grandview Educational Foundation in September 2024; ongoing PREP-KC investments). Describing the district as "post-grant" falsely implies zero external capital.

## 3. Disappearance of RWL Terminology ≠ Program Disappearance
- **Rule**: Do not infer program decay solely because the exact phrase "Real World Learning" or acronym "RWL" diminishes in public documents.
- **Rationale**: School districts frequently absorb grant-funded models into standard state Career and Technical Education (CTE) terminology, MSIP 6 "Success-Ready Students" language, or local course catalog titles. Always verify underlying pathway operations.

## 4. Governance Attention ≠ Operational Persistence
- **Rule**: Board of Education discussion, brief mentions, or presentation slides are evidence of governance visibility, not proof of classroom execution or budgetary absorption.
- **Rationale**: A superintendent presentation on "Foundations for the Future Week" indicates executive framing; it does not prove that course sections, FTE staffing lines, or credential funding streams are operational.

## 5. Regional MVA Attainment ≠ Grandview MVA Attainment
- **Rule**: Never attribute regional aggregate statistics (e.g., Kauffman's reported "79% of seniors earned an MVA in 2024-25 across participating districts") to Grandview C-4.
- **Rationale**: Regional averages aggregate dozens of high schools and districts across the KC metro. Grandview-specific outcomes must derive from district-level disclosures or DESE state records.

## 6. Inaccessible Attachments ≠ Evidence of Absence
- **Rule**: The inability to download binary PDF/DOCX attachments due to Simbli's Imperva Incapsula WAF does not constitute evidence that data or programs do not exist.
- **Rationale**: All 237 attachments are cataloged with official `AttachmentID`, `EncrId`, and original filenames. When attachment text is unavailable, document the access boundary and code the data as `unobservable_in_accessible_text`.

## 7. Rule-Derived Coding Must Be Explicitly Labeled Derived
- **Rule**: Any automated, heuristic, or regex-derived classification (e.g., `career_connected_semantic`, `money_mentioned`) must be stored with an explicit indicator: `coding_method=rule_based_derived`.
- **Rationale**: Prevents subsequent analytical pipelines or LLM prompts from mistaking rule-based machine classifications for primary source facts.

## 8. Do Not Score Institutionalization Yet
- **Rule**: No composite scores, sentiment indices, trajectory models, or institutionalization labels may be assigned at this stage.
- **Rationale**: Institutionalization cannot be reliably distinguished from rebranding or decay without two concurrent longitudinal series: (1) fiscal/staffing resource allocation, and (2) operational course enrollment and credentialing outcomes.
