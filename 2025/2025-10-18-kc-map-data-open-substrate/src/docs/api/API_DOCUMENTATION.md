# API Documentation - Kansas City Data Platform

## Overview

The Kansas City Data Platform provides a RESTful API for accessing crime, 311 service requests, business licenses, food inspections, and OpenStreetMap data. All endpoints return JSON responses and support spatial and temporal filtering.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, no authentication is required for public data access. Rate limiting is applied per IP address.

## Rate Limits

- **Per IP**: 100 requests per minute
- **Per Endpoint**: 50 requests per minute
- **Headers**: Rate limit information included in response headers

## New Features (Post-Refactor)

### Consolidation Settings API
- **Endpoint**: `PUT /api/settings/consolidation`
- **Purpose**: Configure feature consolidation behavior
- **Presets**: Aggressive, Balanced, Loose, Custom

### Simplified Filtering
- **311 Service Requests**: Only issue type filtering
- **Crime Incidents**: Only offense type filtering
- **OSM Points**: No filtering (simplified)

### Cross-Layer Consolidation
- **Endpoint**: `GET /api/features/consolidated`
- **Purpose**: Get consolidated features across multiple layers
- **Features**: Proximity-based grouping with configurable tolerance

## Response Format

All successful responses return JSON with the following structure:

```json
{
  "type": "FeatureCollection",
  "features": [...],
  "total": 1500,
  "limit": 100,
  "offset": 0,
  "execution_time_ms": 45
}
```

Error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional error details"
}
```

## Crime Data API

### Get Crime Incidents

Retrieve crime incident data with optional filtering.

**Endpoint**: `GET /api/v1/crime`

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `bbox` | string | Bounding box (minx,miny,maxx,maxy) | "-94.6,39.0,-94.5,39.1" | No |
| `radius` | number | Search radius in meters | 1000 | No |
| `lat` | number | Center latitude (with radius) | 39.0997 | No |
| `lng` | number | Center longitude (with radius) | -94.5786 | No |
| `date_from` | string | Start date (YYYY-MM-DD) | "2023-01-01" | No |
| `date_to` | string | End date (YYYY-MM-DD) | "2023-12-31" | No |
| `offense_category` | string | Offense category filter | "LARCENY" | No |
| `district` | string | Police district filter | "CENTRAL" | No |
| `limit` | integer | Maximum results (1-1000) | 100 | No |
| `offset` | integer | Results offset | 0 | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/crime?bbox=-94.6,39.0,-94.5,39.1&date_from=2023-01-01&limit=50"
```

#### Example Response

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": 1,
        "case_id": "2023-001234",
        "report_date": "2023-01-15",
        "report_time": "14:30:00",
        "offense_code": "2319",
        "offense_description": "LARCENY - THEFT FROM BUILDING",
        "offense_category": "LARCENY",
        "offense_type": "THEFT FROM BUILDING",
        "address": "123 MAIN ST",
        "city": "KANSAS CITY",
        "state": "MO",
        "zip_code": "64111",
        "district": "CENTRAL",
        "beat": "CENTRAL-1",
        "sector": "CENTRAL-A",
        "latitude": 39.0997,
        "longitude": -94.5786
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-94.5786, 39.0997]
      }
    }
  ],
  "total": 1500,
  "limit": 50,
  "offset": 0,
  "execution_time_ms": 45
}
```

### Get Crime Statistics

Retrieve aggregated crime statistics.

**Endpoint**: `GET /api/v1/crime/stats`

#### Query Parameters

Same as crime incidents endpoint, plus:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `group_by` | string | Group by field | "offense_category" |
| `aggregate` | string | Aggregation function | "count" |

#### Example Response

```json
{
  "total_incidents": 1500,
  "by_category": [
    {"category": "LARCENY", "count": 600},
    {"category": "ASSAULT", "count": 400},
    {"category": "BURGLARY", "count": 300}
  ],
  "by_district": [
    {"district": "CENTRAL", "count": 500},
    {"district": "NORTH", "count": 400},
    {"district": "SOUTH", "count": 600}
  ],
  "date_range": {
    "earliest": "2023-01-01",
    "latest": "2023-12-31"
  }
}
```

## 311 Service Requests API

### Get Service Requests

Retrieve 311 service request data.

**Endpoint**: `GET /api/v1/311`

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `bbox` | string | Bounding box (minx,miny,maxx,maxy) | "-94.6,39.0,-94.5,39.1" | No |
| `radius` | number | Search radius in meters | 1000 | No |
| `lat` | number | Center latitude (with radius) | 39.0997 | No |
| `lng` | number | Center longitude (with radius) | -94.5786 | No |
| `date_from` | string | Start date (YYYY-MM-DD) | "2023-01-01" | No |
| `date_to` | string | End date (YYYY-MM-DD) | "2023-12-31" | No |
| `request_type` | string | Request type filter | "Pothole Repair" | No |
| `status` | string | Status filter | "Open" | No |
| `department` | string | Department filter | "Public Works" | No |
| `limit` | integer | Maximum results (1-1000) | 100 | No |
| `offset` | integer | Results offset | 0 | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/311?status=Open&request_type=Pothole%20Repair&limit=25"
```

