"""
Central configuration for the DataCurate backend.

Kept as plain constants (no python-dotenv) per the project's MVP scope --
if you outgrow this later, swap these for os.environ reads.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
RAW_DIR = STORAGE_DIR / "raw"
CURATED_DIR = STORAGE_DIR / "curated"

DATABASE_PATH = BASE_DIR / "database" / "datacurate.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

ALLOWED_EXTENSIONS = {".csv"}
MAX_UPLOAD_SIZE_MB = 25
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Frontend origins allowed during local development.
# Add your dev server's origin here if it isn't already listed.
CORS_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

for directory in (RAW_DIR, CURATED_DIR):
    directory.mkdir(parents=True, exist_ok=True)
