# DataCurate

DataCurate is a data curation and quality assessment application built to help users upload messy CSV datasets, inspect their structure, clean them, validate consistency, and export the results in a usable format.

It is designed for people who work with imperfect tabular data and need a practical workflow to identify problems, fix issues safely, and keep an audit trail of every action taken.

## What the app does

DataCurate helps users:

- Upload raw CSV files
- Inspect dataset shape, columns, missing values, and duplicates
- Profile each column for type, missing counts, unique values, and summary statistics
- Calculate a quality score across multiple dimensions
- Clean common dataset issues such as whitespace, missing-value tokens, duplicate rows, and basic standardization
- Validate data against rules such as required fields, numeric checks, email checks, and range rules
- Generate metadata and provenance history
- Download the curated CSV or metadata JSON

In short, the app turns a messy dataset into a cleaner, more trustworthy dataset with evidence of what changed.

## How it works

The system follows a simple curation workflow:

1. Upload a CSV file
2. Store the original file safely in the raw data area
3. Profile the dataset to understand structure and quality issues
4. Measure quality using a rule-based scoring engine
5. Clean the dataset without overwriting the original source file
6. Validate the cleaned data against expected rules
7. Save metadata and a curation history
8. Export the curated output for reuse

The backend never destroys the raw upload. Instead, it writes cleaned versions into a separate curated area, which keeps the original dataset intact and makes reprocessing possible.

## Technology stack

### Frontend
- HTML, CSS, JavaScript
- Static dashboard UI for upload, preview, quality summaries, actions, and export

### Backend
- Python
- FastAPI for API endpoints and request handling
- Pydantic for request validation and structured schemas
- Pandas for CSV processing, profiling, and data transformations

### Data and storage
- SQLite for dataset metadata, quality results, and curation history
- Local file storage for raw and curated CSV files

### Testing
- Pytest
- Automated checks for profiling, quality, cleaning, and validation logic

## Simplified system architecture

```text
+---------------------+
| User / Browser      |
| Upload CSV + view   |
| dashboard + actions |
+----------+----------+
           |
           v
+---------------------+
| Frontend UI         |
| HTML/CSS/JS         |
| (upload, preview,   |
| quality, export)    |
+----------+----------+
           |
           v
+---------------------+
| FastAPI Backend     |
| /upload             |
| /profile            |
| /quality            |
| /clean              |
| /validate           |
| /metadata           |
| /download           |
+----------+----------+
           |
           +----------+-------------------+
                      |
                      v
           +---------------------------+
           | Business Logic Services   |
           | - profiler                |
           | - quality_engine          |
           | - cleaner                |
           | - validator              |
           | - metadata_service        |
           | - provenance              |
           +-------------+-------------+
                         |
                         v
           +---------------------------+
           | Storage Layer             |
           | - SQLite database         |
           | - raw CSV files           |
           | - curated CSV files       |
           +---------------------------+
```

## Project structure

```text
DataCurate/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── upload.py
│   │   ├── profiling.py
│   │   ├── quality.py
│   │   ├── curation.py
│   │   ├── validation.py
│   │   ├── metadata.py
│   │   └── export.py
│   ├── services/
│   │   ├── profiler.py
│   │   ├── quality_engine.py
│   │   ├── cleaner.py
│   │   ├── validator.py
│   │   ├── metadata_service.py
│   │   └── provenance.py
│   ├── database/
│   │   ├── database.py
│   │   └── schema.sql
│   ├── models/
│   ├── utils/
│   ├── storage/
│   │   ├── raw/
│   │   └── curated/
│   └── tests/
├── frontend/
│   └── index.html
├── datasets/
│   └── student_raw.csv
├── conftest.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Key data quality features

The project evaluates data quality across four dimensions:

- Completeness
- Uniqueness
- Validity
- Consistency

These are combined into an overall score so users can see how healthy a dataset is before and after curation.

## Data handling approach

A few important design choices make the app reliable:

- CSV files are read as strings to avoid silent type coercion
- Duplicate rows are removed intentionally and transparently
- Missing-value tokens such as "na", "null", and "n/a" are normalized consistently
- Cleaning is explicit and conservative rather than guessing values
- Validation catches rule violations instead of silently altering data
- Provenance logs preserve a record of everything done to the dataset

## Local setup

```bash
cd DataCurate
python -m venv .venv
.venv\Scripts\activate    # On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run the backend

```bash
uvicorn backend.main:app --reload
```

Then open the API docs at:

- http://127.0.0.1:8000/docs

## Run tests

```bash
pytest backend/tests/ -v
```

## Example workflow

```bash
# Upload the sample dataset
curl -X POST -F "file=@datasets/student_raw.csv" http://127.0.0.1:8000/upload

# Get profile information
curl http://127.0.0.1:8000/dataset/1/profile

# Get quality score
curl http://127.0.0.1:8000/dataset/1/quality

# Clean the dataset
curl -X POST http://127.0.0.1:8000/dataset/1/clean

# Validate the dataset
curl -X POST http://127.0.0.1:8000/dataset/1/validate

# Download the curated CSV
curl http://127.0.0.1:8000/dataset/1/download -o curated.csv
```

## Deployment note

This project is best suited for a split deployment model:

- Frontend: static host such as Vercel, Netlify, or GitHub Pages
- Backend: Python hosting service such as Render, Railway, Fly.io, or a VPS

Because the backend handles file uploads, local data storage, and API processing, it cannot run as a pure static site on GitHub Pages alone.

## Summary

DataCurate is a practical data cleaning and quality inspection tool that helps users turn noisy CSV files into trustworthy, curated datasets with clear quality metrics, validation checks, and a traceable history of actions.

## Credits

Developed by:
- YaifabaSapamcha
- anjaliasem2026-git
