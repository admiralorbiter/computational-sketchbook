# Development Standards - Kansas City Data Platform

## Overview

This document establishes coding standards, development practices, and workflow guidelines for the Kansas City Data Platform project to ensure code quality, maintainability, and team collaboration.

## Code Style Standards

### Python Code Style

#### PEP 8 Compliance
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: One import per line, grouped by standard library, third-party, local
- **Naming Conventions**:
  - Variables and functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

#### Code Formatting with Black
```bash
# Install Black
pip install black

# Format all Python files
black .

# Check formatting without changes
black --check .
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime, date
from pathlib import Path

# Third-party imports
import requests
from flask import Flask, jsonify
from sqlalchemy import Column, String, Integer
from geoalchemy2 import Geometry

# Local application imports
from models.base import BaseModel
from services.data_service import DataService
from utils.spatial import parse_bbox
```

#### Docstring Standards
```python
def get_crime_incidents(bbox=None, date_from=None, date_to=None, limit=100):
    """
    Retrieve crime incidents with optional filtering.
    
    Args:
        bbox (tuple, optional): Bounding box as (minx, miny, maxx, maxy)
        date_from (str, optional): Start date in YYYY-MM-DD format
        date_to (str, optional): End date in YYYY-MM-DD format
        limit (int, optional): Maximum number of records to return
        
    Returns:
        list: List of CrimeIncident objects
        
    Raises:
        ValueError: If bbox format is invalid
        DatabaseError: If database query fails
    """
    pass
```

### JavaScript Code Style

#### ESLint Configuration
```json
{
  "extends": ["eslint:recommended"],
  "env": {
    "browser": true,
    "es6": true
  },
  "rules": {
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "always"],
    "no-unused-vars": "error",
    "no-console": "warn"
  }
}
```

#### JavaScript Naming Conventions
```javascript
// Variables and functions: camelCase
const mapInstance = L.map('map');
function loadLayerData() {}

// Constants: UPPER_SNAKE_CASE
const MAX_FEATURES_PER_REQUEST = 5000;

// Classes: PascalCase
class LayerManager {}

// Private methods: _leadingUnderscore
function _createCustomMarker() {}
```

#### Module Organization
```javascript
// Use IIFE for modules
const KCDataPlatform = (function() {
    'use strict';
    
    // Private variables
    let map;
    let layers = {};
    
    // Public API
    return {
        init: init,
        addLayer: addLayer,
        removeLayer: removeLayer
    };
    
    // Private functions
    function init() {
        // Implementation
    }
    
    function addLayer(name, data) {
        // Implementation
    }
})();
```

### CSS Code Style

#### BEM Methodology
```css
/* Block */
.layer-controls {
    padding: 1rem;
}

/* Element */
.layer-controls__item {
    margin-bottom: 0.5rem;
}

/* Modifier */
.layer-controls__item--active {
    background-color: #007bff;
}

.layer-controls__item--disabled {
    opacity: 0.5;
}
```

#### CSS Organization
```css
/* 1. Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* 2. Layout */
.header {
    /* styles */
}

.sidebar {
    /* styles */
}

/* 3. Components */
.layer-control {
    /* styles */
}

.feature-panel {
    /* styles */
}

/* 4. Utilities */
.hidden {
    display: none;
}

.text-center {
    text-align: center;
}
```

## Git Workflow

### Branch Naming Convention
- **Feature branches**: `feature/description` (e.g., `feature/crime-api-endpoints`)
- **Bug fixes**: `bugfix/description` (e.g., `bugfix/geocoding-error`)
- **Hotfixes**: `hotfix/description` (e.g., `hotfix/security-patch`)
- **Documentation**: `docs/description` (e.g., `docs/api-documentation`)

### Commit Message Convention
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Commit Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples
```
feat(api): add crime incidents endpoint with spatial filtering

Add new /api/v1/crime endpoint that supports bounding box
and radius-based spatial filtering. Includes pagination and
basic attribute filtering.

Closes #123
```

```
fix(etl): resolve geocoding timeout issues

Increase timeout for geocoding service calls and add retry
logic with exponential backoff.

Fixes #456
```

### Pull Request Process

#### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

#### Review Guidelines
- **Code Review**: All PRs require at least one approval
- **Testing**: All tests must pass before merge
- **Documentation**: Update docs for new features
- **Breaking Changes**: Must be clearly documented

## Testing Standards

### Unit Testing

#### Python Testing with pytest
```python
# tests/test_models.py
import pytest
from datetime import date
from models.crime import CrimeIncident

class TestCrimeIncident:
    def test_crime_incident_creation(self):
        incident = CrimeIncident(
            case_id="TEST123",
            report_date=date(2023, 1, 1),
            offense_category="Theft",
            address="123 Main St"
        )
        assert incident.case_id == "TEST123"
        assert incident.offense_category == "Theft"
    
    def test_to_dict_method(self):
        incident = CrimeIncident(
            case_id="TEST123",
            report_date=date(2023, 1, 1)
        )
        data = incident.to_dict()
        assert data['case_id'] == "TEST123"
        assert 'report_date' in data
```

#### JavaScript Testing with Jest
```javascript
// tests/layer-manager.test.js
describe('LayerManager', () => {
    beforeEach(() => {
        // Setup
    });
    
    test('should create layer control', () => {
        const control = LayerManager.createLayerControl('crime', {
            name: 'Crime Incidents',
            color: '#e74c3c'
        });
        
        expect(control).toBeDefined();
        expect(control.className).toBe('layer-control');
    });
    
    test('should toggle layer visibility', () => {
        LayerManager.toggleLayer('crime');
        expect(layerConfigs.crime.visible).toBe(true);
    });
});
```

