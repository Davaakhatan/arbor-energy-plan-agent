"""Metrics and monitoring endpoints."""

import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import CacheService, get_redis
from app.models.customer import Customer
from app.models.plan import EnergyPlan, Supplier

router = APIRouter()

# Track application start time
APP_START_TIME = time.time()


class SystemMetrics(BaseModel):
    """System-level metrics."""

    uptime_seconds: float
    uptime_human: str
    started_at: str
    current_time: str


class DatabaseMetrics(BaseModel):
    """Database metrics."""

    status: str
    total_customers: int
    total_plans: int
    total_suppliers: int
    active_plans: int
    response_time_ms: float


class CacheMetrics(BaseModel):
    """Cache metrics."""

    status: str
    connected: bool
    response_time_ms: float
    keys_info: dict[str, Any] | None


class ApplicationMetrics(BaseModel):
    """Application-level metrics."""

    system: SystemMetrics
    database: DatabaseMetrics
    cache: CacheMetrics


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return " ".join(parts)


@router.get("", response_model=ApplicationMetrics)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
) -> ApplicationMetrics:
    """Get comprehensive application metrics for monitoring."""
    current_time = datetime.now(timezone.utc)
    uptime = time.time() - APP_START_TIME

    # System metrics
    system = SystemMetrics(
        uptime_seconds=uptime,
        uptime_human=format_uptime(uptime),
        started_at=datetime.fromtimestamp(APP_START_TIME, tz=timezone.utc).isoformat(),
        current_time=current_time.isoformat(),
    )

    # Database metrics
    db_start = time.perf_counter()
    try:
        # Get counts
        customers_count = await db.scalar(select(func.count(Customer.id)))
        plans_count = await db.scalar(select(func.count(EnergyPlan.id)))
        active_plans_count = await db.scalar(
            select(func.count(EnergyPlan.id)).where(EnergyPlan.is_active.is_(True))
        )
        suppliers_count = await db.scalar(select(func.count(Supplier.id)))

        db_response_time = (time.perf_counter() - db_start) * 1000

        database = DatabaseMetrics(
            status="healthy",
            total_customers=customers_count or 0,
            total_plans=plans_count or 0,
            total_suppliers=suppliers_count or 0,
            active_plans=active_plans_count or 0,
            response_time_ms=round(db_response_time, 2),
        )
    except Exception as e:
        database = DatabaseMetrics(
            status=f"error: {str(e)[:50]}",
            total_customers=0,
            total_plans=0,
            total_suppliers=0,
            active_plans=0,
            response_time_ms=-1,
        )

    # Cache metrics
    cache_start = time.perf_counter()
    try:
        redis = await get_redis()
        await redis.ping()
        cache_response_time = (time.perf_counter() - cache_start) * 1000

        # Get cache info
        info = await redis.info("keyspace")
        keys_info = {}
        if info:
            for key, value in info.items():
                if key.startswith("db"):
                    keys_info[key] = value

        cache = CacheMetrics(
            status="healthy",
            connected=True,
            response_time_ms=round(cache_response_time, 2),
            keys_info=keys_info if keys_info else None,
        )
    except Exception as e:
        cache = CacheMetrics(
            status=f"error: {str(e)[:50]}",
            connected=False,
            response_time_ms=-1,
            keys_info=None,
        )

    return ApplicationMetrics(
        system=system,
        database=database,
        cache=cache,
    )


class ReadinessResponse(BaseModel):
    """Readiness probe response."""

    ready: bool
    checks: dict[str, bool]


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> ReadinessResponse:
    """Kubernetes-style readiness probe."""
    checks = {}

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        checks["cache"] = True
    except Exception:
        checks["cache"] = False

    ready = all(checks.values())

    return ReadinessResponse(ready=ready, checks=checks)


class LivenessResponse(BaseModel):
    """Liveness probe response."""

    alive: bool
    uptime_seconds: float


@router.get("/live", response_model=LivenessResponse)
async def liveness_check() -> LivenessResponse:
    """Kubernetes-style liveness probe."""
    return LivenessResponse(
        alive=True,
        uptime_seconds=time.time() - APP_START_TIME,
    )
