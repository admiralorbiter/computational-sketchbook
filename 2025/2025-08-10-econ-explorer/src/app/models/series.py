from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List

class SeriesPoint(BaseModel):
    date: str = Field(description="YYYY-MM")
    value: float

class SeriesResponse(BaseModel):
    series_id: str
    geo_id: str
    unit: str = "index"
    observations: List[SeriesPoint]
