"""GET /dataset/{id}/download

Returns the curated CSV if cleaning has run, otherwise the raw upload.
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse

from backend.services import provenance
from backend.utils.dataset_loader import get_dataset_or_404
from backend.utils.errors import APIError
from backend.utils.file_utils import curated_path_for, raw_path_for

router = APIRouter(tags=["export"])


@router.get("/dataset/{dataset_id}/download")
def download(dataset_id: int):
    dataset = get_dataset_or_404(dataset_id)

    path = curated_path_for(dataset_id) if dataset.get("curated_filename") else raw_path_for(dataset_id)

    if not path.exists():
        raise APIError("EXPORT_FAILED", "Dataset file not found on disk.", status_code=500)

    provenance.log_event(dataset_id, "EXPORT", f"Dataset exported as {path.name}.")

    return FileResponse(path=str(path), filename=path.name, media_type="text/csv")
