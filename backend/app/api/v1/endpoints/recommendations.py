"""Recommendation API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import CacheService, get_redis
from app.repositories.customer import CustomerRepository
from app.schemas.recommendation import RecommendationRequest, RecommendationSetResponse
from app.services.recommendation import RecommendationService

router = APIRouter()


@router.post("", response_model=RecommendationSetResponse)
async def generate_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
) -> RecommendationSetResponse:
    """Generate top 3 energy plan recommendations for a customer.

    This endpoint analyzes customer usage patterns, preferences, and available
    energy plans to provide personalized recommendations with explanations.

    Performance target: < 2 seconds response time.
    """
    # Verify customer exists
    customer_repo = CustomerRepository(db)
    customer = await customer_repo.get_by_id(request.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id '{request.customer_id}' not found",
        )

    # Check for sufficient usage data
    if len(customer.usage_data) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient usage data. At least 3 months required.",
        )

    # Initialize services
    redis = await get_redis()
    cache = CacheService(redis)
    service = RecommendationService(db, cache)

    # Generate recommendations
    recommendations = await service.generate_recommendations(
        customer=customer,
        preferences_override=request.preferences,
        include_switching_analysis=request.include_switching_analysis,
    )

    return recommendations


@router.get("/{customer_id}", response_model=RecommendationSetResponse)
async def get_cached_recommendations(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> RecommendationSetResponse:
    """Get cached recommendations for a customer if available.

    Returns the most recent recommendations if they haven't expired.
    If no cached recommendations exist, returns 404.
    """
    # Verify customer exists
    customer_repo = CustomerRepository(db)
    customer = await customer_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id '{customer_id}' not found",
        )

    # Check cache
    redis = await get_redis()
    cache = CacheService(redis)
    service = RecommendationService(db, cache)

    cached = await service.get_cached_recommendations(customer_id)
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached recommendations found. Generate new recommendations.",
        )

    return cached


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def invalidate_recommendations(
    customer_id: UUID,
) -> None:
    """Invalidate cached recommendations for a customer.

    Use this when customer data or preferences change significantly.
    """
    redis = await get_redis()
    cache = CacheService(redis)
    await cache.delete(f"recommendations:{customer_id}")
