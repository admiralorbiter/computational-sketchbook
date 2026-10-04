# Methodological Framework: Classroom Capacity and Class Size Measurement

This document details the mathematical, statistical, and econometric specifications governing Study A and the construction of the longitudinal class-size panel.

---

## 1. Class Size Estimands and Weighting Schemes

Let $s$ index schools, $c$ index courses, and $t$ index academic survey waves.

### 1.1 School-Course Mean Class Size
CRDC observes the total course enrollment $E_{sct}$ and the total number of class sections $K_{sct}$. The derived school-course mean is:

$$\bar C_{sct} = \frac{E_{sct}}{K_{sct}}$$

Valid only when $K_{sct} \ge 1$ and $E_{sct} \ge 1$. If $K_{sct} = 0$, $\bar C_{sct}$ is undefined (`NaN`).

### 1.2 Teacher / Section-Weighted Mean (Course-Cell Weighted)
The unweighted mean across course cells answers: **"What is the average size of a course offering?"**

$$\bar C_{\text{course}} = \frac{1}{N} \sum_{i=1}^N \bar C_i$$

Or, when weighted by the reported number of sections $K_i$:

$$\bar C_{\text{section}} = \frac{\sum_i K_i \bar C_i}{\sum_i K_i} = \frac{\sum_i E_i}{\sum_i K_i}$$

### 1.3 Student / Seat-Weighted Mean
The seat-weighted metric answers: **"How large is the classroom experienced by the average student?"**

If true section rosters $n_j$ were observed, the seat-weighted mean would be:

$$\bar C_{\text{student}} = \frac{\sum_j n_j^2}{\sum_j n_j}$$

Using CRDC school-course aggregate cells, each student in cell $i$ experiences the school-course mean $\bar C_i$. Weighting each cell by its total enrollment $E_i$ yields the seat-weighted course-cell mean:

$$\bar C_{\text{seat}} = \frac{\sum_i E_i \bar C_i}{\sum_i E_i} = \frac{\sum_i \frac{E_i^2}{K_i}}{\sum_i E_i}$$

By Jensen's Inequality, whenever class sizes vary across schools or courses, $\bar C_{\text{seat}} > \bar C_{\text{section}}$: larger classes mechanically contain more students, shifting the student experience upward relative to the institutional average.

---

## 2. Staffing Allocation Wedge Metrics

To quantify the structural gap between classroom headcount and aggregate school staffing:

### 2.1 Absolute Staffing Wedge
$$\Delta_{sct} = \bar C_{sct} - \text{PTR}_{st}$$

where $\text{PTR}_{st}$ is the contemporaneous pupil-to-classroom-teacher ratio from CCD (or CRDC School Support).

### 2.2 Relative Staffing Wedge Ratio
$$\Omega_{sct} = \frac{\bar C_{sct}}{\text{PTR}_{st}}$$

In a secondary departmentalized schedule where teachers teach $p$ out of $P$ daily periods (e.g., 5 of 7 periods, planning fraction $\lambda = 5/7 \approx 0.714$), mechanical scheduling alone produces $\Omega \approx 1 / \lambda = 1.40$. Non-instructional specialists, pull-out coaches, and department chairs further expand this wedge.

---

## 3. Econometric Specifications

### 3.1 Within-School Course Hierarchy (School Fixed Effects)
To determine whether certain foundational courses systematically absorb larger enrollments even within the same campus:

$$\bar C_{sct} = \alpha_s + \gamma_c + \delta_t + \epsilon_{sct}$$

where:
- $\alpha_s$ are school fixed effects absorbing campus-specific scale, facility capacity, and district staffing formulas;
- $\gamma_c$ are course fixed effects relative to a reference course (Algebra I);
- $\delta_t$ are survey-wave fixed effects capturing secular trends;
- Standard errors are clustered at the school (or LEA) level.

### 3.2 Longitudinal Panel Robustness: Balanced vs. Repeated Cross-Section
To isolate authentic changes in classroom capacity from compositional changes in the school universe (school openings, closures, and survey response shifts), all trends are estimated on two populations:
1. **Repeated Cross-Section (Full Universe):** All eligible schools reporting valid data in each wave.
2. **Balanced Panel:** The subset of continuous schools that report valid course data across all analyzed waves.
