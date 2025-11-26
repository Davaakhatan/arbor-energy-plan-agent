"""Unit tests for cost calculator service."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest

from app.services.cost_calculator import CostCalculator


class TestCostCalculator:
    """Tests for CostCalculator service."""

    @pytest.fixture
    def calculator(self) -> CostCalculator:
        """Create calculator instance."""
        return CostCalculator()

    @pytest.fixture
    def sample_usage(self) -> list[Any]:
        """Create sample usage data."""
        # Create mock usage data (12 months, 1000 kWh each)
        usage = []
        for month in range(1, 13):
            u = SimpleNamespace()
            u.usage_date = date(2024, month, 1)
            u.kwh_usage = Decimal("1000.00")
            usage.append(u)
        return usage

    @pytest.fixture
    def sample_plan(self) -> Any:
        """Create sample plan."""
        plan = SimpleNamespace()
        plan.rate_per_kwh = Decimal("0.10")
        plan.monthly_fee = Decimal("10.00")
        plan.contract_length_months = 12
        plan.renewable_percentage = 50
        plan.rate_type = "fixed"
        return plan

    def test_calculate_annual_cost_basic(
        self,
        calculator: CostCalculator,
        sample_usage: list[CustomerUsage],
        sample_plan: EnergyPlan,
    ) -> None:
        """Test basic annual cost calculation."""
        cost = calculator.calculate_annual_cost(sample_usage, sample_plan)

        # 12 months * 1000 kWh * $0.10/kWh = $1200
        # Plus 12 months * $10 monthly fee = $120
        # Total = $1320
        assert cost == Decimal("1320.00")

    def test_calculate_annual_cost_partial_year(
        self,
        calculator: CostCalculator,
        sample_plan: Any,
    ) -> None:
        """Test annual cost with less than 12 months of data."""
        # 6 months of data
        usage = []
        for month in range(1, 7):
            u = SimpleNamespace()
            u.usage_date = date(2024, month, 1)
            u.kwh_usage = Decimal("1000.00")
            usage.append(u)

        cost = calculator.calculate_annual_cost(usage, sample_plan)

        # Should annualize: (6000 / 6) * 12 = 12000 kWh annual
        # 12000 * $0.10 = $1200 + $120 fees = $1320
        assert cost == Decimal("1320.00")

    def test_calculate_annual_cost_empty_usage(
        self,
        calculator: CostCalculator,
        sample_plan: Any,
    ) -> None:
        """Test with no usage data."""
        cost = calculator.calculate_annual_cost([], sample_plan)
        assert cost == Decimal("0.00")

    def test_calculate_savings_beneficial(
        self,
        calculator: CostCalculator,
    ) -> None:
        """Test savings calculation when switching is beneficial."""
        result = calculator.calculate_savings(
            current_cost=Decimal("1500.00"),
            new_cost=Decimal("1200.00"),
            switching_cost=Decimal("100.00"),
        )

        assert result["annual_savings"] == Decimal("300.00")
        assert result["first_year_net_savings"] == Decimal("200.00")
        assert result["is_beneficial"] is True
        assert result["break_even_months"] == 4  # $100 / ($300/12) = 4 months

    def test_calculate_savings_not_beneficial(
        self,
        calculator: CostCalculator,
    ) -> None:
        """Test savings calculation when switching is not beneficial."""
        result = calculator.calculate_savings(
            current_cost=Decimal("1200.00"),
            new_cost=Decimal("1200.00"),
            switching_cost=Decimal("100.00"),
        )

        assert result["annual_savings"] == Decimal("0.00")
        assert result["first_year_net_savings"] == Decimal("-100.00")
        assert result["is_beneficial"] is False
