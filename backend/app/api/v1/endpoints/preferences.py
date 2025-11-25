"""Customer preference API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.customer import CustomerRepository
from app.repositories.preference import PreferenceRepository
from app.schemas.preference import CustomerPreferenceCreate, CustomerPreferenceResponse

router = APIRouter()


@router.put(
    "/{customer_id}",
    response_model=CustomerPreferenceResponse,
)
async def upsert_preferences(
    customer_id: UUID,
    preferences: CustomerPreferenceCreate,
    db: AsyncSession = Depends(get_db),
) -> CustomerPreferenceResponse:
    """Create or update customer preferences."""
    # Verify customer exists
    customer_repo = CustomerRepository(db)
    customer = await customer_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id '{customer_id}' not found",
        )

    repo = PreferenceRepository(db)
    preference = await repo.upsert(customer_id, preferences)
    return CustomerPreferenceResponse.model_validate(preference)


@router.get("/{customer_id}", response_model=CustomerPreferenceResponse)
async def get_preferences(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CustomerPreferenceResponse:
    """Get customer preferences."""
    repo = PreferenceRepository(db)
    preference = await repo.get_by_customer_id(customer_id)

    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preferences for customer '{customer_id}' not found",
        )

    return CustomerPreferenceResponse.model_validate(preference)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preferences(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete customer preferences (reset to defaults)."""
    repo = PreferenceRepository(db)
    deleted = await repo.delete(customer_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preferences for customer '{customer_id}' not found",
        )
