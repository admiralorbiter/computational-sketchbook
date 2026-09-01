# Data Sources - Kansas City Data Platform

## Overview

This document catalogs all data sources integrated into the Kansas City Data Platform, including API endpoints, update frequencies, data quality assessments, and integration strategies.

## Kansas City Open Data Portal

### Base URL
- **Portal**: https://data.kcmo.org/
- **API Base**: https://data.kcmo.org/resource/
- **Documentation**: https://data.kcmo.org/api/docs

### Authentication
- **Method**: App Token (recommended for production)
- **Rate Limit**: 1000 requests per hour per token
- **Registration**: https://data.kcmo.org/profile/app_tokens

## Priority 1 Datasets (Phase 1)

### 1. Crime Data

#### API Information
- **Endpoint**: `https://data.kcmo.org/resource/4i7q-w5kf.json`
- **Format**: JSON
- **Update Frequency**: Daily (typically 24-48 hour delay)
- **Volume**: ~100,000 records per year
- **Historical Data**: Available from 2015

#### Data Quality
- **Geocoding**: Latitude/longitude provided for ~95% of records
- **Address Quality**: High - standardized addresses
- **Completeness**: 
  - Case ID: 100%
  - Date/Time: 100%
  - Location: 95%
  - Offense Details: 90%
  - District/Beat: 85%

#### Key Fields
```json
{
  "report_no": "string",
  "report_date": "date",
  "report_time": "time",
  "offense_code": "string",
  "offense_description": "string",
  "offense_category": "string",
  "offense_type": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "district": "string",
  "beat": "string",
  "sector": "string",
  "latitude": "number",
  "longitude": "number"
}
```

#### Data Issues
- **Missing Coordinates**: ~5% of records need geocoding
- **Address Variations**: Some addresses have inconsistent formatting
- **Duplicate Records**: Occasional duplicate case numbers
- **Data Lag**: 1-2 day delay in data availability

### 2. 311 Service Requests

#### API Information
- **Endpoint**: `https://data.kcmo.org/resource/7at3-sxhp.json`
- **Format**: JSON
- **Update Frequency**: Real-time (hourly sync recommended)
- **Volume**: ~300,000 requests per year
- **Historical Data**: Available from 2018

#### Data Quality
- **Geocoding**: Address field provided, needs geocoding
- **Address Quality**: Medium - some addresses incomplete
- **Completeness**:
  - Request ID: 100%
  - Request Type: 100%
  - Status: 100%
  - Created Date: 100%
  - Address: 85%
  - Department: 90%

#### Key Fields
```json
{
  "service_request_id": "string",
  "request_type": "string",
  "request_category": "string",
  "request_subcategory": "string",
  "status": "string",
  "priority": "string",
  "department": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "latitude": "number",
  "longitude": "number",
  "created_date": "datetime",
  "updated_date": "datetime",
  "closed_date": "datetime",
  "resolution_notes": "string"
}
```

#### Data Issues
- **Geocoding Required**: All addresses need geocoding
- **Address Quality**: Some addresses incomplete or invalid
- **Status Updates**: Status changes not always reflected immediately
- **Department Assignment**: Some requests have unclear department assignment

## Priority 2 Datasets (Phase 2)

### 3. Business Licenses

#### API Information
- **Endpoint**: `https://data.kcmo.org/resource/c2zr-wqjd.json`
- **Format**: JSON
- **Update Frequency**: Weekly
- **Volume**: ~50,000 active licenses
- **Historical Data**: Available from 2010

#### Data Quality
- **Geocoding**: Address field provided, needs geocoding
- **Address Quality**: High - business addresses typically complete
- **Completeness**:
  - License Number: 100%
  - Business Name: 100%
  - License Type: 100%
  - Status: 100%
  - Address: 95%
  - Issue/Expiry Dates: 90%

#### Key Fields
```json
{
  "license_number": "string",
  "business_name": "string",
  "dba_name": "string",
  "license_type": "string",
  "license_category": "string",
  "status": "string",
  "issue_date": "date",
  "expiry_date": "date",
  "address": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "phone": "string",
  "email": "string",
  "website": "string"
}
```

#### Data Issues
- **Geocoding Required**: All addresses need geocoding
- **Status Updates**: License status changes may be delayed
- **Contact Information**: Phone/email often missing
- **License Renewals**: Expired licenses not always removed

### 4. Food Inspections

#### API Information
- **Endpoint**: `https://data.kcmo.org/resource/xy4e-d4qt.json`
- **Format**: JSON
- **Update Frequency**: Daily
- **Volume**: ~20,000 inspections per year
- **Historical Data**: Available from 2015

