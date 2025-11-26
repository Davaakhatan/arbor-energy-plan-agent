"""Cached plan service for performance optimization."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.redis import CacheKeys, CacheService
from app.models.plan import EnergyPlan
from app.repositories.plan import PlanRepository

logger = get_logger(__name__)

# Cache TTLs (in seconds)
PLANS_CACHE_TTL = 300  # 5 minutes - plans don't change often
PLAN_DETAIL_TTL = 600  # 10 minutes


class CachedPlanService:
    """Service for retrieving plans with caching layer."""

    def __init__(self, db: AsyncSession, cache: CacheService) -> None:
        """Initialize service with database and cache."""
        self.db = db
        self.cache = cache
        self.repo = PlanRepository(db)

    async def get_all_active_plans(self) -> list[EnergyPlan]:
        """Get all active plans with caching.

        Plans are cached for 5 minutes since they rarely change.
        """
        cache_key = CacheKeys.PLANS_ALL

        # Try to get from cache
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug("Plans cache hit")
            # Reconstruct EnergyPlan objects from cached data
            return [self._dict_to_plan(p) for p in cached]

        logger.debug("Plans cache miss, fetching from database")

        # Fetch from database
        plans = await self.repo.get_all(active_only=True)

        # Cache the results
        await self.cache.set(
            cache_key,
            [self._plan_to_dict(p) for p in plans],
            ttl=PLANS_CACHE_TTL,
        )

        return plans

    async def get_plan_by_id(self, plan_id: UUID) -> EnergyPlan | None:
        """Get a specific plan by ID with caching."""
        cache_key = CacheKeys.plan(str(plan_id))

        # Try to get from cache
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug(f"Plan cache hit for {plan_id}")
            return self._dict_to_plan(cached)

        logger.debug(f"Plan cache miss for {plan_id}")

        # Fetch from database
        plan = await self.repo.get_by_id(plan_id)

        if plan:
            # Cache the result
            await self.cache.set(
                cache_key,
                self._plan_to_dict(plan),
                ttl=PLAN_DETAIL_TTL,
            )

        return plan

    async def invalidate_plans_cache(self) -> int:
        """Invalidate all plan caches.

        Call this when plans are updated.
        """
        deleted = await self.cache.clear_pattern("plans:*")
        logger.info(f"Invalidated {deleted} plan cache entries")
        return deleted

    async def invalidate_plan_cache(self, plan_id: UUID) -> None:
        """Invalidate cache for a specific plan."""
        await self.cache.delete(CacheKeys.plan(str(plan_id)))
        # Also invalidate the all-plans cache
        await self.cache.delete(CacheKeys.PLANS_ALL)
        logger.debug(f"Invalidated cache for plan {plan_id}")

    async def warm_cache(self) -> int:
        """Pre-warm the cache with all active plans.

        Call this on application startup or after bulk updates.
        """
        plans = await self.repo.get_all(active_only=True)

        # Cache the full list
        await self.cache.set(
            CacheKeys.PLANS_ALL,
            [self._plan_to_dict(p) for p in plans],
            ttl=PLANS_CACHE_TTL,
        )

        # Cache individual plans
        plan_cache = {
            CacheKeys.plan(str(p.id)): self._plan_to_dict(p)
            for p in plans
        }
        await self.cache.set_many(plan_cache, ttl=PLAN_DETAIL_TTL)

        logger.info(f"Warmed cache with {len(plans)} plans")
        return len(plans)

    def _plan_to_dict(self, plan: EnergyPlan) -> dict:
        """Convert plan to dictionary for caching."""
        return {
            "id": str(plan.id),
            "supplier_id": str(plan.supplier_id) if plan.supplier_id else None,
            "name": plan.name,
            "description": plan.description,
            "rate_type": plan.rate_type,
            "rate_per_kwh": str(plan.rate_per_kwh),
            "monthly_fee": str(plan.monthly_fee),
            "contract_length_months": plan.contract_length_months,
            "early_termination_fee": str(plan.early_termination_fee) if plan.early_termination_fee else None,
            "cancellation_fee": str(plan.cancellation_fee) if plan.cancellation_fee else None,
            "renewable_percentage": plan.renewable_percentage,
            "is_active": plan.is_active,
            "supplier": {
                "id": str(plan.supplier.id),
                "name": plan.supplier.name,
                "rating": str(plan.supplier.rating) if plan.supplier.rating else None,
                "website": plan.supplier.website,
                "customer_service_rating": str(plan.supplier.customer_service_rating) if plan.supplier.customer_service_rating else None,
            } if plan.supplier else None,
        }

    def _dict_to_plan(self, data: dict) -> EnergyPlan:
        """Reconstruct plan from cached dictionary.

        Note: This creates a detached SQLAlchemy object.
        """
        from decimal import Decimal
        from uuid import UUID as UUIDType

        from app.models.plan import Supplier

        plan = EnergyPlan(
            id=UUIDType(data["id"]),
            supplier_id=UUIDType(data["supplier_id"]) if data.get("supplier_id") else None,
            name=data["name"],
            description=data.get("description"),
            rate_type=data["rate_type"],
            rate_per_kwh=Decimal(data["rate_per_kwh"]),
            monthly_fee=Decimal(data["monthly_fee"]),
            contract_length_months=data["contract_length_months"],
            early_termination_fee=Decimal(data["early_termination_fee"]) if data.get("early_termination_fee") else None,
            cancellation_fee=Decimal(data["cancellation_fee"]) if data.get("cancellation_fee") else None,
            renewable_percentage=data["renewable_percentage"],
            is_active=data.get("is_active", True),
        )

        # Attach supplier if present
        if data.get("supplier"):
            s = data["supplier"]
            plan.supplier = Supplier(
                id=UUIDType(s["id"]),
                name=s["name"],
                rating=Decimal(s["rating"]) if s.get("rating") else None,
                website=s.get("website"),
                customer_service_rating=Decimal(s["customer_service_rating"]) if s.get("customer_service_rating") else None,
            )

        return plan
