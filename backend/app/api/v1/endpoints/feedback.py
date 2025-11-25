"""Feedback API endpoints for collecting and analyzing user feedback."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.customer import CustomerRepository
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStats,
    FeedbackSummary,
)

router = APIRouter()


@router.post(
    "/",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    """Submit feedback for a recommendation.

    Accepts rating (1-5), helpfulness indicator, and optional comment.
    """
    # Verify customer exists
    customer_repo = CustomerRepository(db)
    customer = await customer_repo.get_by_id(feedback.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id '{feedback.customer_id}' not found",
        )

    repo = FeedbackRepository(db)
    created_feedback = await repo.create(feedback)
    await db.commit()

    return FeedbackResponse.model_validate(created_feedback)


@router.get(
    "/customer/{customer_id}",
    response_model=list[FeedbackResponse],
)
async def get_customer_feedback(
    customer_id: UUID,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> list[FeedbackResponse]:
    """Get feedback submitted by a customer."""
    repo = FeedbackRepository(db)
    feedback_list = await repo.get_by_customer_id(customer_id, limit=limit)
    return [FeedbackResponse.model_validate(f) for f in feedback_list]


@router.get(
    "/recommendation/{recommendation_id}",
    response_model=list[FeedbackResponse],
)
async def get_recommendation_feedback(
    recommendation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[FeedbackResponse]:
    """Get all feedback for a specific recommendation."""
    repo = FeedbackRepository(db)
    feedback_list = await repo.get_by_recommendation_id(recommendation_id)
    return [FeedbackResponse.model_validate(f) for f in feedback_list]


@router.get(
    "/stats",
    response_model=FeedbackStats,
)
async def get_feedback_stats(
    db: AsyncSession = Depends(get_db),
) -> FeedbackStats:
    """Get aggregate feedback statistics.

    Returns:
    - Total feedback count
    - Average rating
    - Percentage of users who found recommendations helpful
    - Percentage who switched to a recommended plan
    - Rating distribution (1-5)
    - Feedback count by type
    """
    repo = FeedbackRepository(db)
    return await repo.get_stats()


@router.get(
    "/summary",
    response_model=FeedbackSummary,
)
async def get_feedback_summary(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> FeedbackSummary:
    """Get feedback summary with stats and recent entries."""
    repo = FeedbackRepository(db)
    stats = await repo.get_stats()
    recent = await repo.get_recent(limit=limit)

    return FeedbackSummary(
        stats=stats,
        recent_feedback=[FeedbackResponse.model_validate(f) for f in recent],
    )


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
)
async def get_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    """Get specific feedback by ID."""
    repo = FeedbackRepository(db)
    feedback = await repo.get_by_id(feedback_id)

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with id '{feedback_id}' not found",
        )

    return FeedbackResponse.model_validate(feedback)
