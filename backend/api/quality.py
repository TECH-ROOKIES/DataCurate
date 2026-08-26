"""GET /dataset/{id}/quality

Scores the curated file once cleaning has produced one, otherwise the raw
upload. This is what makes "quality before vs. after cleaning" show a real
difference when called again after POST /clean.
"""
from fastapi import APIRouter

from backend.database import database
from backend.services import provenance
from backend.services.quality_engine import calculate_quality
from backend.utils.dataset_loader import get_dataset_or_404, load_dataframe

router = APIRouter(tags=["quality"])


@router.get("/dataset/{dataset_id}/quality")
def get_quality(dataset_id: int):
    get_dataset_or_404(dataset_id)
    df = load_dataframe(dataset_id, prefer_curated=True)
    result = calculate_quality(df)

    database.save_quality_result(
        dataset_id,
        result["completeness"],
        result["uniqueness"],
        result["validity"],
        result["consistency"],
        result["overall"],
    )
    database.update_dataset_quality_score(dataset_id, result["overall"])
    provenance.log_event(dataset_id, "QUALITY_ANALYSIS", f"Overall quality score: {result['overall']}.")
    return result
