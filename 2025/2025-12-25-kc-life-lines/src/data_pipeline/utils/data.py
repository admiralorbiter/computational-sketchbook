"""General data utility functions."""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_geoid(df, geoid_column: str = "GEOID"):
    """Validate GEOID format and completeness.
    
    Args:
        df: DataFrame to validate
        geoid_column: Name of GEOID column
    
    Returns:
        Boolean indicating if GEOIDs are valid
    """
    if geoid_column not in df.columns:
        logger.warning(f"GEOID column '{geoid_column}' not found")
        return False
    
    # Check for nulls
    if df[geoid_column].isnull().any():
        logger.warning("Found null GEOIDs")
        return False
    
    # TODO: Add more validation (format checks, etc.)
    return True


def standardize_column_names(df):
    """Standardize column names to lowercase with underscores.
    
    Args:
        df: DataFrame to standardize
    
    Returns:
        DataFrame with standardized column names
    """
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df
