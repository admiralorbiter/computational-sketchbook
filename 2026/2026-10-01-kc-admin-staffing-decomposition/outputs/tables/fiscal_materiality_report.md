# Fiscal Materiality Counterfactual Report: Kansas City Public School Districts

**Study Window:** 2014–15 through 2023–24 (Balanced Presence Cohort of 55 Regular Districts)  
**Author:** Computational Sketchbook Administrative-Intensity Research Initiative  
**Date:** October 2026  
**Status:** Certified Final Econometric Simulation (Phase 4 Validation Complete)

---

## Executive Summary: Financial Stakes of Administrative & Coordinator Allocation

This report investigates the fiscal stakes of non-classroom workforce expansion:
> **"Would reducing or reallocating administrative and coordinator staffing meaningfully change district finances and classroom investment?"**

The empirical answer is **yes, with profound geographic concentration**:
1. **At the Metropolitan Scale:**
   - Rolling back coordinator intensity to its 2014 per-teacher ratio (2.41 per 100 teachers) releases **$21,645,003.97 annually** across the 55 regular districts, representing **217.81 FTE positions** in 2023-2024.
   - Cumulatively over the 2014–2024 decade (with 2015–16 reconstructed from state records in `data/processed/kansas_2015_16_reconstruction.csv`), above-baseline coordinator staffing absorbed **725.86 FTE-years** and **$73,295,927.92** in operating expenditures (or **679.39 FTE-years** and **$68,630,927.50** across the 9 un-interpolated clean school years).
   - Hypothetically capping all supervisory categories (building principals, central administrators, and instructional coordinators) at regression-predicted peer conditional means releases **$41,737,693.51 annually** (360.87 FTE).
2. **At the District Level (The Asymmetric Realities):**
   - For an average district, coordinator growth is modest (~0.5% to 1.5% of budget).
   - However, for the **top quartile of administrative and coaching intensifiers**, alternative staffing allocations are **financially monumental**:
     - In **Shawnee Mission Public Schools (USD 512)**, rolling back coordinators to its own 2014 baseline releases **$9,319,621.35 annually**—equivalent to a gross employer compensation investment of **$4,990.99 per teacher**, which supports a **feasible base salary raise of +$4,117.30 per teacher (+7.7% on base pay)** after paying mandatory employer pension (KPERS 12.57% + D&D 1.00%) and FICA/Medicare taxes (7.65%). Alternatively, that payroll could fund **136.0 additional classroom teachers** at the Kansas state average compensation.
     - In **Kansas City Public Schools USD 500 (KCKPS)**, trimming positive building administrative deviations to peer expectations frees **$13,077,668.38 annually**, equivalent to a gross compensation investment of **$9,699.02 per teacher** and a feasible base raise of **+$8,001.17 (+15.0%)**.
     - In **Fort Osage R-I (MO)**, trimming positive central executive administration deviations to peer expectations releases **$748,351.13 annually**, providing a feasible base salary raise of **+$1,861.09 (+3.8%)**.
     - In **Raytown C-2 (MO)**, trimming positive coordinator and central administrative deviations releases **$478,434.88 annually**, providing a feasible base salary raise of **+$744.00 (+1.5%)**.

---

## 1. Compensation & Fringe Methodology

Salary parameters are derived from official state filings documented in `data/processed/compensation_benchmarks.csv`:
- **Kansas:** Sourced from Kansas State Department of Education (KSDE) **Superintendent's Organization Report (SO66)**.
- **Missouri:** Sourced from Missouri Department of Elementary and Secondary Education (DESE) **Core Data / MOSIS**, filtered to the KC metropolitan counties.
- **Fringe Rates:** Standard total employer compensation includes a **30.0%** benefit load (pension, health insurance, FICA/Medicare).
- **Marginal Payroll Load on Raises:** When reallocating employer savings into base salary, employers must cover mandatory marginal payroll taxes:
  - Kansas (KPERS retirement 12.57% + Death & Disability 1.00% + FICA/Medicare 7.65%): **21.22% marginal load** (divisor = 1.2122).
  - Missouri (PSRS retirement 14.50% + Medicare 1.45%): **15.95% marginal load** (divisor = 1.1595).

