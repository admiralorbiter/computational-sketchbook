# Kansas City Administrative Staffing Intensity Decomposition
## Phase 1.1 Semantic Calibration & Calibrated Decomposition Report

**Geographic Universe:** 9-County Mid-America Regional Council (MARC) Metropolitan Area  
**Primary Analytical Population:** Balanced Regular District Cohort (55 Continuous Districts)  
**Calibration Status:** Phase 1.1 Verified (Zero-Negative Assertions, Discontinuity Isolation, Student-Support Quarantine)  

---

## 1. Executive Summary: The Calibrated Findings

Build 1 revealed a striking phenomenon that survives rigorous measurement calibration:

**The primary driver of non-classroom workforce expansion in Kansas City–area public schools has NOT been traditional central-office line administration, but a dramatic, disproportionate expansion in instructional coordination, curriculum supervision, and instructional coaching capacity.**

### 1.1 Primary Benchmark: Clean Pre-Break Modern Era (2014–15 → 2023–24)
Using the clean 10-year pre-break benchmark across the matched cohort of 55 regular school districts present throughout the modern CCD reporting era:
* **Enrollment:** 320,611 → 316,841 (**-1.2%**, -3,770 pupils — virtually flat)
* **Classroom Teachers:** 20,801.0 → 22,365.7 (**+7.5%**, +1,564.7 FTE)
* **District Central Administrators (`LEAADM`):** 175.8 → 197.7 (**+12.5%**, +22.0 FTE)
* **School Building Administrators (`SCHADM`):** 1,055.1 → 1,305.0 (**+23.7%**, +249.8 FTE — scaling with school facilities)
* **Instructional Coordinators & Coaches (`CORSUP`):** 501.3 → 756.8 (**+51.0%**, +255.5 FTE — massive expansion)
* **Broad Supervisory Workforce (`SCHADM + LEAADM + CORSUP`):** 1,732.2 → 2,259.5 (**+30.4%**, +527.3 FTE)
* **Supervisory Intensity per 1,000 Pupils:** 5.40 → 7.13 (**+32.0%**)

### 1.2 Core Substantive Takeaways
1. **Instructional Coordinators Grew at 4x the Rate of Central Administration:**
   Coordinator staffing increased by **+51.0%**, compared to **+12.5%** for district central administrators.
2. **Coordinators Drove ~48.5% of Total Net Supervisory Growth:**
   Of the +527.33 net FTE added to the broad supervisory workforce between 2014–15 and 2023–24, coordinators accounted for **48.45%** (+255.52 FTE), approximately tied with building administration (+249.83 FTE, **47.38%**). Traditional central administration accounted for only **4.17%** (+21.98 FTE).
   *(Note: The initial Build 1 claim that coordinators accounted for 89.5% was an artifact of using the broken 2024–25 Kansas endpoint in the denominator and has been formally retracted.)*
3. **The Divergence is Central Coordination vs. Line Administration:**
   School building administration grew at +23.7% (tracking school reorganizations and student safety demands), while district-level line leadership grew at +12.5%. The standout growth occurred specifically in instructional coordination, coaching, and program supervision.

---

## 2. Measurement Audits, Anomaly Isolations, & Retractions

### 2.1 Kansas 2024–25 Systematic Reporting Break (Affects BOTH SCHADM and LEAADM)
* **The Break:** In Kansas, between 2023–24 and 2024–25, reported school building administrators fell by **-36.8%** (611.6 → 386.7 FTE) and district central administrators fell by **-32.0%** (77.0 → 52.4 FTE), while instructional coordinators remained stable (462.3 → 455.9 FTE, -1.4%).
* **The Mechanism:** Cross-validation against Kansas State Department of Education (KSDE) official SO66 licensed personnel totals reveals that statewide superintendent FTE was unchanged (262.5 FTE), assistant superintendents were virtually flat (97.3 → 97.0 FTE), head principals grew (1,229.3 → 1,232.4 FTE), and assistant principals grew (752.2 → 758.2 FTE). There was **zero underlying personnel collapse**. Kansas CCD line 059 omitted assistant principals and certain central directors in 2024–25.
* **Analytical Treatment:** Tagged as `flag_ks_admin_reporting_break_2425`. The clean pre-break window (**2014–15 to 2023–24**) serves as the primary benchmark. All primary Phase 2 models exclude Kansas 2024–25 from `SCHADM` and `LEAADM` estimation.

### 2.2 Retraction of the Student-Support (+253%) Artifact
* **The Flaw in Build 1:** In early CCD years (2004–2013), broader student support was unpopulated in federal extracts, leading the build script to fall back to `counselors_fte`. In 2014–15, the broader category was populated, creating a phantom jump from 737 to 2,353. Furthermore, in 2016–17 through 2018–19, NCES extracts recorded exactly `0.0` for student support across both states despite active counseling forces.
* **The Correction:** The +253% claim is formally **retracted**. Broader student support is classified as **FAIL (STOPPING RULE)** for 20-year modeling.
* **The Clean Pupil Support Benchmark:** Guidance Counselors (`counselors_fte`), which was stably reported across all 21 years:
  - Balanced 55 cohort (2014–15 → 2023–24): 743.9 → 871.1 FTE (**+17.1%**, +127.2 FTE).
  - Dynamic universe (2014–15 → 2024–25): 779.8 → 909.0 FTE (**+16.6%**, +129.2 FTE).
  - Counselors tracked student population needs steadily without explosive distortion.

