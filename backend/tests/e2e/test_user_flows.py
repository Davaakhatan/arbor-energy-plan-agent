"""End-to-end tests for complete user flows."""

import time
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import EnergyPlan, Supplier


@pytest.mark.asyncio
class TestNewCustomerOnboarding:
    """Test the complete new customer onboarding flow."""

    async def test_new_customer_complete_journey(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Test: New customer uploads data -> sets preferences -> gets recommendations."""
        # Setup: Create suppliers and plans
        suppliers = await self._create_test_suppliers(db_session)
        await self._create_test_plans(db_session, suppliers)

        # Step 1: Customer submits usage data
        usage_data = [
            {"usage_date": f"2024-{month:02d}-01", "kwh_usage": 850 + (month * 30)}
            for month in range(1, 13)
        ]

        customer_response = await client.post(
            "/api/v1/customers",
            json={
                "external_id": "new-customer-e2e-001",
                "usage_data": usage_data,
            },
        )
        assert customer_response.status_code == 201
        customer = customer_response.json()
        customer_id = customer["id"]
        assert customer["external_id"] == "new-customer-e2e-001"

        # Step 2: Customer sets preferences (eco-conscious user)
        preferences_response = await client.put(
            f"/api/v1/preferences/{customer_id}",
            json={
                "cost_savings_weight": 0.30,
                "flexibility_weight": 0.15,
                "renewable_weight": 0.40,
                "supplier_rating_weight": 0.15,
                "min_renewable_percentage": 50,
                "avoid_variable_rates": True,
            },
        )
        assert preferences_response.status_code == 200

        # Step 3: Generate recommendations
        start_time = time.perf_counter()
        recommendations_response = await client.post(
            "/api/v1/recommendations",
            json={"customer_id": customer_id},
        )
        end_time = time.perf_counter()

        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()

        # Verify performance target (< 2 seconds)
        assert (end_time - start_time) < 2.0, "Recommendation generation exceeded 2s"

        # Verify recommendations structure
        assert len(recommendations["recommendations"]) >= 1
        assert recommendations["usage_analysis"] is not None

        # With 50% min renewable, all recommendations should meet threshold
        for rec in recommendations["recommendations"]:
            assert rec["plan"]["renewable_percentage"] >= 50

        # Variable rates should be excluded
        for rec in recommendations["recommendations"]:
            assert rec["plan"]["rate_type"] != "variable"

    async def _create_test_suppliers(self, db_session: AsyncSession) -> list[Supplier]:
        """Create test suppliers."""
        suppliers = [
            Supplier(name="E2E Green Power", rating=Decimal("4.7")),
            Supplier(name="E2E Budget Electric", rating=Decimal("4.2")),
            Supplier(name="E2E Premium Energy", rating=Decimal("4.9")),
        ]
        for s in suppliers:
            db_session.add(s)
        await db_session.flush()
        return suppliers

    async def _create_test_plans(
        self, db_session: AsyncSession, suppliers: list[Supplier]
    ) -> list[EnergyPlan]:
        """Create test plans."""
        plans = [
            # Green Power plans
            EnergyPlan(
                supplier_id=suppliers[0].id,
                name="100% Renewable",
                rate_type="fixed",
                rate_per_kwh=Decimal("0.13"),
                monthly_fee=Decimal("10.00"),
                contract_length_months=12,
                renewable_percentage=100,
            ),
            EnergyPlan(
                supplier_id=suppliers[0].id,
                name="50% Green",
                rate_type="fixed",
                rate_per_kwh=Decimal("0.11"),
                monthly_fee=Decimal("8.00"),
                contract_length_months=12,
                renewable_percentage=50,
            ),
            # Budget Electric plans
            EnergyPlan(
                supplier_id=suppliers[1].id,
                name="Budget Saver",
                rate_type="fixed",
                rate_per_kwh=Decimal("0.08"),
                monthly_fee=Decimal("12.00"),
                contract_length_months=24,
                renewable_percentage=10,
            ),
            EnergyPlan(
                supplier_id=suppliers[1].id,
                name="Variable Value",
                rate_type="variable",
                rate_per_kwh=Decimal("0.07"),
                monthly_fee=Decimal("5.00"),
                contract_length_months=1,
                renewable_percentage=15,
            ),
            # Premium Energy plans
            EnergyPlan(
                supplier_id=suppliers[2].id,
                name="Premium Green",
                rate_type="fixed",
                rate_per_kwh=Decimal("0.15"),
                monthly_fee=Decimal("0.00"),
                contract_length_months=6,
                renewable_percentage=100,
            ),
        ]
        for p in plans:
            db_session.add(p)
        await db_session.commit()
        return plans


@pytest.mark.asyncio
class TestExistingCustomerSwitching:
    """Test flows for existing customers considering switching plans."""

    async def test_customer_with_current_plan_switching(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Test: Customer with current plan evaluates switching options."""
        # Setup: Create supplier and plans
        supplier = Supplier(name="E2E Current Provider", rating=Decimal("4.0"))
        db_session.add(supplier)
        await db_session.flush()

        current_plan = EnergyPlan(
            supplier_id=supplier.id,
            name="Current Expensive Plan",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.18"),
            monthly_fee=Decimal("15.00"),
            contract_length_months=24,
            early_termination_fee=Decimal("150.00"),
            renewable_percentage=20,
        )
        better_plan = EnergyPlan(
            supplier_id=supplier.id,
            name="Better Option",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.10"),
            monthly_fee=Decimal("10.00"),
            contract_length_months=12,
            early_termination_fee=Decimal("75.00"),
            renewable_percentage=50,
        )
        db_session.add(current_plan)
        db_session.add(better_plan)
        await db_session.commit()

        # Create customer with current plan and active contract
        usage_data = [
            {"usage_date": f"2024-{month:02d}-01", "kwh_usage": 1000}
            for month in range(1, 13)
        ]

        customer_response = await client.post(
            "/api/v1/customers",
            json={
                "external_id": "switching-customer-e2e",
                "current_plan_id": str(current_plan.id),
                "contract_end_date": "2025-06-01",
                "early_termination_fee": "150.00",
                "usage_data": usage_data,
            },
        )
        assert customer_response.status_code == 201
        customer_id = customer_response.json()["id"]

        # Generate recommendations with switching analysis
        recommendations_response = await client.post(
            "/api/v1/recommendations",
            json={
                "customer_id": customer_id,
                "include_switching_analysis": True,
            },
        )
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()

        # Should include current annual cost for comparison
        assert recommendations["current_annual_cost"] is not None

        # Each recommendation should have switching cost calculated
        for rec in recommendations["recommendations"]:
            assert "switching_cost" in rec
            assert "net_first_year_savings" in rec

        # Best savings should account for switching costs
        assert recommendations["best_savings"] is not None


@pytest.mark.asyncio
class TestPreferenceScenarios:
    """Test various preference combinations."""

    async def test_cost_focused_customer(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Test recommendations for cost-focused customer."""
        await self._setup_plans(db_session)

        customer_response = await client.post(
            "/api/v1/customers",
            json={
                "external_id": "cost-focused-e2e",
                "usage_data": self._get_usage_data(),
            },
        )
        customer_id = customer_response.json()["id"]

        recommendations_response = await client.post(
            "/api/v1/recommendations",
            json={
                "customer_id": customer_id,
                "preferences": {
                    "cost_savings_weight": 0.80,
                    "flexibility_weight": 0.10,
                    "renewable_weight": 0.05,
                    "supplier_rating_weight": 0.05,
                },
            },
        )
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()

        # Cost-focused should prioritize lowest cost plans
        top_rec = recommendations["recommendations"][0]
        assert top_rec["cost_score"] >= 0.7  # High cost score

    async def test_flexibility_focused_customer(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Test recommendations for flexibility-focused customer."""
        await self._setup_plans(db_session)

        customer_response = await client.post(
            "/api/v1/customers",
            json={
                "external_id": "flex-focused-e2e",
                "usage_data": self._get_usage_data(),
            },
        )
        customer_id = customer_response.json()["id"]

        recommendations_response = await client.post(
            "/api/v1/recommendations",
            json={
                "customer_id": customer_id,
                "preferences": {
                    "cost_savings_weight": 0.10,
                    "flexibility_weight": 0.70,
                    "renewable_weight": 0.10,
                    "supplier_rating_weight": 0.10,
                    "max_contract_months": 6,
                },
            },
        )
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()

        # All recommendations should have short contracts
        for rec in recommendations["recommendations"]:
            assert rec["plan"]["contract_length_months"] <= 6

    async def _setup_plans(self, db_session: AsyncSession) -> None:
        """Create test plans for preference scenarios."""
        supplier = Supplier(name="E2E Pref Test", rating=Decimal("4.5"))
        db_session.add(supplier)
        await db_session.flush()

        plans = [
            EnergyPlan(
                supplier_id=supplier.id,
                name="Cheapest Long Term",
                rate_type="fixed",
                rate_per_kwh=Decimal("0.07"),
                monthly_fee=Decimal("15.00"),
                contract_length_months=36,
                renewable_percentage=10,
            ),
            EnergyPlan(
                supplier_id=supplier.id,
                name="Flexible Monthly",
                rate_type="fixed",
                rate_per_kwh=Decimal("0.12"),
                monthly_fee=Decimal("5.00"),
                contract_length_months=1,
                renewable_percentage=30,
            ),
            EnergyPlan(
                supplier_id=supplier.id,
                name="Short Term",
                rate_type="fixed",
                rate_per_kwh=Decimal("0.11"),
                monthly_fee=Decimal("8.00"),
                contract_length_months=6,
                renewable_percentage=50,
            ),
        ]
        for p in plans:
            db_session.add(p)
        await db_session.commit()

    def _get_usage_data(self) -> list[dict]:
        """Get standard usage data."""
        return [
            {"usage_date": f"2024-{month:02d}-01", "kwh_usage": 900}
            for month in range(1, 13)
        ]


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in user flows."""

    async def test_invalid_customer_id(self, client: AsyncClient) -> None:
        """Test recommendations for non-existent customer."""
        response = await client.post(
            "/api/v1/recommendations",
            json={"customer_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert response.status_code == 404

    async def test_invalid_preferences_weights(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Test that invalid preference weights are rejected."""
        supplier = Supplier(name="E2E Error Test", rating=Decimal("4.0"))
        db_session.add(supplier)
        await db_session.flush()

        plan = EnergyPlan(
            supplier_id=supplier.id,
            name="Test Plan",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.10"),
            monthly_fee=Decimal("10.00"),
            contract_length_months=12,
            renewable_percentage=50,
        )
        db_session.add(plan)
        await db_session.commit()

        # Create customer
        customer_response = await client.post(
            "/api/v1/customers",
            json={
                "external_id": "error-test-e2e",
                "usage_data": [
                    {"usage_date": f"2024-{m:02d}-01", "kwh_usage": 1000}
                    for m in range(1, 13)
                ],
            },
        )
        customer_id = customer_response.json()["id"]

        # Try with weights that don't sum to 1.0
        response = await client.post(
            "/api/v1/recommendations",
            json={
                "customer_id": customer_id,
                "preferences": {
                    "cost_savings_weight": 0.90,
                    "flexibility_weight": 0.90,
                    "renewable_weight": 0.90,
                    "supplier_rating_weight": 0.90,
                },
            },
        )
        # Should either normalize weights or reject
        assert response.status_code in [200, 400, 422]

    async def test_no_matching_plans(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Test when no plans match the criteria."""
        # Create only low-renewable plans
        supplier = Supplier(name="E2E No Match", rating=Decimal("4.0"))
        db_session.add(supplier)
        await db_session.flush()

        plan = EnergyPlan(
            supplier_id=supplier.id,
            name="Dirty Plan",
            rate_type="fixed",
            rate_per_kwh=Decimal("0.10"),
            monthly_fee=Decimal("10.00"),
            contract_length_months=12,
            renewable_percentage=5,
        )
        db_session.add(plan)
        await db_session.commit()

        customer_response = await client.post(
            "/api/v1/customers",
            json={
                "external_id": "no-match-e2e",
                "usage_data": [
                    {"usage_date": f"2024-{m:02d}-01", "kwh_usage": 1000}
                    for m in range(1, 13)
                ],
            },
        )
        customer_id = customer_response.json()["id"]

        # Request 100% renewable minimum
        response = await client.post(
            "/api/v1/recommendations",
            json={
                "customer_id": customer_id,
                "preferences": {
                    "cost_savings_weight": 0.25,
                    "flexibility_weight": 0.25,
                    "renewable_weight": 0.25,
                    "supplier_rating_weight": 0.25,
                    "min_renewable_percentage": 100,
                },
            },
        )

        # Should return empty recommendations or warning
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations["recommendations"]) == 0 or len(recommendations.get("warnings", [])) > 0


@pytest.mark.asyncio
class TestPerformanceBenchmarks:
    """Test performance targets."""

    async def test_recommendation_under_2_seconds(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Verify recommendations are generated within 2 seconds."""
        # Create realistic dataset
        supplier = Supplier(name="E2E Perf Test", rating=Decimal("4.5"))
        db_session.add(supplier)
        await db_session.flush()

        # Create 10 plans (realistic catalog size)
        for i in range(10):
            plan = EnergyPlan(
                supplier_id=supplier.id,
                name=f"Plan {i+1}",
                rate_type="fixed" if i % 2 == 0 else "variable",
                rate_per_kwh=Decimal(f"0.{8 + i:02d}"),
                monthly_fee=Decimal(str(5 + i)),
                contract_length_months=12 * (1 + i % 3),
                renewable_percentage=10 * (i + 1),
            )
            db_session.add(plan)
        await db_session.commit()

        # Create customer
        customer_response = await client.post(
            "/api/v1/customers",
            json={
                "external_id": "perf-test-e2e",
                "usage_data": [
                    {"usage_date": f"2024-{m:02d}-01", "kwh_usage": 800 + m * 50}
                    for m in range(1, 13)
                ],
            },
        )
        customer_id = customer_response.json()["id"]

        # Measure recommendation time
        times = []
        for _ in range(3):  # Run 3 times to get average
            start = time.perf_counter()
            response = await client.post(
                "/api/v1/recommendations",
                json={"customer_id": customer_id},
            )
            end = time.perf_counter()
            assert response.status_code == 200
            times.append(end - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 2.0, f"Average recommendation time {avg_time:.2f}s exceeds 2s target"

        # Also verify the reported processing time
        last_response = response.json()
        assert last_response["processing_time_ms"] < 2000
