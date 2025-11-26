"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.logging import get_logger, setup_logging
from app.core.redis import close_redis, init_redis
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.timing import TimingMiddleware

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        environment=settings.environment,
        version=settings.app_version,
    )

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

    # Initialize Redis with timeout for faster startup
    import asyncio
    try:
        redis_client = await asyncio.wait_for(init_redis(), timeout=10.0)
        logger.info("Redis initialized")

        # Warm plan cache on startup for faster first requests (non-blocking)
        try:
            from app.core.database import get_async_session
            from app.core.redis import CacheService
            from app.services.cached_plan_service import CachedPlanService

            async for session in get_async_session():
                cache = CacheService(redis_client)
                plan_service = CachedPlanService(session, cache)
                plans_cached = await plan_service.warm_cache()
                logger.info(f"Cache warmed with {plans_cached} plans")
                break
        except Exception as e:
            logger.warning("Failed to warm cache", error=str(e))
    except TimeoutError:
        logger.warning("Redis initialization timed out after 10s, continuing without cache")
    except Exception as e:
        logger.warning("Failed to initialize Redis", error=str(e))
        # Continue without Redis - graceful degradation

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_redis()
    await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered energy plan recommendation agent for deregulated markets",
        version=settings.app_version,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add timing middleware (first to measure total response time)
    app.add_middleware(TimingMiddleware)

    # Add rate limiting middleware
    if settings.environment != "test":
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=getattr(settings, "rate_limit_per_minute", 60),
            requests_per_hour=getattr(settings, "rate_limit_per_hour", 1000),
        )

    # Include API routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Global exception handler for database integrity errors
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_request: Request, exc: IntegrityError) -> JSONResponse:
        """Handle database integrity errors gracefully."""
        logger.error("Database integrity error", error=str(exc))
        error_msg = str(exc.orig) if exc.orig else str(exc)
        if "foreign key" in error_msg.lower():
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid reference: one or more referenced records do not exist"},
            )
        return JSONResponse(
            status_code=400,
            content={"detail": "Database constraint violation"},
        )

    # Global exception handler for unhandled errors
    @app.exception_handler(Exception)
    async def global_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions gracefully."""
        logger.error("Unhandled exception", error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        workers=settings.workers,
    )
