# Missouri OpenStreetMap Data Analysis Report
**Generated:** 2025-10-18 16:07:32

## Executive Summary

This analysis covers **3,144,771** OpenStreetMap features across Missouri, 
stored in a 1185.82 MB GeoPackage file. The data is organized into 5 main feature tables 
representing different geometric types and OSM data structures.

### Data Distribution by Table

| Table | Features | Percentage | Description |
|-------|----------|------------|-------------|
| points | 970,588 | 30.86% | Individual nodes (POIs, addresses, etc.) |
| lines | 1,286,119 | 40.90% | Linear features (roads, rivers, boundaries) |
| multipolygons | 874,841 | 27.82% | Area features (buildings, landuse, etc.) |
| multilinestrings | 3,168 | 0.10% | Complex linear features |
| other_relations | 10,055 | 0.32% | OSM relations and complex objects |

### Data Quality Overview

| Table | Avg. Completeness | Most Complete Column | Least Complete Column |
|-------|------------------|---------------------|----------------------|
| points | 21.74% | osm_id (100.00%) | address (0.00%) |
| lines | 40.16% | osm_id (100.00%) | aerialway (0.00%) |
| multipolygons | 9.64% | osm_way_id (98.65%) | geological (0.00%) |
| multilinestrings | 82.84% | osm_id (100.00%) | name (31.47%) |
| other_relations | 75.93% | osm_id (100.00%) | name (4.73%) |

## Detailed Table Analysis

### Points Table

**Total Features:** 970,588
**Columns:** 12

#### Column Completeness Analysis

| Column | Non-Null Count | Completeness | Unique Values | Top Value |
|--------|----------------|--------------|---------------|-----------|
| osm_id | 970,588 | 100.00% | 970,588 | 9999958683 |
| name | 45,394 | 4.68% | 34,687 | Subway |
| barrier | 34,079 | 3.51% | 34 | gate |
| highway | 169,002 | 17.41% | 28 | crossing |
| ref | 6,826 | 0.70% | 5,007 | MO 21 South |
| address | 6 | 0.00% | 6 | 3870 S Lindbergh Blvd #130 St.... |
| is_in | 2 | 0.00% | 2 | USA |
| place | 4,558 | 0.47% | 17 | hamlet |
| man_made | 12,040 | 1.24% | 71 | mast |
| other_tags | 867,883 | 89.42% | 432,884 | "natural"=>"tree" |

#### OSM Tags Analysis

**Total Tag Keys:** 1,306
**Total Tag Occurrences:** 2,956,051

**Most Common Tag Keys:**

| Tag Key | Occurrences | Unique Values | Sample Values |
|---------|-------------|---------------|---------------|
| addr:postcode | 399,097 | 630 | 65262-2118, 63357, 63740 |
| addr:street | 398,896 | 18,849 | Grover Ridge Circle, Fountainhead Drive, Clearl... |
| addr:housenumber | 398,806 | 18,621 | 174, 5069, 10519 |
| addr:city | 275,280 | 514 | Lineville, springfield, Northmoor |
| source:addr | 234,333 | 20 | https://www.jeffcolib.org/contact-us (accessed ... |
| natural | 146,011 | 28 | cave_entrance, gorge, sinkhole |
| power | 105,205 | 14 | portal, tower, catenary_mast |
| note:post_town | 86,113 | 10 | Pacific, Earth City, Eureka |
| addr:unit | 57,387 | 3,245 | 385A, 643, 315E |
| note:addr_place | 49,171 | 616 | Saint Anthonys Medical Center, Hilltop Trails, ... |
| level:ref | 40,756 | 29 | GR, 9, 15 |
| support | 40,205 | 14 | wall, trunk, tree |
| lamp_mount | 39,679 | 9 | wall, straight_mast, bent_mastwest_103rd_street |
| lamp_type | 39,455 | 7 | electric, sodium, e |
| crossing | 37,386 | 15 | unmarked, uncontrolled, marked |

#### Detailed Column Analysis

**osm_id**
- Completeness: 100.00% (970,588/970,588)
- Unique Values: 970,588
- Top Values:
  1. `9999958683` - 1 (0.00%)
  2. `9999958682` - 1 (0.00%)
  3. `9999958681` - 1 (0.00%)
  4. `9999958680` - 1 (0.00%)
  5. `9998294011` - 1 (0.00%)

**name**
- Completeness: 4.68% (45,394/970,588)
- Unique Values: 34,687
- Top Values:
  1. `Subway` - 164 (0.36%)
  2. `McDonald's` - 98 (0.22%)
  3. `Dollar General` - 82 (0.18%)
  4. `Starbucks` - 81 (0.18%)
  5. `CAT Scale` - 76 (0.17%)

**barrier**
- Completeness: 3.51% (34,079/970,588)
- Unique Values: 34
- Top Values:
  1. `gate` - 18,791 (55.14%)
  2. `kerb` - 9,391 (27.56%)
  3. `bollard` - 3,382 (9.92%)
  4. `block` - 702 (2.06%)
  5. `lift_gate` - 688 (2.02%)

