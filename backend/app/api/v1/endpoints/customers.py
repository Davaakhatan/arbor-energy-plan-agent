"""Customer API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter()


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    """Create a new customer with usage data."""
    repo = CustomerRepository(db)

    # Check if external_id already exists
    existing = await repo.get_by_external_id(customer_data.external_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer with external_id '{customer_data.external_id}' already exists",
        )

    customer = await repo.create(customer_data)
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    """Get customer by ID."""
    repo = CustomerRepository(db)
    customer = await repo.get_by_id(customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id '{customer_id}' not found",
        )

    return CustomerResponse.model_validate(customer)


@router.get("/external/{external_id}", response_model=CustomerResponse)
async def get_customer_by_external_id(
    external_id: str,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    """Get customer by external ID."""
    repo = CustomerRepository(db)
    customer = await repo.get_by_external_id(external_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with external_id '{external_id}' not found",
        )

    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete customer and all associated data (GDPR compliance)."""
    repo = CustomerRepository(db)
    deleted = await repo.delete(customer_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id '{customer_id}' not found",
        )