### 2.3 Missouri LEAADM vs. CORSUP Reclassification (2013–14 to 2014–15)
* In Missouri, between 2013–14 and 2014–15, district administrators fell by -102.8 FTE while instructional coordinators rose by +64.9 FTE.
* Combined Central Management + Coordination (`LEAADM + CORSUP`) remained steady (455.0 → 417.2 FTE, -8.3%).
* **Rule:** For cross-era comparisons across 2014, `LEAADM + CORSUP` is the only robust aggregate.

### 2.4 Kansas 2006–2009 Discontinuity Downgrades 20-Year Combined Series to AMBER
* In Kansas, combined `LEAADM + CORSUP` dropped from 286 FTE in 2005–06 to 88, 93, and 95 FTE in 2006–07 through 2008–09 before jumping back to 314 FTE in 2009–10.
* A whole reporting tier went unrecorded in Kansas for three years. Therefore, the 20-year combined series (`central_mgmt_and_coordinators_fte`) is downgraded from GREEN to **AMBER**, requiring reconciliation before 2004–2024 panel modeling.

---

## 3. Balanced Regular Cohort Decomposition (55 Districts)

| Cohort Timeframe | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Total Admin $\Delta$ | Admin/1k Start | Admin/1k End | $\Delta$ Admin/1k (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Balanced 55 Regular Districts (2014-15 to 2023-24 [Clean Pre-Break Benchmark])** | 320,611 → 316,841 (-1.2%) | 20,801.0 → 22,365.7 (+7.5%) | 1,055.1 → 1,305.0 (+249.8) | 175.8 → 197.7 (+22.0) | **501.3 → 756.8 (+255.5, +51.0%)** | 1,732.2 → 2,259.5 (+30.4%) | 5.40 | **7.13** | **+32.0%** |
| **Balanced 55 Regular Districts (2014-15 to 2024-25 [Subject to KS Break])** | 320,611 → 316,617 (-1.2%) | 20,801.0 → 22,247.9 (+7.0%) | 1,055.1 → 1,082.3 (+27.2) | 175.8 → 177.7 (+2.0) | **501.3 → 751.2 (+249.9, +49.9%)** | 1,732.2 → 2,011.3 (+16.1%) | 5.40 | **6.35** | **+17.6%** |
| **Balanced 55 Regular Districts (2004-05 to 2024-25 [AMBER: KS 2006-09 Void])** | 309,287 → 316,617 (+2.4%) | 20,595.0 → 22,247.9 (+8.0%) | 1,000.0 → 1,082.3 (+82.3) | 437.0 → 177.7 (-259.3) | **186.0 → 751.2 (+565.2, +303.9%)** | 1,623.0 → 2,011.3 (+23.9%) | 5.25 | **6.35** | **+21.1%** |

---

## 4. Balanced Cohort State-Level Decompositions

### 4.1 Pre-Break Primary Benchmark (2014–15 to 2023–24)
*Reflects complete reporting before the Kansas 2024–25 reporting break.*

| State | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **KS** | 144,702 → 144,720 (+0.0%) | 9,419.4 → 10,219.2 (+8.5%) | 481.5 → 608.6 (+127.1) | 62.2 → 74.0 (+11.8) | **252.5 → 461.3 (+208.8, +82.7%)** | 5.50 | **7.90** |
| **MO** | 175,909 → 172,121 (-2.2%) | 11,381.6 → 12,146.5 (+6.7%) | 573.6 → 696.4 (+122.7) | 113.5 → 123.7 (+10.2) | **248.8 → 295.5 (+46.7, +18.8%)** | 5.32 | **6.48** |

### 4.2 Ten-Year Horizon (2014–15 to 2024–25)
*Note: Kansas 2024–25 reflects assistant principal & central director omissions.*

| State | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **KS** | 144,702 → 144,571 (-0.1%) | 9,419.4 → 10,157.7 (+7.8%) | 481.5 → 385.3 (-96.2) | 62.2 → 49.4 (-12.8) | **252.5 → 454.9 (+202.4, +80.2%)** | 5.50 | **6.15** |
| **MO** | 175,909 → 172,046 (-2.2%) | 11,381.6 → 12,090.2 (+6.2%) | 573.6 → 697.0 (+123.3) | 113.5 → 128.3 (+14.8) | **248.8 → 296.4 (+47.6, +19.1%)** | 5.32 | **6.52** |

---

## 5. Major District Mechanical Ledger (Pre-Break: 2014–15 to 2023–24)

$$\Delta \text{Total Non-Teaching} = \Delta \text{Principals} + \Delta \text{Central Admin} + \Delta \text{Coordinators} + \Delta \text{Counselors} + \Delta \text{Paras} + \Delta \text{Other}$$

| District | State | Enrollment $\Delta$ | Teachers $\Delta$ | $\Delta$ Principals | $\Delta$ Central | $\Delta$ Coord | $\Delta$ Counselors | $\Delta$ Paras | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BELTON 124** | MO | -15.4% | -8.1% | +1.9 | +1.0 | **+3.8** | +0.0 | +3.8 | 5.60 | **8.21** |
| **BLUE SPRINGS R-IV** | MO | +1.9% | +10.7% | +13.0 | +1.0 | **+6.1** | +18.0 | -22.5 | 4.94 | **6.21** |
| **Blue Valley** | KS | -0.0% | +17.2% | +9.0 | -3.0 | **+0.6** | +7.3 | -39.9 | 4.81 | **5.11** |
| **CENTER 58** | MO | -6.9% | -7.7% | +2.2 | +0.0 | **-2.0** | +1.0 | +9.0 | 7.92 | **8.61** |
| **FORT OSAGE R-I** | MO | -5.8% | +4.8% | +1.9 | +1.2 | **-6.9** | +2.0 | +1.2 | 5.84 | **5.42** |
| **GRAIN VALLEY R-V** | MO | +10.6% | +26.0% | +8.0 | +0.0 | **+5.5** | +2.0 | +3.1 | 4.72 | **7.30** |
| **GRANDVIEW C-4** | MO | -15.4% | -3.8% | -0.1 | +0.0 | **-1.2** | +0.0 | +11.4 | 6.42 | **7.25** |
| **Gardner Edgerton** | KS | +2.9% | +17.3% | +3.0 | +2.0 | **+0.2** | +4.5 | +45.8 | 4.85 | **5.60** |
| **HICKMAN MILLS C-1** | MO | -26.1% | -21.4% | -3.6 | +1.5 | **+8.9** | -2.0 | -43.8 | 5.08 | **8.23** |
| **INDEPENDENCE 30** | MO | -6.0% | +6.2% | +9.0 | +3.0 | **-3.0** | +5.3 | +13.2 | 5.44 | **6.42** |
| **KANSAS CITY 33** | MO | -4.5% | +11.0% | -1.5 | +0.7 | **+20.0** | -7.3 | -101.1 | 6.14 | **7.74** |
| **KEARNEY R-I** | MO | -0.0% | +6.1% | +2.0 | -1.0 | **+3.7** | +3.5 | +31.2 | 5.00 | **6.34** |
| **Kansas City** | KS | -4.5% | -3.1% | +47.3 | +2.0 | **-0.1** | +22.9 | -23.2 | 9.25 | **12.01** |
| **LEE'S SUMMIT R-VII** | MO | -0.3% | +3.3% | +13.0 | +2.0 | **-10.5** | +13.5 | +4.4 | 4.54 | **4.80** |
| **LIBERTY 53** | MO | +1.2% | +14.0% | +12.6 | +2.5 | **-0.2** | +10.0 | +3.5 | 4.15 | **5.32** |
| **Lansing** | KS | +0.3% | -14.5% | +2.0 | -1.0 | **+11.0** | +3.0 | +21.0 | 4.39 | **9.16** |
| **Leavenworth** | KS | -6.8% | +4.7% | +0.0 | -0.7 | **+5.0** | +0.0 | +3.3 | 7.74 | **10.92** |
| **NORTH KANSAS CITY 74** | MO | +5.8% | +18.2% | +22.6 | +1.5 | **+21.5** | +1.1 | +118.2 | 3.77 | **5.74** |
| **Olathe** | KS | -2.4% | +10.1% | +9.0 | +3.0 | **+53.6** | +29.0 | +4.8 | 4.47 | **6.87** |
| **PARK HILL** | MO | +9.1% | +23.1% | +16.0 | +1.0 | **+1.7** | +8.5 | +40.2 | 3.80 | **5.05** |
| **PLATTE CO. R-III** | MO | +8.0% | +10.7% | +4.1 | -4.0 | **+0.8** | -0.1 | +14.0 | 7.13 | **6.81** |
| **Piper-Kansas City** | KS | +35.2% | +60.4% | +6.0 | +3.0 | **+6.0** | +5.0 | +17.9 | 4.39 | **8.65** |
| **RAYMORE-PECULIAR R-II** | MO | +4.6% | +12.6% | +3.4 | +1.0 | **+0.3** | +2.9 | -3.8 | 5.32 | **5.84** |
| **RAYTOWN C-2** | MO | -12.7% | -9.2% | +4.1 | -2.0 | **-6.5** | +0.9 | -57.2 | 6.72 | **7.14** |
| **Shawnee Mission Pub Sch** | KS | -3.7% | +8.7% | +27.5 | +8.0 | **+96.1** | +0.5 | +202.2 | 3.66 | **8.77** |
| **Spring Hill** | KS | +68.2% | +73.6% | +9.0 | -1.0 | **+7.5** | +6.0 | -16.8 | 5.37 | **5.95** |
| **Turner-Kansas City** | KS | -7.6% | +7.0% | +4.0 | +0.0 | **-2.0** | +1.0 | -22.8 | 7.58 | **8.72** |
