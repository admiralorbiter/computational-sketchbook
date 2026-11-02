# Frozen Evidence Extracts and Documented-Headcount Registry

This directory preserves structured, normalized evidence extracts of documented staffing headcounts, board authorizations,
and departmental staffing rosters for the 18 direct-count coordinator positions across the six focal school districts.
These files capture the specific headcount claims, source citations, URLs, page references, and confidence scores
that underpin the `documented_count` partition (244.80 FTE / 64.4% of the reconstructed sample) in `coordinator_role_reconstruction.csv`.

> [!NOTE]
> **Provenance & Epistemic Scope:** These JSON files represent frozen, normalized evidence records rather than complete archival copies of the original primary source documents (e.g., full board packets, PDF rosters). For archival-grade auditability, future research preservation work can archive verbatim primary documents alongside these normalized extracts.


## Registry of Frozen Source Extracts

| File | District | Documented Roles | Documented FTE | SHA256 Checksum |
| :--- | :--- | :---: | :---: | :--- |
| [kckps_documented_positions.json](kckps_documented_positions.json) | Kansas City USD 500 | 3 | 52.80 FTE | 18fc85e5c31906e1e558102dc4e32d1ecf68534fe1a84728b6d2b321c6c7e36a |
| [lsr7_documented_positions.json](lsr7_documented_positions.json) | Lee's Summit R-VII | 3 | 11.00 FTE | 8d4d0d1f5c27ef296e240988bc5da0f9b5ed1771e625cc89fccbc12836cbf969 |
| [nkc_documented_positions.json](nkc_documented_positions.json) | North Kansas City 74 | 3 | 30.00 FTE | 4a042793c3c40ca1c4689fe11e155176fd275b0c5cde483ba4ba6ebe8e778edb |
| [olathe_documented_positions.json](olathe_documented_positions.json) | Olathe USD 233 | 3 | 64.00 FTE | 06c3f5a490bbd8dfd3f4bb9f92b84e83c88d391dfac0827c7b8e3e594b14a84f |
| [raytown_documented_positions.json](raytown_documented_positions.json) | Raytown C-2 | 3 | 12.00 FTE | 3e5835a312b765a19ffdfbf722d9a328c1b882808eef20979b381115d6e3a8fd |
| [smsd_documented_positions.json](smsd_documented_positions.json) | Shawnee Mission USD 512 | 3 | 75.00 FTE | 67f8440a6c57ef7ec5c9b45de57ebd4640208ae11d92f06ec193c2d95486b0b4 |

## Verification Summary
All extract totals sum to **18 roles** and **244.80 FTE**, exactly matching the documented_count partition in data/processed/coordinator_role_reconstruction.csv.