#### Example Response

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": 1,
        "request_id": "311-2023-001234",
        "request_type": "Pothole Repair",
        "request_category": "Street Maintenance",
        "request_subcategory": "Pothole",
        "status": "Open",
        "priority": "High",
        "department": "Public Works",
        "address": "123 MAIN ST",
        "city": "KANSAS CITY",
        "state": "MO",
        "zip_code": "64111",
        "latitude": 39.0997,
        "longitude": -94.5786,
        "created_date": "2023-01-15T10:30:00Z",
        "updated_date": "2023-01-16T14:20:00Z",
        "closed_date": null,
        "resolution_notes": null
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-94.5786, 39.0997]
      }
    }
  ],
  "total": 500,
  "limit": 25,
  "offset": 0,
  "execution_time_ms": 32
}
```

## Business Data API

### Get Business Licenses

Retrieve business license data.

**Endpoint**: `GET /api/v1/businesses`

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `bbox` | string | Bounding box (minx,miny,maxx,maxy) | "-94.6,39.0,-94.5,39.1" | No |
| `radius` | number | Search radius in meters | 1000 | No |
| `lat` | number | Center latitude (with radius) | 39.0997 | No |
| `lng` | number | Center longitude (with radius) | -94.5786 | No |
| `license_type` | string | License type filter | "Restaurant" | No |
| `status` | string | License status filter | "Active" | No |
| `search` | string | Search business name | "Starbucks" | No |
| `limit` | integer | Maximum results (1-1000) | 100 | No |
| `offset` | integer | Results offset | 0 | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/businesses?license_type=Restaurant&status=Active&limit=50"
```

## Food Inspections API

### Get Food Inspections

Retrieve food inspection data.

**Endpoint**: `GET /api/v1/inspections`

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `bbox` | string | Bounding box (minx,miny,maxx,maxy) | "-94.6,39.0,-94.5,39.1" | No |
| `radius` | number | Search radius in meters | 1000 | No |
| `lat` | number | Center latitude (with radius) | 39.0997 | No |
| `lng` | number | Center longitude (with radius) | -94.5786 | No |
| `date_from` | string | Start date (YYYY-MM-DD) | "2023-01-01" | No |
| `date_to` | string | End date (YYYY-MM-DD) | "2023-12-31" | No |
| `score_min` | integer | Minimum inspection score | 80 | No |
| `score_max` | integer | Maximum inspection score | 100 | No |
| `grade` | string | Letter grade filter | "A" | No |
| `search` | string | Search establishment name | "McDonald's" | No |
| `limit` | integer | Maximum results (1-1000) | 100 | No |
| `offset` | integer | Results offset | 0 | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/inspections?score_min=90&grade=A&limit=25"
```

## OSM Data API

### Get OSM Features

Retrieve OpenStreetMap data.

**Endpoint**: `GET /api/v1/osm/{layer}`

#### Path Parameters

| Parameter | Type | Description | Options |
|-----------|------|-------------|---------|
| `layer` | string | OSM layer type | `points`, `lines`, `multipolygons` |

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `bbox` | string | Bounding box (minx,miny,maxx,maxy) | "-94.6,39.0,-94.5,39.1" | No |
| `radius` | number | Search radius in meters | 1000 | No |
| `lat` | number | Center latitude (with radius) | 39.0997 | No |
| `lng` | number | Center longitude (with radius) | -94.5786 | No |
| `filter` | string | Feature type filter | "restaurant" | No |
| `limit` | integer | Maximum results (1-1000) | 100 | No |
| `offset` | integer | Results offset | 0 | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/osm/points?filter=restaurant&bbox=-94.6,39.0,-94.5,39.1"
```

