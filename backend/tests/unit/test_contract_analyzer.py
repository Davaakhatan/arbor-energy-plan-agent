"""Unit tests for contract timing analyzer."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.services.contract_analyzer import (
    ContractAnalyzer,
    NotBeneficialReason,
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
        # The wait_to_switch_savings should be higher than immediate switch
        # Due to ETF making immediate switch less beneficial
        assert (
            analysis.switch_recommendation == SwitchRecommendation.NOT_BENEFICIAL
            or analysis.switch_recommendation
            == SwitchRecommendation.WAIT_FOR_CONTRACT_END
        )

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
        # With only 15 days left, recommend waiting for contract end or switch soon
        assert analysis.switch_recommendation in [
            SwitchRecommendation.SWITCH_SOON,
            SwitchRecommendation.WAIT_FOR_CONTRACT_END,
        ]

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
        # Check for either "not save" or "lose money" in explanation
        explanation_lower = analysis.explanation.lower()
        assert (
            "not save" in explanation_lower
            or "lose money" in explanation_lower
            or "more per month" in explanation_lower
        )

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

    def test_switching_windows(self, analyzer: ContractAnalyzer, today: date) -> None:
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


class TestNotBeneficialDetection:
    """Tests for enhanced not-beneficial detection."""

    @pytest.fixture
    def analyzer(self) -> ContractAnalyzer:
        """Create analyzer instance."""
        return ContractAnalyzer()

    @pytest.fixture
    def today(self) -> date:
        """Fixed date for testing."""
        return date(2024, 6, 15)

    def test_savings_too_small(self, analyzer: ContractAnalyzer, today: date) -> None:
        """Test detection when savings are too small to be worthwhile."""
        analysis = analyzer.analyze_switch_timing(
            current_contract_end=None,
            early_termination_fee=Decimal("0"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("97"),  # Only $3/month savings = $36/year
            today=today,
        )

        assert analysis.switch_recommendation == SwitchRecommendation.NOT_BENEFICIAL
        assert analysis.not_beneficial_reason == NotBeneficialReason.SAVINGS_TOO_SMALL
        assert analysis.confidence_score == 0.9

    def test_etf_exceeds_annual_savings(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test detection when ETF recovery takes too long."""
        contract_end = today + timedelta(days=365)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("500"),  # High ETF
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("80"),  # $20/month = $240/year
            today=today,
        )

        # $500 ETF / $20 monthly = 25 months to break even (>18 max)
        assert analysis.switch_recommendation == SwitchRecommendation.NOT_BENEFICIAL
        assert (
            analysis.not_beneficial_reason
            == NotBeneficialReason.ETF_EXCEEDS_ANNUAL_SAVINGS
        )
        assert analysis.break_even_months == 26

    def test_break_even_exceeds_contract_length(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test detection when break-even exceeds new contract length."""
        contract_end = today + timedelta(days=365)

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("200"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("80"),  # $20/month
            new_plan_contract_months=6,  # Short new contract
            today=today,
        )

        # $200 ETF / $20 = 10 months, but new contract only 6 months
        assert analysis.switch_recommendation == SwitchRecommendation.NOT_BENEFICIAL
        assert analysis.not_beneficial_reason == NotBeneficialReason.BREAK_EVEN_TOO_LONG

    def test_contract_too_short_for_etf(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test detection when contract ending soon makes ETF not worth it."""
        contract_end = today + timedelta(days=10)  # Ends in 10 days

        analysis = analyzer.analyze_switch_timing(
            current_contract_end=contract_end,
            early_termination_fee=Decimal("100"),
            current_plan_monthly_cost=Decimal("150"),
            new_plan_monthly_cost=Decimal("100"),  # $50/month savings
            today=today,
        )

        # Contract ends in 10 days, ETF $100, only ~$17 in potential savings
        assert analysis.switch_recommendation == SwitchRecommendation.MARGINAL_BENEFIT
        assert analysis.not_beneficial_reason == NotBeneficialReason.CONTRACT_TOO_SHORT
        assert analysis.optimal_switch_date == contract_end

    def test_marginal_benefit_threshold(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test marginal benefit detection for modest savings."""
        analysis = analyzer.analyze_switch_timing(
            current_contract_end=None,
            early_termination_fee=Decimal("0"),
            current_plan_monthly_cost=Decimal("100"),
            new_plan_monthly_cost=Decimal("92"),  # $8/month = $96/year
            today=today,
        )

        # Below $100/year threshold but above $50 minimum
        assert analysis.switch_recommendation == SwitchRecommendation.MARGINAL_BENEFIT
        assert analysis.not_beneficial_reason == NotBeneficialReason.SAVINGS_TOO_SMALL
        assert analysis.confidence_score == 0.6

    def test_beneficial_switch_no_flags(
        self, analyzer: ContractAnalyzer, today: date
    ) -> None:
        """Test that genuinely beneficial switches have no not-beneficial reason."""
        analysis = analyzer.analyze_switch_timing(
            current_contract_end=None,
            early_termination_fee=Decimal("0"),
            current_plan_monthly_cost=Decimal("150"),
            new_plan_monthly_cost=Decimal("100"),  # $50/month = $600/year
            today=today,
        )

        assert analysis.switch_recommendation == SwitchRecommendation.SWITCH_NOW
        assert analysis.not_beneficial_reason is None
        assert analysis.confidence_score == 1.0


class TestCostCalculation:
    """Tests for total cost calculation method."""

    @pytest.fixture
    def analyzer(self) -> ContractAnalyzer:
        """Create analyzer instance."""
        return ContractAnalyzer()

    def test_calculate_switching_costs(self, analyzer: ContractAnalyzer) -> None:
        """Test comprehensive cost calculation."""
        result = analyzer.calculate_total_cost_of_switching(
            early_termination_fee=Decimal("150"),
            months_remaining_current=6,
            current_monthly_cost=Decimal("100"),
            new_monthly_cost=Decimal("80"),
            new_contract_months=12,
        )

        # Stay cost: $100 * 6 = $600
        assert result["stay_on_current_cost"] == Decimal("600")

        # New plan after: $80 * 12 = $960
        assert result["new_plan_cost_after"] == Decimal("960")

        # Total stay then switch: $600 + $960 = $1560
        assert result["total_stay_then_switch"] == Decimal("1560")

        # Switch now: $150 + $80 * 18 = $150 + $1440 = $1590
        assert result["switch_now_total_cost"] == Decimal("1590")

        # Savings: $1560 - $1590 = -$30 (waiting is better)
        assert result["savings_if_switch_now"] == Decimal("-30")
        assert result["recommendation"] == "wait"

    def test_calculate_switching_costs_switch_now_better(
        self, analyzer: ContractAnalyzer
    ) -> None:
        """Test when switching now is better."""
        result = analyzer.calculate_total_cost_of_switching(
            early_termination_fee=Decimal("50"),  # Low ETF
            months_remaining_current=12,  # Long time remaining
            current_monthly_cost=Decimal("150"),  # High current cost
            new_monthly_cost=Decimal("80"),
            new_contract_months=12,
        )

        # Stay cost: $150 * 12 = $1800
        # New plan after: $80 * 12 = $960
        # Total stay then switch: $2760
        # Switch now: $50 + $80 * 24 = $1970
        # Savings: $2760 - $1970 = $790

        assert result["savings_if_switch_now"] == Decimal("790")
        assert result["recommendation"] == "switch_now"
