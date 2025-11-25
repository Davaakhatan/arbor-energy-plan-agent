"""Rate limiting middleware using Redis."""

import time
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm.

    Uses Redis for distributed rate limiting across multiple instances.
    Falls back to in-memory limiting if Redis is unavailable.
    """

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        # In-memory fallback (for single instance only)
        self._memory_store: dict[str, list[float]] = {}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limits
        is_allowed, retry_after = await self._check_rate_limit(client_id)

        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                client_id=client_id,
                path=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            await self._get_remaining(client_id)
        )

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get unique identifier for the client.

        Uses X-Forwarded-For header if behind proxy, otherwise client IP.
        Can also use API key if authenticated.
        """
        # Check for forwarded IP (behind load balancer/proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP in the chain (original client)
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Optionally include authenticated user ID for more granular limiting
        # auth_header = request.headers.get("Authorization")
        # if auth_header:
        #     return f"user:{extract_user_id(auth_header)}"

        return f"ip:{client_ip}"

    async def _check_rate_limit(
        self,
        client_id: str,
    ) -> tuple[bool, int]:
        """Check if request is within rate limits.

        Returns (is_allowed, retry_after_seconds).
        """
        try:
            return await self._check_rate_limit_redis(client_id)
        except Exception as e:
            logger.warning(f"Redis rate limit check failed, using memory: {e}")
            return self._check_rate_limit_memory(client_id)

    async def _check_rate_limit_redis(
        self,
        client_id: str,
    ) -> tuple[bool, int]:
        """Check rate limit using Redis sliding window."""
        from app.core.redis import redis_client

        if redis_client is None:
            raise RuntimeError("Redis not available")

        now = time.time()
        minute_key = f"ratelimit:{client_id}:minute"
        hour_key = f"ratelimit:{client_id}:hour"

        pipe = redis_client.pipeline()

        # Remove old entries and count recent ones
        minute_ago = now - 60
        hour_ago = now - 3600

        # Minute window
        pipe.zremrangebyscore(minute_key, 0, minute_ago)
        pipe.zcard(minute_key)

        # Hour window
        pipe.zremrangebyscore(hour_key, 0, hour_ago)
        pipe.zcard(hour_key)

        results = await pipe.execute()
        minute_count = results[1]
        hour_count = results[3]

        # Check limits
        if minute_count >= self.requests_per_minute:
            return False, 60
        if hour_count >= self.requests_per_hour:
            return False, 3600

        # Add current request
        pipe = redis_client.pipeline()
        pipe.zadd(minute_key, {str(now): now})
        pipe.expire(minute_key, 60)
        pipe.zadd(hour_key, {str(now): now})
        pipe.expire(hour_key, 3600)
        await pipe.execute()

        return True, 0

    def _check_rate_limit_memory(
        self,
        client_id: str,
    ) -> tuple[bool, int]:
        """Fallback in-memory rate limiting."""
        now = time.time()

        if client_id not in self._memory_store:
            self._memory_store[client_id] = []

        # Clean old entries
        minute_ago = now - 60
        self._memory_store[client_id] = [
            ts for ts in self._memory_store[client_id] if ts > minute_ago
        ]

        # Check limit
        if len(self._memory_store[client_id]) >= self.requests_per_minute:
            return False, 60

        # Add current request
        self._memory_store[client_id].append(now)

        return True, 0

    async def _get_remaining(self, client_id: str) -> int:
        """Get remaining requests in current window."""
        try:
            from app.core.redis import redis_client

            if redis_client is None:
                raise RuntimeError("Redis not available")

            minute_key = f"ratelimit:{client_id}:minute"
            count = await redis_client.zcard(minute_key)
            return max(0, self.requests_per_minute - count)
        except Exception:
            if client_id in self._memory_store:
                return max(
                    0, self.requests_per_minute - len(self._memory_store[client_id])
                )
            return self.requests_per_minute


def create_rate_limit_middleware(
    app: Any,
    requests_per_minute: int | None = None,
    requests_per_hour: int | None = None,
) -> RateLimitMiddleware:
    """Factory function to create rate limit middleware with config."""
    return RateLimitMiddleware(
        app,
        requests_per_minute=requests_per_minute
        or getattr(settings, "rate_limit_per_minute", 60),
        requests_per_hour=requests_per_hour
        or getattr(settings, "rate_limit_per_hour", 1000),
    )
