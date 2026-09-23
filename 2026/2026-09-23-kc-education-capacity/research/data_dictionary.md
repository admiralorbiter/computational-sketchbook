# Data Dictionary: Kansas City School Universe

| Variable | Type | Source | Description / Valid Values |
| :--- | :--- | :--- | :--- |
| `nces_school_id` | String(12) | NCES CCD / EDGE | Unique 12-digit NCES school identifier (`NCESSCH`). Primary key. |
| `nces_lea_id` | String(7) | NCES CCD / EDGE | Unique 7-digit NCES Local Education Agency identifier (`LEAID`). |
| `school_name` | String | NCES CCD / EDGE | Official name of the school building. |
| `district_name` | String | NCES CCD | Name of the local education agency / district. |
| `state` | String(2) | NCES CCD / EDGE | State abbreviation (`MO` or `KS`). |
| `county_name` | String | NCES EDGE | County name where the school is physically located. |
| `county_fips` | String(5) | NCES EDGE | 5-digit FIPS code of the physical county (`29095`, `20091`, etc.). |
| `street_address` | String | NCES CCD / EDGE | Reported physical street address. |
| `city` | String | NCES CCD / EDGE | Reported physical city. |
| `zip_code` | String(5) | NCES CCD / EDGE | Reported 5-digit ZIP code. |
| `latitude` | Float | NCES EDGE | Geocoded latitude coordinate of the school location. |
| `longitude` | Float | NCES EDGE | Geocoded longitude coordinate of the school location. |
| `lowest_grade` | String | NCES CCD | Lowest grade offered (e.g., `PK`, `KG`, `01`, `09`). |
| `highest_grade` | String | NCES CCD | Highest grade offered (e.g., `05`, `08`, `12`). |
| `school_level` | String | NCES CCD | NCES assigned level: `Primary`, `Middle`, `High`, `Other`. |
| `school_type` | Integer | NCES CCD | 1=Regular, 2=Special Education, 3=Vocational, 4=Alternative/Other. |
| `school_type_desc`| String | NCES CCD | Text description of `school_type`. |
| `charter_status` | String | NCES CCD | Charter indicator (`Yes`, `No`). |
| `operational_status` | Integer | NCES CCD | Operational status code (1=Open, 2=Closed, 3=New, etc.). |
| `operational_status_desc` | String | NCES CCD | Text description of operational status. |
| `virtual_status` | String | NCES CCD Char. | Virtual instruction flag: `NOTVIRT` (No virtual instruction), `FULLVIRT` (Exclusively virtual), `FACEVIRT` (Primarily virtual), `SUPPVIRT` (Supplemental). |
| `virtual_status_desc` | String | NCES CCD Char. | Full descriptive text of virtual status. |
| `locale_code` | String(2) | NCES EDGE | Official NCES 2-digit locale code (11-43). |
| `locale_desc` | String | NCES EDGE / Standard | Text description of locale (e.g., `City: Large`, `Suburb: Large`, `Rural: Fringe`). |
| `locale_group` | String | Derived | Standard 4-category classification: `City`, `Suburb`, `Town`, or `Rural`. |
| `school_year` | String | NCES CCD | School year of the record (e.g., `2024-2025`). |
