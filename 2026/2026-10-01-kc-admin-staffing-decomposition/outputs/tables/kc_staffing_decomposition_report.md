# Kansas City Administrative Staffing Intensity Decomposition
## Phase 1.1 Semantic Calibration & Calibrated Decomposition Report

**Geographic Universe:** 9-County Mid-America Regional Council (MARC) Metropolitan Area  
**Primary Analytical Population:** Balanced Regular District Cohort (55 Continuous Districts)  
**Calibration Status:** Phase 1.1 Verified (Zero-Negative Assertions, Discontinuity Isolation, Student-Support Quarantine)  

---

## 1. Executive Summary: The Calibrated Findings

Build 1 revealed a striking phenomenon that survives rigorous measurement calibration:
**The primary driver of non-classroom workforce expansion in Kansas City–area public schools has NOT been traditional central-office administration, but a dramatic, disproportionate expansion in instructional coordination, curriculum supervision, and instructional coaching capacity.**

In the matched cohort of 55 regular school districts present across the entire modern CCD reporting era:
* **Enrollment:** 320,611 → 316,617 (**-1.2%**, -3,994 pupils)
* **Classroom Teachers:** 20,801.0 → 22,247.9 (**+7.0%**, +1,446.9 FTE)
* **District Central Administrators (LEAADM):** 175.8 → 177.7 (**+1.1%**, +1.9 FTE — virtually flat)
* **Instructional Coordinators & Coaches (CORSUP):** 501.3 → 751.2 (**+49.8%**, +249.9 FTE — massive expansion)
* **Combined Broad Administration (SCHADM + LEAADM + CORSUP):** 1,732.2 → 2,011.3 (**+16.1%**, +279.1 FTE)
* **Broad Administrative Intensity per 1,000 Pupils:** 5.40 → 6.35 (**+17.6%**)

Instructional coordinators accounted for **89.5% of all net administrative and supervisory FTE growth** across the balanced regular district cohort between 2014–15 and 2024–25.

---

## 2. Measurement Audits & Retractions (Phase 1.1 Calibration)

### 2.1 Retraction of the Student-Support (+253%) Finding
* **The Flaw in Build 1:** In early CCD releases (2004–2013), broader student support was unpopulated in federal extracts, leading the build script to fall back to `counselors_fte` (`student_support_staff_fte.fillna(counselors_fte)`). In 2014–15, the broader field was populated with all student support staff, creating a phantom jump from 737 to 2,353. Furthermore, in 2016–17 through 2018–19, NCES extracts recorded exactly `0.0` for student support across both states despite active counseling forces.
* **The Correction:** The +253% claim is formally **retracted**. Student support staff is classified as **NOT longitudinally comparable** across the 20-year span due to reporting voids.
* **The Clean Pupil Support Benchmark:** Guidance Counselors (`counselors_fte`), which was stably reported across all 21 years, grew from 755.0 to 909.0 FTE (**+20.4%**) over 20 years, and from 779.8 to 909.0 FTE (**+16.6%**) over 10 years, tracking student population shifts without explosive distortion.

### 2.2 The 2024–25 Kansas School Administrator (SCHADM) Discontinuity
* **The Break:** Kansas school administrator FTE dropped from 611.6 in 2023–24 to 386.7 in 2024–25 (-36.8% statewide).
* **The Mechanism:** Cross-validation against KSDE SO66 reports and statewide CCD tables confirms that in 2024–25, Kansas reported **only Head Principals** under the NCES "School administrators" category, omitting Assistant Principals (who had been included in all prior years).
* **The Analytical Guardrail:** We provide both the 2014–15 to 2024–25 benchmark and the pre-break 2014–15 to 2023–24 benchmark (where SCHADM grew +23.7%, scaling with building additions). All downstream regressions must include state × year fixed effects or sensitivity exclusions for Kansas in 2024–25.

### 2.3 Missouri LEAADM vs. CORSUP Reclassification (2013–14 to 2014–15)
* In Missouri, between 2013–14 and 2014–15, district administrators fell by -102.8 FTE while instructional coordinators rose by +64.9 FTE.
* Combined Central Management + Coordination (`LEAADM + CORSUP`) remained steady (455.0 → 417.2 FTE, -8.3%).
* **Rule:** For 20-year longitudinal analyses, `LEAADM + CORSUP` is the only robust, reclassification-proof central aggregate.

---

