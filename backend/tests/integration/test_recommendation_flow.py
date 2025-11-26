"""Integration tests for the full recommendation flow."""

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import EnergyPlan, Supplier


@pytest.mark.asyncio
async def test_full_recommendation_flow(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Test the complete recommendation flow from customer creation to recommendations."""
    # Step 1: Create a supplier
    supplier = Supplier(
        name="Test Energy Co",
        rating=Decimal("4.5"),
        customer_service_rating=Decimal("4.2"),
    )
    db_session.add(supplier)
    await db_session.flush()

    # Step 2: Create energy plans
    plans = [
        EnergyPlan(
            supplier_id=supplier.id,
            name="Budget Plan",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.08"),
            monthly_fee=Decimal("10.00"),
            contract_length_months=24,
            renewable_percentage=10,
        ),
        EnergyPlan(
            supplier_id=supplier.id,
            name="Green Plan",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.12"),
            monthly_fee=Decimal("5.00"),
            contract_length_months=12,
            renewable_percentage=100,
        ),
        EnergyPlan(
            supplier_id=supplier.id,
            name="Flex Plan",
            rate_type="variable",
            rate_per_kwh=Decimal("0.10"),
            monthly_fee=Decimal("0.00"),
            contract_length_months=1,
            renewable_percentage=50,
        ),
    ]
    for plan in plans:
        db_session.add(plan)
    await db_session.commit()

    # Step 3: Create a customer with usage data
    usage_data = [
        {"usage_date": f"2024-{month:02d}-01", "kwh_usage": 900 + (month * 20)}
        for month in range(1, 13)
    ]

    customer_response = await client.post(
        "/api/v1/customers",
        json={
            "external_id": "test-customer-flow",
            "usage_data": usage_data,
        },
    )

    assert customer_response.status_code == 201
    customer = customer_response.json()
    customer_id = customer["id"]

    # Step 4: Set customer preferences (cost-focused)
    preferences_response = await client.put(
        f"/api/v1/preferences/{customer_id}",
        json={
            "cost_savings_weight": 0.50,
            "flexibility_weight": 0.20,
            "renewable_weight": 0.15,
            "supplier_rating_weight": 0.15,
            "min_renewable_percentage": 0,
            "avoid_variable_rates": False,
        },
    )

    assert preferences_response.status_code == 200

    # Step 5: Generate recommendations
    recommendations_response = await client.post(
        "/api/v1/recommendations",
        json={
            "customer_id": customer_id,
            "include_switching_analysis": True,
        },
    )

    assert recommendations_response.status_code == 200
    recommendations = recommendations_response.json()

    # Verify recommendation structure
    assert "recommendations" in recommendations
    assert len(recommendations["recommendations"]) == 3
    assert "best_savings" in recommendations
    assert "processing_time_ms" in recommendations

    # Verify each recommendation has required fields
    for rec in recommendations["recommendations"]:
        assert "rank" in rec
        assert "plan" in rec
        assert "overall_score" in rec
        assert "projected_annual_cost" in rec
        assert "projected_annual_savings" in rec
        assert "explanation" in rec
        assert "risk_flags" in rec
        assert "confidence_level" in rec

    # With cost-focused preferences, Budget Plan should rank high
    top_recommendation = recommendations["recommendations"][0]
    assert top_recommendation["rank"] == 1


@pytest.mark.asyncio
async def test_recommendation_with_green_preferences(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Test that green preferences rank renewable plans higher."""
    # Create supplier and plans
    supplier = Supplier(
        name="Green Test Co",
        rating=Decimal("4.0"),
    )
    db_session.add(supplier)
    await db_session.flush()

    plans = [
        EnergyPlan(
            supplier_id=supplier.id,
            name="Cheap Dirty Plan",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.07"),
            monthly_fee=Decimal("5.00"),
            contract_length_months=12,
            renewable_percentage=5,
        ),
        EnergyPlan(
            supplier_id=supplier.id,
            name="100% Green Plan",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.14"),
            monthly_fee=Decimal("8.00"),
            contract_length_months=12,
            renewable_percentage=100,
        ),
    ]
    for plan in plans:
        db_session.add(plan)
    await db_session.commit()

    # Create customer
    usage_data = [
        {"usage_date": f"2024-{month:02d}-01", "kwh_usage": 1000}
        for month in range(1, 13)
    ]

    customer_response = await client.post(
        "/api/v1/customers",
        json={
            "external_id": "green-customer-test",
            "usage_data": usage_data,
        },
    )
    customer_id = customer_response.json()["id"]

    # Generate recommendations with green-focused preferences
    recommendations_response = await client.post(
        "/api/v1/recommendations",
        json={
            "customer_id": customer_id,
            "preferences": {
                "cost_savings_weight": 0.10,
                "flexibility_weight": 0.10,
                "renewable_weight": 0.70,
                "supplier_rating_weight": 0.10,
                "min_renewable_percentage": 0,
                "avoid_variable_rates": False,
            },
        },
    )

    assert recommendations_response.status_code == 200
    recommendations = recommendations_response.json()

    # With green-focused preferences, 100% Green Plan should rank first
    top_plan_name = recommendations["recommendations"][0]["plan"]["name"]
    assert top_plan_name == "100% Green Plan"


@pytest.mark.asyncio
async def test_recommendation_insufficient_data(
    client: AsyncClient,
    _db_session: AsyncSession,
) -> None:
    """Test that insufficient usage data returns appropriate error."""
    # Create customer with only 2 months of data
    usage_data = [
        {"usage_date": "2024-01-01", "kwh_usage": 1000},
        {"usage_date": "2024-02-01", "kwh_usage": 950},
    ]

    customer_response = await client.post(
        "/api/v1/customers",
        json={
            "external_id": "insufficient-data-customer",
            "usage_data": usage_data,
        },
    )
    customer_id = customer_response.json()["id"]

    # Try to generate recommendations
    recommendations_response = await client.post(
        "/api/v1/recommendations",
        json={"customer_id": customer_id},
    )

    # Should fail with insufficient data
    assert recommendations_response.status_code == 400
    assert "insufficient" in recommendations_response.json()["detail"].lower()
