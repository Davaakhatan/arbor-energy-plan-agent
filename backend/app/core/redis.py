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
