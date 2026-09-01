# Geocoding Service - Complete Guide

**Comprehensive documentation for address-to-coordinate conversion with cost optimization and intelligent caching.**

## Overview

The geocoding service provides intelligent address-to-coordinate conversion with aggressive caching, rate limiting, and fallback between free Census API and paid Google Maps API. This minimizes costs while ensuring high geocoding accuracy.

### Features

- **3-tier cache strategy** for maximum cost savings
- **Dual API support** (Census free, Google paid fallback)
- **Rate limiting** and automatic service switching
- **Quality scoring** and confidence metrics
- **Batch processing** for efficient bulk geocoding
- **ETL integration** for automated data loading

## Architecture

### Components

1. **Address Normalizer** - Standardizes address formats and fuzzy matching
2. **Census Geocoder** - Free US Census API client (1,000 requests/day)
3. **Google Geocoder** - Google Maps API client (40,000 requests/month free tier)
4. **Rate Limiter** - Usage tracking and automatic service switching
5. **Geocoding Service** - Main orchestration with 3-tier cache
6. **Database Cache** - Hash-based lookups for fast retrieval

## Cache Strategy

### Tier 1: Exact Hash Match
- MD5 hash of normalized address
- O(1) performance with unique index
- Returns immediately on match

### Tier 2: Fuzzy String Match
- Levenshtein distance comparison
- 85% similarity threshold
- Only searches high/medium quality results

### Tier 3: Component-Based Match
- Matches on parsed components (street, city, state, zip)
- 70% component match threshold
- Weighted scoring by component importance

### Cache Miss: API Geocoding
1. Check Census API rate limit
2. Try Census API (within limits)
3. Fallback to Google API if needed
4. Store result in cache
5. Return with metadata

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Add to `.env` file:

```bash
# Census Geocoding API (Free)
CENSUS_API_URL=https://geocoding.geo.census.gov/geocoder/locations/onelineaddress
CENSUS_DAILY_LIMIT=1000
CENSUS_LIMIT_THRESHOLD=0.9

# Google Maps API (Paid fallback)
GOOGLE_MAPS_API_KEY=your-api-key-here
GOOGLE_GEOCODING_URL=https://maps.googleapis.com/maps/api/geocode/json
GOOGLE_MONTHLY_LIMIT=40000

# Service Settings
GEOCODING_CACHE_ENABLED=true
GEOCODING_FUZZY_THRESHOLD=0.85
GEOCODING_BATCH_SIZE=100
```

### 3. Create Database Tables

```bash
python tools/database/create_geocoding_cache.py
```

## Usage

### REST API

**Geocode Single Address:**
```bash
curl -X POST http://localhost:5000/api/geocoding/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Kansas City, MO 64101"}'
```

**Batch Geocode:**
```bash
curl -X POST http://localhost:5000/api/geocoding/batch \
  -H "Content-Type: application/json" \
  -d '{"addresses": ["address1", "address2"]}'
```

**Get Cache Stats:**
```bash
curl http://localhost:5000/api/geocoding/cache-stats
```

### Python API

```python
from tools.geocoding import GeocodingService

service = GeocodingService(
    db_path="data/processed/kc_data.gpkg",
    google_api_key="your-key"
)

# Single address
result = service.geocode_address("123 Main St, Kansas City, MO")
if result['success']:
    print(f"Coordinates: {result['latitude']}, {result['longitude']}")
    print(f"Confidence: {result['confidence_score']}%")

# Batch geocode
results = service.batch_geocode(addresses, batch_size=100)
```

### CLI Tool

```bash
# Geocode single address
python tools/geocoding/geocode_cli.py geocode "123 Main St, Kansas City, MO"

# Batch from CSV
python tools/geocoding/geocode_cli.py batch addresses.csv --output results.csv

# Backfill missing coordinates
python tools/geocoding/geocode_cli.py backfill businesses --limit 1000

# Show statistics
python tools/geocoding/geocode_cli.py stats

# Clear cache
python tools/geocoding/geocode_cli.py clear-cache --confirm
```

