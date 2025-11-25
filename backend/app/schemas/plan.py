"""Energy plan and supplier schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.plan import RateType


class SupplierCreate(BaseModel):
    """Schema for creating a supplier."""

    name: str = Field(..., min_length=1, max_length=255)
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    website: str | None = Field(default=None, max_length=500)
    customer_service_rating: Decimal | None = Field(default=None, ge=0, le=5)


class SupplierResponse(BaseModel):
    """Schema for supplier response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    rating: Decimal | None
    website: str | None
    customer_service_rating: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EnergyPlanCreate(BaseModel):
    """Schema for creating an energy plan."""

    supplier_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None

    # Rate structure
    rate_type: RateType = RateType.FIXED
    rate_per_kwh: Decimal = Field(..., ge=0, description="Rate in dollars per kWh")
    monthly_fee: Decimal = Field(default=Decimal("0.00"), ge=0)

    # Contract terms
    contract_length_months: int = Field(default=12, ge=1, le=60)
    early_termination_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    cancellation_fee: Decimal = Field(default=Decimal("0.00"), ge=0)

    # Green energy
    renewable_percentage: int = Field(default=0, ge=0, le=100)


class EnergyPlanResponse(BaseModel):
    """Schema for energy plan response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    supplier_id: UUID
    name: str
    description: str | None
    rate_type: str
    rate_per_kwh: Decimal
    monthly_fee: Decimal
    contract_length_months: int
    early_termination_fee: Decimal
    cancellation_fee: Decimal
    renewable_percentage: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Include supplier info
    supplier: SupplierResponse | None = None


class EnergyPlanWithCost(EnergyPlanResponse):
    """Energy plan with calculated costs for a specific customer."""

    projected_annual_cost: Decimal = Field(
        description="Projected annual cost based on customer usage",
    )
    projected_monthly_cost: Decimal = Field(
        description="Average projected monthly cost",
    )
    cost_breakdown: dict = Field(
        default_factory=dict,
        description="Detailed cost breakdown",
    )