**highway**
- Completeness: 17.41% (169,002/970,588)
- Unique Values: 28
- Top Values:
  1. `crossing` - 66,380 (39.28%)
  2. `street_lamp` - 54,357 (32.16%)
  3. `turning_circle` - 23,062 (13.65%)
  4. `traffic_signals` - 7,813 (4.62%)
  5. `stop` - 5,447 (3.22%)

**ref**
- Completeness: 0.70% (6,826/970,588)
- Unique Values: 5,007
- Top Values:
  1. `MO 21 South` - 100 (1.46%)
  2. `MO 21 North` - 100 (1.46%)
  3. `2` - 40 (0.59%)
  4. `4` - 39 (0.57%)
  5. `1` - 39 (0.57%)

**place**
- Completeness: 0.47% (4,558/970,588)
- Unique Values: 17
- Top Values:
  1. `hamlet` - 3,188 (69.94%)
  2. `village` - 682 (14.96%)
  3. `neighbourhood` - 182 (3.99%)
  4. `town` - 149 (3.27%)
  5. `county` - 112 (2.46%)

**man_made**
- Completeness: 1.24% (12,040/970,588)
- Unique Values: 71
- Top Values:
  1. `mast` - 3,758 (31.21%)
  2. `surveillance` - 1,302 (10.81%)
  3. `flagpole` - 1,194 (9.92%)
  4. `tower` - 1,024 (8.50%)
  5. `utility_pole` - 737 (6.12%)

**other_tags**
- Completeness: 89.42% (867,883/970,588)
- Unique Values: 432,884
- Top Values:
  1. `"natural"=>"tree"` - 121,093 (13.95%)
  2. `"power"=>"tower"` - 63,219 (7.28%)
  3. `"power"=>"pole"` - 31,425 (3.62%)
  4. `"lamp:count"=>"1","lamp:shape"=>"directed","lamp:tilt"=>"-90","lamp_mount"=>"bent_mast","lamp_type"=>"electric","support"=>"pole"` - 19,724 (2.27%)
  5. `"crossing"=>"unmarked","crossing:markings"=>"no"` - 17,621 (2.03%)

### Lines Table

**Total Features:** 1,286,119
**Columns:** 12

#### Column Completeness Analysis

| Column | Non-Null Count | Completeness | Unique Values | Top Value |
|--------|----------------|--------------|---------------|-----------|
| osm_id | 1,286,119 | 100.00% | 1,286,119 | 999970508 |
| name | 314,961 | 24.49% | 110,912 | Main Street |
| highway | 1,126,872 | 87.62% | 32 | service |
| waterway | 62,292 | 4.84% | 19 | stream |
| aerialway | 25 | 0.00% | 4 | chair_lift |
| barrier | 33,558 | 2.61% | 29 | fence |
| man_made | 10,353 | 0.80% | 46 | groyne |
| railway | 11,747 | 0.91% | 16 | rail |
| z_order | 1,286,119 | 100.00% | 63 | 0 |
| other_tags | 1,033,056 | 80.32% | 359,742 | "service"=>"driveway" |

#### OSM Tags Analysis

**Total Tag Keys:** 971
**Total Tag Occurrences:** 4,129,705

**Most Common Tag Keys:**

| Tag Key | Occurrences | Unique Values | Sample Values |
|---------|-------------|---------------|---------------|
| tiger:county | 415,915 | 359 | St. Louis, MO:St. Louis-City, MO, Barry, MO, Co... |
| tiger:cfcc | 413,105 | 87 | A74; A41, A41:A49, A74; A49 |
| tiger:reviewed | 401,665 | 11 | name, no, yes |
| service | 265,037 | 27 | yard, alley, acc |
| tiger:name_base | 217,063 | 47,499 | 174, Blackheath, Rebels |
| access | 192,708 | 16 | no, yes, permissive |
| tiger:name_type | 177,586 | 120 | Ave:Blvd:Ct:Dr, Blvd:Plz, St |
| surface | 157,634 | 70 | crushed_limestone, rubber, concreteq |
| tiger:source | 149,097 | 13 | tiger_import_dch_v0.6_20070812, tiger_import_dc... |
| tiger:tlid | 149,047 | 148,685 | 45196257:45196225:45196226:45196246:45201689, 6... |
| tiger:upload_uuid | 145,929 | 161 | bulk_upload.pl-33aab16b-b77d-4a46-b988-e201b6ed... |
| tiger:zip_left | 131,140 | 1,107 | 64092, 64105:64108, 64646 |
| tiger:zip_right | 119,301 | 1,059 | 64105:64108, 64646, 64476 |
| footway | 114,246 | 10 | designated, access_aisle, path |
| oneway | 90,002 | 4 | -1, alternating, no |

#### Detailed Column Analysis

**osm_id**
- Completeness: 100.00% (1,286,119/1,286,119)
- Unique Values: 1,286,119
- Top Values:
  1. `999970508` - 1 (0.00%)
  2. `999970268` - 1 (0.00%)
  3. `999968133` - 1 (0.00%)
  4. `999945937` - 1 (0.00%)
  5. `999945923` - 1 (0.00%)

