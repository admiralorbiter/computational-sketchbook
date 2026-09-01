"""Geography normalization and standardization."""

import logging
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

logger = logging.getLogger(__name__)


def normalize_geography(data, target_geoid_vintage: int = 2020):
    """Normalize geography to consistent GEOID vintage.
    
    Args:
        data: GeoDataFrame or DataFrame with geography columns
        target_geoid_vintage: Target GEOID vintage year
    
    Returns:
        Normalized DataFrame with consistent GEOIDs
    """
    logger.info(f"Normalizing geography to vintage {target_geoid_vintage}")
    # TODO: Implement geography normalization logic
    pass


def assign_tract_to_district(tracts_gdf, districts_gdf):
    """Assign census tracts to school districts using spatial overlay.
    
    Args:
        tracts_gdf: GeoDataFrame of census tracts (from TIGER)
        districts_gdf: GeoDataFrame of school district boundaries (from NCES)
    
    Returns:
        DataFrame with tract-to-district assignments with columns:
        - GEOID: Census tract identifier
        - district_geoid: District GEOID (index from districts_gdf)
        - ncesid: District NCES ID (if available)
        - district_name: District name
        - assignment_method: How assignment was made ("centroid", "largest_overlap", "multiple")
        - overlap_percentage: Percentage of tract area in district (if calculated)
        - is_multiple_districts: Boolean flag if tract spans multiple districts
    """
    logger.info("Assigning tracts to school districts using spatial overlay")
    
    # Validate inputs
    if tracts_gdf is None or len(tracts_gdf) == 0:
        raise ValueError("tracts_gdf is empty or None")
    if districts_gdf is None or len(districts_gdf) == 0:
        raise ValueError("districts_gdf is empty or None")
    
    logger.info(f"Processing {len(tracts_gdf)} tracts against {len(districts_gdf)} districts")
    
    # Make copies to avoid modifying input
    tracts = tracts_gdf.copy()
    districts = districts_gdf.copy()
    
    # CRS validation and normalization
    # Both should be EPSG:4269 (NAD83) based on ingestion functions
    target_crs = "EPSG:4269"
    
    if tracts.crs is None:
        logger.warning("Tracts GeoDataFrame has no CRS, assuming EPSG:4269")
        tracts.set_crs(target_crs, inplace=True)
    elif tracts.crs.to_string() != target_crs:
        logger.info(f"Reprojecting tracts from {tracts.crs} to {target_crs}")
        tracts = tracts.to_crs(target_crs)
    
    if districts.crs is None:
        logger.warning("Districts GeoDataFrame has no CRS, assuming EPSG:4269")
        districts.set_crs(target_crs, inplace=True)
    elif districts.crs.to_string() != target_crs:
        logger.info(f"Reprojecting districts from {districts.crs} to {target_crs}")
        districts = districts.to_crs(target_crs)
    
    logger.info(f"Both GeoDataFrames using CRS: {target_crs}")
    
    # Validate GEOID column in tracts
    if "GEOID" not in tracts.columns and tracts.index.name != "GEOID":
        # Try to construct GEOID from component parts
        if all(col in tracts.columns for col in ["STATEFP", "COUNTYFP", "TRACTCE"]):
            tracts["GEOID"] = (
                tracts["STATEFP"].astype(str).str.zfill(2) +
                tracts["COUNTYFP"].astype(str).str.zfill(3) +
                tracts["TRACTCE"].astype(str).str.zfill(6)
            )
            logger.info("Constructed GEOID from STATEFP + COUNTYFP + TRACTCE")
        else:
            raise ValueError("GEOID column not found in tracts and cannot be constructed")
    
    # Get GEOID as a column (not index)
    if tracts.index.name == "GEOID":
        tracts = tracts.reset_index()
    tract_geoids = tracts["GEOID"].copy()
    
    # Get district identifier (GEOID from index or NCESID)
    if districts.index.name in ["GEOID", "NCESID"]:
        district_id_col = districts.index.name
        districts = districts.reset_index()
    elif "NCESID" in districts.columns:
        district_id_col = "NCESID"
    elif "GEOID" in districts.columns:
        district_id_col = "GEOID"
    else:
        # Use index as fallback
        district_id_col = "district_id"
        districts[district_id_col] = districts.index.astype(str)
        logger.warning("No NCESID or GEOID found in districts, using index as identifier")
    
    # Get district name column
    district_name_col = None
    for col in ["NAME", "district_name", "DISTRICT_NAME"]:
        if col in districts.columns:
            district_name_col = col
            break
    
    if district_name_col is None:
        logger.warning("District name column not found, will use identifier as name")
        district_name_col = district_id_col
    
    # Calculate tract centroids for spatial join
    # Project to a projected CRS for accurate centroid calculation
    logger.info("Calculating tract centroids for spatial join")
    # Use UTM Zone 15N (EPSG:26915) for KC metro area for accurate distance/area calculations
    projected_crs = "EPSG:26915"  # UTM Zone 15N
    tracts_projected = tracts.to_crs(projected_crs)
    districts_projected = districts.to_crs(projected_crs)
    
    tract_centroids = tracts_projected.copy()
    tract_centroids["geometry"] = tract_centroids.geometry.centroid
    # Convert back to geographic CRS for join (districts are already projected)
    tract_centroids = tract_centroids.to_crs(target_crs)
    districts_for_join = districts_projected.to_crs(target_crs)
    
    # Primary spatial join using centroids
    logger.info("Performing spatial join (centroids within districts)")
    # Ensure we have the columns we need
    tract_cols = ["GEOID", "geometry"]
    if "GEOID" not in tract_centroids.columns:
        # If GEOID is the index, reset it
        if tract_centroids.index.name == "GEOID":
            tract_centroids = tract_centroids.reset_index()
        else:
            raise ValueError("GEOID column not found in tracts")
    
    district_cols = [district_id_col, district_name_col, "geometry"]
    # Make sure all district columns exist
    district_cols = [col for col in district_cols if col in districts_for_join.columns]
    
    # Ensure both are in the same CRS for the join
    if tract_centroids.crs != districts_for_join.crs:
        logger.warning(f"CRS mismatch: tracts={tract_centroids.crs}, districts={districts_for_join.crs}")
        districts_for_join = districts_for_join.to_crs(tract_centroids.crs)
    
    joined = gpd.sjoin(
        tract_centroids[tract_cols],
        districts_for_join[district_cols],
        how="left",
        predicate="within"
    )
    
    # Debug: log what columns we got
    logger.debug(f"Join result columns: {list(joined.columns)}")
    logger.debug(f"Join result shape: {joined.shape}")
    
    # Handle tracts with no district assignment
    # The spatial join adds a suffix to right dataframe columns, check for that
    right_district_col = f"{district_id_col}_right" if f"{district_id_col}_right" in joined.columns else district_id_col
    if right_district_col not in joined.columns and district_id_col not in joined.columns:
        logger.warning(f"District ID column not found. Available columns: {list(joined.columns)}")
        unmapped_count = len(joined)
    else:
        # Use whichever column exists
        actual_district_col = right_district_col if right_district_col in joined.columns else district_id_col
        unmapped_count = joined[actual_district_col].isna().sum() if actual_district_col in joined.columns else len(joined)
    
    if unmapped_count > 0:
        logger.warning(f"Found {unmapped_count} tracts with no district assignment")
        # For unmapped tracts, we'll handle them in the result building phase
    
    # Detect tracts that span multiple districts (duplicate GEOIDs in joined result)
    logger.info("Detecting tracts that span multiple districts")
    # Check for GEOID column (might be index or column)
    geoid_col = "GEOID" if "GEOID" in joined.columns else (joined.index.name if joined.index.name == "GEOID" else None)
    multi_district_geoids = []
    duplicate_tracts = pd.DataFrame()
    overlap_results = []  # Initialize early
    
    if geoid_col is None:
        logger.warning("GEOID not found in joined result, cannot detect multiple districts")
        logger.debug(f"Available columns: {list(joined.columns)}, index: {joined.index.name}")
    else:
        if geoid_col == "GEOID":
            duplicate_tracts = joined[joined["GEOID"].duplicated(keep=False)]
        else:
            # GEOID is the index
            duplicate_tracts = joined[joined.index.duplicated(keep=False)]
        
        if len(duplicate_tracts) > 0:
            multi_district_geoids = duplicate_tracts["GEOID"].unique() if geoid_col == "GEOID" else duplicate_tracts.index.unique()
            logger.info(f"Found {len(multi_district_geoids)} tracts spanning multiple districts")
            
            # For tracts spanning multiple districts, calculate area overlap
            logger.info("Calculating area overlap for tracts spanning multiple districts")
            
            # Process each multi-district tract
            # Use projected geometries for accurate area calculations
            # Convert to list if it's a numpy array
            geoid_list = list(multi_district_geoids) if hasattr(multi_district_geoids, '__iter__') and not isinstance(multi_district_geoids, str) else [multi_district_geoids]
            for geoid in geoid_list:
                tract_geom = tracts_projected[tracts_projected["GEOID"] == geoid].geometry.iloc[0]
                overlapping_districts = duplicate_tracts[duplicate_tracts["GEOID"] == geoid] if geoid_col == "GEOID" else duplicate_tracts[duplicate_tracts.index == geoid]
                
                # Calculate overlap percentage for each district
                overlaps = []
                for idx, row in overlapping_districts.iterrows():
                    district_geom = districts_projected[districts_projected[district_id_col] == row[district_id_col]].geometry.iloc[0]
                    try:
                        intersection = tract_geom.intersection(district_geom)
                        if intersection.is_empty:
                            overlap_pct = 0.0
                        else:
                            overlap_pct = (intersection.area / tract_geom.area) * 100
                        overlaps.append({
                            "GEOID": geoid,
                            district_id_col: row[district_id_col],
                            "district_name": row[district_name_col],
                            "overlap_percentage": overlap_pct
                        })
                    except Exception as e:
                        logger.warning(f"Error calculating overlap for tract {geoid}: {e}")
                        overlaps.append({
                            "GEOID": geoid,
                            district_id_col: row[district_id_col],
                            "district_name": row[district_name_col],
                            "overlap_percentage": 0.0
                        })
                
                # Assign to district with largest overlap
                if overlaps:
                    best_overlap = max(overlaps, key=lambda x: x["overlap_percentage"])
                    overlap_results.append({
                        "GEOID": geoid,
                        district_id_col: best_overlap[district_id_col],
                        "district_name": best_overlap["district_name"],
                        "assignment_method": "largest_overlap",
                        "overlap_percentage": best_overlap["overlap_percentage"],
                        "is_multiple_districts": True
                    })
        
    # Remove duplicates from joined and add overlap results
    geoid_col_for_filter = "GEOID" if "GEOID" in joined.columns else None
    if geoid_col_for_filter and len(multi_district_geoids) > 0:
        joined_single = joined[~joined[geoid_col_for_filter].isin(multi_district_geoids)].copy()
    else:
        joined_single = joined.copy()
        if len(multi_district_geoids) > 0:
            logger.warning("Cannot filter multi-district tracts, using all joined results")
    overlap_df = pd.DataFrame(overlap_results) if len(overlap_results) > 0 else pd.DataFrame()
    
    # Build final output DataFrame
    logger.info("Building final assignment DataFrame")
    
    # Start with single-district assignments
    result_data = []
    
    # Determine which columns to use (spatial join may add suffixes)
    geoid_col = "GEOID" if "GEOID" in joined_single.columns else None
    right_district_col = f"{district_id_col}_right" if f"{district_id_col}_right" in joined_single.columns else district_id_col
    right_name_col = f"{district_name_col}_right" if f"{district_name_col}_right" in joined_single.columns else district_name_col
    
    for idx, row in joined_single.iterrows():
        # Get GEOID from column or index
        if geoid_col and geoid_col in row:
            geoid = row[geoid_col]
        elif joined_single.index.name == "GEOID":
            geoid = idx
        else:
            logger.warning(f"Row {idx} missing GEOID, skipping")
            continue
        
        result_data.append({
            "GEOID": geoid,
            "district_geoid": row.get(right_district_col, None) if right_district_col in row else None,
            "ncesid": row.get("NCESID", None) if "NCESID" in row else (row.get(right_district_col, None) if right_district_col in row else None),
            "district_name": row.get(right_name_col, "Unknown") if right_name_col in row else "Unknown",
            "assignment_method": "centroid",
            "overlap_percentage": None,
            "is_multiple_districts": False
        })
    
    # Add multi-district assignments
    if len(overlap_df) > 0:
        for idx, row in overlap_df.iterrows():
            result_data.append({
                "GEOID": row["GEOID"],
                "district_geoid": row.get(district_id_col, None),
                "ncesid": row.get("NCESID", None) if "NCESID" in row else row.get(district_id_col, None),
                "district_name": row.get("district_name", "Unknown"),
                "assignment_method": row.get("assignment_method", "largest_overlap"),
                "overlap_percentage": row.get("overlap_percentage", None),
                "is_multiple_districts": row.get("is_multiple_districts", True)
            })
    
    result_df = pd.DataFrame(result_data)
    
    # Ensure we have all tracts (fill in any missing)
    all_geoids = set(tract_geoids.unique())
    if len(result_df) > 0 and "GEOID" in result_df.columns:
        result_geoids = set(result_df["GEOID"].unique())
    else:
        result_geoids = set()
        logger.warning("Result DataFrame is empty or missing GEOID column")
    missing_geoids = all_geoids - result_geoids
    
    if missing_geoids:
        logger.warning(f"Adding {len(missing_geoids)} tracts with no assignment")
        for geoid in missing_geoids:
            result_df = pd.concat([
                result_df,
                pd.DataFrame([{
                    "GEOID": geoid,
                    "district_geoid": None,
                    "ncesid": None,
                    "district_name": "Unmapped",
                    "assignment_method": "none",
                    "overlap_percentage": None,
                    "is_multiple_districts": False
                }])
            ], ignore_index=True)
    
    # Sort by GEOID for consistency
    result_df = result_df.sort_values("GEOID").reset_index(drop=True)
    
    # Log statistics
    logger.info("Assignment statistics:")
    logger.info(f"  Total tracts: {len(result_df)}")
    logger.info(f"  Assigned via centroid: {(result_df['assignment_method'] == 'centroid').sum()}")
    logger.info(f"  Assigned via overlap: {(result_df['assignment_method'] == 'largest_overlap').sum()}")
    logger.info(f"  Unmapped tracts: {(result_df['assignment_method'] == 'none').sum()}")
    logger.info(f"  Tracts spanning multiple districts: {result_df['is_multiple_districts'].sum()}")
    
    # District coverage
    assigned_districts = result_df[result_df["district_geoid"].notna()]["district_geoid"].nunique()
    logger.info(f"  Districts with assigned tracts: {assigned_districts} / {len(districts)}")
    
    logger.info("Tract-to-district assignment complete")
    
    return result_df
