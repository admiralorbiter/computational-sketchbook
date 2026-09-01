"""Main pipeline orchestrator for KC: Life Lines data pipeline.

This module orchestrates the entire data pipeline:
1. Ingest raw data from various sources
2. Process and normalize data
3. Join data on stable IDs
4. Calculate derived indices
5. Export data packs for game runtime
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from data_pipeline.config import Config

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Config.DATA_DIR / "pipeline.log")
    ]
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the data pipeline workflow."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the pipeline orchestrator.
        
        Args:
            config: Configuration object (defaults to Config class)
        """
        self.config = config or Config
        self.pack_version = self.config.get_pack_version()
        self.output_path = self.config.get_pack_output_path(self.pack_version)
        
        logger.info(f"Initializing pipeline orchestrator")
        logger.info(f"Data year: {self.config.DATA_YEAR}")
        logger.info(f"Geography vintage: {self.config.GEOGRAPHY_VINTAGE}")
        logger.info(f"Pack version: {self.pack_version}")
        logger.info(f"Output path: {self.output_path}")
    
    def run(self):
        """Run the complete pipeline workflow.
        
        Returns:
            Path to created data pack
        """
        logger.info("=" * 60)
        logger.info("Starting KC: Life Lines Data Pipeline")
        logger.info("=" * 60)
        
        try:
            # Stage 1: Ingest raw data
            logger.info("\n" + "=" * 60)
            logger.info("Stage 1: Data Ingestion")
            logger.info("=" * 60)
            raw_data = self._ingest_data()
            
            # Stage 2: Process and normalize data
            logger.info("\n" + "=" * 60)
            logger.info("Stage 2: Data Processing & Normalization")
            logger.info("=" * 60)
            processed_data = self._process_data(raw_data)
            
            # Stage 3: Join data on stable IDs
            logger.info("\n" + "=" * 60)
            logger.info("Stage 3: Data Joining")
            logger.info("=" * 60)
            joined_data = self._join_data(processed_data)
            
            # Stage 4: Calculate derived indices
            logger.info("\n" + "=" * 60)
            logger.info("Stage 4: Index Calculation")
            logger.info("=" * 60)
            indexed_data = self._calculate_indices(joined_data)
            
            # Stage 5: Export data pack
            logger.info("\n" + "=" * 60)
            logger.info("Stage 5: Data Pack Export")
            logger.info("=" * 60)
            pack_path = self._export_data_pack(indexed_data)
            
            logger.info("\n" + "=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info(f"Data pack available at: {pack_path}")
            logger.info("=" * 60)
            
            return pack_path
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}", exc_info=True)
            raise
    
    def _ingest_data(self) -> dict:
        """Ingest raw data from all sources.
        
        Returns:
            Dictionary of raw data by source type
        """
        raw_data = {}
        
        # Import ingest modules (lazy import to avoid errors if not all implemented)
        try:
            from data_pipeline.ingest import census, education, labor, transit, health, housing, local
            
            logger.info("Ingesting Census data (ACS, TIGER/Line)...")
            raw_data["tiger"] = census.ingest_tiger_shapefiles(
                geography="tract",
                vintage=self.config.GEOGRAPHY_VINTAGE
            )
            raw_data["census"] = census.ingest_acs_data(
                geography="tract",
                year=self.config.DATA_YEAR,
                acs_type=self.config.ACS_TYPE
            )
            
            logger.info("Ingesting Education data...")
            raw_data["nces"] = education.ingest_nces_districts(
                vintage=self.config.GEOGRAPHY_VINTAGE
            )
            # raw_data["mo_dese"] = education.ingest_mo_dese_data()
            # raw_data["ksde"] = education.ingest_ksde_data()
            # raw_data["college_scorecard"] = education.ingest_college_scorecard()
            
            logger.info("Ingesting Labor market data...")
            # raw_data["bls"] = labor.ingest_bls_data(...)
            # raw_data["onet"] = labor.ingest_onet_database()
            
            logger.info("Ingesting Transit data...")
            # raw_data["gtfs"] = transit.ingest_kcata_gtfs()
            
            logger.info("Ingesting Health data...")
            # raw_data["places"] = health.ingest_cdc_places(...)
            # raw_data["svi"] = health.ingest_svi(...)
            
            logger.info("Ingesting Housing data...")
            # raw_data["lai"] = housing.ingest_hud_lai()
            
            logger.info("Ingesting Local KC data...")
            # raw_data["crime"] = local.ingest_kc_crime_data(...)
            # raw_data["311"] = local.ingest_kc_311_data(...)
            
            logger.info("Data ingestion stage complete (placeholder - implement actual ingestion)")
            
        except ImportError as e:
            logger.warning(f"Import error in ingestion stage: {e}")
        
        return raw_data
    
    def _process_data(self, raw_data: dict) -> dict:
        """Process and normalize raw data.
        
        Args:
            raw_data: Dictionary of raw data
        
        Returns:
            Dictionary of processed data
        """
        processed_data = {}
        
        try:
            from data_pipeline.process import normalize
            
            # Assign tracts to districts if both are available
            if "tiger" in raw_data and "nces" in raw_data:
                logger.info("Assigning tracts to school districts...")
                processed_data["tract_district_map"] = normalize.assign_tract_to_district(
                    tracts_gdf=raw_data["tiger"],
                    districts_gdf=raw_data["nces"]
                )
            else:
                missing = []
                if "tiger" not in raw_data:
                    missing.append("tiger (tracts)")
                if "nces" not in raw_data:
                    missing.append("nces (districts)")
                logger.warning(f"Cannot assign tracts to districts: missing {', '.join(missing)}")
            
            logger.info("Normalizing geography...")
            # processed_data["tracts"] = normalize.normalize_geography(...)
            
            logger.info("Data processing stage complete")
            
        except ImportError as e:
            logger.warning(f"Import error in processing stage: {e}")
        except Exception as e:
            logger.error(f"Error in processing stage: {e}", exc_info=True)
            raise
        
        return processed_data
    
    def _join_data(self, processed_data: dict) -> dict:
        """Join processed data on stable IDs.
        
        Args:
            processed_data: Dictionary of processed data
        
        Returns:
            Dictionary of joined data
        """
        joined_data = {}
        
        try:
            from data_pipeline.process import join
            
            logger.info("Joining data on GEOID...")
            # joined_data["tracts"] = join.join_on_geoid(...)
            
            logger.info("Joining education data on NCES ID...")
            # joined_data["districts"] = join.join_on_nces_id(...)
            
            logger.info("Joining college data on IPEDS ID...")
            # joined_data["colleges"] = join.join_on_ipeds_id(...)
            
            logger.info("Data joining stage complete (placeholder - implement actual joining)")
            
        except ImportError as e:
            logger.warning(f"Import error in joining stage: {e}")
        
        return joined_data
    
    def _calculate_indices(self, joined_data: dict) -> dict:
        """Calculate derived indices.
        
        Args:
            joined_data: Dictionary of joined data
        
        Returns:
            Dictionary of data with indices added
        """
        indexed_data = {}
        
        try:
            from data_pipeline.process import indices
            
            logger.info("Calculating Opportunity Index...")
            # indexed_data["tracts"] = indices.calculate_opportunity_index(...)
            
            logger.info("Calculating Transit Access Score...")
            # indexed_data["transit"] = indices.calculate_transit_access_score(...)
            
            logger.info("Calculating Housing Stability Risk Score...")
            # indexed_data["housing"] = indices.calculate_housing_stability_risk(...)
            
            logger.info("Index calculation stage complete (placeholder - implement actual calculations)")
            
        except ImportError as e:
            logger.warning(f"Import error in index calculation stage: {e}")
        
        return indexed_data
    
    def _export_data_pack(self, indexed_data: dict) -> Path:
        """Export final data pack.
        
        Args:
            indexed_data: Dictionary of indexed data
        
        Returns:
            Path to created data pack directory
        """
        try:
            from data_pipeline.export import pack_builder
            
            logger.info("Building data pack...")
            
            # Extract data components (placeholder - will be populated when data flows through)
            tract_data = indexed_data.get("tracts", None)
            district_data = indexed_data.get("districts", None)
            college_data = indexed_data.get("colleges", None)
            job_data = indexed_data.get("jobs", None)
            transit_data = indexed_data.get("transit", None)
            
            # Build metadata
            metadata = {
                "region": self.config.REGION_NAME,
                "version": self.pack_version,
                "data_year": self.config.DATA_YEAR,
                "geography_vintage": self.config.GEOGRAPHY_VINTAGE,
                "created_at": datetime.now().isoformat(),
                "acs_type": self.config.ACS_TYPE
            }
            
            pack_path = pack_builder.build_data_pack(
                tract_data=tract_data,
                district_data=district_data,
                college_data=college_data,
                job_data=job_data,
                transit_data=transit_data,
                region_name=self.config.REGION_NAME,
                output_dir=self.output_path,
                metadata=metadata
            )
            
            logger.info(f"Data pack exported to: {pack_path}")
            
            return pack_path
            
        except ImportError as e:
            logger.warning(f"Import error in export stage: {e}")
            return self.output_path


def main():
    """Main entry point for the pipeline."""
    try:
        orchestrator = PipelineOrchestrator()
        pack_path = orchestrator.run()
        print(f"\n[OK] Pipeline completed successfully!")
        print(f"[OK] Data pack: {pack_path}")
        return 0
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\n[ERROR] Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
