"""Redis connection and caching utilities."""

import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Redis connection pool
redis_pool: redis.ConnectionPool | None = None
redis_client: redis.Redis | None = None


async def init_redis() -> redis.Redis:
    """Initialize Redis connection."""
    global redis_pool, redis_client

    redis_pool = redis.ConnectionPool.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=20,
    )
    redis_client = redis.Redis(connection_pool=redis_pool)

    # Test connection
    await redis_client.ping()
    logger.info("Redis connection established")

    return redis_client


async def close_redis() -> None:
    """Close Redis connections."""
    global redis_client, redis_pool

    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()

    logger.info("Redis connection closed")


async def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    if redis_client is None:
        return await init_redis()
    return redis_client


class CacheService:
    """Service for caching operations."""

    def __init__(self, client: redis.Redis) -> None:
        """Initialize cache service."""
        self.client = client
        self.default_ttl = settings.cache_ttl_seconds

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        value = await self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set value in cache with optional TTL."""
        ttl = ttl or self.default_ttl
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await self.client.setex(key, ttl, serialized)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(await self.client.exists(key))

    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        keys = await self.client.keys(pattern)
        if keys:
            return await self.client.delete(*keys)
        return 0

    async def get_or_set(
        self,
        key: str,
        factory,
        ttl: int | None = None,
    ):
        """Get value from cache or compute and set it.

        Args:
            key: Cache key
            factory: Async callable to compute value if not cached
            ttl: Time to live in seconds
        """
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await factory()
        await self.set(key, value, ttl)
        return value

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache."""
        return await self.client.incrby(key, amount)

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        if not keys:
            return {}

        values = await self.client.mget(keys)
        result = {}
        for key, value in zip(keys, values, strict=False):
            if value is not None:
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
        return result

    async def set_many(
        self,
        items: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Set multiple values in cache."""
        ttl = ttl or self.default_ttl
        pipe = self.client.pipeline()
        for key, value in items.items():
            serialized = json.dumps(value) if not isinstance(value, str) else value
            pipe.setex(key, ttl, serialized)
        await pipe.execute()


# Cache key prefixes
class CacheKeys:
    """Constants for cache key prefixes."""

    PLANS = "plans"
    PLANS_ALL = "plans:all"
    RECOMMENDATIONS = "recommendations"
    CUSTOMER = "customer"
    USAGE_ANALYSIS = "usage_analysis"

    @staticmethod
    def plan(plan_id: str) -> str:
        """Get cache key for a specific plan."""
        return f"plans:{plan_id}"

    @staticmethod
    def recommendations(customer_id: str) -> str:
        """Get cache key for customer recommendations."""
        return f"recommendations:{customer_id}"

    @staticmethod
    def usage_analysis(customer_id: str) -> str:
        """Get cache key for customer usage analysis."""
        return f"usage_analysis:{customer_id}"
