"""Energy plan and supplier repositories."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.plan import EnergyPlan, Supplier
from app.schemas.plan import EnergyPlanCreate, SupplierCreate


class SupplierRepository:
    """Repository for supplier database operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.db = db

    async def get_by_id(self, supplier_id: UUID) -> Supplier | None:
        """Get supplier by ID."""
        result = await self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, active_only: bool = True) -> list[Supplier]:
        """Get all suppliers."""
        query = select(Supplier)
        if active_only:
            query = query.where(Supplier.is_active == True)  # noqa: E712
        query = query.order_by(Supplier.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, data: SupplierCreate) -> Supplier:
        """Create a new supplier."""
        supplier = Supplier(
            name=data.name,
            rating=data.rating,
            website=data.website,
            customer_service_rating=data.customer_service_rating,
        )
        self.db.add(supplier)
        await self.db.flush()
        await self.db.refresh(supplier)
        return supplier


class PlanRepository:
    """Repository for energy plan database operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.db = db

    async def get_by_id(self, plan_id: UUID) -> EnergyPlan | None:
        """Get plan by ID with supplier."""
        result = await self.db.execute(
            select(EnergyPlan)
            .options(selectinload(EnergyPlan.supplier))
            .where(EnergyPlan.id == plan_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        active_only: bool = True,
        supplier_id: UUID | None = None,
        min_renewable: int = 0,
    ) -> list[EnergyPlan]:
        """Get all plans with optional filters."""
        query = select(EnergyPlan).options(selectinload(EnergyPlan.supplier))

        if active_only:
            query = query.where(EnergyPlan.is_active == True)  # noqa: E712
        if supplier_id:
            query = query.where(EnergyPlan.supplier_id == supplier_id)
        if min_renewable > 0:
            query = query.where(EnergyPlan.renewable_percentage >= min_renewable)

        query = query.order_by(EnergyPlan.rate_per_kwh)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, data: EnergyPlanCreate) -> EnergyPlan:
        """Create a new energy plan."""
        plan = EnergyPlan(
            supplier_id=data.supplier_id,
            name=data.name,
            description=data.description,
            rate_type=data.rate_type.value,
            rate_per_kwh=data.rate_per_kwh,
            monthly_fee=data.monthly_fee,
            contract_length_months=data.contract_length_months,
            early_termination_fee=data.early_termination_fee,
            cancellation_fee=data.cancellation_fee,
            renewable_percentage=data.renewable_percentage,
        )
        self.db.add(plan)
        await self.db.flush()
        await self.db.refresh(plan)
        return await self.get_by_id(plan.id)  # type: ignore