**name**
- Completeness: 24.49% (314,961/1,286,119)
- Unique Values: 110,912
- Top Values:
  1. `Main Street` - 725 (0.23%)
  2. `Avenue of the Saints` - 558 (0.18%)
  3. `Marceline Subdivision` - 418 (0.13%)
  4. `2nd Street` - 361 (0.11%)
  5. `Walnut Street` - 355 (0.11%)

**highway**
- Completeness: 87.62% (1,126,872/1,286,119)
- Unique Values: 32
- Top Values:
  1. `service` - 547,444 (48.58%)
  2. `residential` - 280,098 (24.86%)
  3. `footway` - 152,370 (13.52%)
  4. `unclassified` - 27,465 (2.44%)
  5. `track` - 26,057 (2.31%)

**waterway**
- Completeness: 4.84% (62,292/1,286,119)
- Unique Values: 19
- Top Values:
  1. `stream` - 45,275 (72.68%)
  2. `ditch` - 7,311 (11.74%)
  3. `drain` - 4,956 (7.96%)
  4. `river` - 3,075 (4.94%)
  5. `dam` - 1,252 (2.01%)

**barrier**
- Completeness: 2.61% (33,558/1,286,119)
- Unique Values: 29
- Top Values:
  1. `fence` - 19,192 (57.19%)
  2. `retaining_wall` - 5,694 (16.97%)
  3. `wall` - 4,092 (12.19%)
  4. `hedge` - 1,511 (4.50%)
  5. `kerb` - 1,192 (3.55%)

**man_made**
- Completeness: 0.80% (10,353/1,286,119)
- Unique Values: 46
- Top Values:
  1. `groyne` - 3,561 (34.40%)
  2. `silo` - 2,934 (28.34%)
  3. `pier` - 888 (8.58%)
  4. `bridge` - 757 (7.31%)
  5. `pipeline` - 478 (4.62%)

**railway**
- Completeness: 0.91% (11,747/1,286,119)
- Unique Values: 16
- Top Values:
  1. `rail` - 8,837 (75.23%)
  2. `abandoned` - 1,706 (14.52%)
  3. `disused` - 482 (4.10%)
  4. `light_rail` - 258 (2.20%)
  5. `razed` - 119 (1.01%)

**z_order**
- Completeness: 100.00% (1,286,119/1,286,119)
- Unique Values: 63
- Top Values:
  1. `0` - 873,629 (67.93%)
  2. `3` - 302,118 (23.49%)
  3. `4` - 19,510 (1.52%)
  4. `6` - 16,124 (1.25%)
  5. `7` - 13,268 (1.03%)

**other_tags**
- Completeness: 80.32% (1,033,056/1,286,119)
- Unique Values: 359,742
- Top Values:
  1. `"service"=>"driveway"` - 116,406 (11.27%)
  2. `"footway"=>"sidewalk"` - 58,336 (5.65%)
  3. `"access"=>"private","service"=>"driveway"` - 48,642 (4.71%)
  4. `"service"=>"parking_aisle"` - 29,943 (2.90%)
  5. `"intermittent"=>"yes"` - 18,858 (1.83%)

### Multipolygons Table

**Total Features:** 874,841
**Columns:** 27

#### Column Completeness Analysis

| Column | Non-Null Count | Completeness | Unique Values | Top Value |
|--------|----------------|--------------|---------------|-----------|
| osm_id | 11,837 | 1.35% | 11,837 | 9998515 |
| osm_way_id | 863,004 | 98.65% | 863,004 | 999979548 |
| name | 52,980 | 6.06% | 40,707 | McDonald's |
| type | 12,106 | 1.38% | 10 | multipolygon |
| aeroway | 1,045 | 0.12% | 12 | hangar |
| amenity | 59,657 | 6.82% | 121 | parking |
| admin_level | 1,234 | 0.14% | 5 | 8 |
| barrier | 1,148 | 0.13% | 10 | kerb |
| boundary | 1,568 | 0.18% | 12 | administrative |
| building | 587,043 | 67.10% | 149 | yes |
| craft | 156 | 0.02% | 36 | brewery |
| geological | 0 | 0.00% | 0 | N |
| historic | 590 | 0.07% | 41 | building |
| land_area | 4 | 0.00% | 2 | administrative |
| landuse | 121,251 | 13.86% | 59 | grass |
| leisure | 28,779 | 3.29% | 47 | pitch |
| man_made | 3,719 | 0.43% | 33 | silo |
| military | 87 | 0.01% | 9 | office |
| natural | 87,260 | 9.97% | 27 | water |
| office | 1,208 | 0.14% | 69 | yes |
| place | 684 | 0.08% | 14 | islet |
| shop | 5,579 | 0.64% | 190 | convenience |
| sport | 10,458 | 1.20% | 156 | baseball |
| tourism | 2,148 | 0.25% | 23 | hotel |
| other_tags | 254,931 | 29.14% | 154,968 | "water"=>"pond" |

#### OSM Tags Analysis

**Total Tag Keys:** 1,242
**Total Tag Occurrences:** 944,571

**Most Common Tag Keys:**

