"""Initial schema for Arbor Energy Plan Agent.

Revision ID: 001_initial
Revises:
Create Date: 2025-01-27

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create suppliers table
    op.create_table(
        "suppliers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("customer_service_rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create energy_plans table
    op.create_table(
        "energy_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rate_type", sa.String(50), default="fixed", nullable=False),
        sa.Column("rate_per_kwh", sa.Numeric(10, 6), nullable=False),
        sa.Column("monthly_fee", sa.Numeric(10, 2), default=0, nullable=False),
        sa.Column("contract_length_months", sa.Integer(), default=12, nullable=False),
        sa.Column("early_termination_fee", sa.Numeric(10, 2), default=0, nullable=False),
        sa.Column("cancellation_fee", sa.Numeric(10, 2), default=0, nullable=False),
        sa.Column("renewable_percentage", sa.Integer(), default=0, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create customers table
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "external_id", sa.String(255), nullable=False, unique=True, index=True
        ),
        sa.Column(
            "current_plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("energy_plans.id"),
            nullable=True,
        ),
        sa.Column("contract_end_date", sa.Date(), nullable=True),
        sa.Column("early_termination_fee", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create customer_usage table
    op.create_table(
        "customer_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("usage_date", sa.Date(), nullable=False, index=True),
        sa.Column("kwh_usage", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Create customer_preferences table
    op.create_table(
        "customer_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("cost_savings_weight", sa.Numeric(3, 2), default=0.40, nullable=False),
        sa.Column("flexibility_weight", sa.Numeric(3, 2), default=0.20, nullable=False),
        sa.Column("renewable_weight", sa.Numeric(3, 2), default=0.20, nullable=False),
        sa.Column(
            "supplier_rating_weight", sa.Numeric(3, 2), default=0.20, nullable=False
        ),
        sa.Column("min_renewable_percentage", sa.Integer(), default=0, nullable=False),
        sa.Column("max_contract_months", sa.Integer(), nullable=True),
        sa.Column("avoid_variable_rates", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create recommendations table
    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("energy_plans.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("overall_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("projected_annual_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("projected_annual_savings", sa.Numeric(12, 2), nullable=False),
        sa.Column("switching_cost", sa.Numeric(10, 2), default=0, nullable=False),
        sa.Column("cost_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("flexibility_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("renewable_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("rating_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("explanation_details", postgresql.JSONB(), default={}, nullable=False),
        sa.Column("risk_flags", postgresql.JSONB(), default=[], nullable=False),
        sa.Column("confidence_level", sa.String(20), default="high", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes for common queries
    op.create_index(
        "ix_customer_usage_customer_date",
        "customer_usage",
        ["customer_id", "usage_date"],
    )
    op.create_index(
        "ix_recommendations_customer_rank",
        "recommendations",
        ["customer_id", "rank"],
    )


def downgrade() -> None:
    op.drop_index("ix_recommendations_customer_rank")
    op.drop_index("ix_customer_usage_customer_date")
    op.drop_table("recommendations")
    op.drop_table("customer_preferences")
    op.drop_table("customer_usage")
    op.drop_table("customers")
    op.drop_table("energy_plans")
    op.drop_table("suppliers")
