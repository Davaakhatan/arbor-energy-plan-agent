"""Pydantic schemas for request/response validation."""

from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUsageCreate,
    CustomerUsageResponse,
)
from app.schemas.plan import (
    EnergyPlanCreate,
    EnergyPlanResponse,
    SupplierCreate,
    SupplierResponse,
)
from app.schemas.preference import CustomerPreferenceCreate, CustomerPreferenceResponse
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationSetResponse,
)

__all__ = [
    "CustomerCreate",
    "CustomerResponse",
    "CustomerUsageCreate",
    "CustomerUsageResponse",
    "EnergyPlanCreate",
    "EnergyPlanResponse",
    "SupplierCreate",
    "SupplierResponse",
    "CustomerPreferenceCreate",
    "CustomerPreferenceResponse",
    "RecommendationRequest",
    "RecommendationResponse",
    "RecommendationSetResponse",
]