| Tag Key | Occurrences | Unique Values | Sample Values |
|---------|-------------|---------------|---------------|
| addr:street | 137,650 | 10,014 | Royal Court, North Riverside Road, Sarpy Avenue |
| addr:housenumber | 134,963 | 13,996 | 174, 10519, 5069 |
| addr:postcode | 131,676 | 867 | 64092, 63703-5742, 63123-3935 |
| addr:city | 123,441 | 763 | Downing, Northmoor, Thomasville |
| addr:state | 111,263 | 12 | mo, Missouri, IL |
| water | 22,193 | 29 | slough, lake;reservoir, high |
| addr:country | 18,284 | 1 | US |
| golf | 17,643 | 12 | water_hazard, green, out_of_bounds |
| access | 15,164 | 18 | permissive, yes, permit |
| parking | 14,959 | 11 | street_side, multi-storey, yes |
| building:levels | 13,881 | 47 | 9, 15, 21 |
| leaf_type | 13,590 | 4 | leafless, broadleaved, mixed |
| leaf_cycle | 13,366 | 5 | deciduous, evergreen, semi_deciduous |
| source:addr | 9,034 | 37 | https://sjsnoballshop.com/locations, https://ww... |
| surface | 8,928 | 58 | sport_tiles, rubber, rubbercrumb |

#### Detailed Column Analysis

**osm_id**
- Completeness: 1.35% (11,837/874,841)
- Unique Values: 11,837
- Top Values:
  1. `9998515` - 1 (0.01%)
  2. `9997810` - 1 (0.01%)
  3. `9997809` - 1 (0.01%)
  4. `9997459` - 1 (0.01%)
  5. `9997458` - 1 (0.01%)

**osm_way_id**
- Completeness: 98.65% (863,004/874,841)
- Unique Values: 863,004
- Top Values:
  1. `999979548` - 1 (0.00%)
  2. `999979547` - 1 (0.00%)
  3. `999979546` - 1 (0.00%)
  4. `999979545` - 1 (0.00%)
  5. `999979544` - 1 (0.00%)

**name**
- Completeness: 6.06% (52,980/874,841)
- Unique Values: 40,707
- Top Values:
  1. `McDonald's` - 219 (0.41%)
  2. `QuikTrip` - 204 (0.39%)
  3. `Buildings/Houses` - 203 (0.38%)
  4. `Casey's General Store` - 198 (0.37%)
  5. `Phillips 66` - 193 (0.36%)

**type**
- Completeness: 1.38% (12,106/874,841)
- Unique Values: 10
- Top Values:
  1. `multipolygon` - 10,362 (85.59%)
  2. `boundary` - 1,484 (12.26%)
  3. `bin` - 222 (1.83%)
  4. `rain garden` - 12 (0.10%)
  5. `public` - 11 (0.09%)

**aeroway**
- Completeness: 0.12% (1,045/874,841)
- Unique Values: 12
- Top Values:
  1. `hangar` - 503 (48.13%)
  2. `helipad` - 208 (19.90%)
  3. `apron` - 177 (16.94%)
  4. `aerodrome` - 100 (9.57%)
  5. `terminal` - 29 (2.78%)

**amenity**
- Completeness: 6.82% (59,657/874,841)
- Unique Values: 121
- Top Values:
  1. `parking` - 24,681 (41.37%)
  2. `parking_space` - 17,114 (28.69%)
  3. `place_of_worship` - 2,846 (4.77%)
  4. `shelter` - 1,899 (3.18%)
  5. `fast_food` - 1,510 (2.53%)

**admin_level**
- Completeness: 0.14% (1,234/874,841)
- Unique Values: 5
- Top Values:
  1. `8` - 971 (78.69%)
  2. `6` - 116 (9.40%)
  3. `10` - 80 (6.48%)
  4. `7` - 66 (5.35%)
  5. `4` - 1 (0.08%)

**barrier**
- Completeness: 0.13% (1,148/874,841)
- Unique Values: 10
- Top Values:
  1. `kerb` - 542 (47.21%)
  2. `fence` - 299 (26.05%)
  3. `retaining_wall` - 138 (12.02%)
  4. `wall` - 117 (10.19%)
  5. `toll_booth` - 31 (2.70%)

**boundary**
- Completeness: 0.18% (1,568/874,841)
- Unique Values: 12
- Top Values:
  1. `administrative` - 1,234 (78.70%)
  2. `protected_area` - 272 (17.35%)
  3. `census` - 36 (2.30%)
  4. `National Forest System Lands` - 10 (0.64%)
  5. `hazard` - 5 (0.32%)

**building**
- Completeness: 67.10% (587,043/874,841)
- Unique Values: 149
- Top Values:
  1. `yes` - 315,080 (53.67%)
  2. `house` - 122,755 (20.91%)
  3. `detached` - 89,362 (15.22%)
  4. `garage` - 8,071 (1.37%)
  5. `residential` - 7,292 (1.24%)

**craft**
- Completeness: 0.02% (156/874,841)
- Unique Values: 36
- Top Values:
  1. `brewery` - 25 (16.03%)
  2. `winery` - 20 (12.82%)
  3. `hvac` - 12 (7.69%)
  4. `distillery` - 9 (5.77%)
  5. `sawmill` - 8 (5.13%)

**historic**
- Completeness: 0.07% (590/874,841)
- Unique Values: 41
- Top Values:
  1. `building` - 138 (23.39%)
  2. `military` - 95 (16.10%)
  3. `yes` - 58 (9.83%)
  4. `maritime` - 48 (8.14%)
  5. `memorial` - 47 (7.97%)

