"""Customer repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer, CustomerUsage
from app.schemas.customer import CustomerCreate


class CustomerRepository:
    """Repository for customer database operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.db = db

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        """Get customer by ID with usage data."""
        result = await self.db.execute(
            select(Customer)
            .options(selectinload(Customer.usage_data))
            .options(selectinload(Customer.preferences))
            .where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Customer | None:
        """Get customer by external ID."""
        result = await self.db.execute(
            select(Customer)
            .options(selectinload(Customer.usage_data))
            .options(selectinload(Customer.preferences))
            .where(Customer.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: CustomerCreate) -> Customer:
        """Create a new customer with usage data."""
        customer = Customer(
            external_id=data.external_id,
            current_plan_id=data.current_plan_id,
            contract_end_date=data.contract_end_date,
            early_termination_fee=data.early_termination_fee,
        )
        self.db.add(customer)
        await self.db.flush()

        # Add usage data
        for usage in data.usage_data:
            usage_record = CustomerUsage(
                customer_id=customer.id,
                usage_date=usage.usage_date,
                kwh_usage=usage.kwh_usage,
            )
            self.db.add(usage_record)

        await self.db.flush()
        await self.db.refresh(customer)

        # Reload with relationships
        return await self.get_by_id(customer.id)  # type: ignore

    async def delete(self, customer_id: UUID) -> bool:
        """Delete customer and all associated data."""
        customer = await self.get_by_id(customer_id)
        if not customer:
            return False

        await self.db.delete(customer)
        await self.db.flush()
        return True

    async def add_usage_data(
        self,
        customer_id: UUID,
        usage_date: "date",  # type: ignore  # noqa: F821
        kwh_usage: "Decimal",  # type: ignore  # noqa: F821
    ) -> CustomerUsage:
        """Add usage data for a customer."""
        usage = CustomerUsage(
            customer_id=customer_id,
            usage_date=usage_date,
            kwh_usage=kwh_usage,
        )
        self.db.add(usage)
        await self.db.flush()
        await self.db.refresh(usage)
        return usage
