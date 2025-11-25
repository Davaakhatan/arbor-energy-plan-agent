"""Feedback schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""

    customer_id: UUID
    recommendation_id: UUID | None = None
    plan_id: UUID | None = None
    feedback_type: str = Field(
        default="recommendation_rating",
        description="Type: recommendation_rating, plan_selected, general_feedback",
    )
    rating: int | None = Field(default=None, ge=1, le=5, description="Rating from 1 to 5")
    was_helpful: bool | None = None
    switched_to_plan: bool | None = None
    comment: str | None = Field(default=None, max_length=2000)
    metadata: dict = Field(default_factory=dict)


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    customer_id: UUID
    recommendation_id: UUID | None = None
    plan_id: UUID | None = None
    feedback_type: str
    rating: int | None = None
    was_helpful: bool | None = None
    switched_to_plan: bool | None = None
    comment: str | None = None
    metadata: dict = Field(default_factory=dict, validation_alias="extra_data")
    created_at: datetime


class FeedbackStats(BaseModel):
    """Schema for feedback statistics."""

    total_feedback_count: int
    average_rating: float | None
    helpful_percentage: float | None
    switch_rate: float | None
    rating_distribution: dict[int, int] = Field(
        default_factory=dict,
        description="Distribution of ratings (1-5)",
    )
    feedback_by_type: dict[str, int] = Field(
        default_factory=dict,
        description="Count by feedback type",
    )


class FeedbackSummary(BaseModel):
    """Schema for feedback summary with recent items."""

    stats: FeedbackStats
    recent_feedback: list[FeedbackResponse] = Field(default_factory=list)
