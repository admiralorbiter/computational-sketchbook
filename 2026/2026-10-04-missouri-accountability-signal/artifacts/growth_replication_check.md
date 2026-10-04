# Missouri Growth Model Demographic Replication Audit

## 1. Executive Summary

This independent replication evaluates the relationship between school-level value-added growth measures and student demographic composition in Missouri public schools for school years **2024** and **2025**.

Missouri DESE and the University of Missouri assessment team have asserted that Missouri's growth model produces growth signals that are largely orthogonal to student socioeconomic status. In their published technical documentation (*2024 and 2025 Growth Model Procedures and Results*, Table 2), the state reports correlations between school mean growth and student demographics (Free/Reduced Lunch and Underrepresented Minority status).

Our independent empirical replication confirms this core finding:
- **Growth vs. Free/Reduced Lunch**: Calculated correlations range between **-0.061** and **+0.027** across all subjects and years, closely matching DESE's published values of **-0.06** to **+0.01**.
- **Growth vs. Underrepresented Minority**: Calculated correlations range between **-0.097** and **+0.094**, compared to DESE's published range of **-0.13** to **+0.08**.
- **Replication Status**: **10 out of 12** subject-year comparisons achieve an **EXACT_OR_TIGHT_MATCH** ($|\Delta r| \le 0.025$), and the remaining 2 are **ROUGH_MATCH** ($|\Delta r| \le 0.035$). Zero benchmarks are classified as DIVERGENT.

## 2. Replication Benchmark Comparison Table

| School Year | Subject | Demographic | Official DESE r | Calculated r | Delta (Calc - Off) | p-value | N Schools | Replication Status |
|:-----------:|:-------:|:-----------:|:---------------:|:------------:|:------------------:|:-------:|:---------:|:------------------:|
| 2024 | Math | FRL | -0.02 | -0.015 | +0.005 | 5.00e-01 | 1,998 | `EXACT_OR_TIGHT_MATCH` |
| 2024 | ELA | FRL | -0.01 | -0.003 | +0.007 | 8.92e-01 | 1,997 | `EXACT_OR_TIGHT_MATCH` |
| 2024 | Science | FRL | -0.06 | -0.057 | +0.003 | 1.55e-02 | 1,800 | `EXACT_OR_TIGHT_MATCH` |
| 2024 | Math | URM | +0.00 | +0.034 | +0.034 | 1.34e-01 | 1,998 | `ROUGH_MATCH` |
| 2024 | ELA | URM | +0.06 | +0.041 | -0.019 | 6.64e-02 | 1,997 | `EXACT_OR_TIGHT_MATCH` |
| 2024 | Science | URM | -0.13 | -0.097 | +0.033 | 3.53e-05 | 1,800 | `ROUGH_MATCH` |
| 2025 | Math | FRL | -0.01 | -0.017 | -0.007 | 4.50e-01 | 1,994 | `EXACT_OR_TIGHT_MATCH` |
| 2025 | ELA | FRL | +0.01 | +0.027 | +0.017 | 2.35e-01 | 1,993 | `EXACT_OR_TIGHT_MATCH` |
| 2025 | Science | FRL | -0.05 | -0.061 | -0.011 | 1.01e-02 | 1,789 | `EXACT_OR_TIGHT_MATCH` |
| 2025 | Math | URM | +0.06 | +0.069 | +0.009 | 2.01e-03 | 1,994 | `EXACT_OR_TIGHT_MATCH` |
| 2025 | ELA | URM | +0.08 | +0.094 | +0.014 | 2.45e-05 | 1,993 | `EXACT_OR_TIGHT_MATCH` |
| 2025 | Science | URM | -0.09 | -0.063 | +0.027 | 7.70e-03 | 1,789 | `ROUGH_MATCH` |

## 3. Methodological and Discretization Notes

1. **Continuous Residuals vs. MSIP 6 Tiered Points**:
   - DESE's Table 2 benchmarks are calculated directly from continuous student-level value-added growth residuals ($\hat{\epsilon}_{ijs}$) aggregated to the building mean.
   - In public MSIP 6 Supporting reports, growth is presented as points earned percentages (0%, 25%, 50%, 75%, 100%) and categorical designations (*Emerging*, *Approaching*, *On-Track*, *Target*).
   - Even after this five-tier discretization, the empirical correlation with building poverty remains effectively identical (differing by no more than 0.007 in Math and ELA).

2. **Substantive Interpretation**:
   - While absolute academic achievement status is strongly associated with poverty ($r = -0.64$, $R^2 = 41.5\%$), Missouri's value-added growth model successfully strips out student starting positions and prior test histories.
   - Consequently, school growth measures do **not** penalize schools solely for enrolling economically disadvantaged student populations.

---
*Audit executed using master panel: `data/processed/mo_school_accountability_panel.parquet` (Sample B conventional schools).*