## Settings API

### Update Consolidation Settings

Configure feature consolidation behavior with presets or custom parameters.

**Endpoint**: `PUT /api/settings/consolidation`

#### Request Body

```json
{
  "enabled": true,
  "strategy": "hybrid",
  "address_tolerance": 0.001,
  "coordinate_precision": 3,
  "min_records_to_consolidate": 3
}
```

#### Preset Values

| Preset | Address Tolerance | Coordinate Precision | Min Records | Description |
|--------|------------------|---------------------|-------------|-------------|
| `aggressive` | 0.001 | 3 | 3 | Moderate consolidation (~110m radius) |
| `balanced` | 0.0005 | 4 | 4 | Minimal consolidation (~55m radius) |
| `loose` | 0.0002 | 5 | 5 | Very minimal consolidation (~22m radius) |
| `custom` | User-defined | User-defined | User-defined | Custom parameters |

#### Example Request

```bash
curl -X PUT "http://localhost:5000/api/settings/consolidation" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "address_tolerance": 0.001, "coordinate_precision": 3, "min_records_to_consolidate": 3}'
```

#### Example Response

```json
{
  "message": "Consolidation settings updated successfully",
  "settings": {
    "enabled": true,
    "address_tolerance": 0.001,
    "coordinate_precision": 3,
    "min_records_to_consolidate": 3
  }
}
```

## Combined Data API

### Get Multi-Dataset Data

Retrieve data from multiple datasets in a single request.

**Endpoint**: `GET /api/v1/combined`

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `layers` | string | Comma-separated layer names | "crime,311,businesses" | Yes |
| `bbox` | string | Bounding box (minx,miny,maxx,maxy) | "-94.6,39.0,-94.5,39.1" | No |
| `radius` | number | Search radius in meters | 1000 | No |
| `lat` | number | Center latitude (with radius) | 39.0997 | No |
| `lng` | number | Center longitude (with radius) | -94.5786 | No |
| `date_from` | string | Start date (YYYY-MM-DD) | "2023-01-01" | No |
| `date_to` | string | End date (YYYY-MM-DD) | "2023-12-31" | No |
| `limit` | integer | Maximum results per layer (1-1000) | 100 | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/combined?layers=crime,311&bbox=-94.6,39.0,-94.5,39.1&date_from=2023-01-01"
```

#### Example Response

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "dataset": "crime",
        "id": 1,
        "case_id": "2023-001234",
        "offense_category": "LARCENY"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-94.5786, 39.0997]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "dataset": "311",
        "id": 1,
        "request_id": "311-2023-001234",
        "request_type": "Pothole Repair"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-94.5786, 39.0997]
      }
    }
  ],
  "total": 2000,
  "by_dataset": {
    "crime": 1000,
    "311": 1000
  },
  "limit": 100,
  "offset": 0,
  "execution_time_ms": 78
}
```

## Analysis API

### Get Proximity Analysis

Find features within specified distance of a point.

