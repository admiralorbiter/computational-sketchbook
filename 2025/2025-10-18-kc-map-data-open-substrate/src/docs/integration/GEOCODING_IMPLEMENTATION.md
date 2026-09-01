# Geocoding Service Implementation

## Overview

The geocoding service provides intelligent address-to-coordinate conversion with aggressive caching, rate limiting, and fallback between free Census API and paid Google Maps API. This minimizes costs while ensuring high geocoding accuracy.

## Architecture

### Components

1. **Address Normalizer** (`tools/geocoding/address_normalizer.py`)
   - Standardizes address formats
   - Parses address components
   - Fuzzy matching for similar addresses
   - Component-based matching

2. **Census Geocoder** (`tools/geocoding/census_geocoder.py`)
   - Free US Census Geocoding API client
   - Daily limit: 1,000 requests
   - Automatic rate limiting
   - Retry logic with exponential backoff

3. **Google Geocoder** (`tools/geocoding/google_geocoder.py`)
   - Google Maps Geocoding API client
   - Monthly limit: 40,000 requests (free tier)
   - Higher accuracy and coverage
   - Regional biasing for Missouri/Kansas

4. **Rate Limiter** (`tools/geocoding/rate_limiter.py`)
   - Tracks daily/monthly usage
   - Auto-switches between services
   - Persists usage to database
   - Provides usage statistics

5. **Geocoding Service** (`tools/geocoding/geocoding_service.py`)
   - Main orchestration service
   - 3-tier cache strategy (exact, fuzzy, component)
   - Batch processing support
   - Quality scoring and validation

6. **Geocoding Cache** (database table)
   - Stores geocoded results
   - Fast hash-based lookups
   - Usage tracking for optimization
   - Quality and confidence metrics

## Cache Strategy

The service uses a 3-tier cache lookup strategy to maximize cache hits:

### Tier 1: Exact Hash Match
- Fastest lookup using MD5 hash of normalized address
- O(1) performance with unique index
- Returns immediately on match

### Tier 2: Fuzzy String Match
- Compares normalized addresses using Levenshtein distance
- Threshold: 85% similarity (configurable)
- Only searches high/medium quality cached results
- Returns best match above threshold

### Tier 3: Component-Based Match
- Matches on parsed address components (street, city, state, zip)
- Useful when address format varies
- Weighted scoring based on component importance
- Threshold: 70% component match (configurable)

### Cache Miss: API Geocoding
If no cache match found:
1. Check Census API rate limit
2. If within limit, try Census API
3. If Census fails or rate limited, try Google API
4. Store successful result in cache
5. Return coordinates with metadata

## API Usage

### REST API Endpoints

All endpoints are under `/api/geocoding`:

#### POST `/api/geocoding/geocode`
Geocode a single address.

**Request:**
```json
{
  "address": "123 Main St, Kansas City, MO 64101",
  "source_priority": ["census", "google"]
}
```

**Response:**
```json
{
  "success": true,
  "latitude": 39.0997,
  "longitude": -94.5786,
  "formatted_address": "123 MAIN STREET, KANSAS CITY, MISSOURI 64101",
  "confidence_score": 95.5,
  "geocoding_quality": "high",
  "match_type": "exact",
  "source": "census",
  "from_cache": false,
  "times_used": 1
}
```

#### POST `/api/geocoding/batch`
Geocode multiple addresses (max 1000 per request).

**Request:**
```json
{
  "addresses": [
    "123 Main St, Kansas City, MO 64101",
    "456 Oak Ave, Kansas City, MO 64102"
  ],
  "source_priority": ["census", "google"],
  "batch_size": 100
}
```

**Response:**
```json
{
  "success": true,
  "results": [...],
  "summary": {
    "total": 2,
    "successful": 2,
    "failed": 0,
    "success_rate": 100.0
  }
}
```

#### GET `/api/geocoding/cache-stats`
Get cache performance metrics.

#### GET `/api/geocoding/usage`
Get API usage statistics.

### Python API

```python
from tools.geocoding import GeocodingService

# Initialize service
service = GeocodingService(
    db_path="data/processed/kc_data.gpkg",
    google_api_key="your-api-key"
)

# Geocode single address
result = service.geocode_address("123 Main St, Kansas City, MO")

if result['success']:
    print(f"Coordinates: {result['latitude']}, {result['longitude']}")
    print(f"Confidence: {result['confidence_score']}%")
    print(f"From cache: {result['from_cache']}")

# Batch geocode
addresses = ["address1", "address2", "address3"]
results = service.batch_geocode(addresses, batch_size=100)

# Get statistics
cache_stats = service.get_cache_stats()
usage_stats = service.get_usage_stats()
```

## ETL Integration

The geocoding service is integrated into the ETL pipeline through `DatabaseHelper.geocode_missing_coordinates()`:

```python
from tools.etl.utils import DatabaseHelper
from web.models import ServiceRequest

db_helper = DatabaseHelper()

# Geocode records without coordinates
stats = db_helper.geocode_missing_coordinates(
    model_class=ServiceRequest,
    batch_size=100
)

print(f"Geocoded: {stats['geocoded']}")
print(f"Errors: {stats['errors']}")
```

This can be added to any ETL script after loading data:

