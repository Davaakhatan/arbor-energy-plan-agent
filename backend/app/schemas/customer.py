"""Customer and usage data schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerUsageCreate(BaseModel):
    """Schema for creating customer usage data."""

    usage_date: date = Field(..., description="First day of the usage month")
    kwh_usage: Decimal = Field(
        ...,
        ge=0,
        description="Energy usage in kilowatt-hours",
    )


class CustomerUsageResponse(BaseModel):
    """Schema for customer usage data response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usage_date: date
    kwh_usage: Decimal
    created_at: datetime


class CustomerCreate(BaseModel):
    """Schema for creating a customer."""

    external_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Anonymized external customer identifier",
    )
    current_plan_id: UUID | None = Field(
        default=None,
        description="Current energy plan ID",
    )
    contract_end_date: date | None = Field(
        default=None,
        description="Current contract end date",
    )
    early_termination_fee: Decimal | None = Field(
        default=None,
        ge=0,
        description="Early termination fee for current plan",
    )
    usage_data: list[CustomerUsageCreate] = Field(
        default_factory=list,
        description="12 months of usage data",
    )


class CustomerResponse(BaseModel):
    """Schema for customer response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    current_plan_id: UUID | None
    contract_end_date: date | None
    early_termination_fee: Decimal | None
    created_at: datetime
    updated_at: datetime
    usage_data: list[CustomerUsageResponse] = []


class CustomerWithUsageStats(BaseModel):
    """Customer with calculated usage statistics."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    total_annual_usage: Decimal = Field(
        description="Total kWh usage over 12 months",
    )
    average_monthly_usage: Decimal = Field(
        description="Average monthly kWh usage",
    )
    peak_month_usage: Decimal = Field(
        description="Highest monthly usage",
    )
    lowest_month_usage: Decimal = Field(
        description="Lowest monthly usage",
    )
    usage_variance: Decimal = Field(
        description="Variance in monthly usage (seasonality indicator)",
    )