### Integration Testing

#### API Testing
```python
# tests/test_api.py
import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_crime_api_endpoint(client):
    response = client.get('/api/v1/crime?limit=10')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'features' in data
    assert 'total' in data
```

### Performance Testing

#### Load Testing with Locust
```python
# tests/load_test.py
from locust import HttpUser, task, between

class KCDataPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_crime_data(self):
        self.client.get('/api/v1/crime?limit=100')
    
    @task(1)
    def get_service_requests(self):
        self.client.get('/api/v1/311?limit=100')
    
    @task(1)
    def get_combined_data(self):
        self.client.get('/api/v1/combined?layers=crime,311')
```

## Error Handling Standards

### Python Error Handling
```python
import logging
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

def get_crime_data(case_id):
    """Get crime data with proper error handling"""
    try:
        incident = CrimeIncident.query.filter_by(case_id=case_id).first()
        if not incident:
            raise ValueError(f"Crime incident {case_id} not found")
        return incident
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving crime {case_id}: {e}")
        raise DatabaseError("Failed to retrieve crime data")
    except Exception as e:
        logger.error(f"Unexpected error retrieving crime {case_id}: {e}")
        raise
```

### JavaScript Error Handling
```javascript
async function loadLayerData(layerName) {
    try {
        const response = await fetch(`/api/v1/${layerName}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error loading ${layerName} data:`, error);
        showErrorMessage(`Failed to load ${layerName} data`);
        throw error;
    }
}
```

## Security Standards

### Input Validation
```python
from marshmallow import Schema, fields, validate

class CrimeQuerySchema(Schema):
    bbox = fields.Str(validate=validate.Regexp(r'^-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*$'))
    date_from = fields.Date()
    date_to = fields.Date()
    limit = fields.Int(validate=validate.Range(min=1, max=1000))
    offset = fields.Int(validate=validate.Range(min=0))

def validate_crime_query(data):
    schema = CrimeQuerySchema()
    return schema.load(data)
```

### SQL Injection Prevention
```python
# Use SQLAlchemy ORM (prevents SQL injection)
def get_crime_by_category(category):
    return CrimeIncident.query.filter_by(offense_category=category).all()

# If using raw SQL, use parameterized queries
def get_crime_raw(category):
    query = text("SELECT * FROM crime_incidents WHERE offense_category = :category")
    return db.session.execute(query, {"category": category}).fetchall()
```

### API Security
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@app.route('/api/v1/crime')
@limiter.limit("100 per minute")
def get_crime_incidents():
    # Endpoint implementation
    pass
```

## Documentation Standards

### Code Documentation
- **Functions**: Docstrings for all public functions
- **Classes**: Class-level docstrings explaining purpose
- **Modules**: Module-level docstrings with overview
- **Complex Logic**: Inline comments for non-obvious code

### API Documentation
- **OpenAPI/Swagger**: Complete API specification
- **Examples**: Request/response examples for all endpoints
- **Error Codes**: Documented error responses
- **Authentication**: Clear authentication requirements

### User Documentation
- **README**: Project overview and setup instructions
- **User Guide**: Step-by-step usage instructions
- **API Guide**: Developer integration guide
- **Troubleshooting**: Common issues and solutions

## Performance Standards

### Database Performance
- **Query Time**: <500ms for 95% of queries
- **Indexing**: Proper indexes on all query fields
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Use EXPLAIN to analyze slow queries

### API Performance
- **Response Time**: <1 second for 90% of requests
- **Caching**: Implement appropriate caching strategies
- **Pagination**: Limit result sets to prevent timeouts
- **Compression**: Enable gzip compression for responses

### Frontend Performance
- **Load Time**: <3 seconds for initial page load
- **Bundle Size**: Minimize JavaScript and CSS bundle sizes
- **Lazy Loading**: Load data on demand
- **Caching**: Browser caching for static assets

## Monitoring and Logging

### Logging Standards
```python
import logging
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

def log_api_request(endpoint, method, status_code, duration):
    logger.info(json.dumps({
        'event': 'api_request',
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'duration_ms': duration,
        'timestamp': datetime.utcnow().isoformat()
    }))
```

### Error Monitoring
- **Exception Tracking**: Log all unhandled exceptions
- **Performance Monitoring**: Track slow queries and requests
- **Health Checks**: Regular system health monitoring
- **Alerting**: Automated alerts for critical issues

## Deployment Standards

### Environment Configuration
```python
# config.py
import os

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # API Keys
    KC_OPEN_DATA_TOKEN = os.environ.get('KC_OPEN_DATA_TOKEN')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
```

### Docker Standards
```dockerfile
# Use specific version tags
FROM python:3.9-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Set working directory
WORKDIR /home/app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```

## Code Review Checklist

### Before Submitting PR
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Performance considerations addressed

### During Code Review
- [ ] Code is readable and maintainable
- [ ] Logic is correct and efficient
- [ ] Security considerations addressed
- [ ] Error handling is appropriate
- [ ] Tests cover new functionality
- [ ] Documentation is accurate

## Conclusion

These development standards ensure consistent, high-quality code across the Kansas City Data Platform project. Regular reviews and updates of these standards help maintain code quality as the project evolves.
