# Geocoding Service

Intelligent address-to-GPS geocoding service with aggressive caching and cost optimization.

## Quick Start

### Basic Usage

```python
from tools.geocoding import GeocodingService

# Initialize
service = GeocodingService(
    db_path="data/processed/kc_data.gpkg",
    google_api_key="your-key"  # Optional
)

# Geocode an address
result = service.geocode_address("123 Main St, Kansas City, MO")

if result['success']:
    print(f"Coordinates: {result['latitude']}, {result['longitude']}")
    print(f"Confidence: {result['confidence_score']}%")
    print(f"Cached: {result['from_cache']}")
```

### Command Line

```bash
# Geocode a single address
python tools/geocoding/geocode_cli.py geocode "123 Main St, Kansas City, MO"

# Show statistics
python tools/geocoding/geocode_cli.py stats

# Batch process
python tools/geocoding/geocode_cli.py batch addresses.csv --output results.csv
```

## Features

- **3-Tier Cache**: Exact, fuzzy, and component-based matching
- **Free Census API**: Primary geocoding source (1,000/day)
- **Google Maps Fallback**: Automatic fallback when needed
- **Rate Limiting**: Tracks usage to stay within free tiers
- **Batch Processing**: Efficient bulk operations
- **Quality Scoring**: Confidence metrics for each result

## Architecture

```
Address Input
    ↓
Normalize Address
    ↓
Cache Check (3 tiers)
    ├─→ Exact Match ──→ Return (fastest)
    ├─→ Fuzzy Match ──→ Return
    └─→ Component Match ─→ Return
    ↓ Cache Miss
API Geocoding
    ├─→ Census API (free)
    └─→ Google Maps (fallback)
    ↓
Cache Result
    ↓
Return Coordinates
```

## Modules

- `address_normalizer.py` - Address parsing and normalization
- `census_geocoder.py` - US Census Geocoding API client
- `google_geocoder.py` - Google Maps Geocoding API client
- `rate_limiter.py` - Usage tracking and rate limiting
- `geocoding_service.py` - Main orchestration service
- `geocode_cli.py` - Command-line interface

## Configuration

Set in your `.env` file:

```bash
GOOGLE_MAPS_API_KEY=your-key-here
CENSUS_DAILY_LIMIT=1000
GEOCODING_CACHE_ENABLED=true
GEOCODING_FUZZY_THRESHOLD=0.85
```

## Documentation

See `docs/integration/GEOCODING_IMPLEMENTATION.md` for complete documentation.

## Testing

```bash
# Run unit tests
python -m pytest tests/unit/test_geocoding_service.py

# Test CLI
python tools/geocoding/geocode_cli.py geocode "123 Main St, Kansas City, MO"
```

## Cost Optimization

- Cache hit rate: >80% target
- Census API: Free (1,000/day)
- Google API: Minimized ($5/1000 requests)
- Expected cost: $0-$10/month with caching
