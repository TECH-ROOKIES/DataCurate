"""
Provenance / curation-history service.

Every meaningful backend operation (upload, profiling, quality analysis,
cleaning, validation, export) calls log_event() so a dataset's full history
can be reconstructed later -- this is the project's provenance trail.
"""
from datetime import datetime, timezone

from backend.database import database


def log_event(dataset_id: int, operation: str, description: str = "") -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    database.add_history_event(dataset_id, operation, description, timestamp)


def get_history(dataset_id: int) -> list:
    return database.get_history(dataset_id)
