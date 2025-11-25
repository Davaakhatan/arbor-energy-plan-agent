"""Health check endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    version: str
    environment: str
    database: str
    cache: str


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
) -> DetailedHealthResponse:
    """Detailed health check including database and cache status."""
    # Check database
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Check Redis
    cache_status = "healthy"
    try:
        redis = await get_redis()
        await redis.ping()
    except Exception:
        cache_status = "unhealthy"

    overall_status = (
        "healthy" if db_status == "healthy" and cache_status == "healthy" else "degraded"
    )

    return DetailedHealthResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.environment,
        database=db_status,
        cache=cache_status,
    )
