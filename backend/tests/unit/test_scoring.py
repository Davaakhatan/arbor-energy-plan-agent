"""Unit tests for MCDA scoring engine."""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.plan import EnergyPlan, Supplier
from app.models.preference import CustomerPreference
from app.services.scoring import ScoringEngine


class TestScoringEngine:
    """Tests for ScoringEngine."""

    @pytest.fixture
    def engine(self) -> ScoringEngine:
        """Create scoring engine instance."""
        return ScoringEngine()

    @pytest.fixture
    def sample_supplier(self) -> Supplier:
        """Create a sample supplier."""
        supplier = Supplier.__new__(Supplier)
        supplier.id = uuid4()
        supplier.name = "Test Supplier"
        supplier.rating = Decimal("4.5")
        return supplier

    @pytest.fixture
    def sample_plans(self, sample_supplier: Supplier) -> list[EnergyPlan]:
        """Create sample plans for testing."""
        plans = []

        # Cheap plan with low renewable
        plan1 = EnergyPlan.__new__(EnergyPlan)
        plan1.id = uuid4()
        plan1.name = "Cheap Plan"
        plan1.rate_per_kwh = Decimal("0.08")
        plan1.monthly_fee = Decimal("10.00")
        plan1.contract_length_months = 24
        plan1.renewable_percentage = 10
        plan1.rate_type = "fixed"
        plan1.supplier = sample_supplier
        plans.append(plan1)

        # Expensive plan with high renewable
        plan2 = EnergyPlan.__new__(EnergyPlan)
        plan2.id = uuid4()
        plan2.name = "Green Plan"
        plan2.rate_per_kwh = Decimal("0.12")
        plan2.monthly_fee = Decimal("5.00")
        plan2.contract_length_months = 12
        plan2.renewable_percentage = 100
        plan2.rate_type = "fixed"
        plan2.supplier = sample_supplier
        plans.append(plan2)

        # Flexible plan
        plan3 = EnergyPlan.__new__(EnergyPlan)
        plan3.id = uuid4()
        plan3.name = "Flex Plan"
        plan3.rate_per_kwh = Decimal("0.10")
        plan3.monthly_fee = Decimal("0.00")
        plan3.contract_length_months = 1
        plan3.renewable_percentage = 50
        plan3.rate_type = "variable"
        plan3.supplier = sample_supplier
        plans.append(plan3)

        return plans

    @pytest.fixture
    def cost_focused_preferences(self) -> CustomerPreference:
        """Create cost-focused preference."""
        pref = CustomerPreference.__new__(CustomerPreference)
        pref.customer_id = uuid4()
        pref.cost_savings_weight = Decimal("0.70")
        pref.flexibility_weight = Decimal("0.10")
        pref.renewable_weight = Decimal("0.10")
        pref.supplier_rating_weight = Decimal("0.10")
        return pref

    @pytest.fixture
    def green_focused_preferences(self) -> CustomerPreference:
        """Create renewable-focused preference."""
        pref = CustomerPreference.__new__(CustomerPreference)
        pref.customer_id = uuid4()
        pref.cost_savings_weight = Decimal("0.10")
        pref.flexibility_weight = Decimal("0.10")
        pref.renewable_weight = Decimal("0.70")
        pref.supplier_rating_weight = Decimal("0.10")
        return pref

    def test_score_plans_cost_focused(
        self,
        engine: ScoringEngine,
        sample_plans: list[EnergyPlan],
        cost_focused_preferences: CustomerPreference,
    ) -> None:
        """Test that cost-focused preferences rank cheap plans higher."""
        # Create costs for each plan
        costs = {
            sample_plans[0].id: {"annual_cost": Decimal("1200")},  # Cheap
            sample_plans[1].id: {"annual_cost": Decimal("1500")},  # Expensive
            sample_plans[2].id: {"annual_cost": Decimal("1300")},  # Middle
        }

        scored = engine.score_plans(
            sample_plans, costs, cost_focused_preferences
        )

        # Sort by overall score
        sorted_plans = sorted(
            scored, key=lambda x: x["overall_score"], reverse=True
        )

        # Cheapest plan should rank first with cost-focused preferences
        assert sorted_plans[0]["plan"].name == "Cheap Plan"

    def test_score_plans_green_focused(
        self,
        engine: ScoringEngine,
        sample_plans: list[EnergyPlan],
        green_focused_preferences: CustomerPreference,
    ) -> None:
        """Test that green-focused preferences rank renewable plans higher."""
        costs = {
            sample_plans[0].id: {"annual_cost": Decimal("1200")},
            sample_plans[1].id: {"annual_cost": Decimal("1500")},
            sample_plans[2].id: {"annual_cost": Decimal("1300")},
        }

        scored = engine.score_plans(
            sample_plans, costs, green_focused_preferences
        )

        sorted_plans = sorted(
            scored, key=lambda x: x["overall_score"], reverse=True
        )

        # 100% renewable plan should rank first with green-focused preferences
        assert sorted_plans[0]["plan"].name == "Green Plan"

    def test_score_all_components_calculated(
        self,
        engine: ScoringEngine,
        sample_plans: list[EnergyPlan],
        cost_focused_preferences: CustomerPreference,
    ) -> None:
        """Test that all score components are calculated."""
        costs = {
            sample_plans[0].id: {"annual_cost": Decimal("1200")},
            sample_plans[1].id: {"annual_cost": Decimal("1500")},
            sample_plans[2].id: {"annual_cost": Decimal("1300")},
        }

        scored = engine.score_plans(
            sample_plans, costs, cost_focused_preferences
        )

        for plan_score in scored:
            assert "cost_score" in plan_score
            assert "flexibility_score" in plan_score
            assert "renewable_score" in plan_score
            assert "rating_score" in plan_score
            assert "overall_score" in plan_score
            assert 0 <= plan_score["overall_score"] <= 1

    def test_empty_plans_returns_empty(
        self,
        engine: ScoringEngine,
        cost_focused_preferences: CustomerPreference,
    ) -> None:
        """Test that empty plan list returns empty scores."""
        scored = engine.score_plans([], {}, cost_focused_preferences)
        assert scored == []
