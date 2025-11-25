"""Recommendation model for storing generated recommendations."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Recommendation(Base):
    """Stores generated plan recommendations for customers."""

    __tablename__ = "recommendations"

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
    plan_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("energy_plans.id", ondelete="CASCADE"),
        index=True,
    )

    # Ranking
    rank: Mapped[int] = mapped_column(
        Integer,
        comment="Recommendation rank (1, 2, or 3)",
    )
    overall_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        comment="MCDA overall score (0.0000 to 1.0000)",
    )

    # Calculated values
    projected_annual_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="Projected annual cost with this plan",
    )
    projected_annual_savings: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="Projected annual savings vs current plan",
    )
    switching_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        comment="One-time switching costs (ETF, etc.)",
    )

    # Component scores (for transparency)
    cost_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        comment="Normalized cost score",
    )
    flexibility_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        comment="Normalized flexibility score",
    )
    renewable_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        comment="Normalized renewable score",
    )
    rating_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        comment="Normalized supplier rating score",
    )

    # Explanation
    explanation: Mapped[str] = mapped_column(
        Text,
        comment="Plain language explanation of recommendation",
    )
    explanation_details: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        comment="Structured explanation data",
    )

    # Risk flags
    risk_flags: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        comment="List of risk warnings",
    )
    confidence_level: Mapped[str] = mapped_column(
        default="high",
        comment="Confidence level: high, medium, low",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this recommendation expires",
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer")
    plan: Mapped["EnergyPlan"] = relationship("EnergyPlan")


# Forward reference resolution
from app.models.customer import Customer  # noqa: E402, F811
from app.models.plan import EnergyPlan  # noqa: E402
