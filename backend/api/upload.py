"""POST /upload, GET /dataset/{id}, GET /datasets

Upload receives a CSV, stores it safely, reads it once to sanity-check it,
records it in SQLite, and returns the new dataset_id for every later step
to reference.
"""
import pandas as pd
from fastapi import APIRouter, File, UploadFile

from backend.database import database
from backend.services import provenance
from backend.utils.dataset_loader import get_dataset_or_404
from backend.utils.errors import APIError
from backend.utils.file_utils import has_allowed_extension, raw_path_for, save_upload
from backend.utils.logger import get_logger

router = APIRouter(tags=["upload"])
logger = get_logger(__name__)


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename:
        raise APIError("INVALID_FILE", "No file was provided.")

    if not has_allowed_extension(file.filename):
        raise APIError("INVALID_FILE", "Only CSV files are supported.")

    # Reserve a dataset row first so we have an id to name the stored file
    # after -- the on-disk filename is always server-generated, never the
    # user's original filename.
    dataset_id = database.create_dataset(
        name=file.filename, filename="", file_format="CSV", rows=0, columns=0
    )
    destination = raw_path_for(dataset_id)

    try:
        await save_upload(file, destination)
    except ValueError as exc:
        raise APIError("INVALID_FILE", str(exc)) from exc

    try:
        df = pd.read_csv(destination, dtype=str)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise APIError("INVALID_FILE", f"Could not parse CSV file: {exc}") from exc

    if df.shape[0] == 0 or df.shape[1] == 0:
        destination.unlink(missing_ok=True)
        raise APIError("EMPTY_FILE", "The uploaded CSV has no usable rows or columns.")

    rows, columns = df.shape
    database.update_dataset_after_upload(dataset_id, destination.name, rows, columns)

    provenance.log_event(
        dataset_id, "UPLOAD", f"Uploaded '{file.filename}' ({rows} rows, {columns} columns)."
    )
    logger.info("Dataset %s uploaded: %s", dataset_id, file.filename)

    return {
        "success": True,
        "dataset_id": dataset_id,
        "filename": file.filename,
        "rows": rows,
        "columns": columns,
    }


@router.get("/dataset/{dataset_id}")
def get_dataset(dataset_id: int):
    return get_dataset_or_404(dataset_id)


@router.get("/datasets")
def list_datasets():
    return {"datasets": database.list_datasets()}
