from typing import Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool = True
    dataset_id: int
    filename: str
    rows: int
    columns: int


class DatasetResponse(BaseModel):
    id: int
    name: str
    filename: str
    curated_filename: Optional[str] = None
    format: str
    rows: int
    columns: int
    quality_score: Optional[float] = None
    created_at: str
    updated_at: str
