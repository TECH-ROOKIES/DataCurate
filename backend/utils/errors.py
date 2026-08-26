"""
Shared API error type and a FastAPI exception handler that produces one
consistent error envelope across every route:

{
    "success": false,
    "error": {"code": "...", "message": "..."}
}
"""
from fastapi import Request
from fastapi.responses import JSONResponse

VALID_CODES = {
    "INVALID_FILE",
    "EMPTY_FILE",
    "INVALID_DATASET",
    "DATASET_NOT_FOUND",
    "CURATION_FAILED",
    "VALIDATION_FAILED",
    "EXPORT_FAILED",
    "INTERNAL_ERROR",
}


class APIError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )
