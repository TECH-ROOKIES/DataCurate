"""Shared helper for API routes: fetch a dataset's DB record and load its
CSV from disk, preferring the curated version once cleaning has produced
one. Centralized here so every route reports DATASET_NOT_FOUND the same way
instead of routes each re-implementing the lookup."""
import pandas as pd

from backend.database import database
from backend.config import RAW_DIR, CURATED_DIR
from backend.utils.errors import APIError


def get_dataset_or_404(dataset_id: int) -> dict:
    dataset = database.get_dataset(dataset_id)
    if not dataset:
        raise APIError("DATASET_NOT_FOUND", f"No dataset with id {dataset_id}.", status_code=404)
    return dataset


def load_dataframe(dataset_id: int, prefer_curated: bool = False) -> pd.DataFrame:
    dataset = get_dataset_or_404(dataset_id)

    path = None
    if prefer_curated and dataset.get("curated_filename"):
        path = CURATED_DIR / dataset["curated_filename"]
    if path is None:
        path = RAW_DIR / dataset["filename"]

    if not path.exists():
        raise APIError(
            "INTERNAL_ERROR", f"Stored file for dataset {dataset_id} is missing on disk.", status_code=500
        )

    try:
        # dtype=str keeps every cell a plain string (or NaN). We do our own
        # type/format checking downstream instead of trusting pandas to
        # silently infer column types -- see the validator/quality_engine
        # modules for why.
        return pd.read_csv(path, dtype=str)
    except Exception as exc:
        raise APIError("INTERNAL_ERROR", f"Could not read stored dataset: {exc}", status_code=500) from exc
