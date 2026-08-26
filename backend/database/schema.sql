-- DataCurate database schema.
-- SQLite stores information ABOUT the dataset files; the CSVs themselves
-- live on disk under backend/storage/raw and backend/storage/curated.

CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    curated_filename TEXT,
    format TEXT NOT NULL,
    rows INTEGER NOT NULL,
    columns INTEGER NOT NULL,
    quality_score REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    description TEXT,
    creator TEXT,
    source TEXT,
    version TEXT,
    curation_date TEXT,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);

CREATE TABLE IF NOT EXISTS quality_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    completeness REAL,
    uniqueness REAL,
    validity REAL,
    consistency REAL,
    overall_score REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);

CREATE TABLE IF NOT EXISTS curation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id INTEGER NOT NULL,
    operation TEXT NOT NULL,
    description TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);