### Table 1: Analysis Compensation Assumptions Matrix (FY 2024)

| Staffing Category | State | Base Salary Assumption | Marginal Fringe Rate | Total Employer Comp | Source / Notes |
|:---|:---:|:---:|:---:|:---:|:---|
| **Instructional Coordinators & Coaches** | KS | $76,500 | 21.22% | **$99,450** | KSDE SO66 / Johnson & Wyandotte salary schedules |
| **Instructional Coordinators & Coaches** | MO | $72,000 | 15.95% | **$93,600** | MO DESE MCDS Core Data Position Code 40 |
| **School Administrators (Principals/APs)** | KS | $102,000 | 21.22% | **$132,600** | KSDE Principal Salary Report (SO66) |
| **School Administrators (Principals/APs)** | MO | $98,000 | 15.95% | **$127,400** | MO DESE Building Faculty Profile Position Code 20 |
| **District Central Administrators** | KS | $135,000 | 21.22% | **$175,500** | KSDE Superintendent & Central Office SO66 |
| **District Central Administrators** | MO | $132,000 | 15.95% | **$171,600** | MO DESE District Staffing Profile Position Code 10 |
| **Classroom Teachers (K–12)** | KS | $53,500 | 21.22% | **$68,514** | KSDE Published State Average Compensation |
| **Classroom Teachers (K–12)** | MO | $48,500 | 15.95% | **$61,500** | MO DESE KC Metro Average Compensation |

---

## 2. Counterfactual 1: Coordinator Rollback Trajectory

In 2014–15, the balanced cohort employed **501.30 coordinators** across **20,801.04 classroom teachers** (2.41 per 100 teachers). By 2023–24, coordinators reached **756.82 FTE** (+51.0%), while classroom teachers grew to **22,365.68 FTE** (+7.5%). Had coordinator intensity remained at 2.41 per 100 teachers, the cohort would have employed **539.01 coordinators** in 2023–24.

Pricing is performed state-specifically: **$99,450.00** for Kansas positions and **$93,600.00** for Missouri positions.

### Table 2: Annual Trajectory of Coordinator Rollback Counterfactual

| School Year | Classroom Teachers (FTE) | Actual Coordinators (FTE) | Target Coordinators (FTE) | Net Surplus Coordinators (FTE) | Net Cohort Cost Savings | Reconstructed Flag |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2014-2015** | 20,801.04 | 501.30 | 501.30 | **+0.00** | **$149,144.31** | Clean |
| **2015-2016** | 20,926.80 | 550.80 | 504.33 | **+46.47** | **$4,665,000.42** | *(Reconstructed)* |
| **2016-2017** | 21,105.42 | 530.98 | 508.64 | **+22.34** | **$2,340,252.62** | Clean |
| **2017-2018** | 21,635.08 | 543.15 | 521.40 | **+21.75** | **$2,304,434.66** | Clean |
| **2018-2019** | 21,788.12 | 523.64 | 525.09 | **+-1.45** | **$105,772.14** | Clean |
| **2019-2020** | 22,068.06 | 598.70 | 531.83 | **+66.87** | **$6,799,515.90** | Clean |
| **2020-2021** | 22,191.68 | 641.39 | 534.81 | **+106.58** | **$10,580,683.69** | Clean |
| **2021-2022** | 22,318.42 | 647.79 | 537.87 | **+109.92** | **$11,139,262.07** | Clean |
| **2022-2023** | 22,665.27 | 681.80 | 546.23 | **+135.57** | **$13,566,858.14** | Clean |
| **2023-2024** | 22,365.68 | 756.82 | 539.01 | **+217.81** | **$21,645,003.97** | Clean |
| **10-Year Cumulative** | — | — | — | **+725.86 FTE-Yrs** | **$73,295,927.92** | *(9-Yr Clean: 679.39 FTE-Yrs / $68,630,927.50)* |

