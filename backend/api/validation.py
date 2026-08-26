"""POST /dataset/{id}/validate

Validates the curated file if cleaning has already run, otherwise falls
back to the raw upload. An optional JSON body can override which columns
are checked; if omitted, columns are auto-detected.
"""
from typing import Optional

from fastapi import APIRouter, Body

from backend.models.quality import ValidationConfig
from backend.services import provenance
from backend.services.validator import run_validation
from backend.utils.dataset_loader import get_dataset_or_404, load_dataframe

router = APIRouter(tags=["validation"])


@router.post("/dataset/{dataset_id}/validate")
def validate(dataset_id: int, config: Optional[ValidationConfig] = Body(default=None)):
    get_dataset_or_404(dataset_id)
    df = load_dataframe(dataset_id, prefer_curated=True)

    config_dict = config.dict(exclude_none=True) if config else None
    result = run_validation(df, config_dict)

    provenance.log_event(
        dataset_id,
        "VALIDATE",
        f"{result['passed']} passed, {result['warnings']} warning(s), {result['errors']} error(s).",
    )
    return result
