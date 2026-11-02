# Step 1 — Ten-Case 2020 Pilot Case Packets

- **Total Cases:** 10
- **Total Claims Extracted & Audited:** 80 (`{'verified': 58, 'unresolved': 22}`)
- **Total Research + Verification Time:** 3205s (320.5s / case)
- **Verifier Corrections / Downgrades:** 12 (1.2 / case)
- **Estimated Effort for Remaining 152 Cases in 2020:** ~13.53 agent-hours

---

## Case 1: `KCPD:KC20001088` (A1_ordinary_09A_baseline)
- **Incident Date / Time:** `2020-01-05` (`12:10`)
- **Reported Location:** `1100  LOCUST ST` (`KANSAS CITY`, `64106`, Div `CPD`, Beat `112`)
- **Source Code & Scope Flag:** `09A` | `Candidate - verify inclusion` | `3` rows (`ARR CHA SOC SUS (1); ARR CHA SUS (1); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`unknown` | Police=`verified` | Prosecutor=`verified` | Court=`unresolved`
- **Effort & Verification:** Research `240s` + Verifier `115s` | Corrections/Downgrades=`1` | Claims=`{'verified': 9, 'unresolved': 4}`

**Case Narrative Summary:** Independently verified against Socrata vsgj-uufz (rows 64, 118, 138), JCPAO press release Detail/882 (2020-01-22), the 5-page redacted felony complaint and Probable Cause Statement PDF (DocumentCenter/View/1411/ADWhite_Redacted, Police No. KC20001088, CRN 20-1088, Prosecutor No. 095456978, Det. Thomas Hammond #4775), and US Census Geocoder. Confirmed conflicting addresses (Socrata 1100 Locust St 64106 near KCPD HQ 1125 Locust St where suspects were interviewed vs. actual shooting scene 4933 Walrond Ave 64130; both inside KCMO GEOID 2938000) and conflicting DOBs for Anderson D. White (09/12/1994 on sworn complaint/PC statement vs. 09/23/1994 in press release text). Corrected one researcher detail: co-defendant Darren D. Hamilton (B/M, DOB 09/09/1994) is named unredacted on p. 4 of ADWhite_Redacted.pdf as well as in Detail/882, and his exact charging date prior to 2020-01-22 is not stated in Detail/882 (removed unsupported '2020-01-10' filing date). Final court dispositions for both defendants remain genuinely unresolved without interactive Missouri Case.net lookup.

**Verifier Audit Summary:** Independently verified against Socrata vsgj-uufz (rows 64, 118, 138), JCPAO press release Detail/882 (2020-01-22), the 5-page redacted felony complaint and Probable Cause Statement PDF (DocumentCenter/View/1411/ADWhite_Redacted, Police No. KC20001088, CRN 20-1088, Prosecutor No. 095456978, Det. Thomas Hammond #4775), and US Census Geocoder. Confirmed conflicting addresses (Socrata 1100 Locust St 64106 near KCPD HQ 1125 Locust St where suspects were interviewed vs. actual shooting scene 4933 Walrond Ave 64130; both inside KCMO GEOID 2938000) and conflicting DOBs for Anderson D. White (09/12/1994 on sworn complaint/PC statement vs. 09/23/1994 in press release text). Corrected one researcher detail: co-defendant Darren D. Hamilton (B/M, DOB 09/09/1994) is named unredacted on p. 4 of ADWhite_Redacted.pdf as well as in Detail/882, and his exact charging date prior to 2020-01-22 is not stated in Detail/882 (removed unsupported '2020-01-10' filing date). Final court dispositions for both defendants remain genuinely unresolved without interactive Missouri Case.net lookup.

### Deceased Victims
- `VIC:KCPD:KC20001088:1`: **Earl Finch III** (`confirmed_named`) | B/M/age 41 | Death: `2020-01-05` | Cause: `Not publicly released (ME restricted)` | Weapon: `Handgun (11x 9mm and 4x .45 cal shell casings recovered at scene per Probable Cause Statement p. 4; KCPD firearm_flag=true)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20001088:1`: **Anderson D. White** | Police: `cleared_by_arrest` (`ARR CHA SOC SUS / ARR CHA SUS (Socrata rows 118, 138, B/M/25); arrested 01-07-2020 at ~1700 hours per PC statement p. 5`) | Prosecutor: `charges_filed` (`2020-01-22`) | Court: `unknown` (`n/a`) — n/a
- `DEF:KCPD:KC20001088:2`: **Darren D. Hamilton** | Police: `cleared_by_arrest` (`ARR CHA SOC SUS / ARR CHA SUS (Socrata rows 118, 138, B/M/25); arrested 01-08-2020 at ~1200 hours per PC statement p. 5`) | Prosecutor: `charges_filed` (`n/a`) | Court: `unknown` (`n/a`) — n/a

### Unresolved Questions & Blockers
- Full 16th Circuit Case.net docket numbers (2016-CRXXXXX) and final court dispositions/sentences for Anderson D. White and Darren D. Hamilton require interactive Missouri Case.net lookup.
- Official Jackson County Medical Examiner autopsy cause-of-death wording is not publicly available.
- What were the final court dispositions and sentences for Anderson D. White and Darren D. Hamilton in 16th Judicial Circuit Court?
- Why did KCPD Socrata vsgj-uufz publish the arrest/interview address (1100 Locust St, 64106, Beat 112) rather than the homicide dispatch scene (4933 Walrond Ave, 64130) for KC20001088?

---

## Case 2: `KCPD:KC20001607` (A2_ordinary_09A_baseline)
- **Incident Date / Time:** `2020-01-07` (`12:24`)
- **Reported Location:** `400  E MINOR DR` (`KANSAS CITY`, `64131`, Div `SPD`, Beat `533`)
- **Source Code & Scope Flag:** `09A` | `Candidate - verify inclusion` | `3` rows (`ARR CHA SUS (1); SUS (1); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`unknown` | Police=`unresolved` | Prosecutor=`unresolved` | Court=`unresolved`
- **Effort & Verification:** Research `210s` + Verifier `90s` | Corrections/Downgrades=`1` | Claims=`{'verified': 4, 'unresolved': 4}`

**Case Narrative Summary:** Independently verified against Socrata vsgj-uufz (rows 62, 83, 102), the full KSHB 41 Action News article ('1 man killed in shooting near Minor Park', published 2020-01-07, updated 2020-01-08), and US Census Geocoder confirming (38.921552, -94.588435) at 400 E Minor Dr (Coach House Apartments) lies inside Kansas City city (GEOID 2938000), Jackson County (GEOID 29095). Applied 1 precision correction on victim name: the full KSHB article confirms 'Raphael Lee', age 32, whereas the middle initial 'O.' ('Raphael O. Lee') comes from a gated Crime Solvers Central snippet (/homicide/101116). Confirmed the unresolved discrepancy between Socrata row 62 ('ARR CHA SUS', M, age 43) and the absence of any public KCPD or Jackson County Prosecutor arrest/charging announcement.

**Verifier Audit Summary:** Independently verified against Socrata vsgj-uufz (rows 62, 83, 102), the full KSHB 41 Action News article ('1 man killed in shooting near Minor Park', published 2020-01-07, updated 2020-01-08), and US Census Geocoder confirming (38.921552, -94.588435) at 400 E Minor Dr (Coach House Apartments) lies inside Kansas City city (GEOID 2938000), Jackson County (GEOID 29095). Applied 1 precision correction on victim name: the full KSHB article confirms 'Raphael Lee', age 32, whereas the middle initial 'O.' ('Raphael O. Lee') comes from a gated Crime Solvers Central snippet (/homicide/101116). Confirmed the unresolved discrepancy between Socrata row 62 ('ARR CHA SUS', M, age 43) and the absence of any public KCPD or Jackson County Prosecutor arrest/charging announcement.

### Deceased Victims
- `VIC:KCPD:KC20001607:1`: **Raphael Lee (reported as Raphael O. Lee in gated Crime Solvers index)** (`confirmed_named`) | B/M/age 32 | Death: `2020-01-07` | Cause: `Not publicly released (ME restricted)` | Weapon: `Firearm / shooting (KCPD firearm_flag=true; KSHB reports victim found suffering from gunshot wounds)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20001607:1`: **Unidentified / Uncharged** | Police: `cleared_by_arrest` (`ARR CHA SUS (Socrata row 62, race null, sex M, age 43)`) | Prosecutor: `unknown` (`n/a`) | Court: `unknown` (`n/a`) — n/a
- `DEF:KCPD:KC20001607:2`: **Unidentified / Uncharged** | Police: `unknown` (`SUS (Socrata row 83, race B, sex M, age 42)`) | Prosecutor: `unknown` (`n/a`) | Court: `unknown` (`n/a`) — n/a

### Unresolved Questions & Blockers
- KCPD Socrata row 62 codes a 43-year-old male suspect as 'ARR CHA SUS' (and row 83 codes a 42-year-old Black male as 'SUS'), but no public news report or Jackson County Prosecutor charging announcement identifies any suspect or confirms whether homicide charges were ever filed.
- Official Jackson County Medical Examiner autopsy cause-of-death wording is not publicly available.
- Was the 43-year-old male coded 'ARR CHA SUS' in Socrata row 62 for KC20001607 charged with homicide, charged with a collateral offense, or released without charges?

---

## Case 3: `KCPD:KC20002513` (A3_ordinary_09A_dv_flag)
- **Incident Date / Time:** `2020-01-10` (`14:15`)
- **Reported Location:** `300  W 98TH ST` (`KANSAS CITY`, `None`, Div `SPD`, Beat `531`)
- **Source Code & Scope Flag:** `09A` | `Candidate - verify inclusion` | `2` rows (`ARR CHA SUS (1); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`verified` | Police=`verified` | Prosecutor=`verified` | Court=`verified`
- **Effort & Verification:** Research `220s` + Verifier `135s` | Corrections/Downgrades=`4` | Claims=`{'verified': 11, 'unresolved': 1}`

**Case Narrative Summary:** Independently verified against Socrata vsgj-uufz (rows 94, 105), JCPAO press release Detail/878 (2020-01-13), the 5-page redacted Complaint and Probable Cause Statement PDF (DocumentCenter/View/1405/BPetsch_redacted, Police No. KC20002513, Prosecutor No. 095457010), the full 2025-02-07 Johnson County Post article confirming Brandon Petsch's Dec. 31, 2024 sentencing to 21 years in prison for second-degree murder, and US Census Geocoder. Caught and corrected 4 factual/citation errors in the researcher's packet by inspecting BPetsch_redacted.pdf page-by-page: (1) the Probable Cause Statement affiant on PDF p. 3 is Det. Mary Kincheloe #5063 (not 'Det. Mark A. Slavens #5213'); (2) Complaint Count I & II on PDF p. 1 charge 'on or about January 11, 2020' (repeated in the 2025 JoCo Post article), whereas the PC Statement (PDF p. 3) and Socrata prove KCPD discovered Georgia Petsch deceased on 2020-01-10 at 15:07 after 24-34 hours had elapsed since the shooting; (3) the PC Statement documents 2 black firearms on the dining table, a spent casing and bullet in the bathroom, and the 2020-01-11 Jackson County ME body examination confirming defects matching the 3 shots in the suspect's letter (leg, bathroom entanglement, head shot), but does NOT specify '9mm' or '3 spent 9mm shell casings'; and (4) in CLM:KC20002513:07, Brandon J. Petsch was NOT arrested by Illinois State Police after crashing a Honda CRV on I-74—both BPetsch_redacted.pdf (p. 3-4) and JCPAO Detail/878 prove KCPD found Petsch unresponsive in his bed at 310 W. 98th St with a firearm underneath his head and 2 empty bottles of sleep aid capsules, and transported him to a local hospital (also corrected signing APA in CLM:KC20002513:08 from 'Jordan R. Bergus' to Brady X. Twenter #49380).

**Verifier Audit Summary:** Independently verified against Socrata vsgj-uufz (rows 94, 105), JCPAO press release Detail/878 (2020-01-13), the 5-page redacted Complaint and Probable Cause Statement PDF (DocumentCenter/View/1405/BPetsch_redacted, Police No. KC20002513, Prosecutor No. 095457010), the full 2025-02-07 Johnson County Post article confirming Brandon Petsch's Dec. 31, 2024 sentencing to 21 years in prison for second-degree murder, and US Census Geocoder. Caught and corrected 4 factual/citation errors in the researcher's packet by inspecting BPetsch_redacted.pdf page-by-page: (1) the Probable Cause Statement affiant on PDF p. 3 is Det. Mary Kincheloe #5063 (not 'Det. Mark A. Slavens #5213'); (2) Complaint Count I & II on PDF p. 1 charge 'on or about January 11, 2020' (repeated in the 2025 JoCo Post article), whereas the PC Statement (PDF p. 3) and Socrata prove KCPD discovered Georgia Petsch deceased on 2020-01-10 at 15:07 after 24-34 hours had elapsed since the shooting; (3) the PC Statement documents 2 black firearms on the dining table, a spent casing and bullet in the bathroom, and the 2020-01-11 Jackson County ME body examination confirming defects matching the 3 shots in the suspect's letter (leg, bathroom entanglement, head shot), but does NOT specify '9mm' or '3 spent 9mm shell casings'; and (4) in CLM:KC20002513:07, Brandon J. Petsch was NOT arrested by Illinois State Police after crashing a Honda CRV on I-74—both BPetsch_redacted.pdf (p. 3-4) and JCPAO Detail/878 prove KCPD found Petsch unresponsive in his bed at 310 W. 98th St with a firearm underneath his head and 2 empty bottles of sleep aid capsules, and transported him to a local hospital (also corrected signing APA in CLM:KC20002513:08 from 'Jordan R. Bergus' to Brady X. Twenter #49380).

### Deceased Victims
- `VIC:KCPD:KC20002513:1`: **Georgia Petsch** (`confirmed_named`) | W/F/age 38 | Death: `2020-01-10` | Cause: `Gunshot defects to the leg, torso/bathroom entanglement, and head confirmed at Jackson County Medical Examiner body examination on 2020-01-11 (matching the 3 shots described in suspect's letter)` | Weapon: `Firearm (2 black firearms on dining room table, 1 spent casing and 1 spent bullet in bathroom per Probable Cause Statement pp. 3-4; KCPD firearm_flag=true, dv_flag=Y)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20002513:1`: **Brandon J. Petsch** | Police: `cleared_by_arrest` (`ARR CHA SUS (Socrata row 105, W/M/36); found unresponsive in bed at 310 W. 98th St on 01-10-2020 and admitted to hospital under police guard per PC Statement pp. 3-4`) | Prosecutor: `charges_filed` (`2020-01-11`) | Court: `convicted_2nd_degree_murder_sentenced_21_years` (`2024-12-31`) — Sentenced on 2024-12-31 to 21 years in prison for Murder 2nd Degree

### Unresolved Questions & Blockers
- Numeric suffix of 16th Circuit docket number (2016-CRXXXXX) is redacted on the public JCPAO complaint PDF.
- What is the exact 2016-CRXXXXX docket number in Missouri Case.net for State v. Brandon J. Petsch (Prosecutor No. 095457010), and what was the disposition of Count II (Armed Criminal Action) at the 2024-12-31 sentencing?

---

## Case 4: `KCPD:KC20001881` (B1_jurisdiction_beat999_missing_coords)
- **Incident Date / Time:** `2020-01-08` (`12:53`)
- **Reported Location:** `2000  PARK TOWER DR` (`KANSAS CITY`, `64126`, Div `EPD`, Beat `999`)
- **Source Code & Scope Flag:** `09A` | `Check jurisdiction` | `5` rows (`ARR CHA SUS (1); SUS (1); VIC (2); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`unknown` | Police=`verified` | Prosecutor=`verified` | Court=`unresolved`
- **Effort & Verification:** Research `210s` + Verifier `110s` | Corrections/Downgrades=`2` | Claims=`{'verified': 8, 'unresolved': 3}`

**Case Narrative Summary:** Independently verified against Socrata vsgj-uufz (5 rows: 1, 2, 112, 128, 207), JCPAO press release Detail/877 (2020-01-10), the 7-page redacted Complaint and Probable Cause Statement PDF (DocumentCenter/View/1404/NJames_Redacted, Police No. KC20001881, Prosecutor No. 095456995, OCN HS016545), and US Census Geocoder confirming 2044 Park Tower Dr, Kansas City, MO 64126 (39.086709, -94.512000) is inside Kansas City city (GEOID 2938000) despite Socrata beat=999 and missing coordinates. Caught and corrected 2 details by inspecting NJames_Redacted.pdf: (1) the Probable Cause Statement affiant on PDF p. 5 is Det. Scott Mullen #5431 (not 'Det. Timothy J. Taylor #5594'); and (2) PDF pp. 5-6 state spent shell casings were recovered on the front porch/steps and living room without specifying '.40 cal and 9mm', and state James was arrested on 01-09-2020 and transported to Police Headquarters (where he initially lied twice before confessing when told the shooting was on video) rather than turning himself in at East Patrol Division. Final court disposition for Nicholas A. James remains genuinely unresolved without interactive Missouri Case.net access.

**Verifier Audit Summary:** Independently verified against Socrata vsgj-uufz (5 rows: 1, 2, 112, 128, 207), JCPAO press release Detail/877 (2020-01-10), the 7-page redacted Complaint and Probable Cause Statement PDF (DocumentCenter/View/1404/NJames_Redacted, Police No. KC20001881, Prosecutor No. 095456995, OCN HS016545), and US Census Geocoder confirming 2044 Park Tower Dr, Kansas City, MO 64126 (39.086709, -94.512000) is inside Kansas City city (GEOID 2938000) despite Socrata beat=999 and missing coordinates. Caught and corrected 2 details by inspecting NJames_Redacted.pdf: (1) the Probable Cause Statement affiant on PDF p. 5 is Det. Scott Mullen #5431 (not 'Det. Timothy J. Taylor #5594'); and (2) PDF pp. 5-6 state spent shell casings were recovered on the front porch/steps and living room without specifying '.40 cal and 9mm', and state James was arrested on 01-09-2020 and transported to Police Headquarters (where he initially lied twice before confessing when told the shooting was on video) rather than turning himself in at East Patrol Division. Final court disposition for Nicholas A. James remains genuinely unresolved without interactive Missouri Case.net access.

### Deceased Victims
- `VIC:KCPD:KC20001881:1`: **Deandre Chiney** (`confirmed_named`) | B/M/age 21 | Death: `2020-01-08` | Cause: `Not publicly released (ME restricted)` | Weapon: `Handgun (spent shell casings recovered on front porch/steps and living room, plus spent bullet inside residence per Probable Cause Statement p. 5; KCPD firearm_flag=true)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20001881:1`: **Nicholas A. James** | Police: `cleared_by_arrest` (`ARR CHA SUS (Socrata row 128, B/M/21); arrested 01-09-2020 and transported to Police Headquarters per PC Statement p. 6`) | Prosecutor: `charges_filed` (`2020-01-10`) | Court: `unknown` (`n/a`) — n/a
- `DEF:KCPD:KC20001881:2`: **Unidentified / Uncharged** | Police: `unknown` (`SUS (Socrata row 207, race null, sex U, age null)`) | Prosecutor: `unknown` (`n/a`) | Court: `unknown` (`n/a`) — n/a

### Unresolved Questions & Blockers
- Full 16th Circuit Case.net docket number (2016-CRXXXXX) and final court disposition/sentence for Nicholas A. James (OCN HS016545) require interactive Missouri Case.net lookup.
- Official Jackson County Medical Examiner autopsy cause-of-death wording is not publicly available.
- What was the final court disposition and sentence for Nicholas A. James (OCN HS016545, Prosecutor No. 095456995) in 16th Judicial Circuit Court?
- Why was KC20001881 coded with beat='999' and missing coordinates in Socrata vsgj-uufz when 2044 Park Tower Drive is a standard residential address inside KCMO East Patrol Division (64126)?

---

## Case 5: `KCPD:KC20030505` (B2_jurisdiction_ospd_independence_postal_city)
- **Incident Date / Time:** `2020-05-09` (`23:00`)
- **Reported Location:** `12800  US 40 HWY` (`INDEPENDENCE`, `64055`, Div `OSPD`, Beat `999`)
- **Source Code & Scope Flag:** `09A` | `Check jurisdiction` | `6` rows (`ARR CHA INA SUS (1); ARR CHA WIT (1); SUS (1); VIC (2); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`excluded_outside_kcmo` | Victim=`rejected` | Medical=`unknown` | Police=`unresolved` | Prosecutor=`unresolved` | Court=`unresolved`
- **Effort & Verification:** Research `300s` + Verifier `85s` | Corrections/Downgrades=`1` | Claims=`{'verified': 1, 'unresolved': 4}`

**Case Narrative Summary:** Independently verified against Socrata vsgj-uufz (6 rows: 145, 166, 169, 181, 202, 268) and US Census Geocoder confirming that coordinates (39.039172, -94.42934) at '12800 US 40 HWY, INDEPENDENCE 64055' fall strictly inside the municipal boundaries of Independence city (GEOID 2935000), Jackson County (GEOID 29095), ~1.5 km east of the Kansas City, MO boundary, matching KCPD's area_raw='OSPD' (Outside Police Department) and beat_raw='999'. Confirmed final_inclusion_decision='excluded_outside_kcmo' and set reviewed_victims verification_state to 'rejected' (Correction #1) so that no non-KCMO victim is added to verified KCMO homicide totals while retaining the raw record for audit.

**Verifier Audit Summary:** Independently verified against Socrata vsgj-uufz (6 rows: 145, 166, 169, 181, 202, 268) and US Census Geocoder confirming that coordinates (39.039172, -94.42934) at '12800 US 40 HWY, INDEPENDENCE 64055' fall strictly inside the municipal boundaries of Independence city (GEOID 2935000), Jackson County (GEOID 29095), ~1.5 km east of the Kansas City, MO boundary, matching KCPD's area_raw='OSPD' (Outside Police Department) and beat_raw='999'. Confirmed final_inclusion_decision='excluded_outside_kcmo' and set reviewed_victims verification_state to 'rejected' (Correction #1) so that no non-KCMO victim is added to verified KCMO homicide totals while retaining the raw record for audit.

### Deceased Victims
- `VIC:KCPD:KC20030505:1`: **Unnamed / Unconfirmed** (`searched_no_result`) | B/M/age 39 | Death: `2020-05-09` | Cause: `Not publicly released (ME restricted)` | Weapon: `Firearm (KCPD firearm_flag=true)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20030505:1`: **Unidentified / Uncharged** | Police: `unresolved` (`ARR CHA INA SUS (Socrata row 145, B/F/30) & ARR CHA WIT (row 181, B/F/30)`) | Prosecutor: `unknown` (`n/a`) | Court: `unknown` (`n/a`) — n/a
- `DEF:KCPD:KC20030505:2`: **Unidentified / Uncharged** | Police: `unknown` (`SUS (Socrata row 169, B/M/27, dv=N) & VIC (row 202, B/M/27, dv=Y)`) | Prosecutor: `unknown` (`n/a`) | Court: `unknown` (`n/a`) — n/a

### Unresolved Questions & Blockers
- 12800 US 40 Hwy (39.039172, -94.42934) is verified inside the City of Independence (GEOID 2935000) ~1.5 km east of KCMO city limits and is coded area_raw='OSPD' (Outside Police Department) and beat='999' by KCPD, supporting exclusion from KCMO municipal scope. However, without a public KCPD incident narrative, we cannot completely rule out the small possibility that 12800 US 40 Hwy was an arrest/follow-up location in Independence for a crime scene elsewhere.
- No public source identifies the 39-year-old Black male deceased victim (row 166) or clarifies the cross-coded domestic violence victim/suspect rows (30yo B/F ARR CHA INA SUS / ARR CHA WIT and 27yo B/M SUS / VIC).
- Why did KCPD record an 'OSPD' 09A Murder report (KC20030505) at 12800 US 40 Hwy inside Independence city limits (e.g., KCPD assist/arrest for an Independence PD homicide vs. hospital/follow-up contact)?

---

## Case 6: `KCPD:KC20004297` (C1_multi_row_9_involvements)
- **Incident Date / Time:** `2020-01-18` (`01:56`)
- **Reported Location:** `8400  E 109TH TER` (`KANSAS CITY`, `64134`, Div `SPD`, Beat `545`)
- **Source Code & Scope Flag:** `09A` | `Candidate - verify inclusion` | `9` rows (`ARR CHA SUS (2); CHA INA (1); CHA SUS (1); SUS (1); VIC (3); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`unknown` | Police=`unresolved` | Prosecutor=`unresolved` | Court=`unresolved`
- **Effort & Verification:** Research `210s` + Verifier `95s` | Corrections/Downgrades=`1` | Claims=`{'verified': 3, 'unresolved': 3}`

**Case Narrative Summary:** Around 1:56 a.m. on Saturday, January 18, 2020, KCPD officers responded to a reported shooting in the 8400 block of East 109th Terrace (near 109th Terrace and Marsh Avenue in the Ruskin Hills/Ruskin Heights area of southeastern Kansas City, Missouri) and found an 18-year-old Black male, publicly identified as Bobby Joe Bernard Wallace (Bobby J. Wallace), lying on the ground with a gunshot wound. He was transported in extremely critical condition to a local hospital, where he died in surgery that same day (KCMO's 8th homicide of 2020). KCPD's 2020 offense snapshot contains 9 involvement rows for KC20004297: 1 deceased victim (VIC DEC B/M/18), 3 non-deceased victims (VIC B/M ages 47, 53, and null), 4 arrest/charge suspect entries for a 19-year-old Black male (ARR CHA SUS, CHA SUS, and inactivated charge code CHA INA), and 1 unknown-race male suspect (SUS); however, public searches of Jackson County Prosecutor releases and local media found no publicly named defendant or homicide indictment.

**Verifier Audit Summary:** Independently verified against Socrata vsgj-uufz (9 rows: 38, 39, 92, 101, 103, 107, 115, 131, 173), US Census Geocoder confirming (38.925038, -94.49379) at 8400 E 109th Ter lies inside Kansas City city (GEOID 2938000), Jackson County (GEOID 29095), and full inspection of WIBW/AP, Tony's KC (quoting KMBC), and Gun Memorial. Confirmed 1 deceased victim (Bobby J. Wallace, 18, B/M, row 39; full middle name 'Joe Bernard' noted as from search snippet of HTTP-403 Crime Solvers page) and 3 non-deceased male victims (rows 38, 92, 103). Downgraded CLM:KC20004297:05 (police_clearance_status) from 'proposed' to 'unresolved' (Downgrade #1) because Socrata rows 101, 107, 115, and 173 contain conflicting 'ARR CHA SUS' and 'CHA INA' ('Charge Inactivated') codes for the 19-year-old Black male suspect and no public arrest or charging record exists.

### Deceased Victims
- `VIC:KCPD:KC20004297:1`: **Bobby Joe Bernard Wallace (Bobby J. Wallace)** (`confirmed_named`) | B/M/age 18 | Death: `2020-01-18` | Cause: `Not publicly released (ME restricted)` | Weapon: `Firearm / shooting reported (victim found with gunshot wound; KCPD firearm_flag=true)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20004297:1`: **Unidentified / Uncharged** | Police: `cleared_by_arrest` (`ARR CHA SUS (rows 115, 173); CHA SUS (row 107); CHA INA (row 101)`) | Prosecutor: `unknown` (`n/a`) | Court: `pending_or_unknown` (`n/a`) — n/a
- `DEF:KCPD:KC20004297:2`: **Unidentified / Uncharged** | Police: `unknown` (`SUS (row 131, race U, sex M, age null)`) | Prosecutor: `unknown` (`n/a`) | Court: `pending_or_unknown` (`n/a`) — n/a

### Unresolved Questions & Blockers
- Does the 'ARR CHA SUS' / 'CHA INA' coding for the 19-year-old Black male in KC20004297 reflect an arrest where homicide charges were declined/inactivated ('CHA INA'), or a separate non-homicide charge arising from the same incident?
- What was the relationship of the three non-deceased male victims (ages 47, 53, and null) to the shooting of 18-year-old Bobby Joe Bernard Wallace?
- Does 'CHA INA' (row 101) alongside 'ARR CHA SUS' (rows 115, 173) for the 19-year-old Black male in KC20004297 indicate that homicide charges were declined/inactivated or that the arrest was for a non-homicide offense?

---

## Case 7: `KCPD:KC20004714` (C2_multi_row_20_involvements_mass_event)
- **Incident Date / Time:** `2020-01-19` (`23:27`)
- **Reported Location:** `4800  NOLAND RD` (`KANSAS CITY`, `64133`, Div `EPD`, Beat `345`)
- **Source Code & Scope Flag:** `09A` | `Candidate - verify inclusion` | `20` rows (`ARR OTH SUS (1); CMP VIC (1); VIC (16); VIC DEC (1); VIC SUS (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`unknown` | Police=`verified` | Prosecutor=`verified` | Court=`verified`
- **Effort & Verification:** Research `195s` + Verifier `95s` | Corrections/Downgrades=`1` | Claims=`{'verified': 5, 'unresolved': 1}`

**Case Narrative Summary:** Shortly before midnight on Sunday, January 19, 2020 (reported at 23:27), 29-year-old Jahron Swift opened fire on a line of patrons waiting to enter the 9ine Ultra Lounge nightclub in the 4800 block of Noland Road in Kansas City, Missouri, during a celebration following the Kansas City Chiefs' AFC Championship victory. Patron Raeven A. Parks (25, Black female) was fatally shot, at least 15 other people were injured, and an armed private security guard employed by the lounge fatally shot Swift outside the business. KCPD's 20-row offense record for KC20004714 carefully distinguishes Raeven A. Parks as the sole 'VIC DEC' (B/F/25, row 211), codes deceased gunman Jahron Swift as 'VIC SUS' (B/M/29, row 132), records 17 non-deceased 'VIC'/'CMP VIC' rows, and includes 1 'ARR OTH SUS' row (M/38, row 42) for a collateral arrest.

**Verifier Audit Summary:** Independently verified against all 20 Socrata vsgj-uufz rows for KC20004714, the official KCPD news release ('15 injured in mass shooting at club, 2 killed, including shooter', 2020-01-20), KCUR, CBS News, and US Census Geocoder confirming (39.033747, -94.41578) at 4800 Noland Rd (9ine Ultra Lounge) lies inside Kansas City city (GEOID 2938000), Jackson County (GEOID 29095). Verified the 20-row structure: 1 criminal homicide victim (Raeven A. Parks, B/F/25, row 211 VIC DEC), 1 deceased active shooter killed at the scene by an armed private security guard (Jahron Swift, B/M/29, row 132 VIC SUS), 17 surviving victim rows (16 VIC, 1 CMP VIC), and 1 collateral arrest row (row 42 ARR OTH SUS, M/38). Downgraded CLM:KC20004714:06 (DEF:KCPD:KC20004714:2 police_clearance_status) from 'proposed' to 'unresolved' with corrected_proposed_value='collateral_arrest_other_offense_ARR_OTH_SUS' because KCPD explicitly confirmed only deceased shooter Jahron Swift and the security guard fired weapons, so row 42 is a collateral non-homicide arrest rather than a homicide arrest clearance.

### Deceased Victims
- `VIC:KCPD:KC20004714:1`: **Raeven A. Parks** (`confirmed_named`) | B/F/age 25 | Death: `2020-01-19` | Cause: `Not publicly released (ME restricted)` | Weapon: `Firearm / mass shooting outside nightclub (KCPD firearm_flag=true)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20004714:1`: **Jahron Swift** | Police: `exceptional_clearance_offender_death` (`VIC SUS (row 132, B/M/29; shot and killed at the scene by private security guard)`) | Prosecutor: `not_applicable_offender_deceased` (`2020-01-20`) | Court: `not_applicable_offender_deceased` (`n/a`) — Not applicable — suspect deceased at scene on 2020-01-19.
- `DEF:KCPD:KC20004714:2`: **Unidentified / Uncharged** | Police: `collateral_arrest_other_offense_ARR_OTH_SUS` (`ARR OTH SUS (row 42, race null, sex M, age 38)`) | Prosecutor: `unknown` (`n/a`) | Court: `not_researched` (`n/a`) — n/a

### Unresolved Questions & Blockers
- How does KCPD classify the private security guard's fatal shooting of active shooter Jahron Swift ('VIC SUS' row 132) in internal UCR/SHR submissions (e.g., private-citizen justifiable homicide vs. excluded offender death)?
- What collateral offense prompted the 'ARR OTH SUS' (M, age 38) entry in Socrata row 42 of KC20004714?

---

## Case 8: `KCPD:KC20008191` (D1_missing_coords_non_firearm_intersection)
- **Incident Date / Time:** `2020-02-02` (`07:33`)
- **Reported Location:** `E 9TH ST and HARDESTY AVE` (`KANSAS CITY`, `64124`, Div `EPD`, Beat `315`)
- **Source Code & Scope Flag:** `09A` | `Candidate - verify inclusion` | `3` rows (`ARR CHA SUS (1); SUS (1); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`verified` | Police=`verified` | Prosecutor=`verified` | Court=`unresolved`
- **Effort & Verification:** Research `240s` + Verifier `120s` | Corrections/Downgrades=`0` | Claims=`{'verified': 8, 'unresolved': 2}`

**Case Narrative Summary:** At approximately 7:33 a.m. on Sunday, February 2, 2020, KCPD officers responded to E. 9th Street and Hardesty Avenue in Kansas City, Missouri, where they discovered the smoldering, burned body of 31-year-old Derrick L. Wallace (Black male, DOB 05/08/1988) on top of a shopping cart in an abandoned homeless camp. Although KCPD's initial offense row recorded firearm_flag='false' due to the burned state of the body, the Jackson County Medical Examiner's autopsy on February 3, 2020 recovered .380-caliber bullets, determined the cause of death to be multiple gunshot wounds (noting skull fractures likely from thermal injury while not ruling out blunt force trauma), and ruled the death a homicide; detectives determined Wallace was shot and struck with a machete 4-5 days earlier at 5209 Independence Ave #2. On June 22, 2020, Jackson County prosecutors charged Mark S. Salisbury (W/M, DOB 04/25/1979) in KC20008191 (Prosecutor No. 095458988) with 2nd-Degree Murder, Armed Criminal Action, and Unlawful Possession of a Firearm.

**Verifier Audit Summary:** Independently verified against Socrata vsgj-uufz (rows 75, 88, 104), JCPAO press release Detail/955 (2020-06-22), the 7-page redacted Complaint and Probable Cause Statement PDF (DocumentCenter/View/1537/MSalisbury_Redacted, Police No. KC20008191, CRN 20-008191, Prosecutor No. 095458988, Det. Kari E. Mutschler #5702, signed by APA Jamie K. Hunt #50401), Northeast News articles (2020-02-19 and 2020-06-23), and US Census Geocoder confirming both the body-burn discovery site (E 9th St & Hardesty Ave, 64124 -> 39.101403, -94.519060) and the apartment killing site (5209 Independence Ave #2, 64124 -> 39.105222, -94.520957) lie inside Kansas City city (GEOID 2938000). Verified all researcher claims with zero corrections required, including the critical finding that Socrata's firearm_flag_raw='false' is contradicted by the 2020-02-03 Jackson County Medical Examiner autopsy (which recovered .380 bullets and determined cause of death to be multiple gunshot wounds), and that Salisbury was arrested on 2020-02-14 (correcting Northeast News's 'Feb. 3' typo). Final court disposition for Mark S. Salisbury remains genuinely unresolved without interactive Missouri Case.net lookup.

### Deceased Victims
- `VIC:KCPD:KC20008191:1`: **Derrick L. Wallace** (`confirmed_named`) | B/M/age 31 | Death: `2020-02-02` | Cause: `Multiple gunshot wounds (with multiple skull fractures likely due to thermal injury; blunt force trauma could not be ruled out due to body condition)` | Weapon: `Firearm (Bryco .380 handgun ballistically matched to bullet recovered from victim's body) and machete/hatchet; body subsequently burned in shopping cart (note: KCPD initial Socrata row recorded firearm_flag=false before autopsy)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20008191:1`: **Mark S. Salisbury** | Police: `cleared_by_arrest` (`ARR CHA SUS (row 104, race null, sex M, age 40)`) | Prosecutor: `charges_filed` (`2020-06-22`) | Court: `pending_or_unknown` (`n/a`) — n/a
- `DEF:KCPD:KC20008191:2`: **Unidentified / Uncharged** | Police: `unknown` (`SUS (row 75, race B, sex M, age 57; referred to as redacted 'Suspect #2' in Probable Cause Statement CRN 20-008191)`) | Prosecutor: `unknown` (`n/a`) | Court: `pending_or_unknown` (`n/a`) — n/a

### Unresolved Questions & Blockers
- What was the final disposition and sentence for Mark S. Salisbury in Jackson County Circuit Court (Prosecutor No. 095458988)?
- Were charges ever filed against 'Suspect #2' (B/M/57) for murder or abandonment/burning of a corpse?
- What was the final court disposition and sentence for Mark S. Salisbury (Prosecutor No. 095458988) in 16th Judicial Circuit Court?
- Why did KCPD's 2020 Socrata snapshot retain firearm_flag_raw='false' and the body-dump intersection ('E 9TH ST and HARDESTY AVE', missing coordinates) after the Feb. 3, 2020 autopsy and June 22, 2020 murder complaint established a .380 shooting at 5209 Independence Ave #2?

---

## Case 9: `KCPD:KC20009618` (E1_non_09A_justifiable_homicide_09C)
- **Incident Date / Time:** `2020-02-07` (`01:07`)
- **Reported Location:** `E 8TH ST and GLADSTONE AVE` (`KANSAS CITY`, `64108`, Div `EPD`, Beat `313`)
- **Source Code & Scope Flag:** `09C` | `Candidate - verify inclusion` | `8` rows (`SUS DEC (1); VOD (5); VOD SWM (2)`)
- **Reviewed States:** Inclusion=`included_separate_category_09C_justifiable_police_shooting` | Victim=`verified` | Medical=`unknown` | Police=`verified` | Prosecutor=`unknown` | Court=`unknown`
- **Effort & Verification:** Research `175s` + Verifier `85s` | Corrections/Downgrades=`0` | Claims=`{'verified': 4}`

**Case Narrative Summary:** Just after 1:00 a.m. on Friday, February 7, 2020 (reported at 01:07), KCPD officers responded to the 3200 block of Independence Avenue on a report of a man carrying a rifle, located 37-year-old Joshua Downing (White male) in the street at E. 6th Street and Gladstone Boulevard, and commanded him to drop the weapon. After less-lethal beanbag rounds failed to disarm him, officers followed Downing on foot to E. 8th Street and Gladstone Avenue in Kansas City, Missouri, where multiple KCPD officers fatally shot him when he turned and pointed his rifle at them; he was pronounced dead at an area hospital. In Socrata vsgj-uufz, KC20009618 is coded under NIBRS 09C ('Officer Involved Shooting - Fatal' / 'Justifiable Homicide') with 1 deceased suspect row ('SUS DEC' W/M/37, row 32) and 7 involved-officer rows ('VOD' / 'VOD SWM'), placing it in the separate fatal-police-shooting / 09C justifiable homicide category rather than 09A criminal murder.

**Verifier Audit Summary:** Independently verified against all 8 Socrata vsgj-uufz rows for KC20009618 (ibrs=09C, 'Officer Involved Shooting - Fatal' / 'Justifiable Homicide'), US Census Geocoder confirming (39.103326, -94.546061) at E 8th St & Gladstone Ave lies inside Kansas City city (GEOID 2938000), Jackson County (GEOID 29095), and full inspection of both Northeast News articles (2020-02-07 quoting KCPD spokesperson Doaa El-Ashkar and 2020-12-31 year-end homicide compilation). Confirmed 1 deceased subject (Joshua Downing, 37, W/M, row 32 SUS DEC) and 7 involved KCPD officer rows (5 VOD, 2 VOD SWM), and verified inclusion in the separate 09C justifiable police shooting category.

### Deceased Victims
- `VIC:KCPD:KC20009618:1`: **Joshua Downing** (`confirmed_named`) | W/M/age 37 | Death: `2020-02-07` | Cause: `Not publicly released (ME restricted)` | Weapon: `Firearm — police lethal force after less-lethal beanbag rounds failed and subject pointed a rifle at officers (KCPD firearm_flag=true)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20009618:1`: **Unidentified / Uncharged** | Police: `justifiable_homicide_09c` (`09C Officer Involved Shooting - Fatal / Justifiable Homicide; SUS DEC (row 32) & 7 VOD / VOD SWM officer rows (rows 47, 51, 57, 63, 69, 76, 127)`) | Prosecutor: `unknown` (`n/a`) | Court: `pending_or_unknown` (`n/a`) — No criminal court case filed.

### Unresolved Questions & Blockers
- On what date did the Jackson County Prosecutor's Office complete its formal use-of-force review of the February 7, 2020 fatal police shooting of Joshua Downing?
- On what date did the Jackson County Prosecutor's Office conclude its formal review of the Feb. 7, 2020 fatal police shooting of Joshua Downing (KC20009618)?

---

## Case 10: `KCPD:KC20041259` (F1_mixed_09A_and_excluded_09D_murder_suicide)
- **Incident Date / Time:** `2020-06-22` (`09:58`)
- **Reported Location:** `9400  NE 91ST ST` (`KANSAS CITY`, `64157`, Div `SCP`, Beat `643`)
- **Source Code & Scope Flag:** `09A` | `Candidate - verify inclusion` | `2` rows (`SUS DEC (1); VIC DEC (1)`)
- **Reviewed States:** Inclusion=`included_kcmo_homicide` | Victim=`verified` | Medical=`unknown` | Police=`verified` | Prosecutor=`verified` | Court=`verified`
- **Effort & Verification:** Research `185s` + Verifier `90s` | Corrections/Downgrades=`1` | Claims=`{'verified': 5}`

**Case Narrative Summary:** On Monday, June 22, 2020 (reported at 09:56), KCPD officers responded to a domestic disturbance and reports of gunshots at a residence in the 9400 block of NE 91st Street in the Clay County (Northland) portion of Kansas City, Missouri (ZIP 64157). Following a multi-hour standoff, officers entered the home and found married couple Jamie Lynn Williams (48, White female) and Damone E. Williams (45, Black male) both dead from gunshot wounds; investigators determined that Damone Williams fatally shot his wife Jamie Williams before taking his own life. In Socrata vsgj-uufz, KC20041259 contains both 09A Murder rows (rows 225 and 389) and excluded 09D 'DV Related Suicide' rows (rows 72 and 295) for the pair; separating 'VIC DEC' (Jamie Lynn Williams, 1 included 09A homicide victim) from 'SUS DEC' (Damone E. Williams, 09D suicide offender) prevents double-counting the perpetrator's suicide as a homicide victim.

**Verifier Audit Summary:** Independently verified against all 4 Socrata vsgj-uufz rows for KC20041259 (rows 72, 225, 295, 389), US Census Geocoder confirming (39.257217, -94.461581) at 9400 NE 91st St (ZIP 64157) lies inside Kansas City city (GEOID 2938000) within Clay County (GEOID 29047), and full inspection of Tony's Kansas City (reproducing FOX4KC's report 'Police identify 2 killed in apparent murder-suicide in the Northland'), Gun Memorial, and the News-Press NOW obituary preview. Confirmed the mixed 09A/09D deduplication rule: Jamie Lynn Cox Craig Williams (48, W/F, VIC DEC in 09A row 225 and excluded 09D row 72) is the sole criminal homicide victim, while husband Damone Williams (45, B/M, SUS DEC in 09A row 389 and excluded 09D row 295) is the deceased murder-suicide offender. Applied 1 provenance refinement on CLM:KC20041259:04 noting that 'Damone Williams' is verified in the full FOX4KC text on Tony's KC while the middle initial 'E.' comes from the HTTP-403 AP News search summary.

### Deceased Victims
- `VIC:KCPD:KC20041259:1`: **Jamie Lynn Cox Craig Williams (Jamie Williams)** (`confirmed_named`) | W/F/age 48 | Death: `2020-06-22` | Cause: `Not publicly released (ME restricted)` | Weapon: `Firearm / domestic shooting (KCPD firearm_flag=true, dv_flag=Y)`

### Defendants & Court Outcomes
- `DEF:KCPD:KC20041259:1`: **Damone Williams (reported as Damone E. Williams in AP summary)** | Police: `exceptional_clearance_offender_death` (`SUS DEC (09A Murder row 389 & 09D DV Related Suicide row 295, B/M/45)`) | Prosecutor: `not_applicable_offender_deceased` (`2020-06-22`) | Court: `not_applicable_offender_deceased` (`n/a`) — Not applicable — offender deceased by suicide at scene on 2020-06-22.

### Unresolved Questions & Blockers
- Why did contemporaneous June 2020 media coverage refer to the deaths of Jamie Williams and Damone Williams as KCMO's '90th and 91st homicides' when Damone Williams was the suspect who died by suicide (09D DV Related Suicide)?
- Did KCPD's official 2020 homicide total (179) exclude Damone Williams ('SUS DEC' in 09A row 389 and 09D row 295) as a suicide while local media initially referred to the pair as homicides #90 and #91?

---