### ETL Integration

```python
from tools.etl.utils import DatabaseHelper
from web.models import ServiceRequest

db_helper = DatabaseHelper()

# Geocode missing coordinates in table
stats = db_helper.geocode_missing_coordinates(
    model_class=ServiceRequest,
    batch_size=100
)

print(f"Geocoded: {stats['geocoded']}")
print(f"Errors: {stats['errors']}")
```

## Testing

### Quick Test

```bash
python tools/geocoding/geocode_cli.py geocode "123 Main St, Kansas City, MO" --verbose
```

### Test with Real Data

```bash
# Test with Land Bank data (10 addresses)
python tools/geocoding/test_landbank_geocoding.py --sample-size 10

# Full test (all addresses)
python tools/geocoding/test_landbank_geocoding.py --sample-size 0
```

### Cache Performance Test

```bash
# First run - hits APIs
python tools/geocoding/test_landbank_geocoding.py --sample-size 20

# Second run - uses cache
python tools/geocoding/test_landbank_geocoding.py --sample-size 20
```

### ETL Integration Test

```bash
# Test Land Bank ETL with geocoding
python tools/etl/load_landbank_data.py --test --limit 10 --verbose

# Full ETL
python tools/etl/load_landbank_data.py --initial --verbose
```

## Performance

### Cache Hit Rate
- **Target**: >80% after initial load
- Fuzzy matching improves hit rate for variations
- Component matching catches format differences

### API Usage
- **Census API**: <1,000 requests/day (free tier)
- **Google API**: <100/month (minimize costs)
- Auto-switch at 90% of limit

### Expected Performance

| Scenario | Daily Requests | Census API | Google API | Monthly Cost |
|----------|---------------|------------|------------|---------------|
| Initial Load | 10,000 | 1,000 | 1,000 | $150 |
| Steady State | 100 | 20 | 0 | $0 |
| Peak Usage | 1,000 | 200 | 0 | $0 |

With aggressive caching, ongoing costs should be **$0-$10/month**.

## Quality Assurance

### Confidence Scoring

- **High Quality (85-100%)**: Exact match, all components
- **Medium Quality (70-84%)**: Street-level with interpolation
- **Low Quality (<70%)**: City-level or approximate

### Validation

- Coordinates validated within KC metro bounds
- Invalid coordinates flagged and not cached
- Low-confidence results flagged for review

## Troubleshooting

### Common Issues

**Rate limit exceeded:**
```bash
python tools/geocoding/geocode_cli.py stats
# Wait for daily/monthly reset
```

**Low confidence scores:**
- Review address format
- Ensure city/state included
- Consider manual review

**Cache not being used:**
- Check `GEOCODING_CACHE_ENABLED=true`
- Verify database table exists

**Coordinates outside expected area:**
- Review validation bounds
- Adjust bounds if needed

### Monitoring

```bash
# Cache statistics
python tools/geocoding/geocode_cli.py stats

# API usage
python tools/geocoding/geocode_cli.py usage

# Failed addresses
python tools/geocoding/geocode_cli.py failed
```

## Best Practices

1. **Normalize addresses** before manual entry
2. **Use batch operations** for bulk geocoding
3. **Monitor usage regularly** to avoid costs
4. **Review low-confidence results** for quality
5. **Clean cache periodically** of outdated entries
6. **Test with Census API first** before Google
7. **Set up alerts** for approaching limits

## File Structure

```
tools/geocoding/
├── address_normalizer.py      # Address standardization
├── census_geocoder.py          # Free Census API
├── google_geocoder.py          # Paid Google API
├── rate_limiter.py            # Usage tracking
├── geocoding_service.py        # Main orchestration
├── geocode_cli.py              # CLI tool
└── test_landbank_geocoding.py  # Test script

web/api/
└── geocoding.py                # REST API endpoints
```

## References

- [Census Geocoding API](https://www.census.gov/programs-surveys/geography/geocoding-services.html)
- [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding)
- Service Implementation: `docs/integration/GEOCODING_IMPLEMENTATION.md`
