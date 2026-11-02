# Missouri Accountability Signal
## Research Design v0.1

## 1. Purpose

Determine what Missouri's existing measures of school performance actually measure before the state's new A–F grades are published.

The central question is:

> **When Missouri reports that a school is performing well or poorly, how much of that signal tracks the characteristics and starting position of the students attending the school, and how much is contained in measures of student growth after starting position is accounted for?**

This project must **not** begin from the assumption that Missouri's accountability system is good, bad, fair, unfair, biased, or unbiased.

The goal is to measure it.

The eventual A–F system will use academic achievement, value-added growth, growth toward proficiency, and—for high schools—Success Ready Graduate measures and graduation rates. Missouri has approved the framework but has not yet publicly released the actual pilot grades.

Therefore the project has two stages:

**Stage I — now:** analyze the existing underlying accountability signals.

**Stage II — later:** ingest the official A–F pilot and determine what changes when those signals are collapsed into a letter grade.

---

# 2. Do not call this a causal experiment

This is primarily an:
- accountability-measurement study;
- predictive/decomposition study;
- longitudinal observational study.

It does **not** estimate the causal effect of poverty on achievement.
It does **not** estimate the causal effect of schools on children.

The strongest permissible claim from a regression such as:
`Achievement ~ Poverty`
is:
> "School poverty is strongly/weakly associated with, or predictive of, measured achievement."

Never write:
> "Poverty causes X percent of achievement."

Likewise, an R² of .60 does **not** mean "60% of the school's score is caused by poverty."

---

# 3. Main empirical questions

Answer these separately.

### Q1. Achievement status
How strongly is a school's measured academic achievement associated with student socioeconomic composition?

### Q2. Growth
How strongly is Missouri's value-added growth measure associated with socioeconomic composition?
Missouri's own 2024 and 2025 Growth Model reports say growth measures generally show small or statistically insignificant relationships with free-meal direct-certification rates. Replicate this independently rather than accepting it as given.

### Q3. Existing APR
How strongly is the current Annual Performance Report associated with socioeconomic composition?

### Q4. Component decomposition
Which components of APR/accountability are most associated with student composition?

### Q5. Status versus growth
Do schools with high achievement necessarily produce high growth?

### Q6. Starting position
Once prior achievement is known, how much additional predictive information is provided by poverty and other student-composition measures?

### Q7. Stability
How stable are achievement, growth, and APR results from year to year?

### Q8. Eventually: A–F
When official pilot grades appear: How much information survives after everything is compressed into one letter?

---

# 4. Primary unit of analysis
The main dataset must contain: **one row per school/building per year.**
Canonical key:
- school_year
- district_code
- building_code
- nces_school_id_if_available

Primary years: **2022, 2023, 2024, 2025**
The 2025 cross-section is the primary contemporary analysis; 2022–2025 panel is the stability analysis.
