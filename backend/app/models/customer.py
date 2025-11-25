"""Customer and usage data models."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    """Customer model representing energy consumers."""

    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    external_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        comment="Anonymized external customer identifier",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Current plan details
    current_plan_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("energy_plans.id"),
        nullable=True,
    )
    contract_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    early_termination_fee: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # Relationships
    usage_data: Mapped[list["CustomerUsage"]] = relationship(
        "CustomerUsage",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    preferences: Mapped["CustomerPreference | None"] = relationship(
        "CustomerPreference",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan",
    )
    current_plan: Mapped["EnergyPlan | None"] = relationship(
        "EnergyPlan",
        foreign_keys=[current_plan_id],
    )


class CustomerUsage(Base):
    """Monthly energy usage data for customers (12 months)."""

    __tablename__ = "customer_usage"

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
    usage_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        comment="First day of the usage month",
    )
    kwh_usage: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="Energy usage in kilowatt-hours",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="usage_data",
    )

    # Ensure unique usage per customer per month
    __table_args__ = (
        {"comment": "Stores 12 months of customer energy usage data"},
    )


# Forward reference resolution
from app.models.plan import EnergyPlan  # noqa: E402
from app.models.preference import CustomerPreference  # noqa: E402
