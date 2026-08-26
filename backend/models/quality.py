from typing import Dict, List, Optional

from pydantic import BaseModel


class ValidationConfig(BaseModel):
    """Optional, user-supplied rule configuration for POST /validate.

    Example body:
    {
        "required": ["name", "email"],
        "numeric": ["age"],
        "range": {"age": [0, 120]},
        "email": ["email"]
    }

    If omitted entirely, columns are auto-classified instead
    (see services/validator.py::auto_detect_config).
    """
    required: Optional[List[str]] = None
    numeric: Optional[List[str]] = None
    email: Optional[List[str]] = None
    range: Optional[Dict[str, List[float]]] = None


class QualityResponse(BaseModel):
    completeness: float
    uniqueness: float
    validity: float
    consistency: float
    overall: float
