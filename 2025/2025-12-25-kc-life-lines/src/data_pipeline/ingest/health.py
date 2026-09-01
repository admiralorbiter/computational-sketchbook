"""Health data ingestion: CDC PLACES, ATSDR SVI."""

import logging

logger = logging.getLogger(__name__)


def ingest_cdc_places(year: int = 2023):
    """Ingest CDC PLACES data (modeled local health indicators).
    
    Args:
        year: Year of PLACES data
    
    Returns:
        DataFrame with tract-level health indicators
    """
    logger.info(f"Ingesting CDC PLACES data for year {year}")
    # TODO: Implement CDC PLACES download
    pass


def ingest_svi(year: int = 2020):
    """Ingest CDC/ATSDR Social Vulnerability Index data.
    
    Args:
        year: Year of SVI data
    
    Returns:
        DataFrame with SVI indicators (use carefully)
    """
    logger.info(f"Ingesting SVI data for year {year}")
    # TODO: Implement SVI download
    pass
