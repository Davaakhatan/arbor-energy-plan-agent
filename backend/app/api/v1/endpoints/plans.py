"""Energy plan API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.plan import PlanRepository, SupplierRepository
from app.schemas.plan import (
    EnergyPlanCreate,
    EnergyPlanResponse,
    SupplierCreate,
    SupplierResponse,
)

router = APIRouter()


# Supplier endpoints
@router.post(
    "/suppliers",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    """Create a new energy supplier."""
    repo = SupplierRepository(db)
    supplier = await repo.create(supplier_data)
    return SupplierResponse.model_validate(supplier)


@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    active_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> list[SupplierResponse]:
    """List all energy suppliers."""
    repo = SupplierRepository(db)
    suppliers = await repo.get_all(active_only=active_only)
    return [SupplierResponse.model_validate(s) for s in suppliers]


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    """Get supplier by ID."""
    repo = SupplierRepository(db)
    supplier = await repo.get_by_id(supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id '{supplier_id}' not found",
        )

    return SupplierResponse.model_validate(supplier)


# Plan endpoints
@router.post(
    "",
    response_model=EnergyPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    plan_data: EnergyPlanCreate,
    db: AsyncSession = Depends(get_db),
) -> EnergyPlanResponse:
    """Create a new energy plan."""
    repo = PlanRepository(db)

    # Verify supplier exists
    supplier_repo = SupplierRepository(db)
    supplier = await supplier_repo.get_by_id(plan_data.supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id '{plan_data.supplier_id}' not found",
        )

    plan = await repo.create(plan_data)
    return EnergyPlanResponse.model_validate(plan)


@router.get("", response_model=list[EnergyPlanResponse])
async def list_plans(
    active_only: bool = Query(default=True),
    supplier_id: UUID | None = Query(default=None),
    min_renewable: int = Query(default=0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[EnergyPlanResponse]:
    """List energy plans with optional filters."""
    repo = PlanRepository(db)
    plans = await repo.get_all(
        active_only=active_only,
        supplier_id=supplier_id,
        min_renewable=min_renewable,
    )
    return [EnergyPlanResponse.model_validate(p) for p in plans]


@router.get("/{plan_id}", response_model=EnergyPlanResponse)
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EnergyPlanResponse:
    """Get energy plan by ID."""
    repo = PlanRepository(db)
    plan = await repo.get_by_id(plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with id '{plan_id}' not found",
        )

    return EnergyPlanResponse.model_validate(plan)
