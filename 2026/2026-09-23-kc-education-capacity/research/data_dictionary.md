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
| `distance_downtown_kc_miles` | Float | Derived | Haversine distance in statute miles from Kansas City Hall ($39.1027^\circ \text{N}, -94.5779^\circ \text{W}$). |
| `lowest_grade` | String | NCES CCD | Lowest grade offered (e.g., `PK`, `KG`, `01`, `09`). |
| `highest_grade` | String | NCES CCD | Highest grade offered (e.g., `05`, `08`, `12`). |
| `school_level` | String | NCES CCD | NCES assigned level: `Primary`, `Middle`, `High`, `Other`. |
| `school_type` | Integer | NCES CCD | 1=Regular, 2=Special Education, 3=Vocational, 4=Alternative/Other. |
| `school_type_desc`| String | NCES CCD | Text description of `school_type`. |
| `charter_status` | String | NCES CCD | Charter indicator (`Yes`, `No`). |
| `operational_status` | Integer | NCES CCD | Operational status code: 1=Open, 2=Closed, 3=New, 4=Added, 5=Changed Agency, 6=Inactive, 7=Future, 8=Reopened. |
| `operational_status_desc` | String | NCES CCD | Text description of operational status. |
| `virtual_status` | String | NCES CCD Char. | Virtual instruction flag: `NOTVIRT` (No virtual instruction), `FULLVIRT` (Exclusively virtual), `FACEVIRT` (Primarily virtual), `SUPPVIRT` (Supplemental). |
| `virtual_status_desc` | String | NCES CCD Char. | Full descriptive text of virtual status. |
| `locale_code` | String(2) | NCES EDGE | Official NCES 2-digit locale code (11-43). |
| `locale_desc` | String | NCES EDGE / Standard | Text description of locale (e.g., `City: Large`, `Suburb: Large`, `Rural: Fringe`). |
| `locale_group` | String | Derived | Standard 4-category classification: `City`, `Suburb`, `Town`, or `Rural`. |
| `cbsa_code` | String(5) | NCES EDGE | Core Based Statistical Area code (e.g., `28140` for Kansas City, MO-KS). |
| `cbsa_name` | String | NCES EDGE | Core Based Statistical Area name. |
| `csa_code` | String(3) | NCES EDGE | Combined Statistical Area code (e.g., `312` for Kansas City-Overland Park-Kansas City, MO-KS). |
| `csa_name` | String | NCES EDGE | Combined Statistical Area name. |
| `is_charter` | Boolean | Derived | `True` if `charter_status == 'Yes'`. |
| `is_virtual` | Boolean | Derived | `True` if school offers exclusively or primarily virtual instruction. |
| `is_regular` | Boolean | Derived | `True` if `school_type == '1'` (Regular School). |
| `is_special_ed` | Boolean | Derived | `True` if `school_type == '2'` (Special Education School). |
| `is_vocational` | Boolean | Derived | `True` if `school_type == '3'` (Career and Technical School). |
| `is_alternative` | Boolean | Derived | `True` if `school_type == '4'` (Alternative School). |
| `is_operating` | Boolean | Derived | `True` for schools actively operating in the survey year (status 1=Open, 3=New, 4=Added, 5=Changed Agency, 8=Reopened). `False` for status 2=Closed, 6=Inactive, 7=Future. |
| `is_continuing_school` | Boolean | Derived | `True` strictly for continuing open schools (`operational_status == '1'`). |
| `school_year` | String | NCES CCD | School year of the record (e.g., `2024-2025`). |
