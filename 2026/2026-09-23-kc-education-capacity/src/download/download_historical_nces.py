"""
Download official NCES CCD and EDGE Geocode datasets across 11 school years (2014–15 through 2024–25).
Maintains exact provenance, computes SHA256 hashes, and populates research/historical_source_matrix.csv.
"""

import sys
import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_NCES_DIR = PROJECT_ROOT / "data" / "raw" / "nces"
RESEARCH_DIR = PROJECT_ROOT / "research"
MATRIX_CSV = RESEARCH_DIR / "historical_source_matrix.csv"

# Pre-compiled catalog of official NCES files across all 11 years
# Maps school_year -> list of datasets
CATALOG = [
    # 2014-2015 (Era 1)
    {"school_year": "2014-2015", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_1415_w_0216601a_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_1415_w_0216601a_txt.zip", "schema_notes": "School Directory tab-delimited text"},
    {"school_year": "2014-2015", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_sch_052_1415_w_0216161a_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_1415_w_0216161a_txt.zip", "schema_notes": "School Membership wide table"},
    {"school_year": "2014-2015", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_1415_w_0216161a_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_1415_w_0216161a_txt.zip", "schema_notes": "School Staff wide table with FTE"},
    {"school_year": "2014-2015", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_1415_w_0216161a_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_1415_w_0216161a_txt.zip", "schema_notes": "School Characteristics wide table"},
    {"school_year": "2014-2015", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_1415_w_0216161a_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_1415_w_0216161a_txt.zip", "schema_notes": "School Lunch wide table with TOTFRL"},
    {"school_year": "2014-2015", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_1415_w_0216161ar_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_1415_w_0216161ar_txt.zip", "schema_notes": "LEA Directory tab-delimited text"},
    {"school_year": "2014-2015", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_1415_w_0216161a_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_1415_w_0216161a_txt.zip", "schema_notes": "LEA Membership wide table"},
    {"school_year": "2014-2015", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_1415_w_0216161a_txt.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_1415_w_0216161a_txt.zip", "schema_notes": "LEA Staff wide table with TOTTCH/PARA"},
    {"school_year": "2014-2015", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOIDS_201415_PUBLIC_SCHOOL_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/EDGE_GEOIDS_201415_PUBLIC_SCHOOL_csv.zip", "schema_notes": "EDGE Public School Geocodes CSV"},

    # 2015-2016 (Era 1)
    {"school_year": "2015-2016", "dataset": "CCD School Directory", "release_version": "v.2a", "filename": "ccd_sch_029_1516_w_2a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_1516_w_2a_011717_csv.zip", "schema_notes": "School Directory CSV"},
    {"school_year": "2015-2016", "dataset": "CCD School Membership", "release_version": "v.2a", "filename": "ccd_sch_052_1516_w_2a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_1516_w_2a_011717_csv.zip", "schema_notes": "School Membership wide table CSV"},
    {"school_year": "2015-2016", "dataset": "CCD School Staff", "release_version": "v.2a", "filename": "ccd_sch_059_1516_w_2a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_1516_w_2a_011717_csv.zip", "schema_notes": "School Staff wide table CSV"},
    {"school_year": "2015-2016", "dataset": "CCD School Characteristics", "release_version": "v.2a", "filename": "ccd_sch_129_1516_w_2a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_1516_w_2a_011717_csv.zip", "schema_notes": "School Characteristics CSV"},
    {"school_year": "2015-2016", "dataset": "CCD School Lunch", "release_version": "v.2a", "filename": "ccd_sch_033_1516_w_2a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_1516_w_2a_011717_csv.zip", "schema_notes": "School Lunch wide table CSV"},
    {"school_year": "2015-2016", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_1516_w_1a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_1516_w_1a_011717_csv.zip", "schema_notes": "LEA Directory CSV"},
    {"school_year": "2015-2016", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_1516_w_1a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_1516_w_1a_011717_csv.zip", "schema_notes": "LEA Membership wide table CSV"},
    {"school_year": "2015-2016", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "CCD_LEA_059_1516_W_1a_011717_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/CCD_LEA_059_1516_W_1a_011717_csv.zip", "schema_notes": "LEA Staff wide table CSV"},
    {"school_year": "2015-2016", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_1516.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_1516.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2016-2017 (Era 2)
    {"school_year": "2016-2017", "dataset": "CCD School Directory", "release_version": "v.2a", "filename": "ccd_sch_029_1617_w_1a_11212017_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_1617_w_1a_11212017_csv.zip", "schema_notes": "School Directory CSV"},
    {"school_year": "2016-2017", "dataset": "CCD School Membership", "release_version": "v.2a", "filename": "ccd_sch_052_1617_l_2a_11212017_CSV.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_1617_l_2a_11212017_CSV.zip", "schema_notes": "School Membership long table CSV (Deflate64)"},
    {"school_year": "2016-2017", "dataset": "CCD School Staff", "release_version": "v.2a", "filename": "ccd_sch_059_1617_l_2a_11212017.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_1617_l_2a_11212017.zip", "schema_notes": "School Staff long table CSV with TEACHERS"},
    {"school_year": "2016-2017", "dataset": "CCD School Characteristics", "release_version": "v.2a", "filename": "ccd_sch_129_1617_w_1a_11212017.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_1617_w_1a_11212017.zip", "schema_notes": "School Characteristics CSV"},
    {"school_year": "2016-2017", "dataset": "CCD School Lunch", "release_version": "v.2a", "filename": "ccd_sch_033_1617_l_2a_11212017.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_1617_l_2a_11212017.zip", "schema_notes": "School Lunch long table CSV"},
    {"school_year": "2016-2017", "dataset": "CCD LEA Directory", "release_version": "v.2a", "filename": "ccd_lea_029_1617_w_1a_11212017_csv.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_1617_w_1a_11212017_csv.zip", "schema_notes": "LEA Directory CSV"},
    {"school_year": "2016-2017", "dataset": "CCD LEA Membership", "release_version": "v.2a", "filename": "ccd_lea_052_1617_l_2a_11212017.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_1617_l_2a_11212017.zip", "schema_notes": "LEA Membership long table CSV"},
    {"school_year": "2016-2017", "dataset": "CCD LEA Staff", "release_version": "v.2a", "filename": "ccd_lea_059_1617_l_2a_11212017.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_1617_l_2a_11212017.zip", "schema_notes": "LEA Staff long table CSV"},
    {"school_year": "2016-2017", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_1617.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_1617.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2017-2018 (Era 3)
    {"school_year": "2017-2018", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_1718_w_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_1718_w_1a_083118.zip", "schema_notes": "School Directory archive"},
    {"school_year": "2017-2018", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_sch_052_1718_l_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_1718_l_1a_083118.zip", "schema_notes": "School Membership long table archive"},
    {"school_year": "2017-2018", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_1718_l_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_1718_l_1a_083118.zip", "schema_notes": "School Staff long table archive"},
    {"school_year": "2017-2018", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_1718_w_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_1718_w_1a_083118.zip", "schema_notes": "School Characteristics archive"},
    {"school_year": "2017-2018", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_1718_l_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_1718_l_1a_083118.zip", "schema_notes": "School Lunch long table archive"},
    {"school_year": "2017-2018", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_1718_w_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_1718_w_1a_083118.zip", "schema_notes": "LEA Directory archive"},
    {"school_year": "2017-2018", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_1718_l_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_1718_l_1a_083118.zip", "schema_notes": "LEA Membership long table archive"},
    {"school_year": "2017-2018", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_1718_l_1a_083118.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_1718_l_1a_083118.zip", "schema_notes": "LEA Staff long table archive"},
    {"school_year": "2017-2018", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_1718.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_1718.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2018-2019 (Era 3)
    {"school_year": "2018-2019", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_1819_w_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_1819_w_1a_091019.zip", "schema_notes": "School Directory archive"},
    {"school_year": "2018-2019", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_sch_052_1819_l_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_1819_l_1a_091019.zip", "schema_notes": "School Membership long table archive"},
    {"school_year": "2018-2019", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_1819_l_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_1819_l_1a_091019.zip", "schema_notes": "School Staff long table archive"},
    {"school_year": "2018-2019", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_1819_w_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_1819_w_1a_091019.zip", "schema_notes": "School Characteristics archive"},
    {"school_year": "2018-2019", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_1819_l_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_1819_l_1a_091019.zip", "schema_notes": "School Lunch long table archive"},
    {"school_year": "2018-2019", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_1819_l_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_1819_l_1a_091019.zip", "schema_notes": "LEA Directory archive"},
    {"school_year": "2018-2019", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_1819_l_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_1819_l_1a_091019.zip", "schema_notes": "LEA Membership long table archive"},
    {"school_year": "2018-2019", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_1819_l_1a_091019.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_1819_l_1a_091019.zip", "schema_notes": "LEA Staff long table archive"},
    {"school_year": "2018-2019", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_1819.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_1819.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2019-2020 (Era 3)
    {"school_year": "2019-2020", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_1920_w_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_1920_w_1a_082120.zip", "schema_notes": "School Directory archive"},
    {"school_year": "2019-2020", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_SCH_052_1920_l_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_SCH_052_1920_l_1a_082120.zip", "schema_notes": "School Membership long table archive"},
    {"school_year": "2019-2020", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_1920_l_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_1920_l_1a_082120.zip", "schema_notes": "School Staff long table archive"},
    {"school_year": "2019-2020", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_1920_w_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_1920_w_1a_082120.zip", "schema_notes": "School Characteristics archive"},
    {"school_year": "2019-2020", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_1920_l_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_1920_l_1a_082120.zip", "schema_notes": "School Lunch long table archive"},
    {"school_year": "2019-2020", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_1920_w_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_1920_w_1a_082120.zip", "schema_notes": "LEA Directory archive"},
    {"school_year": "2019-2020", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_1920_l_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_1920_l_1a_082120.zip", "schema_notes": "LEA Membership long table archive"},
    {"school_year": "2019-2020", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_1920_l_1a_082120.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_1920_l_1a_082120.zip", "schema_notes": "LEA Staff long table archive"},
    {"school_year": "2019-2020", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_1920.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_1920.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2020-2021 (Era 3)
    {"school_year": "2020-2021", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_2021_w_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_2021_w_1a_080621.zip", "schema_notes": "School Directory archive"},
    {"school_year": "2020-2021", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_sch_052_2021_l_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_2021_l_1a_080621.zip", "schema_notes": "School Membership long table archive"},
    {"school_year": "2020-2021", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_2021_l_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_2021_l_1a_080621.zip", "schema_notes": "School Staff long table archive"},
    {"school_year": "2020-2021", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_2021_w_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_2021_w_1a_080621.zip", "schema_notes": "School Characteristics archive"},
    {"school_year": "2020-2021", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_2021_l_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_2021_l_1a_080621.zip", "schema_notes": "School Lunch long table archive"},
    {"school_year": "2020-2021", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_2021_w_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_2021_w_1a_080621.zip", "schema_notes": "LEA Directory archive"},
    {"school_year": "2020-2021", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_2021_l_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_2021_l_1a_080621.zip", "schema_notes": "LEA Membership long table archive"},
    {"school_year": "2020-2021", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_2021_l_1a_080621.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_2021_l_1a_080621.zip", "schema_notes": "LEA Staff long table archive"},
    {"school_year": "2020-2021", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_2021.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2021.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2021-2022 (Era 3)
    {"school_year": "2021-2022", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_2122_w_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_2122_w_1a_071722.zip", "schema_notes": "School Directory archive"},
    {"school_year": "2021-2022", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_SCH_052_2122_l_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_SCH_052_2122_l_1a_071722.zip", "schema_notes": "School Membership long table archive"},
    {"school_year": "2021-2022", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_2122_l_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_2122_l_1a_071722.zip", "schema_notes": "School Staff long table archive"},
    {"school_year": "2021-2022", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_2122_w_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_2122_w_1a_071722.zip", "schema_notes": "School Characteristics archive"},
    {"school_year": "2021-2022", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_2122_l_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_2122_l_1a_071722.zip", "schema_notes": "School Lunch long table archive"},
    {"school_year": "2021-2022", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_2122_w_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_2122_w_1a_071722.zip", "schema_notes": "LEA Directory archive"},
    {"school_year": "2021-2022", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_2122_l_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_2122_l_1a_071722.zip", "schema_notes": "LEA Membership long table archive"},
    {"school_year": "2021-2022", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_2122_l_1a_071722.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_2122_l_1a_071722.zip", "schema_notes": "LEA Staff long table archive"},
    {"school_year": "2021-2022", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_2122.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2122.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2022-2023 (Era 3)
    {"school_year": "2022-2023", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_2223_w_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_2223_w_1a_083023.zip", "schema_notes": "School Directory archive"},
    {"school_year": "2022-2023", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_sch_052_2223_l_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_2223_l_1a_083023.zip", "schema_notes": "School Membership long table archive"},
    {"school_year": "2022-2023", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_2223_l_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_2223_l_1a_083023.zip", "schema_notes": "School Staff long table archive"},
    {"school_year": "2022-2023", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_2223_w_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_2223_w_1a_083023.zip", "schema_notes": "School Characteristics archive"},
    {"school_year": "2022-2023", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_2223_l_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_2223_l_1a_083023.zip", "schema_notes": "School Lunch long table archive"},
    {"school_year": "2022-2023", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_2223_w_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_2223_w_1a_083023.zip", "schema_notes": "LEA Directory archive"},
    {"school_year": "2022-2023", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_2223_l_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_2223_l_1a_083023.zip", "schema_notes": "LEA Membership long table archive"},
    {"school_year": "2022-2023", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_2223_l_1a_083023.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_2223_l_1a_083023.zip", "schema_notes": "LEA Staff long table archive"},
    {"school_year": "2022-2023", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_2223.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2223.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2023-2024 (Era 3)
    {"school_year": "2023-2024", "dataset": "CCD School Directory", "release_version": "v.1a", "filename": "ccd_sch_029_2324_w_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_2324_w_1a_073124.zip", "schema_notes": "School Directory archive"},
    {"school_year": "2023-2024", "dataset": "CCD School Membership", "release_version": "v.1a", "filename": "ccd_sch_052_2324_l_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_2324_l_1a_073124.zip", "schema_notes": "School Membership long table archive"},
    {"school_year": "2023-2024", "dataset": "CCD School Staff", "release_version": "v.1a", "filename": "ccd_sch_059_2324_l_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_2324_l_1a_073124.zip", "schema_notes": "School Staff long table archive"},
    {"school_year": "2023-2024", "dataset": "CCD School Characteristics", "release_version": "v.1a", "filename": "ccd_sch_129_2324_w_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_2324_w_1a_073124.zip", "schema_notes": "School Characteristics archive"},
    {"school_year": "2023-2024", "dataset": "CCD School Lunch", "release_version": "v.1a", "filename": "ccd_sch_033_2324_l_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_2324_l_1a_073124.zip", "schema_notes": "School Lunch long table archive"},
    {"school_year": "2023-2024", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_2324_w_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_2324_w_1a_073124.zip", "schema_notes": "LEA Directory archive"},
    {"school_year": "2023-2024", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_2324_l_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_2324_l_1a_073124.zip", "schema_notes": "LEA Membership long table archive"},
    {"school_year": "2023-2024", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_2324_l_1a_073124.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_2324_l_1a_073124.zip", "schema_notes": "LEA Staff long table archive"},
    {"school_year": "2023-2024", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_2324.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2324.zip", "schema_notes": "EDGE Public School Geocodes TXT"},

    # 2024-2025 (Era 4 - Baseline)
    {"school_year": "2024-2025", "dataset": "CCD School Directory", "release_version": "v.2a", "filename": "ccd_sch_029_2425_w_1a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_029_2425_w_1a_073025.zip", "schema_notes": "Baseline School Directory CSV"},
    {"school_year": "2024-2025", "dataset": "CCD School Membership", "release_version": "v.2a", "filename": "ccd_sch_052_2425_l_1a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_052_2425_l_1a_073025.zip", "schema_notes": "Baseline School Membership long table CSV"},
    {"school_year": "2024-2025", "dataset": "CCD School Staff", "release_version": "v.2a", "filename": "ccd_sch_059_2425_l_1a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_059_2425_l_1a_073025.zip", "schema_notes": "Baseline School Staff long table CSV with TEACHERS"},
    {"school_year": "2024-2025", "dataset": "CCD School Characteristics", "release_version": "v.2a", "filename": "ccd_sch_129_2425_w_1a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_129_2425_w_1a_073025.zip", "schema_notes": "Baseline School Characteristics CSV"},
    {"school_year": "2024-2025", "dataset": "CCD School Lunch", "release_version": "v.2a", "filename": "ccd_sch_033_2425_l_2a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_sch_033_2425_l_2a_073025.zip", "schema_notes": "Baseline School Lunch long table CSV"},
    {"school_year": "2024-2025", "dataset": "CCD LEA Directory", "release_version": "v.1a", "filename": "ccd_lea_029_2425_w_1a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_029_2425_w_1a_073025.zip", "schema_notes": "Baseline LEA Directory CSV"},
    {"school_year": "2024-2025", "dataset": "CCD LEA Membership", "release_version": "v.1a", "filename": "ccd_lea_052_2425_l_1a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_052_2425_l_1a_073025.zip", "schema_notes": "Baseline LEA Membership long table CSV"},
    {"school_year": "2024-2025", "dataset": "CCD LEA Staff", "release_version": "v.1a", "filename": "ccd_lea_059_2425_l_1a_073025.zip", "source_url": "https://nces.ed.gov/ccd/data/zip/ccd_lea_059_2425_l_1a_073025.zip", "schema_notes": "Baseline LEA Staff long table CSV"},
    {"school_year": "2024-2025", "dataset": "NCES EDGE Public School Geocodes", "release_version": "Final", "filename": "EDGE_GEOCODE_PUBLICSCH_2425.zip", "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2425.zip", "schema_notes": "Baseline EDGE Public School Geocodes TXT"},
]

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            sha.update(chunk)
    return sha.hexdigest()

def get_target_path(entry):
    sy = entry["school_year"]
    fn = entry["filename"]
    if sy == "2024-2025":
        # 2024-2025 baseline files sit directly in data/raw/nces/
        return RAW_NCES_DIR / fn
    else:
        folder_sy = sy.replace("-", "_")
        return RAW_NCES_DIR / folder_sy / fn

def download_file(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    tmp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")
    
    sha = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=30) as resp, open(tmp_path, "wb") as out:
        while chunk := resp.read(1024 * 1024):
            sha.update(chunk)
            out.write(chunk)
            
    tmp_path.replace(dest_path)
    return sha.hexdigest()

def update_source_matrix():
    rows = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    for item in CATALOG:
        p = get_target_path(item)
        status = "Available" if p.exists() else "Pending"
        sha = compute_sha256(p) if p.exists() else ""
        size_str = f"{p.stat().st_size:,} bytes" if p.exists() else ""
        
        rows.append({
            "school_year": item["school_year"],
            "dataset": item["dataset"],
            "release_version": item["release_version"],
            "filename": item["filename"],
            "source_url": item["source_url"],
            "download_date": today if p.exists() else "",
            "sha256": sha,
            "schema_notes": item["schema_notes"],
            "availability_status": status
        })
        
    df_mat = pd.DataFrame(rows)
    df_mat.to_csv(MATRIX_CSV, index=False)
    print(f"Updated {MATRIX_CSV} ({len(df_mat)} entries)")
    return df_mat

def main():
    parser = argparse.ArgumentParser(description="Download NCES CCD/EDGE historical archives.")
    parser.add_argument("--pilot", action="store_true", help="Download only representative pilot years (2014-15, 2016-17, 2018-19, 2024-25)")
    parser.add_argument("--year", type=str, help="Download a specific school year, e.g. 2014-2015")
    parser.add_argument("--all", action="store_true", help="Download all 11 years")
    args = parser.parse_args()

    pilot_years = ["2014-2015", "2016-2017", "2018-2019", "2024-2025"]
    
    targets = CATALOG
    if args.pilot:
        targets = [c for c in CATALOG if c["school_year"] in pilot_years]
    elif args.year:
        targets = [c for c in CATALOG if c["school_year"] == args.year]
    elif not args.all:
        print("Please specify --pilot, --year YYYY-YYYY, or --all.")
        update_source_matrix()
        return

    print(f"Targeting {len(targets)} archives for download...")
    for idx, item in enumerate(targets, 1):
        p = get_target_path(item)
        if p.exists() and p.stat().st_size > 0:
            print(f"[{idx}/{len(targets)}] Already exists: {item['school_year']} / {p.name} ({p.stat().st_size:,} bytes)")
            continue
            
        print(f"[{idx}/{len(targets)}] Downloading {item['school_year']} / {item['filename']} from {item['source_url']}...")
        sha = download_file(item["source_url"], p)
        print(f"   Done -> {p.stat().st_size:,} bytes | SHA256: {sha[:16]}...")
        
    update_source_matrix()

if __name__ == "__main__":
    main()
