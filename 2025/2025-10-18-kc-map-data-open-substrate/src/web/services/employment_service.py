# Employment Data Service

import os
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, box
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class EmploymentService:
    """Service for querying LODES employment data"""
    
    def __init__(self, lodes_db_path=None):
        if lodes_db_path is None:
            project_root = Path(__file__).parent.parent.parent
            lodes_db_path = project_root / "data" / "processed" / "lodes_data.gpkg"
        
        self.lodes_db_path = Path(lodes_db_path)
        
        if not self.lodes_db_path.exists():
            raise FileNotFoundError(f"LODES database not found: {lodes_db_path}")
        
        # Connection for spatial queries
        self.gdf_wac = None
        self.gdf_rac = None
        self.gdf_od = None
        self.gdf_blocks = None
    
    def _load_data(self):
        """Lazy load of LODES and census block data"""
        if self.gdf_wac is None:
            if self.lodes_db_path.exists():
                try:
                    # Load from SQLite database
                    import sqlite3
                    conn = sqlite3.connect(self.lodes_db_path)
                    self.gdf_wac = pd.read_sql('SELECT * FROM lodes_wac', conn)
                    self.gdf_rac = pd.read_sql('SELECT * FROM lodes_rac', conn)
                    try:
                        self.gdf_od = pd.read_sql('SELECT * FROM lodes_od', conn)
                    except:
                        self.gdf_od = None
                    conn.close()
                except Exception as e:
                    print(f"Error loading LODES data: {e}")
                    self.gdf_wac = None
                    self.gdf_rac = None
                    self.gdf_od = None
        
        if self.gdf_blocks is None:
            # Load census block groups for geometry
            project_root = Path(__file__).parent.parent.parent
            tiger_path = project_root / "data" / "processed" / "tiger_boundaries.gpkg"
            try:
                self.gdf_blocks = gpd.read_file(tiger_path, layer='bg')
            except:
                print("Census block groups not available")
    
    def get_workplace_jobs(self, bbox=None, industry_sector=None, earnings_range=None, limit=10000):
        """Get jobs by workplace location (WAC)
        
        Args:
            bbox: [min_x, min_y, max_x, max_y] for spatial filtering
            industry_sector: NAICS sector code (CNS01-CNS20) or None
            earnings_range: 'low' (<$1250), 'mid' ($1251-3333), 'high' (>$3333)
            limit: Maximum number of records to return
        
        Returns:
            GeoDataFrame with workplace job counts by block
        """
        self._load_data()
        
        if self.gdf_wac is None or self.gdf_blocks is None:
            return gpd.GeoDataFrame()
        
        # Start with WAC data
        result = self.gdf_wac.copy()
        
        # Filter by industry sector
        if industry_sector is not None:
            sector_col = f'CNS{industry_sector:02d}'
            if sector_col in result.columns:
                result = result[result[sector_col].notna() & (result[sector_col] > 0)]
        
        # Filter by earnings
        if earnings_range == 'low':
            result = result[result['CE01'].notna() & (result['CE01'] > 0)]
        elif earnings_range == 'mid':
            result = result[result['CE02'].notna() & (result['CE02'] > 0)]
        elif earnings_range == 'high':
            result = result[result['CE03'].notna() & (result['CE03'] > 0)]
        
        # Always join with blocks for geometry
        # LODES uses 15-digit GEOID, TIGER uses 12-digit for block groups
        # Extract first 12 digits for join
        result['w_geocode_12'] = result['w_geocode'].astype(str).str[:12]
        self.gdf_blocks['geoid'] = self.gdf_blocks['GEOID'].astype(str)
        
        merged = result.merge(
            self.gdf_blocks[['geoid', 'geometry']],
            left_on='w_geocode_12',
            right_on='geoid',
            how='inner'
        )
        
        # Convert to GeoDataFrame
        if 'geometry' in merged.columns:
            merged = gpd.GeoDataFrame(merged, geometry='geometry', crs='EPSG:4326')
        
        # Spatial filter if bbox provided
        if bbox:
            min_x, min_y, max_x, max_y = bbox
            # Get centroids for point-in-box test
            centroids = merged.geometry.centroid
            mask = (
                (centroids.x >= min_x) &
                (centroids.x <= max_x) &
                (centroids.y >= min_y) &
                (centroids.y <= max_y)
            )
            result = merged[mask]
        else:
            result = merged
        
        # Limit results
        if len(result) > limit:
            result = result.head(limit)
        
        return result
    
    def get_residence_jobs(self, bbox=None, age_group=None, limit=10000):
        """Get jobs by residence location (RAC)
        
        Args:
            bbox: [min_x, min_y, max_x, max_y] for spatial filtering
            age_group: 'young' (29 or less), 'middle' (30-54), 'senior' (55+)
            limit: Maximum number of records to return
        
        Returns:
            GeoDataFrame with residence job counts by block
        """
        self._load_data()
        
        if self.gdf_rac is None or self.gdf_blocks is None:
            return gpd.GeoDataFrame()
        
        result = self.gdf_rac.copy()
        
        # Filter by age group
        if age_group == 'young':
            result = result[result['CA01'] > 0]
        elif age_group == 'middle':
            result = result[result['CA02'] > 0]
        elif age_group == 'senior':
            result = result[result['CA03'] > 0]
        
        # Always join with blocks for geometry
        # LODES uses 15-digit GEOID, TIGER uses 12-digit for block groups
        # Extract first 12 digits for join
        result['h_geocode_12'] = result['h_geocode'].astype(str).str[:12]
        self.gdf_blocks['geoid'] = self.gdf_blocks['GEOID'].astype(str)
        merged = result.merge(
            self.gdf_blocks[['geoid', 'geometry']],
            left_on='h_geocode_12',
            right_on='geoid',
            how='inner'
        )
        
        # Convert to GeoDataFrame
        if 'geometry' in merged.columns:
            merged = gpd.GeoDataFrame(merged, geometry='geometry', crs='EPSG:4326')
        
        # Spatial filter if bbox provided
        if bbox:
            min_x, min_y, max_x, max_y = bbox
            centroids = merged.geometry.centroid
            mask = (
                (centroids.x >= min_x) &
                (centroids.x <= max_x) &
                (centroids.y >= min_y) &
                (centroids.y <= max_y)
            )
            result = merged[mask]
        else:
            result = merged
        
        if len(result) > limit:
            result = result.head(limit)
        
        return result
    
    def get_commute_flows(self, bbox=None, min_jobs=1, limit=5000):
        """Get origin-destination commute flows
        
        Args:
            bbox: [min_x, min_y, max_x, max_y] for workplace or home location
            min_jobs: Minimum number of jobs in a flow to include
            limit: Maximum number of flows to return
        
        Returns:
            GeoDataFrame with LineStrings representing commute flows
        """
        self._load_data()
        
        if self.gdf_od is None or self.gdf_blocks is None:
            return gpd.GeoDataFrame()
        
        result = self.gdf_od.copy()
        
        # Filter by minimum jobs
        result = result[result['S000'] >= min_jobs]
        
        # Get unique blocks involved in flows
        self.gdf_blocks['geoid'] = self.gdf_blocks['GEOID20'].astype(str)
        blocks_dict = dict(zip(self.gdf_blocks['geoid'], self.gdf_blocks['geometry'].centroid))
        
        # Create lines from OD pairs
        lines = []
        for idx, row in result.iterrows():
            w_geocode = str(row['w_geocode'])
            h_geocode = str(row['h_geocode'])
            
            if w_geocode in blocks_dict and h_geocode in blocks_dict:
                # Create line from home to work
                line = LineString([
                    (blocks_dict[h_geocode].x, blocks_dict[h_geocode].y),
                    (blocks_dict[w_geocode].x, blocks_dict[w_geocode].y)
                ])
                lines.append(line)
        
        if not lines:
            return gpd.GeoDataFrame()
        
        # Create GeoDataFrame with flows
        gdf_flows = gpd.GeoDataFrame(result.reset_index(drop=True), geometry=lines)
        
        # Spatial filter if provided
        if bbox:
            min_x, min_y, max_x, max_y = bbox
            bounding_box = box(min_x, min_y, max_x, max_y)
            mask = gdf_flows.geometry.intersects(bounding_box)
            result = gdf_flows[mask]
        else:
            result = gdf_flows
        
        if len(result) > limit:
            result = result.head(limit)
        
        return result
    
    def aggregate_to_block_groups(self, level='block_group'):
        """Aggregate block-level LODES data to block groups
        
        Args:
            level: 'block_group' or 'tract'
        
        Returns:
            Aggregated statistics by block group or tract
        """
        self._load_data()
        
        if self.gdf_wac is None:
            return pd.DataFrame()
        
        # Extract state, county, tract, block group from GEOID
        self.gdf_wac['state_fips'] = self.gdf_wac['w_geocode'].str[:2]
        self.gdf_wac['county_fips'] = self.gdf_wac['w_geocode'].str[2:5]
        self.gdf_wac['tract_fips'] = self.gdf_wac['w_geocode'].str[5:11]
        self.gdf_wac['bg_fips'] = self.gdf_wac['w_geocode'].str[11:]
        
        if level == 'block_group':
            group_cols = ['state_fips', 'county_fips', 'tract_fips', 'bg_fips']
            group_cols.append('C000')
            aggregated = self.gdf_wac.groupby(group_cols[:-1])[group_cols[-1]].sum().reset_index()
        else:  # tract
            group_cols = ['state_fips', 'county_fips', 'tract_fips']
            group_cols.append('C000')
            aggregated = self.gdf_wac.groupby(group_cols[:-1])[group_cols[-1]].sum().reset_index()
        
        return aggregated
    
    def get_top_industries(self, bbox=None, limit=10):
        """Get top industries by job count in a given area
        
        Args:
            bbox: Spatial filter
            limit: Number of top industries to return
        
        Returns:
            DataFrame with industry codes and job counts
        """
        wac = self.get_workplace_jobs(bbox=bbox)
        
        if wac.empty:
            return pd.DataFrame()
        
        # Sum by industry
        cns_cols = [f'CNS{i:02d}' for i in range(1, 21)]
        industry_totals = []
        
        for i, col in enumerate(cns_cols, 1):
            if col in wac.columns:
                total = wac[col].sum()
                if total > 0:
                    industry_totals.append({'industry_code': i, 'job_count': total})
        
        df = pd.DataFrame(industry_totals)
        df = df.sort_values('job_count', ascending=False).head(limit)
        
        return df
    
    def calculate_jobs_housing_balance(self, bbox=None):
        """Calculate jobs-to-workers ratio by block
        
        Args:
            bbox: Spatial filter
        
        Returns:
            DataFrame with jobs (WAC), workers (RAC), and ratio
        """
        wac = self.get_workplace_jobs(bbox=bbox)
        rac = self.get_residence_jobs(bbox=bbox)
        
        if wac.empty or rac.empty:
            return pd.DataFrame()
        
        # Aggregate to block level
        jobs = wac.groupby('w_geocode')['C000'].sum()
        workers = rac.groupby('h_geocode')['C000'].sum()
        
        # Merge
        result = pd.DataFrame({
            'geocode': jobs.index,
            'jobs': jobs.values,
            'workers': workers.values
        })
        result['balance_ratio'] = result['jobs'] / result['workers'].replace(0, 1)
        
        return result
    
    def get_block_group_employment(self, geoid):
        """Get employment data for a specific block group
        
        Args:
            geoid: 12-digit block group GEOID
        
        Returns:
            Dict with employment statistics for the block group
        """
        self._load_data()
        
        if self.gdf_wac is None or self.gdf_rac is None:
            return None
        
        try:
            # Filter WAC (jobs at workplace) for this block group
            # LODES uses 15-digit block GEOID, extract first 12 for block group
            wac_bg = self.gdf_wac[self.gdf_wac['w_geocode'].astype(str).str[:12] == geoid]
            rac_bg = self.gdf_rac[self.gdf_rac['h_geocode'].astype(str).str[:12] == geoid]
            
            # Calculate total jobs at workplace
            jobs_at_workplace = int(wac_bg['C000'].sum()) if len(wac_bg) > 0 else 0
            
            # Calculate total workers living here
            workers_living_here = int(rac_bg['C000'].sum()) if len(rac_bg) > 0 else 0
            
            # Calculate jobs-housing ratio
            jobs_housing_ratio = jobs_at_workplace / workers_living_here if workers_living_here > 0 else 0
            
            # Get top industries (CNS01-CNS20)
            top_industries = []
            industry_totals = {}
            
            for i in range(1, 21):
                col_wac = f'CNS{i:02d}'
                col_rac = f'CNS{i:02d}'
                
                # Sum from WAC data
                wac_sum = wac_bg[col_wac].sum() if col_wac in wac_bg.columns else 0
                
                # Convert to int, handling NaN
                try:
                    industry_total = int(wac_sum) if pd.notna(wac_sum) else 0
                    if industry_total > 0:
                        industry_totals[i] = industry_total
                except (ValueError, TypeError):
                    industry_total = 0
            
            # Sort by total jobs and take top 5
            top_5 = sorted(industry_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for code, jobs in top_5:
                industry_name = self._get_industry_name(code)
                top_industries.append({'code': code, 'name': industry_name, 'jobs': int(jobs)})
            
            # Worker age groups (from RAC data)
            age_29_under = int(rac_bg['CA01'].sum()) if 'CA01' in rac_bg.columns else 0
            age_30_54 = int(rac_bg['CA02'].sum()) if 'CA02' in rac_bg.columns else 0
            age_55_plus = int(rac_bg['CA03'].sum()) if 'CA03' in rac_bg.columns else 0
            
            # Earnings distribution (from RAC data)
            earnings_low = int(rac_bg['CE01'].sum()) if 'CE01' in rac_bg.columns else 0
            earnings_mid = int(rac_bg['CE02'].sum()) if 'CE02' in rac_bg.columns else 0
            earnings_high = int(rac_bg['CE03'].sum()) if 'CE03' in rac_bg.columns else 0
            
            # Worker demographics (from RAC data)
            worker_race = {}
            if 'CR01' in rac_bg.columns: worker_race['white'] = int(rac_bg['CR01'].sum())
            if 'CR02' in rac_bg.columns: worker_race['black'] = int(rac_bg['CR02'].sum())
            if 'CR03' in rac_bg.columns: worker_race['american_indian'] = int(rac_bg['CR03'].sum())
            if 'CR04' in rac_bg.columns: worker_race['asian'] = int(rac_bg['CR04'].sum())
            if 'CR05' in rac_bg.columns: worker_race['native_hawaiian'] = int(rac_bg['CR05'].sum())
            if 'CR07' in rac_bg.columns: worker_race['two_or_more_races'] = int(rac_bg['CR07'].sum())
            
            worker_ethnicity = {}
            if 'CT01' in rac_bg.columns: worker_ethnicity['not_hispanic'] = int(rac_bg['CT01'].sum())
            if 'CT02' in rac_bg.columns: worker_ethnicity['hispanic'] = int(rac_bg['CT02'].sum())
            
            # Education (from RAC data)
            worker_education = {}
            if 'CD01' in rac_bg.columns: worker_education['less_than_hs'] = int(rac_bg['CD01'].sum())
            if 'CD02' in rac_bg.columns: worker_education['high_school'] = int(rac_bg['CD02'].sum())
            if 'CD03' in rac_bg.columns: worker_education['some_college'] = int(rac_bg['CD03'].sum())
            if 'CD04' in rac_bg.columns: worker_education['bachelors_plus'] = int(rac_bg['CD04'].sum())
            
            # Sex (from RAC data)
            worker_sex = {}
            if 'CS01' in rac_bg.columns: worker_sex['male'] = int(rac_bg['CS01'].sum())
            if 'CS02' in rac_bg.columns: worker_sex['female'] = int(rac_bg['CS02'].sum())
            
            # Firm characteristics (from WAC data)
            firm_age = {}
            if 'CFA01' in wac_bg.columns: firm_age['age_0_2'] = int(wac_bg['CFA01'].sum())
            if 'CFA02' in wac_bg.columns: firm_age['age_3_5'] = int(wac_bg['CFA02'].sum())
            if 'CFA03' in wac_bg.columns: firm_age['age_6_10'] = int(wac_bg['CFA03'].sum())
            if 'CFA04' in wac_bg.columns: firm_age['age_11_plus'] = int(wac_bg['CFA04'].sum())
            
            firm_size = {}
            if 'CFS01' in wac_bg.columns: firm_size['size_0_19'] = int(wac_bg['CFS01'].sum())
            if 'CFS02' in wac_bg.columns: firm_size['size_20_49'] = int(wac_bg['CFS02'].sum())
            if 'CFS03' in wac_bg.columns: firm_size['size_50_249'] = int(wac_bg['CFS03'].sum())
            if 'CFS04' in wac_bg.columns: firm_size['size_250_499'] = int(wac_bg['CFS04'].sum())
            if 'CFS05' in wac_bg.columns: firm_size['size_500_plus'] = int(wac_bg['CFS05'].sum())
            
            return {
                'jobs_at_workplace': jobs_at_workplace,
                'workers_living_here': workers_living_here,
                'jobs_housing_ratio': round(jobs_housing_ratio, 2),
                'top_industries': top_industries,
                'worker_age_groups': {
                    'age_29_under': age_29_under,
                    'age_30_54': age_30_54,
                    'age_55_plus': age_55_plus
                },
                'earnings_distribution': {
                    'low': earnings_low,
                    'mid': earnings_mid,
                    'high': earnings_high
                },
                'worker_race': worker_race,
                'worker_ethnicity': worker_ethnicity,
                'worker_education': worker_education,
                'worker_sex': worker_sex,
                'firm_age': firm_age,
                'firm_size': firm_size
            }
        except Exception as e:
            print(f"Error getting block group employment: {e}")
            return None
    
    def _get_industry_name(self, code):
        """Get human-readable NAICS industry name"""
        naics_names = {
            1: "Agriculture/Mining",
            2: "Utilities",
            3: "Construction",
            4: "Manufacturing",
            5: "Wholesale Trade",
            6: "Retail Trade",
            7: "Transportation/Warehousing",
            8: "Information",
            9: "Finance/Insurance",
            10: "Real Estate",
            11: "Professional/Scientific Services",
            12: "Management",
            13: "Administrative Services",
            14: "Educational Services",
            15: "Health Care/Social Assistance",
            16: "Arts/Entertainment",
            17: "Accommodation/Food Services",
            18: "Other Services",
            19: "Public Administration",
            20: "Unclassified"
        }
        return naics_names.get(code, f"Industry {code}")

