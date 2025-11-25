"""Customer preference schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CustomerPreferenceCreate(BaseModel):
    """Schema for creating/updating customer preferences."""

    # Preference weights (should sum to 1.0)
    cost_savings_weight: Decimal = Field(
        default=Decimal("0.40"),
        ge=0,
        le=1,
        description="Weight for cost savings priority (0.0-1.0)",
    )
    flexibility_weight: Decimal = Field(
        default=Decimal("0.20"),
        ge=0,
        le=1,
        description="Weight for contract flexibility (0.0-1.0)",
    )
    renewable_weight: Decimal = Field(
        default=Decimal("0.20"),
        ge=0,
        le=1,
        description="Weight for renewable energy (0.0-1.0)",
    )
    supplier_rating_weight: Decimal = Field(
        default=Decimal("0.20"),
        ge=0,
        le=1,
        description="Weight for supplier rating (0.0-1.0)",
    )

    # Constraints
    min_renewable_percentage: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Minimum acceptable renewable energy percentage",
    )
    max_contract_months: int | None = Field(
        default=None,
        ge=1,
        le=60,
        description="Maximum acceptable contract length",
    )
    avoid_variable_rates: bool = Field(
        default=False,
        description="Avoid variable/indexed rate plans",
    )

    @model_validator(mode="after")
    def validate_weights_sum(self) -> "CustomerPreferenceCreate":
        """Ensure weights sum to approximately 1.0."""
        total = (
            self.cost_savings_weight
            + self.flexibility_weight
            + self.renewable_weight
            + self.supplier_rating_weight
        )
        if not (Decimal("0.99") <= total <= Decimal("1.01")):
            raise ValueError(
                f"Preference weights must sum to 1.0, got {total}. "
                "Adjust weights so they total 1.0."
            )
        return self


class CustomerPreferenceResponse(BaseModel):
    """Schema for customer preference response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    cost_savings_weight: Decimal
    flexibility_weight: Decimal
    renewable_weight: Decimal
    supplier_rating_weight: Decimal
    min_renewable_percentage: int
    max_contract_months: int | None
    avoid_variable_rates: bool
    created_at: datetime
    updated_at: datetime
