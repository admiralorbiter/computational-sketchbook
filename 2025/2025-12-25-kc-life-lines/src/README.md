# KC: Life Lines — Data Pipeline

Data pipeline for **KC: Life Lines**, a data-driven life simulation game set in Kansas City.

## Quick Start

### Single Command to Run

```bash
python app.py
```

That's it! This runs the complete data pipeline.

### Setup (One Time)

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Prerequisites

- Python 3.9+

3. (Optional) Create a `.env` file for API keys:
   ```bash
   # Copy template (if .env.example exists, or create manually)
   # Add any required API keys
   CENSUS_API_KEY=your_key_here
   BLS_API_KEY=your_key_here
   ```

## Project Structure

```
life-sim/
├── requirements.txt          # Python dependencies
├── data_pipeline/            # Main Python package
│   ├── main.py              # Pipeline orchestrator (entry point)
│   ├── config.py            # Configuration management
│   ├── ingest/              # Data ingestion modules
│   │   ├── census.py        # ACS, TIGER/Line
│   │   ├── education.py     # MO DESE, KSDE, NCES, College Scorecard
│   │   ├── labor.py         # BLS, O*NET
│   │   ├── transit.py       # KCATA GTFS
│   │   ├── health.py        # CDC PLACES, SVI
│   │   ├── housing.py       # HUD LAI
│   │   └── local.py         # Open Data KC
│   ├── process/             # Data processing
│   │   ├── normalize.py     # Geography normalization
│   │   ├── join.py          # Data joining
│   │   └── indices.py       # Derived indices
│   ├── export/              # Data pack generation
│   │   ├── pack_builder.py
│   │   └── formats.py
│   └── utils/               # Utilities
│       ├── geo.py           # Geospatial helpers
│       └── data.py          # Data helpers
└── data/                    # Data directories (gitignored)
    ├── raw/                 # Raw downloaded data
    ├── processed/           # Intermediate processed data
    └── packs/               # Final data packs (versioned)
```

## Configuration

Configuration is managed in `data_pipeline/config.py`. Key settings:

- `DATA_YEAR`: Year of ACS data (default: 2023)
- `GEOGRAPHY_VINTAGE`: Census geography vintage (default: 2020)
- `KC_METRO_COUNTIES`: List of county FIPS codes for KC metro area
- `ACS_TYPE`: "1year" or "5year" estimates (default: "5year")

Override via environment variables in `.env` file or system environment.

## Pipeline Workflow

The pipeline runs in 5 stages:

1. **Ingest**: Download/load raw data from all sources
2. **Process**: Normalize geography, clean data
3. **Join**: Join datasets on stable IDs (GEOID, NCES ID, IPEDS ID)
4. **Indices**: Calculate derived indices (Opportunity Index, Transit Access Score, etc.)
5. **Export**: Generate versioned data packs for game runtime

## Development

The pipeline is structured modularly - each data source has its own module in `ingest/`, and you can implement them incrementally. Currently, modules are scaffolded with placeholder implementations - implement the actual data fetching logic as needed.

## License

See project license file.
