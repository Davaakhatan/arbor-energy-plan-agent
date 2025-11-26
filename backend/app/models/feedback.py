"""Feedback model for collecting user feedback on recommendations."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, JSONType


class FeedbackType(str, Enum):
    """Types of feedback."""

    RECOMMENDATION_RATING = "recommendation_rating"
    PLAN_SELECTED = "plan_selected"
    GENERAL_FEEDBACK = "general_feedback"


class Feedback(Base):
    """Stores user feedback on recommendations."""

    __tablename__ = "feedback"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    customer_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        index=True,
    )
    recommendation_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    plan_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("energy_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Feedback type
    feedback_type: Mapped[str] = mapped_column(
        String(50),
        default=FeedbackType.RECOMMENDATION_RATING.value,
        comment="Type of feedback: recommendation_rating, plan_selected, general_feedback",
    )

    # Rating (1-5 stars)
    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Rating from 1 to 5",
    )

    # Was the recommendation helpful?
    was_helpful: Mapped[bool | None] = mapped_column(
        nullable=True,
        comment="Whether the recommendation was helpful",
    )

    # Did user switch to recommended plan?
    switched_to_plan: Mapped[bool | None] = mapped_column(
        nullable=True,
        comment="Whether the user switched to this plan",
    )

    # Free-form feedback
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User's comment or feedback",
    )

    # Additional data
    extra_data: Mapped[dict] = mapped_column(
        JSONType,
        default=dict,
        comment="Additional feedback data",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer")
    recommendation: Mapped["Recommendation"] = relationship(
        "Recommendation",
        foreign_keys=[recommendation_id],
    )
    plan: Mapped["EnergyPlan"] = relationship("EnergyPlan")


# Forward reference resolution
from app.models.customer import Customer  # noqa: E402, F811
from app.models.plan import EnergyPlan  # noqa: E402
from app.models.recommendation import Recommendation  # noqa: E402, F811
