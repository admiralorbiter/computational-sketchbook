"""Configuration management for the data pipeline."""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Pipeline configuration."""
    
    # API Keys (from environment variables)
    CENSUS_API_KEY: Optional[str] = os.getenv("CENSUS_API_KEY")
    BLS_API_KEY: Optional[str] = os.getenv("BLS_API_KEY")
    
    # Data source configuration
    DATA_YEAR: int = int(os.getenv("DATA_YEAR", "2023"))
    GEOGRAPHY_VINTAGE: int = int(os.getenv("GEOGRAPHY_VINTAGE", "2020"))
    ACS_TYPE: str = os.getenv("ACS_TYPE", "5year")  # 1year or 5year
    
    # Kansas City metro region definition
    # Default: MO counties (29047 Jackson, 29095 Platte, 29165 Clay)
    # KS counties (20091 Johnson, 20013 Cass, 20107 Leavenworth, 20121 Miami)
    KC_METRO_COUNTIES: list = os.getenv(
        "KC_METRO_COUNTIES",
        "29047,29095,29165,20091,20013,20107,20121"
    ).split(",")
    
    # Directory paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    PACKS_DIR: Path = DATA_DIR / "packs"
    
    # Output configuration
    DATA_OUTPUT_DIR: Path = Path(os.getenv("DATA_OUTPUT_DIR", str(PACKS_DIR)))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Region metadata
    REGION_NAME: str = "KC_v1"
    
    # Data source URLs (can be overridden via environment)
    CENSUS_API_BASE: str = "https://api.census.gov/data"
    BLS_API_BASE: str = "https://api.bls.gov/publicAPI/v2"
    COLLEGE_SCORECARD_API: str = "https://api.data.gov/ed/collegescorecard/v1"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist."""
        directories = [
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.PACKS_DIR,
            cls.DATA_OUTPUT_DIR
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    @classmethod
    def get_pack_version(cls, year: Optional[int] = None, vintage: Optional[int] = None) -> str:
        """Generate a data pack version string.
        
        Args:
            year: Data year (defaults to DATA_YEAR)
            vintage: Geography vintage (defaults to GEOGRAPHY_VINTAGE)
        
        Returns:
            Version string (e.g., "KC_v1_2023_2020")
        """
        year = year or cls.DATA_YEAR
        vintage = vintage or cls.GEOGRAPHY_VINTAGE
        return f"{cls.REGION_NAME}_{year}_{vintage}"
    
    @classmethod
    def get_pack_output_path(cls, version: Optional[str] = None) -> Path:
        """Get the output path for a data pack.
        
        Args:
            version: Pack version string (defaults to generated version)
        
        Returns:
            Path to pack directory
        """
        version = version or cls.get_pack_version()
        return cls.DATA_OUTPUT_DIR / version


# Initialize directories on import
Config.ensure_directories()
