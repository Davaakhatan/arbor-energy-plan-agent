"""Unit tests for contract timing analyzer."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.services.contract_analyzer import (
    ContractAnalyzer,
    SwitchRecommendation,
)


class TestContractAnalyzer:
    """Tests for ContractAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> ContractAnalyzer:
        """Create analyzer instance."""
        return ContractAnalyzer()

    @pytest.fixture
    def today(self) -> date:
        """Fixed date for testing."""
        return date(2024, 6, 15)

    def test_no_contract_switch_now(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test recommendation when no active contract."""
        analysis = analyzer.analyze_switch_timing(
            current_contract_end=None,
            early_termination_fee=Decimal("0"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("80"),
            today=today,
        )

        assert analysis.has_active_contract is False
        assert analysis.switch_recommendation == SwitchRecommendation.SWITCH_NOW
        assert analysis.optimal_switch_date == today
        assert analysis.immediate_switch_savings == Decimal("240")  # $20/month * 12

    def test_expired_contract_switch_now(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test recommendation when contract has expired."""
        past_date = today - timedelta(days=30)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=past_date,
            early_termination_fee=Decimal("150"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("80"),
            today=today,
        )

        assert analysis.has_active_contract is False
        assert analysis.switch_recommendation == SwitchRecommendation.SWITCH_NOW

    def test_active_contract_etf_worthwhile(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test when paying ETF is worthwhile due to high savings."""
        # Contract ends in 6 months
        contract_end = today + timedelta(days=180)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("100"),
            current_plan_monthly_cost=Decimal("150"),
            new_plan_monthly_cost=Decimal("100"),
            today=today,
        )

        assert analysis.has_active_contract is True
        # $50/month * 6 months = $300 savings, minus $100 ETF = $200 net savings
        assert analysis.immediate_switch_savings == Decimal("200")
        assert analysis.switch_recommendation == SwitchRecommendation.SWITCH_NOW

    def test_active_contract_wait_recommended(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test when waiting for contract end is recommended."""
        # Contract ends in 2 months
        contract_end = today + timedelta(days=60)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("200"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("90"),
            today=today,
        )

        assert analysis.has_active_contract is True
        # $10/month * 2 months = $20 savings, minus $200 ETF = -$180
        assert analysis.immediate_switch_savings < 0
        assert analysis.switch_recommendation == SwitchRecommendation.WAIT_FOR_CONTRACT_END
        assert analysis.optimal_switch_date == contract_end

    def test_contract_ending_soon(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test when contract ends within 30 days."""
        # Contract ends in 15 days
        contract_end = today + timedelta(days=15)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("100"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("80"),
            today=today,
        )

        assert analysis.has_active_contract is True
        assert analysis.days_until_contract_end == 15
        # With only 15 days left, even if ETF is "worth it", recommend waiting
        assert analysis.switch_recommendation == SwitchRecommendation.SWITCH_SOON
        assert analysis.optimal_switch_date == contract_end

    def test_new_plan_more_expensive(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test when new plan is more expensive."""
        analysis = analyzer.analyze_switch_timing(
            current_contract_end=None,
            early_termination_fee=Decimal("0"),
            current_plan_monthly_cost=Decimal("80"),
            new_plan_monthly_cost=Decimal("100"),
            today=today,
        )

        assert analysis.switch_recommendation == SwitchRecommendation.NOT_BENEFICIAL
        assert analysis.immediate_switch_savings < 0
        assert "not save" in analysis.explanation.lower()

    def test_break_even_calculation(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test break-even month calculation."""
        contract_end = today + timedelta(days=365)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("120"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("80"),
            today=today,
        )

        # $120 ETF / $20 monthly savings = 6 months to break even
        assert analysis.break_even_months == 7  # Rounds up

    def test_switching_windows(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test switching window calculations."""
        contract_end = today + timedelta(days=90)

        windows = analyzer.get_switching_windows(
            contract_end_date=contract_end,
            today=today,
        )

        assert windows["today"] == today
        assert windows["contract_end"] == contract_end
        assert windows["optimal_notice_date"] == contract_end - timedelta(days=60)
        assert windows["final_switch_date"] == contract_end - timedelta(days=7)

    def test_switching_windows_no_contract(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test switching windows with no contract."""
        windows = analyzer.get_switching_windows(
            contract_end_date=None,
            today=today,
        )

        assert windows["today"] == today
        assert windows["contract_end"] is None
        assert windows["optimal_notice_date"] is None

    def test_switching_windows_contract_ending_soon(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test switching windows when contract ends very soon."""
        # Contract ends in 20 days
        contract_end = today + timedelta(days=20)

        windows = analyzer.get_switching_windows(
            contract_end_date=contract_end,
            today=today,
        )

        # Optimal notice date would be in the past, so use today
        assert windows["optimal_notice_date"] == today

    def test_analysis_details_included(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test that analysis includes detailed breakdown."""
        contract_end = today + timedelta(days=180)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("100"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("80"),
            today=today,
        )

        assert "monthly_savings" in analysis.details
        assert "annual_savings" in analysis.details
        assert len(analysis.explanation) > 0
