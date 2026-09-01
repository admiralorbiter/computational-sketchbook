# Kansas City Data-Driven Life Sim — Extensive Game Design Document (GDD)
*Working title:* **"KC: Life Lines"** (placeholder)  
*Document type:* Living design + data architecture spec  
*Version:* v0.1  
*Date:* 2025-12-25  

> **One-sentence pitch:** A narrative life-simulation game set in Kansas City where every “random start,” opportunity, and constraint is generated from real public datasets—so players explore how geography, schools, transit, jobs, and policy shape life outcomes, while still making meaningful choices.

---

## 0) Why this exists
This project sits at the intersection of:
- **Life-sim gameplay** (choices, stats, events, progression)
- **Civics/education** (systems thinking about opportunity structures)
- **Data-driven simulation** (real distributions, real geography, transparent assumptions)

The player experience is *not* “the game predicts your life.”  
It is: **the game simulates plausible life paths conditioned on real-world context**.

---

## 1) Design pillars
1. **Real distributions, not real people.**  
   Every character is synthetic. The game uses aggregated statistics and/or microdata to generate plausible households—never identifying individuals.
2. **Choices matter, but constraints are real.**  
   You can “play well,” but you can’t ignore commute time, rent burden, school access, or recession shocks.
3. **Transparent modeling.**  
   A *Data Mode* explains what inputs informed a number or probability (dataset, geography, year, limitations).
4. **Respectful depiction.**  
   Avoid stereotypes. Focus on systems, tradeoffs, and uncertainty.
5. **Expandable geography.**  
   Kansas City is v1. The architecture supports adding other metros by swapping boundary sets + local datasets.

---

## 2) Target audience and outcomes
### 2.1 Primary audiences
- Teens/young adults (classroom or informal learning)
- Community members curious about KC systems
- Policy/education audiences (as a conversation starter)

### 2.2 Intended learning outcomes
Players should walk away understanding:
- “Where you start” affects access to schools, transit, jobs, and health environments.
- Opportunity is shaped by *interacting systems* (education + housing + transportation + labor market shocks).
- Most outcomes are probabilistic—even with “good decisions.”

---

## 3) Scope definition
### 3.1 Kansas City focus (v1)
**Recommended v1 geography unit:** Census **tract** (or block group for some layers).  
This supports:
- neighborhood context from ACS
- joinability to many federal datasets (health, vulnerability, affordability, environment)
- mapping and visualization without exposing household-level detail

**KC region definition (design choice):**
- “KC Metro” polygon built from a county list, or CBSA definition, or a custom polygon.
- The exact region can be versioned in a config file (so the game can be updated without breaking saves).

### 3.2 Timeline
- Start: age **10–13** (middle school)  
- End: age **22–26** (early adult outcomes)
- Turns: **1 year** per turn (with optional “moments” inside a year)

---

## 4) Core gameplay loop
Each year (turn) has:
1. **Context update** (neighborhood stats, school quality signal, labor market conditions)
2. **Mandatory expenses** (housing, food, transportation, healthcare)
3. **Choice moments** (1–3 major decisions)
4. **Events** (0–2 random or triggered event cards)
5. **Outcome calculations** (skills, grades, money, stress, network, health)
6. **Reflection** (Data Mode + “What changed and why?”)

---

## 5) Player state model (what the sim tracks)
### 5.1 Core attributes (high-level)
- **Money & resources**
  - Cash on hand
  - Household income band (for family context)
  - Debt (student loans, medical, credit)
- **Education**
  - Attendance/engagement
  - GPA or skill mastery bands
  - Credits / certifications
- **Work**
  - Employment status
  - Occupation / industry
  - Work experience (months)
  - Job stability
- **Health**
  - Physical health
  - Mental health / stress
  - Access to care
- **Housing stability**
  - Rent burden (share of income)
  - Housing tenure (renter/owner/unstable)
  - Overcrowding risk
- **Mobility**
  - Vehicle access
  - Transit accessibility index (from GTFS)
  - Commute reliability
- **Social capital**
  - Support network strength
  - Mentor count / quality
  - Neighborhood cohesion
- **Civic access**
  - Awareness of resources
  - Participation level (optional system)
- **Luck / shock buffer**
  - Emergency fund
  - Coping skills
  - Safety net access

