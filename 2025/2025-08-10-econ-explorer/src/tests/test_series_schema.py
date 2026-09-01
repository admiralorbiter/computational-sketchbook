from app.models.series import SeriesResponse, SeriesPoint

def test_series_model():
    s = SeriesResponse(series_id="x", geo_id="US", unit="index", observations=[SeriesPoint(date="2024-01", value=1.23)])
    d = s.model_dump()
    assert d["observations"][0]["date"] == "2024-01"
