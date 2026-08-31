"""POST/GET /dataset/{id}/metadata, GET /dataset/{id}/history"""
from fastapi import APIRouter

from backend.database import database
from backend.models.metadata import MetadataRequest
from backend.services import provenance
from backend.services.metadata_service import build_metadata
from backend.utils.dataset_loader import get_dataset_or_404
from backend.utils.errors import APIError

router = APIRouter(tags=["metadata"])


@router.post("/dataset/{dataset_id}/metadata")
def create_metadata(dataset_id: int, payload: MetadataRequest):
    dataset = get_dataset_or_404(dataset_id)

    metadata = build_metadata(
        dataset_name=dataset["name"],
        file_format=dataset["format"],
        rows=dataset["rows"],
        columns=dataset["columns"],
        quality_score=dataset.get("quality_score"),
        creator=payload.creator,
        description=payload.description,
        source=payload.source,
        version=payload.version,
    )

    database.save_metadata(
        dataset_id,
        metadata["description"],
        metadata["creator"],
        metadata["source"],
        metadata["version"],
        metadata["curation_date"],
    )
    provenance.log_event(dataset_id, "METADATA", "Metadata generated.")
    return metadata


@router.get("/dataset/{dataset_id}/metadata")
def get_metadata(dataset_id: int):
    dataset = get_dataset_or_404(dataset_id)
    metadata = database.get_metadata(dataset_id)
    
    # Auto-generate metadata if it doesn't exist yet
    if not metadata:
        auto_metadata = build_metadata(
            dataset_name=dataset["name"],
            file_format=dataset["format"],
            rows=dataset["rows"],
            columns=dataset["columns"],
            quality_score=dataset.get("quality_score", 0),
            creator="System",
            description="Auto-generated metadata",
            source="uploaded",
            version="1.0.0",
        )
        return auto_metadata
    
    return metadata


@router.get("/dataset/{dataset_id}/history")
def get_history(dataset_id: int):
    get_dataset_or_404(dataset_id)
    return {"history": provenance.get_history(dataset_id)}