### 5.2 Environment state (per neighborhood/tract)
- Poverty rate, median rent, household vehicle access (ACS)
- School district context (NCES boundaries + state education indicators)
- Local labor market (BLS series, local employment proxies)
- Crime rate signal (local open data)
- Health risk environment (CDC PLACES)
- Housing+transport affordability (HUD LAI)
- Environmental burdens (EJScreen), flood risk (FEMA NFHL), heat/precip events (NOAA/NWS)

---

## 6) Choice systems (how decisions work)
### 6.1 Choices are “menu + constraints”
Players see:
- options available *to them* (filtered by constraints)
- cost (money/time/commute/stress)
- probability bands (chance of admission, job offer, scholarship)
- tradeoffs (short-term vs long-term)

Constraints can include:
- commute time (transit/car)
- tuition net price vs aid likelihood
- prerequisite credits
- household obligations (caregiving, part-time work)
- health/stress state
- “information access” (you might not know about a program unless you have a mentor or counselor access)

### 6.2 Modeling style
Use a layered approach:
- **Eligibility gates:** simple rules (age, GPA band, completed prerequisite)
- **Probability model:** logistic / weighted scoring using player stats + environment
- **Outcome distribution:** random draw + modifiers from player actions

The model should be *explainable* in Data Mode (no black box required).

---

## 7) Major simulation systems (with data hooks)

### 7.1 Education system
**Gameplay:**
- Attendance, discipline, course track, tutoring, extracurriculars
- College/career counseling quality as a resource
- Dual-credit / AP / CTE pathways (where available)

**Data inputs (examples):**
- School district boundaries (NCES EDGE)
- State education dashboards (MO DESE, KSDE)
- Optional: school locations (NCES) for commute estimation
- Optional: graduation rates, attendance, discipline signals (state report generators)

**Outputs:**
- academic skill growth
- scholarship eligibility
- college admissions probability bands

**Events:**
- “New principal: policy changes”
- “Teacher shortage: class size up”
- “Counselor leaves mid-year”
- “Program launch: new CTE pathway”

---

### 7.2 Housing system
**Gameplay:**
- rent vs savings vs stability
- move decisions (school changes, commute changes, social network disruption)
- eviction risk when rent burden exceeds thresholds
- repairs, landlord issues, utility shutoff risk

**Data inputs:**
- ACS: median rent, rent burden, vacancy rate, household income distribution
- HUD LAI: combined housing + transportation cost pressure
- Optional: local code violations / 311 data (if available)

**Events:**
- “Rent increase notice”
- “Roommate moves out”
- “Lease nonrenewal”
- “Opportunity: move closer to job (tradeoff: higher rent)”

---

### 7.3 Transportation system
**Gameplay:**
- commuting is a real constraint (time cost + reliability)
- car ownership is expensive but increases opportunity access
- transit access unlocks some choices; lack of transit locks others
- missed shift risk due to unreliable commute

**Data inputs:**
- KCATA GTFS schedules/stops/routes (and potentially GTFS-RT if available)
- ACS: vehicle availability (% households with zero vehicles)
- Optional: travel time to work distributions (ACS)

**Events:**
- “Bus route detour”
- “Car repair bill”
- “Winter storm impacts service”
- “New route added / schedule changes”

---

### 7.4 Work and labor market system
**Gameplay:**
- job search as a set of offers with wage bands
- skill requirements derived from occupation data
- recession/boom years shift offer probability & wage growth
- informal work and gig work (optional)

**Data inputs:**
- BLS time-series data (unemployment rates, CPI, industry series)
- O*NET (occupation skills, tasks, abilities)
- Optional: local wage distributions via ACS

**Events:**
- “Layoff wave”
- “Minimum wage change (policy scenario)”
- “Internship opportunity”
- “Workplace injury (health + income shock)”

---

### 7.5 Health and stress system
**Gameplay:**
- stress affects performance at school/work
- health shocks consume money and time
- preventive care reduces shock probability but costs time/money
- mental health support can be scarce (resource gating)

**Data inputs:**
- CDC PLACES (modeled local estimates for risk factors/outcomes)
- ACS: health insurance coverage
- Optional: resource layers (clinics, providers) if sourced

**Events:**
- “ER visit”
- “Chronic condition flare-up”
- “Therapy waitlist”
- “Caregiver stress”