**landuse**
- Completeness: 13.86% (121,251/874,841)
- Unique Values: 59
- Top Values:
  1. `grass` - 32,569 (26.86%)
  2. `residential` - 24,313 (20.05%)
  3. `farmland` - 19,735 (16.28%)
  4. `meadow` - 15,413 (12.71%)
  5. `commercial` - 7,031 (5.80%)

**leisure**
- Completeness: 3.29% (28,779/874,841)
- Unique Values: 47
- Top Values:
  1. `pitch` - 9,780 (33.98%)
  2. `garden` - 6,156 (21.39%)
  3. `swimming_pool` - 4,171 (14.49%)
  4. `playground` - 2,849 (9.90%)
  5. `park` - 2,716 (9.44%)

**man_made**
- Completeness: 0.43% (3,719/874,841)
- Unique Values: 33
- Top Values:
  1. `silo` - 2,300 (61.84%)
  2. `storage_tank` - 554 (14.90%)
  3. `pier` - 353 (9.49%)
  4. `breakwater` - 147 (3.95%)
  5. `tower` - 69 (1.86%)

**military**
- Completeness: 0.01% (87/874,841)
- Unique Values: 9
- Top Values:
  1. `office` - 51 (58.62%)
  2. `bunker` - 17 (19.54%)
  3. `checkpoint` - 8 (9.20%)
  4. `airfield` - 3 (3.45%)
  5. `training_area` - 2 (2.30%)

**natural**
- Completeness: 9.97% (87,260/874,841)
- Unique Values: 27
- Top Values:
  1. `water` - 34,137 (39.12%)
  2. `wood` - 29,625 (33.95%)
  3. `scrub` - 10,239 (11.73%)
  4. `sand` - 5,759 (6.60%)
  5. `grassland` - 4,696 (5.38%)

**office**
- Completeness: 0.14% (1,208/874,841)
- Unique Values: 69
- Top Values:
  1. `yes` - 442 (36.59%)
  2. `government` - 211 (17.47%)
  3. `insurance` - 103 (8.53%)
  4. `lawyer` - 68 (5.63%)
  5. `estate_agent` - 44 (3.64%)

**place**
- Completeness: 0.08% (684/874,841)
- Unique Values: 14
- Top Values:
  1. `islet` - 298 (43.57%)
  2. `island` - 190 (27.78%)
  3. `city` - 66 (9.65%)
  4. `neighbourhood` - 57 (8.33%)
  5. `village` - 29 (4.24%)

**shop**
- Completeness: 0.64% (5,579/874,841)
- Unique Values: 190
- Top Values:
  1. `convenience` - 825 (14.79%)
  2. `storage_rental` - 513 (9.20%)
  3. `car_repair` - 509 (9.12%)
  4. `supermarket` - 450 (8.07%)
  5. `car` - 337 (6.04%)

**sport**
- Completeness: 1.20% (10,458/874,841)
- Unique Values: 156
- Top Values:
  1. `baseball` - 2,491 (23.82%)
  2. `tennis` - 2,410 (23.04%)
  3. `soccer` - 1,079 (10.32%)
  4. `basketball` - 940 (8.99%)
  5. `golf` - 686 (6.56%)

**tourism**
- Completeness: 0.25% (2,148/874,841)
- Unique Values: 23
- Top Values:
  1. `hotel` - 749 (34.87%)
  2. `camp_site` - 266 (12.38%)
  3. `motel` - 254 (11.82%)
  4. `museum` - 206 (9.59%)
  5. `camp_pitch` - 184 (8.57%)

**other_tags**
- Completeness: 29.14% (254,931/874,841)
- Unique Values: 154,968
- Top Values:
  1. `"water"=>"pond"` - 15,116 (5.93%)
  2. `"leaf_cycle"=>"deciduous","leaf_type"=>"broadleaved"` - 11,809 (4.63%)
  3. `"golf"=>"tee"` - 5,778 (2.27%)
  4. `"golf"=>"bunker"` - 4,792 (1.88%)
  5. `"parking"=>"surface"` - 3,281 (1.29%)

### Multilinestrings Table

**Total Features:** 3,168
**Columns:** 6

#### Column Completeness Analysis

| Column | Non-Null Count | Completeness | Unique Values | Top Value |
|--------|----------------|--------------|---------------|-----------|
| osm_id | 3,168 | 100.00% | 3,168 | 9982304 |
| name | 997 | 31.47% | 892 | San Sebastian Drive |
| type | 3,168 | 100.00% | 1 | route |
| other_tags | 3,165 | 99.91% | 2,532 | "network"=>"lcn","route"=>"bic... |

#### OSM Tags Analysis

**Total Tag Keys:** 100
**Total Tag Occurrences:** 17,042

**Most Common Tag Keys:**