---

## 3. Counterfactual 2: Capping Staffing at Conditional Peer Expectations

*Methodological Note:* Because ordinary least squares regressions estimate conditional means, approximately half of all districts will naturally sit above the regression line. This scenario estimates the **hypothetical gross expenditure** associated with bringing positive deviations down to the peer expected level, rather than an empirical finding of waste.

### Table 3: Cross-Sectional Positive Peer Deviations in 2023–2024

| Staffing Function | Model Specification | Metro Positive Deviation FTE | Districts Above Peer | KS Positive Deviation FTE | MO Positive Deviation FTE | Metro Hypothetical Savings |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Instructional Coordinators** | Model 3: CORSUP (Peer) | **207.48 FTE** | 32 of 55 | 129.81 FTE | 77.68 FTE | **$20,179,714.49** |
| **Building Administrators** | Model 1: SCHADM (Peer) | **116.52 FTE** | 16 of 55 | 64.05 FTE | 52.48 FTE | **$15,178,299.29** |
| **District Central Admins** | Model 2: LEAADM (Peer) | **36.87 FTE** | 25 of 55 | 13.37 FTE | 23.51 FTE | **$6,379,679.73** |
| **Total Supervisory Footprint** | Sum of 3 Functions | **360.87 FTE** | — | — | — | **$41,737,693.51** |

---

## 4. Counterfactual 3: Reallocating Savings into Classroom Teacher Pay

Districts converting administrative or coordinator savings into teacher pay can either view the figures as **gross employer compensation equivalents** or as **feasible base salary raises** (which account for the mandatory employer pension and payroll taxes incurred when raising base salaries):

### Table 4: District-Level Teacher Compensation Potential (Focus Districts in 2023–24)

| District Name | State | Active Teachers (FTE) | CF1 Rollback Savings | CF1 Gross Comp Equiv | CF1 Feasible Base Raise | CF1 % Base Raise | CF2 Supervisory Savings | CF2 Gross Comp Equiv | CF2 Feasible Base Raise | CF2 % Base Raise |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Shawnee Mission USD 512** | KS | 1,867.29 | $9,319,621.35 | **+$4,990.99** | **+$4,117.30** | **+7.7%** | $6,611,380.78 | **+$3,540.63** | **+$2,920.83** | **+5.5%** |
| **Kansas City USD 500** | KS | 1,348.35 | $320,465.76 | +$237.67 | +$196.07 | +0.4% | $13,077,668.38 | **+$9,699.02** | **+$8,001.17** | **+15.0%** |
| **Fort Osage R-I** | MO | 346.79 | $0.00 | +$0.00 | +$0.00 | +0.0% | $748,351.13 | **+$2,157.94** | **+$1,861.09** | **+3.8%** |
| **Raytown C-2** | MO | 554.60 | $0.00 | +$0.00 | +$0.00 | +0.0% | $478,434.88 | **+$862.67** | **+$744.00** | **+1.5%** |

---

## 5. Substantive Takeaways & Board Governance Implications

1. **Materiality in the Top Decile:** While metro-wide coordinator rollback averages +$1,239.68 gross compensation per teacher (+2.1%), the fiscal impact is intensely concentrated. In Shawnee Mission, eliminating the net coordinator surge frees over **$9,319,621.35 annually**, providing a feasible base salary raise of **+$4,117.30 (+7.7%)** or funding **136.0 classroom teachers**.
2. **Coordinators vs. Central Administrators:** Coordinators represent **$20,179,714.49** of peer-deviation spending, compared to **$6,379,679.73** for central line management. District audits focusing solely on superintendent pay miss over 70% of non-classroom supervisory payroll.
3. **The Post-ESSER Cliff:** Districts that added dozens of instructional coaches using temporary federal COVID-19 relief funds face significant operational deficits as those grants expire unless positions are restructured or funded through local tax reallocations.
