"""Housing data ingestion: HUD Location Affordability Index."""

import logging

logger = logging.getLogger(__name__)


def ingest_hud_lai():
    """Ingest HUD Location Affordability Index data.
    
    Returns:
        GeoDataFrame with block-group level housing+transport cost data
    """
    logger.info("Ingesting HUD Location Affordability Index data")
    # TODO: Implement HUD LAI download
    pass
