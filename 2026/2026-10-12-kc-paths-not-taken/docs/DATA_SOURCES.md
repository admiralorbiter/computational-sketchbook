# KC Pathways — Data Provenance & Verification Registry

**Audit Date:** October 12, 2026  
**Auditor Protocol:** Strict verification against official district websites, NCES Common Core of Data, and institutional catalogs. Zero synthetic numbers or unverified assertions.

---

## 1. Verified Institutional Records

| Location / Program | Field | Verified Value | Official Source | Source URL | Epistemic Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ruskin High School** | Address | 7000 E 111th St, Kansas City, MO 64134 | NCES CCD / Hickman Mills | `https://ruskin.hickmanmills.org` | `verified_fact` |
| **Ruskin High School** | NCES School ID | `291434003156` | NCES CCD Public School Universe | `https://nces.ed.gov/ccd/` | `verified_fact` |
| **Ruskin High School** | Coordinates | Lat: `38.923090`, Lon: `-94.506760` | NCES CCD / EDGE Geocode | NCES Official Record | `verified_fact` |
| **Ruskin High School** | Grades Served | 9–12 | Missouri DESE / District | DESE School Directory | `verified_fact` |
| **RWL Center** | Address | 10301 Hickman Mills Dr, Kansas City, MO 64137 | Hickman Mills District Portal | `https://realworldlearning.hickmanmills.org` | `verified_fact` |
| **RWL Center** | Coordinates | Lat: `38.939400`, Lon: `-94.532954` | OpenStreetMap Nominatim Geocode | OSM Geocoding Service | `verified_fact` |
| **MCC–Penn Valley HSI** | Address | 3444 Broadway Blvd, Kansas City, MO 64111 | MCC-KC Campus Directory | `https://mcckc.edu/campuses/penn-valley/hsi/` | `verified_fact` |
| **MCC–Penn Valley HSI** | Coordinates | Lat: `39.064955`, Lon: `-94.590989` | OpenStreetMap Nominatim Geocode | OSM Geocoding Service | `verified_fact` |
| **Health Start Academy** | Grades Served | 10, 11, 12 | Ruskin Real World Learning Site | `https://ruskin.hickmanmills.org/our-school/academics/real-world-learning` | `verified_fact` |
| **Health Start Academy** | College Partner | MCC–Penn Valley | Ruskin Real World Learning Site | Official Site | `verified_fact` |
| **Health Start Academy** | Credential Paths | CNA, Pharmacology Tech, Phlebotomy | Ruskin Real World Learning Site | Official Site | `verified_fact` |
| **Health Start Academy** | Application Window | January – April | Ruskin Real World Learning Site | Official Site | `verified_fact` |
| **Early College Academy** | College Partner | MCC–Longview | Hickman Mills RWL Portal | `https://realworldlearning.hickmanmills.org/about/early-college-academy` | `verified_fact` |
| **Early College Academy** | Credits Available | Up to 42 credits | Hickman Mills RWL Portal | Official Site | `verified_fact` |
| **Early College Academy** | Eligibility Rules | 3.0 unweighted GPA, Accuplacer score | Hickman Mills RWL Portal | Official Site | `verified_fact` |

---

## 2. Explicit Simulation Assumptions

These parameters are declared scenario design decisions for gameplay balance, not empirical claims:
1. **Planning Rounds & Action Points:** 3 rounds of 2 Action Points each represent limited student time during a planning semester.
2. **Transportation Scenario Branching:** Profile A (reliable) vs. Profile B (needs coordination) models the friction of navigating off-campus opportunities without assuming deterministic demographic sorting.
3. **Counselor Meeting:** 1 AP representing scheduling and meeting with high school counseling staff.

---

## 3. Explicitly Documented Unknowns & Non-Claims

The following items are deliberately NOT hardcoded or guessed, because doing so would fabricate institutional reality:
- **Annual Cohort Caps:** The exact seat limit for Health Start Academy varies year-to-year and is marked `unknown`.
- **Individual Admissions Probabilities:** We do NOT assign a probabilistic success rate ($P(\text{admitted}) = 0.72$) based on race, income, or neighborhood.
- **Specific Transit Route Travel Times:** While RideKC routes run along 111th, Hickman Mills Dr, and Broadway, real travel time depends on current run schedules, walking transfers, and peak headway, which are reserved for later GTFS pipeline integration.