| Tag Key | Occurrences | Unique Values | Sample Values |
|---------|-------------|---------------|---------------|
| route | 3,161 | 25 | road, boat, hiking;mtb; |
| network | 2,703 | 70 | lwn, US:I:Business:Loop, US:MO:Supplemental:Spur |
| ref | 2,457 | 420 | 138, 174, FF |
| description | 1,870 | 1,784 | Missouri Route KK (Buchanan County), US 50 (MO,... |
| symbol | 1,506 | 327 | http://upload.wikimedia.org/wikipedia/commons/c... |
| is_in:county | 1,050 | 218 | Clinton;DeKalb, Monroe;Audrain, Linn;Sullivan |
| is_in:state | 618 | 17 | OK;MO, IL, KS |
| operator | 472 | 63 | Norfolk Southern, Lee's Summit Parks & Recreati... |
| wikipedia | 325 | 276 | en:Missouri Route 34, en:Missouri Route 138, en... |
| wikidata | 322 | 277 | Q94369, Q2485394, Q2443245 |
| from | 222 | 135 | Ashland Rd & Tara Apt, Kansas City Union Statio... |
| to | 222 | 128 | Ashland Rd & Tara Apt, KC Medical Center, Kansa... |
| network:wikidata | 186 | 7 | Q6364652, Q23239, Q755309 |
| network:wikipedia | 175 | 7 | en:MetroBus (St. Louis), en:MetroLink (St. Loui... |
| operator:wikidata | 142 | 14 | Q4902339, Q5160697, Q725793 |

#### Detailed Column Analysis

**osm_id**
- Completeness: 100.00% (3,168/3,168)
- Unique Values: 3,168
- Top Values:
  1. `9982304` - 1 (0.03%)
  2. `9982303` - 1 (0.03%)
  3. `9965864` - 1 (0.03%)
  4. `9964037` - 1 (0.03%)
  5. `9956978` - 1 (0.03%)

**name**
- Completeness: 31.47% (997/3,168)
- Unique Values: 892
- Top Values:
  1. `San Sebastian Drive` - 20 (2.01%)
  2. `San Martin Drive` - 19 (1.91%)
  3. `Villa Gran Way` - 9 (0.90%)
  4. `La Palma Drive` - 9 (0.90%)
  5. `Coronita Drive` - 8 (0.80%)

**type**
- Completeness: 100.00% (3,168/3,168)
- Unique Values: 1
- Top Values:
  1. `route` - 3,168 (100.00%)

**other_tags**
- Completeness: 99.91% (3,165/3,168)
- Unique Values: 2,532
- Top Values:
  1. `"network"=>"lcn","route"=>"bicycle"` - 129 (4.08%)
  2. `"route"=>"road"` - 104 (3.29%)
  3. `"route"=>"mtb"` - 64 (2.02%)
  4. `"cables"=>"3","frequency"=>"60","route"=>"power","wires"=>"single"` - 34 (1.07%)
  5. `"cables"=>"3","frequency"=>"60","route"=>"power","voltage"=>"345000","wires"=>"double"` - 28 (0.88%)

### Other_Relations Table

**Total Features:** 10,055
**Columns:** 6

#### Column Completeness Analysis

| Column | Non-Null Count | Completeness | Unique Values | Top Value |
|--------|----------------|--------------|---------------|-----------|
| osm_id | 10,055 | 100.00% | 10,055 | 9980137 |
| name | 476 | 4.73% | 466 | Winnebago Street |
| type | 10,055 | 100.00% | 20 | restriction |
| other_tags | 9,953 | 98.99% | 268 | "restriction"=>"no_left_turn" |

#### OSM Tags Analysis

**Total Tag Keys:** 177
**Total Tag Occurrences:** 11,057

**Most Common Tag Keys:**

| Tag Key | Occurrences | Unique Values | Sample Values |
|---------|-------------|---------------|---------------|
| restriction | 9,407 | 8 | only_straight_on, no_straight_on, no_right_turn |
| public_transport | 170 | 1 | stop_area |
| network | 169 | 4 | Amtrak, Ride KC, MetroLink |
| waterway | 151 | 3 | river, canal, stream |
| operator | 148 | 21 | Ameren, Cow Branch Wind Power, LLC, Clear Creek... |
| implicit | 108 | 1 | yes |
| wikidata | 77 | 77 | Q3395961, Q14704468, Q27985071 |
| restriction:conditional | 77 | 30 | no_right_turn @ (Mo-Su 07:00-09:00; 15:00-16:00... |
| destination | 64 | 31 | Gulf of Mexico, Hog Creek, Missouri River |
| railway | 51 | 1 | facility |
| wikipedia | 46 | 46 | en:Ike Skelton Bridge, en:Ohio River, en:Jacks ... |
| gnis:feature_id | 33 | 33 | 759310, 426459, 410769 |
| man_made | 30 | 1 | antenna |
| check_date | 29 | 5 | 2025-05-18, 2025-02-15, 2025-05-24 |
| site | 25 | 17 | hospital, yes, parking |

#### Detailed Column Analysis

**osm_id**
- Completeness: 100.00% (10,055/10,055)
- Unique Values: 10,055
- Top Values:
  1. `9980137` - 1 (0.01%)
  2. `9980136` - 1 (0.01%)
  3. `9980135` - 1 (0.01%)
  4. `9980134` - 1 (0.01%)
  5. `9976525` - 1 (0.01%)

**name**
- Completeness: 4.73% (476/10,055)
- Unique Values: 466
- Top Values:
  1. `Winnebago Street` - 2 (0.42%)
  2. `Whitewater River` - 2 (0.42%)
  3. `Union Station` - 2 (0.42%)
  4. `Saline Creek` - 2 (0.42%)
  5. `Panther Creek` - 2 (0.42%)

**type**
- Completeness: 100.00% (10,055/10,055)
- Unique Values: 20
- Top Values:
  1. `restriction` - 9,478 (94.26%)
  2. `public_transport` - 170 (1.69%)
  3. `waterway` - 162 (1.61%)
  4. `site` - 66 (0.66%)
  5. `street` - 45 (0.45%)

**other_tags**
- Completeness: 98.99% (9,953/10,055)
- Unique Values: 268
- Top Values:
  1. `"restriction"=>"no_left_turn"` - 3,178 (31.93%)
  2. `"restriction"=>"no_u_turn"` - 2,686 (26.99%)
  3. `"restriction"=>"no_right_turn"` - 1,208 (12.14%)
  4. `"restriction"=>"only_straight_on"` - 1,054 (10.59%)
  5. `"restriction"=>"only_right_turn"` - 882 (8.86%)

## Cross-Table Analysis

### Feature Type Distribution

The data shows a typical OSM distribution pattern:

1. **lines**: 1,286,119 features (40.90%)
2. **points**: 970,588 features (30.86%)
3. **multipolygons**: 874,841 features (27.82%)
4. **other_relations**: 10,055 features (0.32%)
5. **multilinestrings**: 3,168 features (0.10%)

### Data Quality Insights

- **Best Data Quality**: multilinestrings (82.84% average completeness)
- **Worst Data Quality**: multipolygons (9.64% average completeness)

### OSM Tags Insights

- **Total Unique Tag Keys Across All Tables**: 2,412
- **Total Tag Occurrences**: 8,058,426

**Most Common Tags Across All Tables:**

| Tag Key | Total Occurrences |
|---------|-------------------|
| addr:street | 536,876 |
| addr:housenumber | 534,042 |
| addr:postcode | 531,125 |
| tiger:county | 415,922 |
| tiger:cfcc | 413,107 |
| tiger:reviewed | 401,674 |
| addr:city | 398,990 |
| service | 265,101 |
| source:addr | 243,369 |
| tiger:name_base | 217,066 |
| access | 211,545 |
| tiger:name_type | 177,587 |
| surface | 167,621 |
| tiger:source | 149,097 |
| tiger:tlid | 149,047 |
| natural | 148,761 |
| tiger:upload_uuid | 145,929 |
| tiger:zip_left | 131,141 |
| addr:state | 126,910 |
| power | 125,774 |

## Recommendations for Data Usage

### High-Quality Data Sources

- **points**: osm_id, other_tags
- **lines**: osm_id, highway, z_order, other_tags
- **multipolygons**: osm_way_id
- **multilinestrings**: osm_id, type, other_tags
- **other_relations**: osm_id, type, other_tags

### Data Gaps to Consider

- **points**: name, barrier, highway, ref, address, is_in, place, man_made (completeness < 20%)
- **lines**: waterway, aerialway, barrier, man_made, railway (completeness < 20%)
- **multipolygons**: osm_id, name, type, aeroway, amenity, admin_level, barrier, boundary, craft, geological, historic, land_area, landuse, leisure, man_made, military, natural, office, place, shop, sport, tourism (completeness < 20%)
- **other_relations**: name (completeness < 20%)

### Feature Development Priorities

Based on data completeness and availability:

- **lines.highway**: 87.62% completeness
- **multipolygons.building**: 67.10% completeness

## Geographical Analysis### Spatial Distribution Patterns#### Feature Distribution by Table| Table | Total Features | With Geometry | Geometry Coverage ||-------|----------------|---------------|-------------------|| points | 970,588 | 970,588 | 100.00% || lines | 1,286,119 | 1,286,119 | 100.00% || multipolygons | 874,841 | 874,841 | 100.00% || multilinestrings | 3,168 | 3,168 | 100.00% || other_relations | 10,055 | 10,055 | 100.00% |#### Feature Type Distribution**Points - Top Feature Types:**- **highway**: 168,680 features (17.38% completeness)  - Top types:    1. `crossing` - 66,380 (39.35%)    2. `street_lamp` - 54,357 (32.22%)    3. `turning_circle` - 23,062 (13.67%)    4. `traffic_signals` - 7,813 (4.63%)    5. `stop` - 5,447 (3.23%)**Lines - Top Feature Types:**- **highway**: 1,099,680 features (85.50% completeness)  - Top types:    1. `service` - 547,444 (49.78%)    2. `residential` - 280,098 (25.47%)    3. `footway` - 152,370 (13.86%)    4. `unclassified` - 27,465 (2.50%)    5. `track` - 26,057 (2.37%)**Multipolygons - Top Feature Types:**- **building**: 566,260 features (64.73% completeness)  - Top types:    1. `yes` - 315,080 (55.64%)    2. `house` - 122,755 (21.68%)    3. `detached` - 89,362 (15.78%)    4. `garage` - 8,071 (1.43%)    5. `residential` - 7,292 (1.29%)- **amenity**: 53,986 features (6.17% completeness)  - Top types:    1. `parking` - 24,681 (45.72%)    2. `parking_space` - 17,114 (31.70%)    3. `place_of_worship` - 2,846 (5.27%)    4. `shelter` - 1,899 (3.52%)    5. `fast_food` - 1,510 (2.80%)- **natural**: 87,023 features (9.95% completeness)  - Top types:    1. `water` - 34,137 (39.23%)    2. `wood` - 29,625 (34.04%)    3. `scrub` - 10,239 (11.77%)    4. `sand` - 5,759 (6.62%)    5. `grassland` - 4,696 (5.40%)- **landuse**: 116,230 features (13.29% completeness)  - Top types:    1. `grass` - 32,569 (28.02%)    2. `residential` - 24,313 (20.92%)    3. `farmland` - 19,735 (16.98%)    4. `meadow` - 15,413 (13.26%)    5. `commercial` - 7,031 (6.05%)- **tourism**: 2,023 features (0.23% completeness)  - Top types:    1. `hotel` - 749 (37.02%)    2. `camp_site` - 266 (13.15%)    3. `motel` - 254 (12.56%)    4. `museum` - 206 (10.18%)    5. `camp_pitch` - 184 (9.10%)- **shop**: 3,408 features (0.39% completeness)  - Top types:    1. `convenience` - 825 (24.21%)    2. `storage_rental` - 513 (15.05%)    3. `car_repair` - 509 (14.94%)    4. `supermarket` - 450 (13.20%)    5. `car` - 337 (9.89%)### Data Quality Geographical Patterns#### Data Completeness by Table| Table | Named Features | Tagged Features | High Quality ||-------|----------------|-----------------|--------------|| points | 4.68% | 89.42% | 4.59% || lines | 24.49% | 80.32% | 22.05% || multipolygons | 6.06% | 29.14% | 4.25% || multilinestrings | 31.47% | 99.91% | 31.47% || other_relations | 4.73% | 98.99% | 4.13% |### Missouri-Specific Characteristics#### Road Network AnalysisMissouri's road network shows the following distribution:**Lines - Highway Types:**1. `service` - 547,444 features2. `residential` - 280,098 features3. `footway` - 152,370 features4. `unclassified` - 27,465 features5. `track` - 26,057 features6. `tertiary` - 20,864 features7. `secondary` - 16,715 features8. `primary` - 12,281 features9. `path` - 9,306 features10. `motorway_link` - 7,080 features#### Water Features AnalysisMissouri's water features (rivers, streams, etc.):**Lines - Waterway Types:**1. `stream` - 45,275 features2. `ditch` - 7,311 features3. `drain` - 4,956 features4. `river` - 3,075 features5. `dam` - 1,252 features6. `canal` - 296 features7. `weir` - 57 features8. `lock_gate` - 17 features9. `flowline` - 14 features10. `dock` - 13 features#### Administrative Boundaries**Multipolygons - Administrative Levels:**1. Level 8 - 971 features2. Level 6 - 116 features3. Level 10 - 80 features4. Level 7 - 66 features5. Level 4 - 1 features### OSM Tag Patterns#### Location Tag AnalysisAnalysis of location-related tags across all tables:| Location Tag Type | Total Occurrences ||-------------------|-------------------|| city | 14,815 || county | 9,200 || addr: | 3,263 || postcode | 2,402 || state | 1,172 || country | 94 || place | 1 |#### Tag Complexity DistributionDistribution of tag complexity (number of tags per feature):**Points:**- 1_tags: 267,220 features- 2_tags: 38,118 features- 3_tags: 26,988 features- 4_tags: 4,406 features- 5_tags: 3,821 features- 6_tags: 32,603 features- 9_tags: 504 features- 10_tags: 491 features**Lines:**- 1_tags: 311,297 features- 2_tags: 107,111 features- 3_tags: 38,863 features- 4_tags: 2,118 features- 5_tags: 1,615 features- 6_tags: 10,315 features**Multipolygons:**- 1_tags: 57,907 features- 2_tags: 20,607 features- 3_tags: 2,563 features- 4_tags: 94 features- 6_tags: 856 features**Multilinestrings:**- 1_tags: 225 features- 2_tags: 150 features- 3_tags: 119 features- 4_tags: 52 features- 5_tags: 61 features- 6_tags: 111 features- 7_tags: 2 features- 13_tags: 2 features**Other_Relations:**- 1_tags: 9,445 features- 2_tags: 158 features- 3_tags: 144 features- 4_tags: 36 features- 6_tags: 2 features### Geographical Insights- **Overall Geometry Coverage**: 100.00% of features have valid geometry- **Total Features Analyzed**: 3,144,771- **Best Geometry Coverage**: points (100.00%)- **Most Named Features**: multilinestrings (31.47%)## Technical Notes

- **File Format**: GeoPackage (SQLite-based)
- **Coordinate System**: WGS84 (EPSG:4326)
- **Spatial Indexing**: R-tree indexes available for all geometry columns
- **Data Source**: OpenStreetMap Missouri extract
- **Analysis Date**: 2025-10-18 16:07:32

---
*This report was generated automatically from the Missouri GeoPackage analysis.*