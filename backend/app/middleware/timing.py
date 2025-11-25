"""Response time tracking middleware."""

import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)

# Performance thresholds (in seconds)
SLOW_REQUEST_THRESHOLD = 1.0  # Log warning for requests > 1s
CRITICAL_REQUEST_THRESHOLD = 2.0  # Log error for requests > 2s


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track and log API response times.

    Adds X-Response-Time header and logs slow requests.
    """

    def __init__(self, app: Any, slow_threshold: float = SLOW_REQUEST_THRESHOLD):
        super().__init__(app)
        self.slow_threshold = slow_threshold

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and track timing."""
        start_time = time.perf_counter()

        response = await call_next(request)

        # Calculate response time
        process_time = time.perf_counter() - start_time
        process_time_ms = int(process_time * 1000)

        # Add timing header
        response.headers["X-Response-Time"] = f"{process_time_ms}ms"

        # Log based on thresholds
        path = request.url.path
        method = request.method

        if process_time >= CRITICAL_REQUEST_THRESHOLD:
            logger.error(
                "Critical slow request",
                method=method,
                path=path,
                response_time_ms=process_time_ms,
                status_code=response.status_code,
            )
        elif process_time >= self.slow_threshold:
            logger.warning(
                "Slow request detected",
                method=method,
                path=path,
                response_time_ms=process_time_ms,
                status_code=response.status_code,
            )
        else:
            logger.debug(
                "Request completed",
                method=method,
                path=path,
                response_time_ms=process_time_ms,
                status_code=response.status_code,
            )

        return response
