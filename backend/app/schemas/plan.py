"""Energy plan and supplier schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
    rating: Decimal | None = None
    website: str | None = None
    customer_service_rating: Decimal | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("is_active", mode="before")
    @classmethod
    def default_is_active(cls, v: Any) -> bool:
        """Default is_active to True if None."""
        return True if v is None else v


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
    description: str | None = None
    rate_type: str
    rate_per_kwh: Decimal
    monthly_fee: Decimal = Decimal("0.00")
    contract_length_months: int = 12
    early_termination_fee: Decimal = Decimal("0.00")
    cancellation_fee: Decimal = Decimal("0.00")
    renewable_percentage: int = 0
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Include supplier info
    supplier: SupplierResponse | None = None

    @field_validator(
        "cancellation_fee", "monthly_fee", "early_termination_fee", mode="before"
    )
    @classmethod
    def default_decimal_fields(cls, v: Any) -> Decimal:
        """Default decimal fields to 0.00 if None."""
        return Decimal("0.00") if v is None else v

    @field_validator("contract_length_months", mode="before")
    @classmethod
    def default_contract_length(cls, v: Any) -> int:
        """Default contract_length_months to 12 if None."""
        return 12 if v is None else v

    @field_validator("renewable_percentage", mode="before")
    @classmethod
    def default_renewable_percentage(cls, v: Any) -> int:
        """Default renewable_percentage to 0 if None."""
        return 0 if v is None else v

    @field_validator("is_active", mode="before")
    @classmethod
    def default_is_active(cls, v: Any) -> bool:
        """Default is_active to True if None."""
        return True if v is None else v


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
