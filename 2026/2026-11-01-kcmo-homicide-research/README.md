# KCMO Homicide Research Project (`2026-11-01-kcmo-homicide-research`)

Source-supported investigative data foundation for homicide incidents within **Kansas City, Missouri (KCMO)** from **2020 onward**, built in small, reviewable steps from original Socrata API records and multi-source verification.

---

## Current Milestone: Step 0 & Step 1 (Ten-Case 2020 Research Pilot) Complete

1. **Immutable Starter Snapshot (Step 0):** Preserves [`input/Kansas_City_Homicide_Project_Starter.xlsx`](input/Kansas_City_Homicide_Project_Starter.xlsx) unchanged (`SHA-256: 6221d85597ca6b747098278b07816d9a7e70e9acb53548899273d6fe61751717`).
2. **Raw JSON Reconstruction (`raw_rows`, Step 0):** Parses all **3,146** original Socrata API JSON records across the 2020–2026 annual KCPD crime datasets (`vsgj-uufz`, `w795-ffu6`, `x39y-7d3m`, `bfyq-5nh6`, `isbe-v4d8`, `dmnp-9ajg`, `f7wj-ckmw`), normalizing schema aliases while preserving raw values, text identifiers (`report_number`, `zip_code`, `beat`, `rep_dist`), date precision, and distinct `false` vs. `NULL` flags.
3. **Candidate Incident Roster (`incident_candidates`, Step 0):** Reconstructs all **974** candidate police report numbers (`09A` Murder, `09B` Manslaughter by Negligence, `09C` Justifiable Homicide) from **3,103** candidate offense rows while retaining **43** locally labeled `09D` (`DV Related Suicide`) rows in the raw audit trail.
4. **Ten-Case 2020 Research Pilot (Step 1):**
   * Selected a deterministic 10-case pilot sample across 6 workflow strata ([`src/pilot_select.py`](src/pilot_select.py)).
   * Ran isolated **Incident/Outcome Researchers** (`kcmo-case-researcher` $\to$ [`researcher_batch_a_output.jsonl`](data/research/pilot_batch_1/researcher_batch_a_output.jsonl), [`researcher_batch_b_output.jsonl`](data/research/pilot_batch_1/researcher_batch_b_output.jsonl)) and an independent **Evidence Verifier** (`kcmo-evidence-verifier` $\to$ [`verifier_review.jsonl`](data/research/pilot_batch_1/verifier_review.jsonl)), merged via the Coordinator pipeline ([`src/pilot_merge.py`](src/pilot_merge.py)).
   * Extracted and audited **80 atomic claims** (`58 verified`, `22 unresolved`) with **12 verifier corrections/downgrades** across 10 cases, exported to [`exports/pilot_2020_case_packets.md`](exports/pilot_2020_case_packets.md), [`exports/pilot_2020_claims_evidence.csv`](exports/pilot_2020_claims_evidence.csv), and [`exports/pilot_2020_unresolved_questions.md`](exports/pilot_2020_unresolved_questions.md).

---

## Audit & Discrepancy Findings from Step 0 JSON Reconstruction

1. **Recovered 2024 Firearm Flags (`fire_arm_used_flag`):**
   - The starter workbook's `Field guide` notes three firearm flag aliases (`firearm_used_flag` in 2020, `firearmused_flag` in 2021, `firearmusedflag` in 2022/2023/2025/2026), causing all **138** candidate cases in 2024 to display `None` in the workbook's `Candidate cases` sheet.
   - Inspecting the 2024 `Original API row JSON` revealed a fourth Socrata field alias, `fire_arm_used_flag` (`471` `true` rows, `53` `false` rows). Step 0 preserves both `firearm_flag_values_workbook` (for exact snapshot comparison) and `firearm_flag_values_normalized` (recovering all 138 candidate flags in 2024).
2. **Mixed `09A` + `09D` Reports (Possible Murder-Suicide Incidents):**
   - Of the **43** excluded `09D` (`DV Related Suicide`) rows, **20** rows belong to **9** reports that contain *only* `09D` rows (excluded from `incident_candidates`), while **23** rows belong to **10** reports that *also* contain `09A` Murder rows (`KC20041259`, `KC20045825`, `KC21041838`, `KC23043826`, `KC24020215`, `KC25000421`, `KC25012977`, `KC25030838`, `KC26014954`, `KC26030042`).
   - Those 10 candidate incidents are flagged with `has_excluded_09d_rows = 1` so researchers separate homicide victims from perpetrator suicides.
3. **Date/Time Precision Variations Across Socrata Vintages:**
   - **2020 (`vsgj-uufz`):** All `from_date`, `to_date`, and `reported_date` strings are encoded as `YYYY-MM-DDT00:00:00.000` with the actual clock time stored in `from_time`, `to_time`, and `reported_time`. Step 0 labels these `date_only_with_separate_time` rather than midnight timestamps.
   - **2022 (`x39y-7d3m`):** All 425 rows populate `to_date` (repeating `from_date` even when `to_time` is absent in 381 rows). Step 0 records `date_and_time_duplicated_from_start_without_to_time` and adds an explicit `to_date_note`.
4. **Domestic Violence Flag Encoding Shift:**
   - 2020 encodes `dvflag` as strings `'Y'`/`'N'`, whereas 2021–2026 encode boolean `true`/`false`. Both `domestic_flag_values_raw` and `domestic_flag_values_normalized` are preserved.

---

## Exact Commands to Reproduce

From `2026/2026-11-01-kcmo-homicide-research`:

```powershell
# Rebuild SQLite database from immutable starter workbook, export 2020 queue, and run Step 0 checks
python -m src.cli --rebuild

# Run automated unit tests (including synthetic 1-incident / 2-victim / 2-defendant fixture)
python -m unittest discover -s tests -v
```
