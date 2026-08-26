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
