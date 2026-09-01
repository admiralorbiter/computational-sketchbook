# KC: Life Lines — Data Sources Catalog (v1)
*Companion to the GDD*  
*Version:* v0.1  
*Date:* 2025-12-25  

This catalog is organized for **implementation**: what you can pull, at what geography, how you join it, and what it does in the game.

> **Reminder:** Always confirm licensing/terms before shipping a commercial product. Even “public” data can carry usage conditions, attribution requirements, or disclaimers.

---

## 1) Foundation datasets (required)

### 1.1 American Community Survey (ACS) — U.S. Census Bureau
**What it gives you**
- Poverty & income distributions
- Rent, housing tenure, vacancy
- Vehicle access
- Insurance coverage
- Commute time to work
- Household structure

**Access**
- Census Data API (recommended for automated builds)
- Bulk downloads / data.census.gov

**Best geography**
- Census tract or block group for neighborhood context  
- Use **5-year** estimates for small geographies (stability vs timeliness)

**Join keys**
- GEOID (tract / block group)

**Key implementation notes**
- ACS estimates include **margins of error**; consider smoothing or using bands.

Links:
- https://www.census.gov/programs-surveys/acs/data/data-via-api.html  
- https://www.census.gov/data/developers/data-sets.html  

---

### 1.2 TIGER/Line Shapefiles — U.S. Census Bureau
**What it gives you**
- Boundaries for tracts, counties, congressional districts, etc.

**Access**
- Download shapefiles by year/vintage

**Join keys**
- GEOID and other geography codes

Links:
- https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html  

---

### 1.3 NCES EDGE School District Boundaries — U.S. Department of Education
**What it gives you**
- Unified/elementary/secondary district polygons (updated annually)

**Use in game**
- Assign player to district
- Allow district-level context (funding signals, performance indicators)

Links:
- https://nces.ed.gov/programs/edge/Geographic/DistrictBoundaries  

---

## 2) Education data (KC-specific)

### 2.1 Missouri DESE (district/school indicators)
**Use in game**
- District “opportunity signals”: graduation rate, assessment performance, staff counts
- Optional: attendance/discipline indicators (where available)

Links:
- https://dese.mo.gov/school-data  
- https://dese.mo.gov/school-directory/data-downloads  

---

### 2.2 Kansas KSDE Data Central / K-12 Report Generator
**Use in game**
- Kansas-side district/school indicators (graduation, dropout, attendance, staffing, etc.)

Links:
- https://datacentral.ksde.gov/  
- https://datacentral.ksde.gov/report_gen.aspx/default.aspx  

---

## 3) Postsecondary choices

### 3.1 College Scorecard API + bulk downloads
**Use in game**
- Net price, graduation rates, earnings outcomes
- Program-level options

**Join keys**
- IPEDS unit ID

Links:
- https://collegescorecard.ed.gov/data/api-documentation  
- https://collegescorecard.ed.gov/data  

---

## 4) Jobs and the labor market

### 4.1 BLS Public Data API
**Use in game**
- Yearly labor market conditions (unemployment shocks)
- Inflation context (cost-of-living pressure)

Links:
- https://www.bls.gov/developers/  

---

### 4.2 O*NET database
**Use in game**
- Occupation skill requirements
- Tasks, abilities, work context
- Career ladders

License:
- Creative Commons Attribution 4.0 (check exceptions)

Links:
- https://www.onetcenter.org/license_db.html  

---

## 5) Transportation

### 5.1 KCATA GTFS
**Use in game**
- Transit access score
- Commute times and reliability approximation

Important:
- KCATA pages describe a limited/revocable license and liability disclaimers—review terms.

Links:
- https://www.kcata.org/transit_data/access_gtdf  
- https://www.kcata.org/transit_data  

---

## 6) Local KC immersion datasets

### 6.1 Open Data KC (Socrata)
**Use in game**
- Crime reports (aggregate for safety signal)
- 311/service calls (optional neighborhood disorder proxy)
- Permits, inspections (optional neighborhood change)

Links:
- https://data.kcmo.org/  
- Socrata API docs: https://dev.socrata.com/  

---

## 7) Health & vulnerability

### 7.1 CDC PLACES (modeled local health indicators)
**Use in game**
- Health risk environment modifiers
- Preventive care and chronic condition context

Links:
- https://www.cdc.gov/places/  
- Data portal: https://www.cdc.gov/places/tools/data-portal.html  

---

### 7.2 CDC/ATSDR Social Vulnerability Index (SVI)
**Use in game**
- Vulnerability modifier for certain disruptions
- Use cautiously; avoid stigmatizing “scores” in UI

Links:
- https://atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html  

---

## 8) Housing + transportation affordability

### 8.1 HUD Location Affordability Index (LAI)
**Use in game**
- Block-group level combined housing+transport cost pressure
- Helps model “hidden cost of distance”

Links:
- https://www.hudexchange.info/programs/location-affordability-index/  
- https://www.locationaffordability.info/home/  

---

## 9) Environment + hazards

### 9.1 FEMA National Flood Hazard Layer (NFHL)
**Use in game**
- Flood risk for housing choice
- Flood event disruptions

Links:
- https://www.fema.gov/flood-maps/national-flood-hazard-layer  

---

### 9.2 NOAA Climate Data Online (CDO) API / NWS API
**Use in game**
- Weather shocks (heat waves, storms)
- Optional “historical replay” mode by year

Links:
- NOAA CDO API: https://www.ncdc.noaa.gov/cdo-web/webservices/v2  
- NWS API: https://www.weather.gov/documentation/services-web-api  

---

### 9.3 EPA EJScreen (environmental burden indicators)
**Use in game**
- Environmental burden context for neighborhoods
- Use carefully; emphasize uncertainty and systems context

Link:
- EPA API hub (includes EJScreen API): https://www.epa.gov/data/application-programming-interface-api  

---

## 10) Food access

### 10.1 USDA Food Access Research Atlas
**Use in game**
- Food access constraints and time cost modifiers

Important:
- Some versions use older tract polygons (vintage mismatch). Treat with care.

Links:
- https://www.ers.usda.gov/data-products/food-access-research-atlas  
- https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data  

---

## 11) Recommended “Data Pack” build schedule
- **Quarterly** rebuild (education dashboards, local open data)
- **Annual** rebuild (ACS 1-year if used; district boundaries; Scorecard updates)
- **On-demand** rebuild for scenario packs or bug fixes

---

*End of catalog.*
