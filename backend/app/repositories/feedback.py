"""Feedback repository for database operations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackStats


class FeedbackRepository:
    """Repository for feedback database operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.db = db

    async def create(self, data: FeedbackCreate) -> Feedback:
        """Create new feedback."""
        feedback = Feedback(
            customer_id=data.customer_id,
            recommendation_id=data.recommendation_id,
            plan_id=data.plan_id,
            feedback_type=data.feedback_type,
            rating=data.rating,
            was_helpful=data.was_helpful,
            switched_to_plan=data.switched_to_plan,
            comment=data.comment,
            extra_data=data.metadata,
        )
        self.db.add(feedback)
        await self.db.flush()
        await self.db.refresh(feedback)
        return feedback

    async def get_by_id(self, feedback_id: UUID) -> Feedback | None:
        """Get feedback by ID."""
        result = await self.db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        return result.scalar_one_or_none()

    async def get_by_customer_id(
        self,
        customer_id: UUID,
        limit: int = 10,
    ) -> list[Feedback]:
        """Get feedback by customer ID."""
        result = await self.db.execute(
            select(Feedback)
            .where(Feedback.customer_id == customer_id)
            .order_by(Feedback.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_recommendation_id(
        self,
        recommendation_id: UUID,
    ) -> list[Feedback]:
        """Get feedback for a specific recommendation."""
        result = await self.db.execute(
            select(Feedback)
            .where(Feedback.recommendation_id == recommendation_id)
            .order_by(Feedback.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 50) -> list[Feedback]:
        """Get recent feedback entries."""
        result = await self.db.execute(
            select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(self) -> FeedbackStats:
        """Get feedback statistics."""
        # Total count
        total_result = await self.db.execute(select(func.count(Feedback.id)))
        total_count = total_result.scalar() or 0

        # Average rating (only where rating is not null)
        avg_result = await self.db.execute(
            select(func.avg(Feedback.rating)).where(Feedback.rating.isnot(None))
        )
        avg_rating = avg_result.scalar()

        # Helpful percentage
        helpful_count_result = await self.db.execute(
            select(func.count(Feedback.id)).where(Feedback.was_helpful == True)  # noqa: E712
        )
        helpful_count = helpful_count_result.scalar() or 0

        total_helpful_responses_result = await self.db.execute(
            select(func.count(Feedback.id)).where(Feedback.was_helpful.isnot(None))
        )
        total_helpful_responses = total_helpful_responses_result.scalar() or 0

        helpful_percentage = (
            (helpful_count / total_helpful_responses * 100)
            if total_helpful_responses > 0
            else None
        )

        # Switch rate
        switched_count_result = await self.db.execute(
            select(func.count(Feedback.id)).where(Feedback.switched_to_plan == True)  # noqa: E712
        )
        switched_count = switched_count_result.scalar() or 0

        total_switch_responses_result = await self.db.execute(
            select(func.count(Feedback.id)).where(Feedback.switched_to_plan.isnot(None))
        )
        total_switch_responses = total_switch_responses_result.scalar() or 0

        switch_rate = (
            (switched_count / total_switch_responses * 100)
            if total_switch_responses > 0
            else None
        )

        # Rating distribution
        rating_distribution = {}
        for rating in range(1, 6):
            count_result = await self.db.execute(
                select(func.count(Feedback.id)).where(Feedback.rating == rating)
            )
            rating_distribution[rating] = count_result.scalar() or 0

        # Feedback by type
        feedback_by_type = {}
        type_result = await self.db.execute(
            select(Feedback.feedback_type, func.count(Feedback.id)).group_by(
                Feedback.feedback_type
            )
        )
        for row in type_result.all():
            feedback_by_type[row[0]] = row[1]

        return FeedbackStats(
            total_feedback_count=total_count,
            average_rating=float(avg_rating) if avg_rating else None,
            helpful_percentage=helpful_percentage,
            switch_rate=switch_rate,
            rating_distribution=rating_distribution,
            feedback_by_type=feedback_by_type,
        )
