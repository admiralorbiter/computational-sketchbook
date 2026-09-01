"""Local Kansas City data ingestion: Open Data KC (Socrata)."""

import logging

logger = logging.getLogger(__name__)


def ingest_kc_crime_data(start_date: str = None, end_date: str = None):
    """Ingest KCPD crime reports from Open Data KC.
    
    Args:
        start_date: Start date for crime data (YYYY-MM-DD)
        end_date: End date for crime data (YYYY-MM-DD)
    
    Returns:
        DataFrame with crime reports (aggregated to tract)
    """
    logger.info("Ingesting KCPD crime data from Open Data KC")
    # TODO: Implement Socrata API calls for crime data
    pass


def ingest_kc_311_data(start_date: str = None, end_date: str = None):
    """Ingest 311/service calls from Open Data KC.
    
    Args:
        start_date: Start date for 311 data
        end_date: End date for 311 data
    
    Returns:
        DataFrame with 311 service calls
    """
    logger.info("Ingesting 311 data from Open Data KC")
    # TODO: Implement Socrata API calls for 311 data
    pass