---

### 7.6 Safety / community conditions system
**Gameplay:**
- safety is represented as *risk exposure* and *time cost* (not sensational)
- certain events (robbery, victimization, witnessing violence) are rare but impactful
- emphasize uncertainty and avoid deterministic moral framing

**Data inputs:**
- Open Data KC: KCPD crime reports (aggregated to tract/neighborhood)
- Optional: 311/service calls for neighborhood disorder proxies

**Events:**
- “Bike stolen”
- “You avoid a late shift due to safety concerns”
- “Community clean-up reduces disorder signal”

---

### 7.7 Climate/environment system
**Gameplay:**
- extreme heat/cold affects health, transit reliability, and utility bills
- flood risk influences housing choice, insurance cost, and disruption

**Data inputs:**
- FEMA NFHL flood hazard layers
- NOAA Climate Data Online or NWS API for historical/forecast data (depending on mode)
- EPA EJScreen for environmental burden indicators (if accessible/allowed)

**Events:**
- “Flash flood: commute disrupted”
- “Heat wave: higher energy bill + health risk”
- “Air quality alert: outdoor job penalty”

---

### 7.8 Food access system (optional but powerful)
**Gameplay:**
- food costs and access affect health/stress
- “food desert” style constraints can add time cost to healthy food choices

**Data inputs:**
- USDA Food Access Research Atlas (tract-level indicators; note tract vintage issues)
- Optional: local grocery locations (if sourced openly)

**Events:**
- “Grocery store closes”
- “New farmers market opens”
- “SNAP benefit change (scenario)”

---

### 7.9 Social capital / mentorship system
**Gameplay:**
- mentors unlock information and opportunities (scholarships, internships, programs)
- strong networks buffer shocks (small loans, childcare help, referrals)
- network growth through activities, church/community groups, sports, clubs

**Data inputs:**
- Mostly modeled (few direct public datasets)
- Optional: civic org directories (but licensing and coverage vary)

**Events:**
- “Teacher becomes mentor”
- “Friend’s family helps with ride”
- “Community program referral”

---

### 7.10 Policy scenario system (optional but high engagement)
**Gameplay:**
- optional “scenario toggles” modify systems:
  - transit expansion
  - childcare subsidy
  - tuition-free community college
  - housing voucher availability
  - increased minimum wage

**Data inputs:**
- Mix of public policy parameters + scenario assumptions
- Must be clearly labeled as “scenario” not “observed reality”

---

## 8) Data-first architecture (how the game uses real datasets)

### 8.1 Data pipeline overview
1. **Ingest** raw datasets (download/API)
2. **Normalize** to consistent geography + year
3. **Join** using stable IDs (GEOID for tracts/block groups; NCES IDs for districts; IPEDS for colleges)
4. **Derive** indices used by gameplay (transit access, affordability, school opportunity signal)
5. **Export** a “Game Data Pack” (versioned) consumed by the game runtime

### 8.2 Versioning rules
- Every data pack has:
  - region name (KC_v1)
  - year range (e.g., ACS 2019–2023 5-year)
  - boundary vintage (tracts 2020, districts 2023–2024, CDs 118th, etc.)
- Save files reference the pack version to ensure reproducibility.

### 8.3 Geography joins (recommended)
- Primary join key: **Census GEOID** (tract or block group)
- District join: polygon overlay (tract centroid → district polygon)
- Congress district join: polygon overlay from TIGER/Line
- Transit join: stops within buffer distance of player home / school / job

---

## 9) Data Mode (player-facing transparency)
Data Mode should show:
- the geography used (tract name/ID, district)
- the data year(s)
- what variable(s) influenced the mechanic
- uncertainty notes (“ACS estimates have margins of error”)

Example Data Mode card:
- “Rent burden risk uses ACS estimate of % households spending >30% income on housing in your tract.”
- “Commute reliability uses GTFS frequency + transfer count.”

---

## 10) Content system: Event cards
### 10.1 Event card anatomy
Every event is defined in JSON (or similar) with:
- `id`, `title`, `description`
- `tags` (education, housing, health)
- `trigger` (probabilistic rules)
- `choices` (0–4 options)
- `effects` (stat changes, flags, unlocks)
- `data_explainers` (what data informed it)
- `cooldowns` (avoid repeats)
- `sensitivity_level` (for content filters)

