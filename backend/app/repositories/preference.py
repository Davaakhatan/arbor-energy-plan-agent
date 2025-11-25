"""Customer preference repository."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preference import CustomerPreference
from app.schemas.preference import CustomerPreferenceCreate


class PreferenceRepository:
    """Repository for customer preference database operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.db = db

    async def get_by_customer_id(self, customer_id: UUID) -> CustomerPreference | None:
        """Get preferences by customer ID."""
        result = await self.db.execute(
            select(CustomerPreference).where(
                CustomerPreference.customer_id == customer_id
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        customer_id: UUID,
        data: CustomerPreferenceCreate,
    ) -> CustomerPreference:
        """Create or update customer preferences."""
        existing = await self.get_by_customer_id(customer_id)

        if existing:
            # Update existing
            existing.cost_savings_weight = data.cost_savings_weight
            existing.flexibility_weight = data.flexibility_weight
            existing.renewable_weight = data.renewable_weight
            existing.supplier_rating_weight = data.supplier_rating_weight
            existing.min_renewable_percentage = data.min_renewable_percentage
            existing.max_contract_months = data.max_contract_months
            existing.avoid_variable_rates = data.avoid_variable_rates
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new
            preference = CustomerPreference(
                customer_id=customer_id,
                cost_savings_weight=data.cost_savings_weight,
                flexibility_weight=data.flexibility_weight,
                renewable_weight=data.renewable_weight,
                supplier_rating_weight=data.supplier_rating_weight,
                min_renewable_percentage=data.min_renewable_percentage,
                max_contract_months=data.max_contract_months,
                avoid_variable_rates=data.avoid_variable_rates,
            )
            self.db.add(preference)
            await self.db.flush()
            await self.db.refresh(preference)
            return preference

    async def delete(self, customer_id: UUID) -> bool:
        """Delete customer preferences."""
        result = await self.db.execute(
            delete(CustomerPreference).where(
                CustomerPreference.customer_id == customer_id
            )
        )
        await self.db.flush()
        return result.rowcount > 0
