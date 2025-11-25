"""Seed data for development and testing."""

import asyncio
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker, init_db
from app.core.logging import get_logger, setup_logging
from app.models.plan import EnergyPlan, Supplier

setup_logging()
logger = get_logger(__name__)

# Seed data for suppliers
SUPPLIERS = [
    {
        "id": uuid4(),
        "name": "Green Power Co",
        "rating": Decimal("4.5"),
        "website": "https://greenpower.example.com",
        "customer_service_rating": Decimal("4.3"),
    },
    {
        "id": uuid4(),
        "name": "EcoEnergy Solutions",
        "rating": Decimal("4.2"),
        "website": "https://ecoenergy.example.com",
        "customer_service_rating": Decimal("4.0"),
    },
    {
        "id": uuid4(),
        "name": "ValueElectric",
        "rating": Decimal("3.8"),
        "website": "https://valueelectric.example.com",
        "customer_service_rating": Decimal("3.5"),
    },
    {
        "id": uuid4(),
        "name": "SunState Energy",
        "rating": Decimal("4.7"),
        "website": "https://sunstate.example.com",
        "customer_service_rating": Decimal("4.6"),
    },
    {
        "id": uuid4(),
        "name": "Budget Power",
        "rating": Decimal("3.5"),
        "website": "https://budgetpower.example.com",
        "customer_service_rating": Decimal("3.2"),
    },
]


def get_plans(suppliers: list[dict]) -> list[dict]:
    """Generate energy plans for each supplier."""
    plans = []

    # Green Power Co plans
    plans.extend([
        {
            "supplier_id": suppliers[0]["id"],
            "name": "Green Basic",
            "description": "Affordable green energy for budget-conscious households",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.095"),
            "monthly_fee": Decimal("5.99"),
            "contract_length_months": 12,
            "early_termination_fee": Decimal("75.00"),
            "renewable_percentage": 50,
        },
        {
            "supplier_id": suppliers[0]["id"],
            "name": "Green Premium",
            "description": "100% renewable energy with premium service",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.125"),
            "monthly_fee": Decimal("9.99"),
            "contract_length_months": 24,
            "early_termination_fee": Decimal("150.00"),
            "renewable_percentage": 100,
        },
        {
            "supplier_id": suppliers[0]["id"],
            "name": "Green Flex",
            "description": "Month-to-month green energy with no commitment",
            "rate_type": "variable",
            "rate_per_kwh": Decimal("0.115"),
            "monthly_fee": Decimal("0.00"),
            "contract_length_months": 1,
            "early_termination_fee": Decimal("0.00"),
            "renewable_percentage": 75,
        },
    ])

    # EcoEnergy Solutions plans
    plans.extend([
        {
            "supplier_id": suppliers[1]["id"],
            "name": "Eco Saver",
            "description": "Low-cost energy with environmental responsibility",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.088"),
            "monthly_fee": Decimal("7.99"),
            "contract_length_months": 12,
            "early_termination_fee": Decimal("100.00"),
            "renewable_percentage": 35,
        },
        {
            "supplier_id": suppliers[1]["id"],
            "name": "Eco Max",
            "description": "Maximum renewable energy percentage",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.135"),
            "monthly_fee": Decimal("4.99"),
            "contract_length_months": 18,
            "early_termination_fee": Decimal("125.00"),
            "renewable_percentage": 100,
        },
    ])

    # ValueElectric plans
    plans.extend([
        {
            "supplier_id": suppliers[2]["id"],
            "name": "Value Basic",
            "description": "Simple, affordable electricity",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.082"),
            "monthly_fee": Decimal("9.99"),
            "contract_length_months": 12,
            "early_termination_fee": Decimal("50.00"),
            "renewable_percentage": 15,
        },
        {
            "supplier_id": suppliers[2]["id"],
            "name": "Value Plus",
            "description": "Better rates with longer commitment",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.075"),
            "monthly_fee": Decimal("12.99"),
            "contract_length_months": 24,
            "early_termination_fee": Decimal("175.00"),
            "renewable_percentage": 20,
        },
        {
            "supplier_id": suppliers[2]["id"],
            "name": "Value Index",
            "description": "Rates tied to wholesale market prices",
            "rate_type": "indexed",
            "rate_per_kwh": Decimal("0.078"),
            "monthly_fee": Decimal("4.99"),
            "contract_length_months": 6,
            "early_termination_fee": Decimal("25.00"),
            "renewable_percentage": 10,
        },
    ])

    # SunState Energy plans
    plans.extend([
        {
            "supplier_id": suppliers[3]["id"],
            "name": "Solar Standard",
            "description": "Solar-powered energy at competitive rates",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.105"),
            "monthly_fee": Decimal("6.99"),
            "contract_length_months": 12,
            "early_termination_fee": Decimal("100.00"),
            "renewable_percentage": 85,
        },
        {
            "supplier_id": suppliers[3]["id"],
            "name": "Solar Premium",
            "description": "100% solar with time-of-use savings",
            "rate_type": "time_of_use",
            "rate_per_kwh": Decimal("0.098"),
            "monthly_fee": Decimal("8.99"),
            "contract_length_months": 24,
            "early_termination_fee": Decimal("200.00"),
            "renewable_percentage": 100,
        },
        {
            "supplier_id": suppliers[3]["id"],
            "name": "Solar Flex",
            "description": "Flexible solar plan with no contract",
            "rate_type": "variable",
            "rate_per_kwh": Decimal("0.118"),
            "monthly_fee": Decimal("0.00"),
            "contract_length_months": 1,
            "early_termination_fee": Decimal("0.00"),
            "renewable_percentage": 90,
        },
    ])

    # Budget Power plans
    plans.extend([
        {
            "supplier_id": suppliers[4]["id"],
            "name": "Budget Basic",
            "description": "Lowest rates in the market",
            "rate_type": "fixed",
            "rate_per_kwh": Decimal("0.072"),
            "monthly_fee": Decimal("14.99"),
            "contract_length_months": 24,
            "early_termination_fee": Decimal("200.00"),
            "renewable_percentage": 5,
        },
        {
            "supplier_id": suppliers[4]["id"],
            "name": "Budget Flex",
            "description": "Low rates without long-term commitment",
            "rate_type": "variable",
            "rate_per_kwh": Decimal("0.085"),
            "monthly_fee": Decimal("8.99"),
            "contract_length_months": 3,
            "early_termination_fee": Decimal("0.00"),
            "renewable_percentage": 10,
        },
    ])

    return plans


async def seed_database(db: AsyncSession) -> None:
    """Seed the database with initial data."""
    logger.info("Starting database seeding...")

    # Check if data already exists
    from sqlalchemy import select
    result = await db.execute(select(Supplier).limit(1))
    if result.scalar_one_or_none():
        logger.info("Database already seeded, skipping...")
        return

    # Create suppliers
    suppliers = []
    for supplier_data in SUPPLIERS:
        supplier = Supplier(**supplier_data)
        db.add(supplier)
        suppliers.append(supplier_data)
    await db.flush()
    logger.info(f"Created {len(suppliers)} suppliers")

    # Create plans
    plans_data = get_plans(suppliers)
    for plan_data in plans_data:
        plan = EnergyPlan(**plan_data)
        db.add(plan)
    await db.flush()
    logger.info(f"Created {len(plans_data)} energy plans")

    await db.commit()
    logger.info("Database seeding completed successfully!")


async def main() -> None:
    """Main entry point for seeding."""
    # Initialize database tables
    await init_db()

    # Seed data
    async with async_session_maker() as session:
        await seed_database(session)


if __name__ == "__main__":
    asyncio.run(main())