**Endpoint**: `GET /api/v1/analysis/proximity`

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `lat` | number | Center latitude | 39.0997 | Yes |
| `lng` | number | Center longitude | -94.5786 | Yes |
| `radius` | number | Search radius in meters | 1000 | Yes |
| `layers` | string | Comma-separated layer names | "crime,311" | Yes |
| `limit` | integer | Maximum results per layer | 100 | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/analysis/proximity?lat=39.0997&lng=-94.5786&radius=1000&layers=crime,311"
```

### Get Correlation Analysis

Analyze correlations between datasets.

**Endpoint**: `GET /api/v1/analysis/correlation`

#### Query Parameters

| Parameter | Type | Description | Example | Required |
|-----------|------|-------------|---------|----------|
| `dataset1` | string | First dataset | "crime" | Yes |
| `dataset2` | string | Second dataset | "311" | Yes |
| `field1` | string | Field from first dataset | "offense_category" | Yes |
| `field2` | string | Field from second dataset | "request_type" | Yes |
| `bbox` | string | Bounding box filter | "-94.6,39.0,-94.5,39.1" | No |
| `date_from` | string | Start date filter | "2023-01-01" | No |
| `date_to` | string | End date filter | "2023-12-31" | No |

#### Example Request

```bash
curl "https://kc-data-platform.example.com/api/v1/analysis/correlation?dataset1=crime&dataset2=311&field1=offense_category&field2=request_type"
```

#### Example Response

```json
{
  "correlation_type": "spatial",
  "dataset1": "crime",
  "dataset2": "311",
  "field1": "offense_category",
  "field2": "request_type",
  "correlation_score": 0.75,
  "sample_size": 1000,
  "analysis_details": {
    "method": "pearson_correlation",
    "confidence_interval": [0.70, 0.80],
    "p_value": 0.001
  },
  "correlation_matrix": [
    {
      "value1": "LARCENY",
      "value2": "Pothole Repair",
      "correlation": 0.65
    }
  ]
}
```

## Export API

### Export Data

Export filtered data in various formats.

**Endpoint**: `POST /api/v1/export`

#### Request Body

```json
{
  "layers": ["crime", "311"],
  "filters": {
    "bbox": [-94.6, 39.0, -94.5, 39.1],
    "date_from": "2023-01-01",
    "date_to": "2023-12-31"
  },
  "format": "csv",
  "fields": ["id", "name", "address", "latitude", "longitude"]
}
```

#### Response

```json
{
  "export_id": "exp_123456789",
  "status": "processing",
  "estimated_completion": "2023-01-15T10:35:00Z",
  "download_url": null
}
```

### Get Export Status

Check export status and download completed exports.

**Endpoint**: `GET /api/v1/export/{export_id}`

#### Example Response

```json
{
  "export_id": "exp_123456789",
  "status": "completed",
  "format": "csv",
  "file_size": 2048576,
  "record_count": 5000,
  "download_url": "https://kc-data-platform.example.com/downloads/exp_123456789.csv",
  "expires_at": "2023-01-22T10:30:00Z"
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_BBOX` | Invalid bounding box format | 400 |
| `INVALID_DATE` | Invalid date format | 400 |
| `INVALID_LIMIT` | Limit exceeds maximum | 400 |
| `INVALID_LAYER` | Unknown layer name | 400 |
| `GEOCODING_FAILED` | Address geocoding failed | 422 |
| `QUERY_TIMEOUT` | Query execution timeout | 504 |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | 429 |
| `INTERNAL_ERROR` | Internal server error | 500 |

## Rate Limiting

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

All list endpoints support pagination:

- `limit`: Number of results per page (1-1000, default 100)
- `offset`: Number of results to skip (default 0)

Pagination information in response:

```json
{
  "total": 1500,
  "limit": 100,
  "offset": 0,
  "has_next": true,
  "has_prev": false
}
```

## Spatial Queries

### Bounding Box Format

```
bbox=minx,miny,maxx,maxy
```

Example: `bbox=-94.6,39.0,-94.5,39.1`

### Radius Queries

Use `lat`, `lng`, and `radius` parameters:

```
lat=39.0997&lng=-94.5786&radius=1000
```

Radius is specified in meters.

## Temporal Queries

### Date Format

All dates use ISO 8601 format: `YYYY-MM-DD`

### Time Range

Use `date_from` and `date_to` parameters:

```
date_from=2023-01-01&date_to=2023-12-31
```

## Client Libraries

### Python Example

```python
import requests

# Get crime data
response = requests.get(
    'https://kc-data-platform.example.com/api/v1/crime',
    params={
        'bbox': '-94.6,39.0,-94.5,39.1',
        'date_from': '2023-01-01',
        'limit': 100
    }
)

data = response.json()
print(f"Found {data['total']} crime incidents")
```

### JavaScript Example

```javascript
// Get 311 service requests
async function getServiceRequests() {
    const response = await fetch(
        'https://kc-data-platform.example.com/api/v1/311?' +
        'status=Open&limit=50'
    );
    
    const data = await response.json();
    console.log(`Found ${data.total} service requests`);
    return data.features;
}
```

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:

```
https://kc-data-platform.example.com/api/docs
```

This specification can be used to generate client libraries in various programming languages.

## Support

For API support and questions:

- **Documentation**: https://kc-data-platform.example.com/docs
- **Issues**: https://github.com/kc-data-platform/issues
- **Email**: api-support@kc-data-platform.example.com

This API documentation provides comprehensive guidance for integrating with the Kansas City Data Platform API.
