"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.logging import get_logger, setup_logging
from app.core.redis import close_redis, init_redis

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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

    # Initialize Redis
    try:
        await init_redis()
        logger.info("Redis initialized")
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

    # Include API routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

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
