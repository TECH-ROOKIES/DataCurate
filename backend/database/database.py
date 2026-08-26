"""
SQLite access layer.

All SQL lives in this module. Services and API routes call these functions
instead of writing SQL directly, per the project's layering rule
(API routes coordinate, services hold logic, this module holds persistence).
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from backend.config import DATABASE_PATH, SCHEMA_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the database file and tables if they don't already exist."""
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    schema = Path(SCHEMA_PATH).read_text()
    conn = get_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


# --- datasets ---------------------------------------------------------

def create_dataset(name: str, filename: str, file_format: str, rows: int, columns: int) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO datasets (name, filename, format, rows, columns, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, filename, file_format, rows, columns, now, now),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_dataset(dataset_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_datasets() -> list:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM datasets ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_dataset_after_upload(dataset_id: int, filename: str, rows: int, columns: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE datasets SET filename = ?, rows = ?, columns = ?, updated_at = ? WHERE id = ?",
            (filename, rows, columns, now, dataset_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_dataset_after_cleaning(dataset_id: int, curated_filename: str, rows: int, columns: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE datasets
            SET curated_filename = ?, rows = ?, columns = ?, updated_at = ?
            WHERE id = ?
            """,
            (curated_filename, rows, columns, now, dataset_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_dataset_quality_score(dataset_id: int, score: float) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE datasets SET quality_score = ?, updated_at = ? WHERE id = ?",
            (score, now, dataset_id),
        )
        conn.commit()
    finally:
        conn.close()


# --- quality_results ---------------------------------------------------

def save_quality_result(dataset_id, completeness, uniqueness, validity, consistency, overall_score) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO quality_results
                (dataset_id, completeness, uniqueness, validity, consistency, overall_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (dataset_id, completeness, uniqueness, validity, consistency, overall_score, now),
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_quality_result(dataset_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM quality_results WHERE dataset_id = ? ORDER BY id DESC LIMIT 1",
            (dataset_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# --- metadata ------------------------------------------------------------

def save_metadata(dataset_id, description, creator, source, version, curation_date) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO metadata (dataset_id, description, creator, source, version, curation_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (dataset_id, description, creator, source, version, curation_date),
        )
        conn.commit()
    finally:
        conn.close()


def get_metadata(dataset_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM metadata WHERE dataset_id = ? ORDER BY id DESC LIMIT 1",
            (dataset_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# --- curation_history (provenance) ---------------------------------------

def add_history_event(dataset_id, operation, description, timestamp) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO curation_history (dataset_id, operation, description, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (dataset_id, operation, description, timestamp),
        )
        conn.commit()
    finally:
        conn.close()


def get_history(dataset_id: int) -> list:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM curation_history WHERE dataset_id = ? ORDER BY id ASC",
            (dataset_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
