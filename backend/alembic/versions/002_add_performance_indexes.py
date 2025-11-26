"""Add performance optimization indexes.

Revision ID: 002_perf_indexes
Revises: 001_initial
Create Date: 2025-01-27

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_perf_indexes"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Composite index for plan filtering (active plans sorted by rate)
    op.create_index(
        "ix_energy_plans_active_rate",
        "energy_plans",
        ["is_active", "rate_per_kwh"],
    )

    # Index for renewable filtering
    op.create_index(
        "ix_energy_plans_renewable",
        "energy_plans",
        ["renewable_percentage"],
    )

    # Index for filtering active suppliers
    op.create_index(
        "ix_suppliers_active",
        "suppliers",
        ["is_active"],
    )

    # Unique constraint for customer usage (one entry per customer per month)
    op.create_unique_constraint(
        "uq_customer_usage_date",
        "customer_usage",
        ["customer_id", "usage_date"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_customer_usage_date", "customer_usage", type_="unique")
    op.drop_index("ix_suppliers_active")
    op.drop_index("ix_energy_plans_renewable")
    op.drop_index("ix_energy_plans_active_rate")
