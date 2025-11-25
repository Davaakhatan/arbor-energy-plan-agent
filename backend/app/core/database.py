"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables.

    Creates tables that don't exist and silently skips those that do.
    Uses Alembic migrations for production; this is for dev/initial setup.
    """
    from sqlalchemy import inspect

    async with engine.begin() as conn:
        # Get existing tables
        def get_existing_tables(sync_conn):
            inspector = inspect(sync_conn)
            return set(inspector.get_table_names())

        existing = await conn.run_sync(get_existing_tables)

        # Only create tables that don't exist
        tables_to_create = [
            table for table in Base.metadata.sorted_tables
            if table.name not in existing
        ]

        if tables_to_create:
            # Create only missing tables
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn,
                    tables=tables_to_create,
                    checkfirst=True
                )
            )


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