### 10.2 Example event schema (pseudo)
```json
{
  "id": "HOUSING_RENT_INCREASE_01",
  "title": "Rent Increase Notice",
  "tags": ["housing", "finance"],
  "trigger": {
    "type": "annual_check",
    "conditions": [
      {"var": "housing.tenure", "eq": "renter"},
      {"var": "env.rent_burden_rate", "gte": 0.35}
    ],
    "base_probability": 0.18,
    "modifiers": [
      {"if": {"var": "player.savings_months", "lt": 1}, "mult": 1.4},
      {"if": {"var": "env.vacancy_rate", "lt": 0.07}, "mult": 1.2}
    ]
  },
  "choices": [
    {"label": "Pay and stay", "effects": {"money.monthly_rent": "+$75", "stress": "+5"}},
    {"label": "Negotiate with landlord", "effects": {"chance": "reduce_increase", "stress": "+3"}},
    {"label": "Move", "effects": {"housing.move": true, "network": "-3", "stress": "+8"}}
  ],
  "data_explainers": [
    "Uses ACS tract-level rent + vacancy conditions to set baseline risk."
  ]
}
```

### 10.3 Event library categories (starter list)
- **Education:** teacher turnover, program access, disciplinary incident, scholarship info
- **Housing:** eviction risk, rent increase, utility shutoff, move opportunity
- **Work:** job offer, layoff, schedule conflict, training opportunity
- **Health:** acute illness, mental health stress, preventive care
- **Transport:** route change, breakdown, snow/ice disruption
- **Safety:** property crime exposure, neighborhood improvement effort
- **Environment:** flood, extreme heat/cold, air quality alert
- **Family:** caregiving responsibilities, household job loss, family conflict
- **Civic:** voting eligibility, local meeting, community resource fair
- **Windfalls:** small scholarship, tax refund, found program, mentor referral

---

## 11) Data sources catalog (v1 — Kansas City)
This section lists **recommended** sources and how to use them.  
**Important:** confirm licensing/terms for each source before shipping a commercial product.

### 11.1 Essential “foundation” datasets
1. **U.S. Census / American Community Survey (ACS)**
   - Use: poverty, income distributions, rent, vehicle access, insurance, commute time
   - Access: Census API + downloaded tables
   - Notes: margins of error; choose 5-year for small geographies

2. **Census TIGER/Line Shapefiles**
   - Use: tract boundaries, congressional districts, other base geographies
   - Access: downloadable shapefiles (versioned by year)

3. **NCES EDGE School District Boundaries**
   - Use: assign player to school district; enable district-level context
   - Access: annually updated boundary files

4. **State education data**
   - Missouri: DESE School Data + downloads
   - Kansas: KSDE Data Central / report generator
   - Use: district performance indicators, graduation rates, enrollment, staffing

5. **College Scorecard**
   - Use: realistic college costs/outcomes
   - Access: API + bulk downloads
   - Key joins: IPEDS unit ID

6. **BLS Public Data API**
   - Use: unemployment, inflation context, time-series shocks

7. **O*NET database**
   - Use: skill requirements, occupation attributes for jobs and training

### 11.2 Kansas City local datasets (high value for immersion)
- **Open Data KC** (Socrata)
  - Use: crime reports (aggregate), 311, permits, neighborhood assets
- **KCATA GTFS**
  - Use: transit access index, commute calculation
  - Notes: KCATA data terms describe a limited/revocable license—confirm acceptable use.

### 11.3 Optional “depth” datasets
- **CDC PLACES**
  - Use: tract-level modeled health risk environment
- **ATSDR/CDC Social Vulnerability Index (SVI)**
  - Use: vulnerability index for event probability modifiers (carefully; avoid stigmatizing)
- **HUD Location Affordability Index**
  - Use: combined housing+transport cost pressure at block group
- **FEMA NFHL**
  - Use: flood risk layers for housing choice + disruption events
- **NOAA/NWS APIs**
  - Use: extreme weather event timing (optional “historical replay” mode)
- **USDA Food Access Research Atlas**
  - Use: food access constraints (watch tract vintage)

---

## 12) Derived indices (game-friendly metrics built from data)
To avoid overwhelming the player with raw variables, build a few interpretable indices:

