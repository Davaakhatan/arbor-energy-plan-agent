"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from decimal import Decimal
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app
from app.models.customer import Customer, CustomerUsage
from app.models.plan import EnergyPlan, Supplier
from app.models.preference import CustomerPreference

# Test database URL (SQLite for simplicity in tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_supplier(db_session: AsyncSession) -> Supplier:
    """Create a sample supplier."""
    supplier = Supplier(
        name="Green Energy Co",
        rating=Decimal("4.5"),
        website="https://greenenergy.example.com",
        customer_service_rating=Decimal("4.2"),
    )
    db_session.add(supplier)
    await db_session.commit()
    await db_session.refresh(supplier)
    return supplier


@pytest_asyncio.fixture
async def sample_plan(
    db_session: AsyncSession,
    sample_supplier: Supplier,
) -> EnergyPlan:
    """Create a sample energy plan."""
    plan = EnergyPlan(
        supplier_id=sample_supplier.id,
        name="Basic Green Plan",
        description="Affordable green energy for households",
        rate_type="fixed",
        rate_per_kwh=Decimal("0.12"),
        monthly_fee=Decimal("9.99"),
        contract_length_months=12,
        early_termination_fee=Decimal("100.00"),
        renewable_percentage=50,
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest_asyncio.fixture
async def sample_customer(db_session: AsyncSession) -> Customer:
    """Create a sample customer with usage data."""
    customer = Customer(external_id="test-customer-001")
    db_session.add(customer)
    await db_session.flush()

    # Add 12 months of usage data
    usage_data = [
        CustomerUsage(
            customer_id=customer.id,
            usage_date=f"2024-{month:02d}-01",
            kwh_usage=Decimal(str(800 + (month * 50))),  # Varying usage
        )
        for month in range(1, 13)
    ]
    db_session.add_all(usage_data)
    await db_session.commit()
    await db_session.refresh(customer)
    return customer


@pytest_asyncio.fixture
async def sample_preferences(
    db_session: AsyncSession,
    sample_customer: Customer,
) -> CustomerPreference:
    """Create sample customer preferences."""
    preferences = CustomerPreference(
        customer_id=sample_customer.id,
        cost_savings_weight=Decimal("0.40"),
        flexibility_weight=Decimal("0.20"),
        renewable_weight=Decimal("0.25"),
        supplier_rating_weight=Decimal("0.15"),
        min_renewable_percentage=25,
    )
    db_session.add(preferences)
    await db_session.commit()
    await db_session.refresh(preferences)
    return preferences
