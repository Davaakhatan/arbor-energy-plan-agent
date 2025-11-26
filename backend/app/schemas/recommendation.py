"""Recommendation schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.plan import EnergyPlanResponse
from app.schemas.preference import CustomerPreferenceCreate


class UsageAnalysisResponse(BaseModel):
    """Response schema for usage pattern analysis."""

    # Basic statistics
    total_annual_kwh: Decimal
    average_monthly_kwh: Decimal
    min_monthly_kwh: Decimal
    max_monthly_kwh: Decimal

    # Seasonal analysis
    seasonal_pattern: str = Field(
        description="summer_peak, winter_peak, dual_peak, flat, or unknown"
    )
    seasonal_variation_percent: Decimal
    peak_months: list[int] = Field(description="Months with highest usage (1-12)")
    low_months: list[int] = Field(description="Months with lowest usage (1-12)")

    # Trend analysis
    usage_trend: str = Field(description="increasing, decreasing, stable, or unknown")
    trend_percent_change: Decimal

    # Consumption insights
    consumption_tier: str = Field(description="low, medium, high, or very_high")
    is_high_consumer: bool

    # Data quality
    months_of_data: int
    data_quality_score: Decimal = Field(ge=0, le=1)

    # Plan suitability insights
    insights: dict[str, str] = Field(
        default_factory=dict,
        description="Personalized insights based on usage patterns",
    )


class RecommendationRequest(BaseModel):
    """Request schema for generating recommendations."""

    customer_id: UUID = Field(description="Customer ID to generate recommendations for")
    preferences: CustomerPreferenceCreate | None = Field(
        default=None,
        description="Optional preferences override for this request",
    )
    include_switching_analysis: bool = Field(
        default=True,
        description="Include switching cost analysis",
    )


class RiskFlag(BaseModel):
    """Risk flag for a recommendation."""

    code: str = Field(description="Risk code identifier")
    severity: str = Field(description="low, medium, or high")
    message: str = Field(description="Human-readable risk description")
    details: dict = Field(default_factory=dict)


class RecommendationResponse(BaseModel):
    """Schema for a single recommendation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rank: int = Field(ge=1, le=3, description="Recommendation rank (1-3)")
    plan: EnergyPlanResponse

    # Scores
    overall_score: Decimal = Field(description="Overall MCDA score (0-1)")
    cost_score: Decimal
    flexibility_score: Decimal
    renewable_score: Decimal
    rating_score: Decimal

    # Calculated values
    projected_annual_cost: Decimal
    projected_annual_savings: Decimal
    switching_cost: Decimal
    net_first_year_savings: Decimal = Field(
        description="Savings minus switching costs",
    )

    # Explanation
    explanation: str = Field(description="Plain language explanation")
    explanation_details: dict = Field(
        default_factory=dict,
        description="Structured explanation data",
    )

    # Risk assessment
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    confidence_level: str = Field(description="high, medium, or low")

    # Timestamps
    created_at: datetime
    expires_at: datetime | None


class FilteredPlanResponse(BaseModel):
    """Schema for a plan that was filtered out with explanation."""

    plan_id: UUID
    plan_name: str
    supplier_name: str | None
    filter_reason: str = Field(description="Why the plan was filtered out")
    filter_code: str = Field(
        description="Code: LOW_RENEWABLE, LONG_CONTRACT, VARIABLE_RATE, or LOW_SCORE"
    )
    details: dict = Field(default_factory=dict)


class RecommendationSetResponse(BaseModel):
    """Response containing top 3 recommendations."""

    customer_id: UUID
    recommendations: list[RecommendationResponse] = Field(
        max_length=3,
        description="Top 3 plan recommendations",
    )

    # Filtered plans with explanations
    filtered_plans: list[FilteredPlanResponse] = Field(
        default_factory=list,
        description="Plans that were filtered out with reasons",
    )

    # Usage analysis
    usage_analysis: UsageAnalysisResponse | None = Field(
        default=None,
        description="Analysis of customer usage patterns",
    )

    # Summary
    current_annual_cost: Decimal | None = Field(
        description="Current plan annual cost (if known)",
    )
    best_savings: Decimal = Field(
        description="Maximum potential annual savings",
    )

    # Metadata
    generated_at: datetime
    expires_at: datetime
    processing_time_ms: int = Field(
        description="Time to generate recommendations in milliseconds",
    )

    # Warnings
    warnings: list[str] = Field(
        default_factory=list,
        description="General warnings about the recommendations",
    )


class SwitchingAnalysis(BaseModel):
    """Analysis of switching from current plan to recommended plan."""

    current_plan_id: UUID | None
    recommended_plan_id: UUID
    days_until_contract_end: int | None
    early_termination_fee: Decimal
    estimated_switching_benefit: Decimal = Field(
        description="Net benefit after switching costs",
    )
    break_even_months: int | None = Field(
        description="Months until switching costs are recovered",
    )
    recommendation: str = Field(
        description="switch_now, wait_for_contract_end, or not_beneficial",
    )
    explanation: str
