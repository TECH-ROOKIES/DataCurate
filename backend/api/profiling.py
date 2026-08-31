"""GET /dataset/{id}/profile

Profiles the curated file once cleaning has produced one, otherwise the
raw upload -- consistent with how /quality and /validate treat "the
current dataset".
"""
from fastapi import APIRouter

from backend.services import provenance
from backend.services.profiler import profile_dataset
from backend.utils.dataset_loader import get_dataset_or_404, load_dataframe

router = APIRouter(tags=["profiling"])


@router.get("/dataset/{dataset_id}/profile")
def get_profile(dataset_id: int):
    get_dataset_or_404(dataset_id)
    df = load_dataframe(dataset_id, prefer_curated=True)
    profile = profile_dataset(df)
    provenance.log_event(dataset_id, "PROFILE", "Dataset profiled.")
    return profile


@router.get("/dataset/{dataset_id}/preview")
def get_preview(dataset_id: int, limit: int = 10):
    """Get a preview of the dataset with first N rows."""
    get_dataset_or_404(dataset_id)
    df = load_dataframe(dataset_id, prefer_curated=True)
    
    # Get column names
    columns = df.columns.tolist()
    
    # Get first N rows, convert to list of dicts
    preview_df = df.head(limit)
    preview_rows = preview_df.to_dict(orient="records")
    
    # Add row index
    for idx, row in enumerate(preview_rows):
        row["row_index"] = idx + 1
    
    provenance.log_event(dataset_id, "PREVIEW", f"Dataset preview retrieved ({limit} rows).")
    
    return {
        "columns": columns,
        "preview": preview_rows,
        "total_rows": len(df),
        "preview_rows": len(preview_rows)
    }
