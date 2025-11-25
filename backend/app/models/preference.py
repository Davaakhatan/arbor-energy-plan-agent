"""Customer preference model for recommendation weighting."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CustomerPreference(Base):
    """Customer preferences for energy plan recommendations.

    Weights are on a scale of 0.0 to 1.0, representing relative importance.
    All weights should sum to 1.0 for proper MCDA scoring.
    """

    __tablename__ = "customer_preferences"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    customer_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # Preference weights (0.0 to 1.0)
    cost_savings_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.40"),
        comment="Weight for cost savings priority (0.0-1.0)",
    )
    flexibility_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.20"),
        comment="Weight for contract flexibility (0.0-1.0)",
    )
    renewable_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.20"),
        comment="Weight for renewable energy percentage (0.0-1.0)",
    )
    supplier_rating_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.20"),
        comment="Weight for supplier rating (0.0-1.0)",
    )

    # Constraints and preferences
    min_renewable_percentage: Mapped[int] = mapped_column(
        default=0,
        comment="Minimum acceptable renewable energy percentage",
    )
    max_contract_months: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Maximum acceptable contract length",
    )
    avoid_variable_rates: Mapped[bool] = mapped_column(
        default=False,
        comment="Avoid variable/indexed rate plans",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="preferences",
    )


# Forward reference resolution
from app.models.customer import Customer  # noqa: E402, F811