#### Data Quality
- **Geocoding**: Address field provided, needs geocoding
- **Address Quality**: High - establishment addresses complete
- **Completeness**:
  - Inspection ID: 100%
  - Establishment Name: 100%
  - Inspection Date: 100%
  - Score: 95%
  - Address: 90%
  - Violations: 85%

#### Key Fields
```json
{
  "inspection_id": "string",
  "establishment_name": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "latitude": "number",
  "longitude": "number",
  "inspection_date": "date",
  "inspection_type": "string",
  "score": "number",
  "grade": "string",
  "violations": "string",
  "critical_violations": "number",
  "non_critical_violations": "number",
  "inspector_name": "string"
}
```

#### Data Issues
- **Geocoding Required**: Most addresses need geocoding
- **Violation Details**: Violation descriptions in free text
- **Score Variations**: Different scoring systems over time
- **Establishment Matching**: Difficult to match with business licenses

## Priority 3 Datasets (Future)

### 5. Economic Indicators

#### API Information
- **Endpoint**: `https://data.kcmo.org/resource/economic-indicators.json`
- **Format**: JSON
- **Update Frequency**: Quarterly
- **Volume**: ~500 records per year
- **Historical Data**: Available from 2010

#### Data Quality
- **Geocoding**: Census tract based, no geocoding needed
- **Data Quality**: High - official government statistics
- **Completeness**: 95%+

#### Key Fields
```json
{
  "census_tract": "string",
  "metric_type": "string",
  "metric_name": "string",
  "value": "number",
  "unit": "string",
  "date_period": "string",
  "year": "number",
  "quarter": "number",
  "source": "string"
}
```

### 6. Property Data

#### API Information
- **Endpoint**: `https://data.kcmo.org/resource/property-data.json`
- **Format**: JSON
- **Update Frequency**: Monthly
- **Volume**: ~200,000 properties
- **Historical Data**: Available from 2015

#### Data Quality
- **Geocoding**: Parcel-based, coordinates available
- **Data Quality**: High - official property records
- **Completeness**: 90%+

### 7. Transportation Data

#### API Information
- **Endpoint**: `https://data.kcmo.org/resource/transportation.json`
- **Format**: JSON
- **Update Frequency**: Real-time
- **Volume**: Variable
- **Historical Data**: Limited

## Data Integration Strategy

### ETL Pipeline Design

#### 1. Data Ingestion
```python
# Example ETL workflow
def ingest_crime_data():
    # 1. Fetch data from API
    data = fetch_from_api('crime')
    
    # 2. Validate data
    validated_data = validate_crime_data(data)
    
    # 3. Geocode addresses
    geocoded_data = geocode_addresses(validated_data)
    
    # 4. Store in database
    store_crime_data(geocoded_data)
    
    # 5. Update sync log
    update_sync_log('crime', 'completed')
```

#### 2. Data Validation
- **Schema Validation**: Ensure required fields present
- **Data Type Validation**: Convert strings to appropriate types
- **Range Validation**: Check numeric values within expected ranges
- **Format Validation**: Validate dates, phone numbers, etc.

#### 3. Geocoding Strategy
- **Primary**: US Census Geocoder API (free, reliable)
- **Fallback**: Google Maps Geocoding API (paid, high accuracy)
- **Caching**: Store geocoded results to avoid re-processing
- **Quality Scoring**: Rate geocoding confidence

#### 4. Error Handling
- **Retry Logic**: Exponential backoff for API failures
- **Dead Letter Queue**: Store failed records for manual review
- **Monitoring**: Alert on high error rates
- **Logging**: Detailed logs for debugging

### Data Quality Monitoring

#### Quality Metrics
- **Completeness**: Percentage of non-null values
- **Accuracy**: Validation against known good data
- **Consistency**: Cross-field validation
- **Timeliness**: Data freshness monitoring

#### Quality Dashboard
- **Real-time Metrics**: Current data quality scores
- **Trend Analysis**: Quality trends over time
- **Issue Alerts**: Notifications for quality problems
- **Data Lineage**: Track data transformations

### Update Strategies

#### Incremental Updates
- **Crime Data**: Daily full refresh (small dataset)
- **311 Requests**: Hourly incremental (new/updated records)
- **Business Licenses**: Weekly incremental
- **Food Inspections**: Daily incremental

#### Full Refresh
- **When**: Major schema changes or data corruption
- **Frequency**: Monthly for large datasets
- **Process**: Backup current data, full reload, validate

### Data Storage

