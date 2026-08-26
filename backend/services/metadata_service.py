"""
Metadata service.

Builds the descriptive/administrative metadata record for a curated
dataset: what it is, who curated it, when, and its final quality score.
"""
from datetime import datetime, timezone


def build_metadata(
    dataset_name: str,
    file_format: str,
    rows: int,
    columns: int,
    quality_score: float = None,
    creator: str = None,
    description: str = None,
    source: str = None,
    version: str = "1.0",
) -> dict:
    return {
        "dataset_name": dataset_name,
        "description": description or "Curated dataset.",
        "format": file_format,
        "records": rows,
        "attributes": columns,
        "creator": creator or "Unknown",
        "source": source or "User-provided dataset",
        "version": version,
        "quality_score": quality_score,
        "curation_date": datetime.now(timezone.utc).isoformat(),
    }
