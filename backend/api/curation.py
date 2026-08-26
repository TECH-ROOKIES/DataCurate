"""POST /dataset/{id}/clean

Never overwrites the raw upload -- writes a separate curated CSV, per the
project's "never destroy the raw dataset" principle.
"""
from fastapi import APIRouter

from backend.database import database
from backend.services import provenance
from backend.services.cleaner import clean_dataset
from backend.utils.dataset_loader import get_dataset_or_404, load_dataframe
from backend.utils.errors import APIError
from backend.utils.file_utils import curated_path_for

router = APIRouter(tags=["curation"])


@router.post("/dataset/{dataset_id}/clean")
def clean(dataset_id: int):
    get_dataset_or_404(dataset_id)
    df = load_dataframe(dataset_id)

    try:
        cleaned_df, summary = clean_dataset(df)
    except Exception as exc:
        raise APIError("CURATION_FAILED", f"Cleaning failed: {exc}", status_code=500) from exc

    destination = curated_path_for(dataset_id)
    cleaned_df.to_csv(destination, index=False)

    rows, columns = cleaned_df.shape
    database.update_dataset_after_cleaning(dataset_id, destination.name, rows, columns)

    description = (
        f"{summary['duplicates_removed']} duplicate(s) removed, "
        f"{summary['whitespace_fixed']} whitespace value(s) fixed, "
        f"{summary['missing_values_normalized']} missing-value token(s) normalized, "
        f"{summary['standardized_fields']} field(s) standardized."
    )
    provenance.log_event(dataset_id, "CLEAN", description)

    return {"success": True, "curated_file": destination.name, **summary}