```python
# In your ETL script
load_stats = self.load_data(transformed_data)

# Geocode missing coordinates
geocode_stats = self.db_helper.geocode_missing_coordinates(
    model_class=YourModel,
    batch_size=100
)

self.logger.info(f"Geocoded {geocode_stats['geocoded']} addresses")
```

## CLI Tool

The CLI tool (`tools/geocoding/geocode_cli.py`) provides command-line management:

```bash
# Geocode single address
python tools/geocoding/geocode_cli.py geocode "123 Main St, Kansas City, MO"

# Batch geocode from CSV file
python tools/geocoding/geocode_cli.py batch addresses.csv --output results.csv

# Backfill missing coordinates in a table
python tools/geocoding/geocode_cli.py backfill businesses --limit 1000

# Show statistics
python tools/geocoding/geocode_cli.py stats

# Clear cache
python tools/geocoding/geocode_cli.py clear-cache --confirm
```

## Configuration

Add these environment variables to your `.env` file:

```bash
# Census Geocoding API
CENSUS_API_URL=https://geocoding.geo.census.gov/geocoder/locations/onelineaddress
CENSUS_DAILY_LIMIT=1000
CENSUS_LIMIT_THRESHOLD=0.9

# Google Maps Geocoding API
GOOGLE_MAPS_API_KEY=your-api-key-here
GOOGLE_GEOCODING_URL=https://maps.googleapis.com/maps/api/geocode/json
GOOGLE_MONTHLY_LIMIT=40000

# Geocoding Service Settings
GEOCODING_CACHE_ENABLED=true
GEOCODING_FUZZY_THRESHOLD=0.85
GEOCODING_BATCH_SIZE=100
```

## Performance Optimization

### Cache Hit Rate
- Target: >80% after initial data load
- Fuzzy matching improves hit rate for address variations
- Component matching catches format differences

### API Usage
- Census API: <1,000 requests/day (stay in free tier)
- Google API: Minimize usage, target <100/month
- Auto-switch at 90% of rate limit

### Database Optimization
- Hash-based exact lookups: O(1)
- Indexed normalized addresses
- Component-based indexes for partial matches
- Spatial indexes for coordinate queries

## Quality Assurance

### Confidence Scoring
Each geocoded address receives a confidence score (0-100):

- **High Quality (85-100%)**: Exact address match, all components present
- **Medium Quality (70-84%)**: Street-level match with interpolation
- **Low Quality (<70%)**: City-level or approximate match

### Quality Metrics
- `geocoding_quality`: high | medium | low
- `confidence_score`: 0-100 numerical score
- `match_type`: exact | fuzzy | component
- `geocoding_source`: census | google | manual

### Validation
- Coordinates validated within Kansas City metro area bounds
- Invalid coordinates flagged and not cached
- Low-confidence results can be flagged for manual review

## Cost Optimization

### Census API (Free)
- 1,000 requests/day limit
- Primary service for all geocoding
- Automatic tracking and limit enforcement

### Google Maps API (Paid)
- $5 per 1,000 requests after free tier
- Used only when Census fails or rate limited
- Monthly limit tracking
- Cost monitoring and alerts

### Estimated Costs
Assuming 80% cache hit rate after initial load:

| Scenario | Daily Requests | Census API | Google API | Monthly Cost |
|----------|---------------|------------|------------|--------------|
| Initial Load | 10,000 | 1,000 | 1,000 | $150 |
| Steady State | 100 | 20 | 0 | $0 |
| Peak Usage | 1,000 | 200 | 0 | $0 |

With aggressive caching, ongoing costs should be $0-$10/month.

## Troubleshooting

### Common Issues

**Issue**: Geocoding fails with "Rate limit exceeded"
- **Solution**: Check usage with `geocode_cli.py stats`, wait for daily/monthly reset

**Issue**: Low confidence scores
- **Solution**: Review address format, ensure city/state included, consider manual review

**Issue**: Cache not being used
- **Solution**: Check `GEOCODING_CACHE_ENABLED=true` in config, verify database table exists

**Issue**: Coordinates outside expected area
- **Solution**: Review validation bounds in `DataValidator.KC_BOUNDS`, adjust if needed

### Monitoring

Check service health:
```bash
# Get cache statistics
python tools/geocoding/geocode_cli.py stats

# Test geocoding
python tools/geocoding/geocode_cli.py geocode "123 Main St, Kansas City, MO"
```

Monitor via API:
```bash
curl http://localhost:5000/api/geocoding/cache-stats
curl http://localhost:5000/api/geocoding/usage
curl http://localhost:5000/api/geocoding/health
```

## Best Practices

1. **Always normalize addresses** before manual entry to improve cache hits
2. **Use batch operations** for bulk geocoding (more efficient)
3. **Monitor usage regularly** to avoid unexpected costs
4. **Review low-confidence results** for data quality
5. **Clean cache periodically** of outdated or low-quality entries
6. **Test with Census API first** before enabling Google API
7. **Set up alerts** for approaching rate limits

## Future Enhancements

- Reverse geocoding (coordinates to address)
- Address validation and correction suggestions
- Integration with additional geocoding services (Mapbox, OpenCage)
- Machine learning for address parsing improvement
- Real-time cache warming for frequently accessed areas
- Bulk export/import of geocoding cache
- Administrative UI for cache management
