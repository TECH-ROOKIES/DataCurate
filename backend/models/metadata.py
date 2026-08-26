from typing import Optional

from pydantic import BaseModel


class MetadataRequest(BaseModel):
    creator: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    version: str = "1.0"


class MetadataResponse(BaseModel):
    dataset_name: str
    description: str
    format: str
    records: int
    attributes: int
    creator: str
    source: str
    version: str
    quality_score: Optional[float] = None
    curation_date: str
