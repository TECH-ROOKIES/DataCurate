"""File-handling helpers: safe server-side filenames, streamed saving with a
size cap, and extension checks. Uploaded files are never trusted by their
original name -- see raw_path_for()."""
from pathlib import Path

from fastapi import UploadFile

from backend.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES, RAW_DIR, CURATED_DIR


def has_allowed_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def raw_path_for(dataset_id: int) -> Path:
    return RAW_DIR / f"dataset_{dataset_id}.csv"


def curated_path_for(dataset_id: int) -> Path:
    return CURATED_DIR / f"dataset_{dataset_id}_curated.csv"


async def save_upload(file: UploadFile, destination: Path) -> int:
    """Stream the upload to disk in chunks, enforcing the size limit.
    Returns the number of bytes written."""
    size = 0
    with open(destination, "wb") as out_file:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_UPLOAD_SIZE_BYTES:
                out_file.close()
                destination.unlink(missing_ok=True)
                raise ValueError(
                    f"File exceeds the maximum upload size of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB."
                )
            out_file.write(chunk)
    return size
