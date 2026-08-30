"""
DataCurate API entry point.

Keeps route registration and app wiring here; all business logic lives in
backend/services, all persistence in backend/database. Run with:

    uvicorn backend.main:app --reload

from the DataCurate/ project root.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import curation, export, metadata, profiling, quality, upload, validation
from backend.config import CORS_ORIGINS
from backend.database.database import init_db
from backend.utils.errors import APIError, api_error_handler
from backend.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="DataCurate API",
    description="Dataset curation and data-quality assessment backend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.(vercel\.app|netlify\.app|github\.io)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(APIError, api_error_handler)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("DataCurate API started. Database initialized.")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(upload.router)
app.include_router(profiling.router)
app.include_router(quality.router)
app.include_router(curation.router)
app.include_router(validation.router)
app.include_router(metadata.router)
app.include_router(export.router)
