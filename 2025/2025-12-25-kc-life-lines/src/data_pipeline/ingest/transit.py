"""Transit data ingestion: KCATA GTFS."""

import logging

logger = logging.getLogger(__name__)


def ingest_kcata_gtfs():
    """Ingest KCATA GTFS data (schedules, stops, routes).
    
    Returns:
        Dictionary of GTFS dataframes (stops, routes, trips, etc.)
    """
    logger.info("Ingesting KCATA GTFS data")
    # TODO: Implement GTFS download and parsing
    pass