#### Database Organization
- **Raw Data**: Store original API responses
- **Processed Data**: Cleaned and geocoded data
- **Derived Data**: Calculated fields and aggregations
- **Metadata**: Data source information and quality scores

#### Backup Strategy
- **Frequency**: Daily automated backups
- **Retention**: 30 days of backups
- **Location**: Separate storage location
- **Testing**: Monthly restore tests

## API Integration Details

### SODA API Client

#### Authentication
```python
class SODAClient:
    def __init__(self, app_token=None):
        self.base_url = "https://data.kcmo.org/resource/"
        self.app_token = app_token
        self.session = requests.Session()
        
    def get_data(self, dataset, **params):
        url = f"{self.base_url}{dataset}.json"
        if self.app_token:
            params['$$app_token'] = self.app_token
        return self.session.get(url, params=params)
```

#### Rate Limiting
- **Implementation**: Exponential backoff with jitter
- **Monitoring**: Track request rates and failures
- **Caching**: Cache responses to reduce API calls

#### Error Handling
- **HTTP Errors**: Retry with backoff
- **Data Errors**: Log and skip invalid records
- **Network Errors**: Retry with exponential backoff
- **Rate Limits**: Wait and retry

### Data Transformation

#### Common Transformations
- **Date Parsing**: Convert string dates to datetime objects
- **Coordinate Conversion**: Ensure consistent coordinate format
- **Address Normalization**: Standardize address formats
- **Text Cleaning**: Remove special characters, normalize case

#### Geocoding Pipeline
```python
def geocode_address(address):
    # Try Census geocoder first
    result = census_geocoder.geocode(address)
    if result.confidence > 0.8:
        return result
    
    # Fallback to Google
    result = google_geocoder.geocode(address)
    if result.confidence > 0.9:
        return result
    
    # Manual review needed
    return None
```

## Monitoring and Alerting

### Key Metrics
- **Data Freshness**: Time since last successful update
- **Data Quality**: Completeness and accuracy scores
- **API Performance**: Response times and error rates
- **Geocoding Success**: Percentage of successful geocoding

### Alerts
- **Data Stale**: Alert if data >24 hours old
- **Quality Degraded**: Alert if quality score drops
- **API Errors**: Alert on high error rates
- **Geocoding Failures**: Alert on low geocoding success

### Dashboards
- **Data Health**: Overall system health metrics
- **Update Status**: Status of all data sources
- **Quality Trends**: Data quality over time
- **Performance**: API and processing performance

### 8. LEHD Origin-Destination Employment Statistics (LODES)

#### API Information
- **Endpoint**: https://lehd.ces.census.gov/data/lodes/LODES8/
- **Format**: CSV.gz files
- **Update Frequency**: Annually (2+ year lag)
- **Volume**: ~150K census blocks × multiple segments
- **Historical Data**: Available from 2002

#### Data Quality
- **Geocoding**: Census block-level (15-digit GEOID)
- **Data Quality**: High - official Census Bureau statistics
- **Completeness**: 95%+ (some blocks suppressed for privacy)

#### Key Fields
```json
{
  "w_geocode": "15-digit GEOID of workplace",
  "h_geocode": "15-digit GEOID of residence",
  "C000": "Total jobs",
  "CA01-CA03": "Jobs by age groups",
  "CE01-CE03": "Jobs by earnings",
  "CNS01-CNS20": "Jobs by NAICS industry",
  "S000": "Total jobs in OD flow"
}
```

#### Data Structure
- **WAC**: Workplace area characteristics (where jobs are located)
- **RAC**: Residence area characteristics (where workers live)
- **OD**: Origin-destination flows (commute patterns)

#### Integration Benefits
- Employment center identification
- Workforce catchment area analysis
- Commute pattern visualization
- Jobs-housing balance assessment
- Education-to-employment pipeline analysis

#### Data Issues
- Two-year data lag (latest: 2021)
- Privacy suppression for small counts (<10 jobs)
- Large file sizes require efficient processing
- Complex join operations needed for flow analysis

## Future Enhancements

### Additional Data Sources
- **Real-time Traffic**: Traffic flow and incident data
- **Weather Data**: Weather conditions and forecasts
- **Social Media**: Social media mentions and sentiment
- **Satellite Imagery**: Aerial and satellite imagery

### Advanced Integration
- **Streaming Data**: Real-time data processing
- **Machine Learning**: Predictive analytics and anomaly detection
- **External APIs**: Integration with third-party services
- **Data Marketplace**: Share data with other organizations

This comprehensive data source integration strategy ensures reliable, high-quality data for the Kansas City Data Platform while maintaining simplicity and performance.
