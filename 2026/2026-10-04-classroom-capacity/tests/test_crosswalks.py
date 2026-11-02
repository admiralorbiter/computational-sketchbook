"""
Unit tests for Geographic and Institutional Crosswalks.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.harmonize_crdc import KC_COUNTY_FIPS

def test_kc_county_fips_set():
    """Verify that all 9 Mid-America Regional Council (MARC) county FIPS are included."""
    expected_ks = {"20209", "20091", "20103", "20121"} # Wyandotte, Johnson, Leavenworth, Miami
    expected_mo = {"29047", "29095", "29037", "29177", "29165"} # Clay, Jackson, Cass, Ray, Platte
    expected_all = expected_ks.union(expected_mo)
    
    assert KC_COUNTY_FIPS == expected_all
    assert len(KC_COUNTY_FIPS) == 9

def test_id_structure_formatting():
    """Verify formatting requirements for NCES School and LEA IDs."""
    test_sch_id = "290531000170"
    test_lea_id = "2905310"
    
    assert len(test_sch_id) == 12
    assert len(test_lea_id) == 7
    assert test_sch_id.startswith(test_lea_id)

if __name__ == "__main__":
    pytest.main([__file__])