### 12.1 Opportunity Index (neighborhood)
A weighted index using:
- poverty rate (ACS)
- vehicle access (ACS)
- housing+transport cost pressure (HUD LAI)
- transit frequency within 0.5 miles (GTFS)
- school district opportunity signal (state indicators)
- health risk environment (PLACES)

### 12.2 Transit Access Score
- stops within radius
- service frequency on weekdays
- number of transfers to major job centers
- reliability penalty for low-frequency routes

### 12.3 Housing Stability Risk Score
- rent burden prevalence
- vacancy rate
- income volatility (modeled)
- emergency fund level

Each index should expose components in Data Mode.

---

## 13) Progression and endings
### 13.1 Milestones
- Middle school transition
- High school track selection
- First job
- Graduation / dropout pivot
- Postsecondary entry (college, training, apprenticeship)
- First independent housing
- Career specialization

### 13.2 End states (non-judgmental)
Instead of a single “win,” present:
- stability summary (housing, health, income)
- education/skills summary
- time-to-recovery after shocks
- “counterfactual” reflection: how much outcomes changed due to decisions vs environment

---

## 14) Difficulty and accessibility
- **Story Mode:** softer penalties, more explanation
- **Simulation Mode:** stronger constraints, higher realism
- **Data Sandbox:** pick starting tract/district intentionally, run multiple lives, compare outcomes

Content settings:
- reduce/remove violence-related events
- reduce/remove severe health events
- adjust financial stress intensity

---

## 15) Ethics, fairness, and safety notes (non-negotiable)
- Never generate content that blames individuals for structural conditions.
- Avoid “crime tourism.” Safety events should be rare, optional, and framed as risk exposure.
- Clearly label:
  - modeled estimates (PLACES)
  - scenario assumptions (policy toggles)
  - margins of error / uncertainty (ACS)
- If monetized, re-check every dataset’s terms and licensing.

---

## 16) Technical implementation sketch (data + game engine)
### 16.1 Suggested stack (example)
- Data engineering: Python + GeoPandas + DuckDB/Parquet
- API pulls: scheduled builds of “data packs”
- Game runtime: Unity/Godot/Web (any) reading prebuilt packs

### 16.2 Data pack format
- `region.json` (metadata + boundary vintage)
- `tracts.parquet` (ACS + derived indices)
- `districts.parquet` (education indicators)
- `colleges.parquet` (Scorecard subset)
- `jobs.parquet` (occupation library)
- `transit.parquet` (precomputed access metrics)
- `events/*.json` (event library)

---

## 17) Next deliverables (suggested)
1. A **data dictionary**: exact variables + tables + joins
2. A **minimum viable event library** (100–200 events)
3. A **KC v1 data pack build script**
4. A **playable prototype** (ages 13–18 first)

---

## Appendix A — Quick reference links (official or primary where possible)
*(These are included in the companion “Data Sources Catalog” markdown as well.)*
- ACS data via API: https://www.census.gov/programs-surveys/acs/data/data-via-api.html  
- Census APIs index: https://www.census.gov/data/developers/data-sets.html  
- TIGER/Line shapefiles: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html  
- NCES EDGE district boundaries: https://nces.ed.gov/programs/edge/Geographic/DistrictBoundaries  
- Missouri DESE School Data: https://dese.mo.gov/school-data  
- KSDE Data Central: https://datacentral.ksde.gov/  
- College Scorecard API: https://collegescorecard.ed.gov/data/api-documentation  
- BLS Data API: https://www.bls.gov/developers/  
- O*NET database license: https://www.onetcenter.org/license_db.html  
- Open Data KC: https://data.kcmo.org/  
- KCATA GTFS: https://www.kcata.org/transit_data/access_gtdf  
- HUD Location Affordability Index: https://www.hudexchange.info/programs/location-affordability-index/  
- CDC PLACES: https://www.cdc.gov/places/  
- FEMA NFHL: https://www.fema.gov/flood-maps/national-flood-hazard-layer  
- NOAA CDO API: https://www.ncdc.noaa.gov/cdo-web/webservices/v2  
- USDA Food Access Research Atlas: https://www.ers.usda.gov/data-products/food-access-research-atlas/  

---

*End of document.*
