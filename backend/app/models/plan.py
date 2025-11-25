"""Energy plan and supplier models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RateType(str, Enum):
    """Energy plan rate types."""

    FIXED = "fixed"
    VARIABLE = "variable"
    INDEXED = "indexed"
    TIME_OF_USE = "time_of_use"


class Supplier(Base):
    """Energy supplier model."""

    __tablename__ = "suppliers"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    rating: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        comment="Supplier rating from 0.00 to 5.00",
    )
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    customer_service_rating: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(default=True)
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
    plans: Mapped[list["EnergyPlan"]] = relationship(
        "EnergyPlan",
        back_populates="supplier",
        cascade="all, delete-orphan",
    )


class EnergyPlan(Base):
    """Energy plan model with pricing and terms."""

    __tablename__ = "energy_plans"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    supplier_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Rate structure
    rate_type: Mapped[str] = mapped_column(
        String(50),
        default=RateType.FIXED.value,
        comment="fixed, variable, indexed, or time_of_use",
    )
    rate_per_kwh: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        comment="Base rate in dollars per kWh",
    )
    monthly_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        comment="Fixed monthly service fee",
    )

    # Contract terms
    contract_length_months: Mapped[int] = mapped_column(
        Integer,
        default=12,
        comment="Contract duration in months",
    )
    early_termination_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
    )
    cancellation_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
    )

    # Green energy
    renewable_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Percentage of renewable energy (0-100)",
    )

    # Metadata
    is_active: Mapped[bool] = mapped_column(default=True)
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
    supplier: Mapped["Supplier"] = relationship(
        "Supplier",
        back_populates="plans",
    )
