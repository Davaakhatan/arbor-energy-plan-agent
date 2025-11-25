"""API v1 router aggregating all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, customers, health, ingestion, metrics, plans, preferences, recommendations

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

# Health check endpoints
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
)

# Customer endpoints
api_router.include_router(
    customers.router,
    prefix="/customers",
    tags=["customers"],
)

# Plan endpoints
api_router.include_router(
    plans.router,
    prefix="/plans",
    tags=["plans"],
)

# Preference endpoints
api_router.include_router(
    preferences.router,
    prefix="/preferences",
    tags=["preferences"],
)

# Recommendation endpoints
api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"],
)

# Data ingestion endpoints
api_router.include_router(
    ingestion.router,
    prefix="/ingest",
    tags=["ingestion"],
)

# Metrics and monitoring endpoints
api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["monitoring"],
)
