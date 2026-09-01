"""Data format exporters: Parquet, JSON, etc."""

import logging
import pandas as pd
import geopandas as gpd
from pathlib import Path

logger = logging.getLogger(__name__)


def export_to_parquet(data, output_path: Path, compression: str = "snappy"):
    """Export DataFrame or GeoDataFrame to Parquet format.
    
    Args:
        data: DataFrame or GeoDataFrame to export
        output_path: Output file path
        compression: Compression codec (snappy, gzip, brotli, etc.)
    """
    logger.info(f"Exporting to Parquet: {output_path}")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(data, gpd.GeoDataFrame):
        # GeoDataFrame needs special handling for geometry column
        data.to_parquet(output_path, compression=compression, index=False)
    else:
        data.to_parquet(output_path, compression=compression, index=False)


def export_to_json(data, output_path: Path, orient: str = "records"):
    """Export DataFrame to JSON format.
    
    Args:
        data: DataFrame to export
        output_path: Output file path
        orient: JSON orientation (records, index, values, etc.)
    """
    logger.info(f"Exporting to JSON: {output_path}")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data.to_json(output_path, orient=orient, date_format="iso", indent=2)
