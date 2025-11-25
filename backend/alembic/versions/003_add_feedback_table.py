"""Add feedback table for user feedback collection.

Revision ID: 003_feedback
Revises: 002_perf_indexes
Create Date: 2025-01-25

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "003_feedback"
down_revision: Union[str, None] = "002_perf_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "recommendation_id",
            UUID(as_uuid=True),
            sa.ForeignKey("recommendations.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "plan_id",
            UUID(as_uuid=True),
            sa.ForeignKey("energy_plans.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "feedback_type",
            sa.String(50),
            nullable=False,
            default="recommendation_rating",
        ),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("was_helpful", sa.Boolean, nullable=True),
        sa.Column("switched_to_plan", sa.Boolean, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("extra_data", JSONB, nullable=False, default={}),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Index for analytics queries
    op.create_index(
        "ix_feedback_created_at",
        "feedback",
        ["created_at"],
    )

    op.create_index(
        "ix_feedback_type",
        "feedback",
        ["feedback_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_feedback_type")
    op.drop_index("ix_feedback_created_at")
    op.drop_table("feedback")