## 3. Balanced Regular Cohort Decomposition (55 Districts)

| Cohort Timeframe | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Total Admin $\Delta$ | Admin/1k Start | Admin/1k End | $\Delta$ Admin/1k (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Balanced 55 Regular Districts (2014-15 to 2024-25)** | 320,611 → 316,617 (-1.2%) | 20,801.0 → 22,247.9 (+7.0%) | 1,055.1 → 1,082.3 (+27.2) | 175.8 → 177.7 (+2.0) | **501.3 → 751.2 (+249.9, +49.9%)** | 1,732.2 → 2,011.3 (+16.1%) | 5.40 | **6.35** | **+17.6%** |
| **Balanced 55 Regular Districts (2014-15 to 2023-24 [Pre-KS-Break])** | 320,611 → 316,841 (-1.2%) | 20,801.0 → 22,365.7 (+7.5%) | 1,055.1 → 1,305.0 (+249.8) | 175.8 → 197.7 (+22.0) | **501.3 → 756.8 (+255.5, +51.0%)** | 1,732.2 → 2,259.5 (+30.4%) | 5.40 | **7.13** | **+32.0%** |
| **Balanced 55 Regular Districts (2004-05 to 2024-25)** | 309,287 → 316,617 (+2.4%) | 20,595.0 → 22,247.9 (+8.0%) | 1,000.0 → 1,082.3 (+82.3) | 437.0 → 177.7 (-259.3) | **186.0 → 751.2 (+565.2, +303.9%)** | 1,623.0 → 2,011.3 (+23.9%) | 5.25 | **6.35** | **+21.1%** |

---

## 4. Balanced Cohort State-Level Decompositions

### 4.1 Ten-Year Period (2014–15 to 2024–25)
*Note: Kansas 2024–25 SCHADM reflects assistant principal omission.*

| State | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **KS** | 144,702 → 144,571 (-0.1%) | 9,419.4 → 10,157.7 (+7.8%) | 481.5 → 385.3 (-96.2) | 62.2 → 49.4 (-12.8) | **252.5 → 454.9 (+202.4, +80.2%)** | 5.50 | **6.15** |
| **MO** | 175,909 → 172,046 (-2.2%) | 11,381.6 → 12,090.2 (+6.2%) | 573.6 → 697.0 (+123.3) | 113.5 → 128.3 (+14.8) | **248.8 → 296.4 (+47.6, +19.1%)** | 5.32 | **6.52** |

### 4.2 Pre-Break Period (2014–15 to 2023–24)
*Reflects complete reporting before the Kansas SCHADM reporting break.*

| State | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **KS** | 144,702 → 144,720 (+0.0%) | 9,419.4 → 10,219.2 (+8.5%) | 481.5 → 608.6 (+127.1) | 62.2 → 74.0 (+11.8) | **252.5 → 461.3 (+208.8, +82.7%)** | 5.50 | **7.90** |
| **MO** | 175,909 → 172,121 (-2.2%) | 11,381.6 → 12,146.5 (+6.7%) | 573.6 → 696.4 (+122.7) | 113.5 → 123.7 (+10.2) | **248.8 → 295.5 (+46.7, +18.8%)** | 5.32 | **6.48** |

---

## 5. Major District Mechanical Ledger (2014–15 to 2024–25)

$$\Delta \text{Total Non-Teaching} = \Delta \text{Principals} + \Delta \text{Central Admin} + \Delta \text{Coordinators} + \Delta \text{Counselors} + \Delta \text{Paras} + \Delta \text{Other}$$

| District | State | Enrollment $\Delta$ | Teachers $\Delta$ | $\Delta$ Principals | $\Delta$ Central | $\Delta$ Coord | $\Delta$ Counselors | $\Delta$ Paras | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BELTON 124** | N/A | -14.9% | -2.6% | +2.9 | +0.0 | **+0.7** | -1.0 | +17.4 | 5.60 | **7.43** |
| **BLUE SPRINGS R-IV** | N/A | +1.3% | +11.6% | +13.0 | +3.0 | **+0.6** | +18.0 | -9.5 | 4.94 | **6.01** |
| **Blue Valley** | N/A | -0.7% | +15.0% | -19.7 | -4.0 | **+11.7** | +4.0 | -39.9 | 4.81 | **4.31** |
| **CENTER 58** | N/A | -11.3% | -6.1% | +2.2 | +2.3 | **-0.1** | +3.2 | +10.0 | 7.92 | **10.83** |
| **FORT OSAGE R-I** | N/A | -7.3% | +4.7% | +2.0 | +0.5 | **-6.0** | +2.0 | -6.4 | 5.84 | **5.56** |
| **GRAIN VALLEY R-V** | N/A | +13.0% | +31.7% | +8.3 | +0.0 | **+5.6** | +2.0 | +10.2 | 4.72 | **7.24** |
| **GRANDVIEW C-4** | N/A | -16.0% | -9.4% | -2.1 | +0.0 | **+4.0** | -2.0 | +3.2 | 6.42 | **8.17** |
| **Gardner Edgerton** | N/A | +2.2% | +19.9% | -4.0 | +0.0 | **+0.2** | +4.0 | +45.8 | 4.85 | **4.10** |
| **HICKMAN MILLS C-1** | N/A | -24.8% | -19.6% | -2.6 | +0.5 | **+9.9** | +0.0 | -48.8 | 5.08 | **8.29** |
| **INDEPENDENCE 30** | N/A | -5.3% | +8.4% | +9.0 | +3.0 | **-3.0** | +5.3 | +25.1 | 5.44 | **6.38** |
| **KANSAS CITY 33** | N/A | -2.0% | +4.7% | -10.2 | -0.5 | **+14.6** | -11.5 | -118.7 | 6.14 | **6.52** |
| **KEARNEY R-I** | N/A | -2.2% | +4.4% | +2.0 | -1.0 | **+2.8** | +3.0 | +30.1 | 5.00 | **6.24** |
| **Kansas City** | N/A | -2.7% | -2.8% | -17.7 | -1.0 | **+14.1** | +16.4 | -23.2 | 9.25 | **9.28** |
| **LEE'S SUMMIT R-VII** | N/A | +0.1% | +2.8% | +15.5 | +2.0 | **-11.8** | +10.0 | -18.2 | 4.54 | **4.85** |
| **LIBERTY 53** | N/A | -1.5% | +12.0% | +8.8 | +3.5 | **+10.5** | +10.3 | +23.8 | 4.15 | **6.14** |
| **Lansing** | N/A | +4.9% | -10.9% | -2.0 | -1.0 | **+11.5** | +4.7 | +21.0 | 4.39 | **7.43** |
| **Leavenworth** | N/A | -12.8% | +0.2% | -2.0 | -1.7 | **+6.0** | +0.0 | +3.3 | 7.74 | **10.38** |
| **NORTH KANSAS CITY 74** | N/A | +7.0% | +16.6% | +26.6 | +0.5 | **+22.9** | +5.5 | +150.9 | 3.77 | **5.88** |
| **Olathe** | N/A | -3.8% | +10.4% | -24.7 | -4.1 | **+30.1** | +26.4 | +4.8 | 4.47 | **4.69** |
| **PARK HILL** | N/A | +9.3% | +23.1% | +17.0 | +1.0 | **+5.2** | +8.4 | +62.0 | 3.80 | **5.42** |
| **PLATTE CO. R-III** | N/A | +10.3% | +12.7% | +4.0 | -2.0 | **-3.2** | +0.9 | +31.0 | 7.13 | **6.17** |
| **Piper-Kansas City** | N/A | +38.4% | +62.8% | +0.0 | +0.0 | **+9.0** | +5.0 | +17.9 | 4.39 | **6.34** |
| **RAYMORE-PECULIAR R-II** | N/A | +4.9% | +11.6% | +4.8 | +1.0 | **-0.6** | +3.6 | +9.2 | 5.32 | **5.89** |
| **RAYTOWN C-2** | N/A | -15.8% | -8.8% | +5.1 | -2.0 | **-5.3** | +1.0 | -59.4 | 6.72 | **7.68** |
| **Shawnee Mission Pub Sch** | N/A | -3.5% | +4.3% | +2.8 | +3.0 | **+88.4** | -1.8 | +202.2 | 3.66 | **7.35** |
| **Spring Hill** | N/A | +75.0% | +77.3% | +7.0 | -2.0 | **+9.7** | +5.5 | -16.8 | 5.37 | **5.58** |
| **Turner-Kansas City** | N/A | -7.0% | +1.6% | -6.0 | +0.0 | **-4.7** | -0.8 | -22.8 | 7.58 | **5.43** |
