"""Unit tests for usage pattern analyzer."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.services.usage_analyzer import (
    SeasonalPattern,
    UsageAnalyzer,
    UsageTrend,
)


class TestUsageAnalyzer:
    """Tests for UsageAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> UsageAnalyzer:
        """Create analyzer instance."""
        return UsageAnalyzer()

    @pytest.fixture
    def summer_peak_data(self) -> list[Any]:
        """Create data with summer peak pattern (AC usage)."""
        customer_id = uuid4()
        data = []

        # Monthly usage with summer peak
        monthly_kwh = {
            1: 800,  # January - low
            2: 750,  # February - low
            3: 850,  # March
            4: 900,  # April
            5: 1000,  # May
            6: 1400,  # June - high
            7: 1600,  # July - peak
            8: 1500,  # August - high
            9: 1100,  # September
            10: 900,  # October
            11: 800,  # November
            12: 750,  # December - low
        }

        for month, kwh in monthly_kwh.items():
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal(str(kwh))
            data.append(usage)

        return data

    @pytest.fixture
    def winter_peak_data(self) -> list[Any]:
        """Create data with winter peak pattern (heating)."""
        customer_id = uuid4()
        data = []

        # Monthly usage with winter peak
        monthly_kwh = {
            1: 1500,  # January - peak
            2: 1400,  # February - high
            3: 1100,  # March
            4: 800,  # April
            5: 700,  # May - low
            6: 750,  # June - low
            7: 800,  # July - low
            8: 750,  # August - low
            9: 850,  # September
            10: 1000,  # October
            11: 1200,  # November
            12: 1450,  # December - high
        }

        for month, kwh in monthly_kwh.items():
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal(str(kwh))
            data.append(usage)

        return data

    @pytest.fixture
    def flat_usage_data(self) -> list[Any]:
        """Create data with flat/consistent usage pattern."""
        customer_id = uuid4()
        data = []

        for month in range(1, 13):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("900")  # Consistent
            data.append(usage)

        return data

    @pytest.fixture
    def increasing_trend_data(self) -> list[Any]:
        """Create data with increasing usage trend."""
        customer_id = uuid4()
        data = []

        base_kwh = 800
        for month in range(1, 13):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            # Increase by 50 kWh each month
            usage.kwh_usage = Decimal(str(base_kwh + (month * 50)))
            data.append(usage)

        return data

    def test_analyze_summer_peak(
        self, analyzer: UsageAnalyzer, summer_peak_data: list[Any]
    ) -> None:
        """Test detection of summer peak pattern."""
        analysis = analyzer.analyze(summer_peak_data)

        assert analysis.seasonal_pattern == SeasonalPattern.SUMMER_PEAK
        assert (
            6 in analysis.peak_months
            or 7 in analysis.peak_months
            or 8 in analysis.peak_months
        )
        assert analysis.seasonal_variation_percent > Decimal("0")
        assert analysis.months_of_data == 12

    def test_analyze_winter_peak(
        self, analyzer: UsageAnalyzer, winter_peak_data: list[Any]
    ) -> None:
        """Test detection of winter peak pattern."""
        analysis = analyzer.analyze(winter_peak_data)

        assert analysis.seasonal_pattern == SeasonalPattern.WINTER_PEAK
        assert (
            1 in analysis.peak_months
            or 2 in analysis.peak_months
            or 12 in analysis.peak_months
        )
        assert analysis.seasonal_variation_percent > Decimal("0")

    def test_analyze_flat_pattern(
        self, analyzer: UsageAnalyzer, flat_usage_data: list[Any]
    ) -> None:
        """Test detection of flat usage pattern."""
        analysis = analyzer.analyze(flat_usage_data)

        assert analysis.seasonal_pattern == SeasonalPattern.FLAT
        assert analysis.standard_deviation < Decimal("50")  # Low variance

    def test_analyze_increasing_trend(
        self, analyzer: UsageAnalyzer, increasing_trend_data: list[Any]
    ) -> None:
        """Test detection of increasing usage trend."""
        analysis = analyzer.analyze(increasing_trend_data)

        assert analysis.usage_trend == UsageTrend.INCREASING
        assert analysis.trend_percent_change > Decimal("0")

    def test_consumption_tier_high(
        self, analyzer: UsageAnalyzer, summer_peak_data: list[Any]
    ) -> None:
        """Test high consumption tier detection."""
        analysis = analyzer.analyze(summer_peak_data)

        # Summer peak data has ~12,350 kWh annual
        assert analysis.is_high_consumer is True
        assert analysis.consumption_tier in ["high", "very_high"]

    def test_consumption_tier_low(self, analyzer: UsageAnalyzer) -> None:
        """Test low consumption tier detection."""
        customer_id = uuid4()
        data = []

        # Low usage household
        for month in range(1, 13):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("400")  # Very low
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.is_high_consumer is False
        assert analysis.consumption_tier == "low"

    def test_data_quality_full_year(
        self, analyzer: UsageAnalyzer, flat_usage_data: list[Any]
    ) -> None:
        """Test data quality score with full year of data."""
        analysis = analyzer.analyze(flat_usage_data)

        assert analysis.data_quality_score >= Decimal("0.9")
        assert analysis.has_gaps is False

    def test_data_quality_partial_data(self, analyzer: UsageAnalyzer) -> None:
        """Test data quality score with partial data."""
        customer_id = uuid4()
        data = []

        # Only 6 months of data
        for month in range(1, 7):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("900")
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.data_quality_score < Decimal("0.9")
        assert analysis.months_of_data == 6

    def test_gap_detection(self, analyzer: UsageAnalyzer) -> None:
        """Test detection of gaps in data."""
        customer_id = uuid4()
        data = []

        # Create data with a gap (missing March)
        for month in [1, 2, 4, 5, 6]:
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("900")
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.has_gaps is True
        assert 3 in analysis.gap_months  # March is missing

    def test_empty_data(self, analyzer: UsageAnalyzer) -> None:
        """Test handling of empty data."""
        analysis = analyzer.analyze([])

        assert analysis.seasonal_pattern == SeasonalPattern.UNKNOWN
        assert analysis.usage_trend == UsageTrend.UNKNOWN
        assert analysis.months_of_data == 0
        assert analysis.data_quality_score == Decimal("0")

    def test_insufficient_data_for_seasonal(self, analyzer: UsageAnalyzer) -> None:
        """Test seasonal detection with insufficient data."""
        customer_id = uuid4()
        data = []

        # Only 3 months - not enough for seasonal detection
        for month in range(1, 4):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("900")
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.seasonal_pattern == SeasonalPattern.UNKNOWN

    def test_statistics_calculation(
        self, analyzer: UsageAnalyzer, summer_peak_data: list[Any]
    ) -> None:
        """Test basic statistics are calculated correctly."""
        analysis = analyzer.analyze(summer_peak_data)

        assert analysis.total_annual_kwh > Decimal("0")
        assert analysis.average_monthly_kwh > Decimal("0")
        assert analysis.min_monthly_kwh <= analysis.average_monthly_kwh
        assert analysis.max_monthly_kwh >= analysis.average_monthly_kwh
        assert analysis.standard_deviation >= Decimal("0")

    def test_plan_suitability_insights_summer_peak(
        self, analyzer: UsageAnalyzer, summer_peak_data: list[Any]
    ) -> None:
        """Test plan suitability insights for summer peak pattern."""
        analysis = analyzer.analyze(summer_peak_data)
        insights = analyzer.get_plan_suitability_insights(analysis)

        assert "seasonal" in insights
        assert (
            "summer" in insights["seasonal"].lower()
            or "air conditioning" in insights["seasonal"].lower()
        )

    def test_plan_suitability_insights_high_consumer(
        self, analyzer: UsageAnalyzer, summer_peak_data: list[Any]
    ) -> None:
        """Test insights for high consumption."""
        analysis = analyzer.analyze(summer_peak_data)
        insights = analyzer.get_plan_suitability_insights(analysis)

        # High consumer should get advice about rate per kWh
        if "consumption" in insights:
            assert "rate" in insights["consumption"].lower()

    def test_dual_peak_pattern(self, analyzer: UsageAnalyzer) -> None:
        """Test detection of dual peak pattern (heating and AC)."""
        customer_id = uuid4()
        data = []

        # High in both summer and winter
        monthly_kwh = {
            1: 1400,  # January - high (heating)
            2: 1350,  # February - high
            3: 900,  # March - shoulder
            4: 850,  # April
            5: 900,  # May
            6: 1300,  # June - high (AC)
            7: 1500,  # July - peak
            8: 1400,  # August - high
            9: 950,  # September
            10: 850,  # October
            11: 1000,  # November
            12: 1350,  # December - high
        }

        for month, kwh in monthly_kwh.items():
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal(str(kwh))
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.seasonal_pattern == SeasonalPattern.DUAL_PEAK

    def test_decreasing_trend(self, analyzer: UsageAnalyzer) -> None:
        """Test detection of decreasing usage trend."""
        customer_id = uuid4()
        data = []

        base_kwh = 1400
        for month in range(1, 13):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            # Decrease by 50 kWh each month
            usage.kwh_usage = Decimal(str(base_kwh - (month * 50)))
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.usage_trend == UsageTrend.DECREASING
        assert analysis.trend_percent_change < Decimal("0")

    def test_stable_trend(self, analyzer: UsageAnalyzer) -> None:
        """Test detection of stable usage trend."""
        customer_id = uuid4()
        data = []

        # Very consistent usage with minor variation
        monthly_kwh = [900, 905, 895, 910, 890, 900, 905, 895, 910, 890, 900, 905]

        for month, kwh in enumerate(monthly_kwh, 1):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal(str(kwh))
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.usage_trend == UsageTrend.STABLE
        assert abs(analysis.trend_percent_change) < Decimal("5")

    def test_medium_consumption_tier(self, analyzer: UsageAnalyzer) -> None:
        """Test medium consumption tier detection."""
        customer_id = uuid4()
        data = []

        # Medium usage household (~8400 kWh/year)
        for month in range(1, 13):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("700")
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.consumption_tier == "medium"
        assert analysis.is_high_consumer is False

    def test_very_high_consumption_tier(self, analyzer: UsageAnalyzer) -> None:
        """Test very high consumption tier detection."""
        customer_id = uuid4()
        data = []

        # Very high usage household (~18000 kWh/year)
        for month in range(1, 13):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("1500")
            data.append(usage)

        analysis = analyzer.analyze(data)

        assert analysis.consumption_tier == "very_high"
        assert analysis.is_high_consumer is True

    def test_plan_suitability_insights_winter_peak(
        self, analyzer: UsageAnalyzer, winter_peak_data: list[Any]
    ) -> None:
        """Test plan suitability insights for winter peak pattern."""
        analysis = analyzer.analyze(winter_peak_data)
        insights = analyzer.get_plan_suitability_insights(analysis)

        assert "seasonal" in insights
        assert (
            "winter" in insights["seasonal"].lower()
            or "heating" in insights["seasonal"].lower()
        )

    def test_plan_suitability_insights_flat_pattern(
        self, analyzer: UsageAnalyzer, flat_usage_data: list[Any]
    ) -> None:
        """Test plan suitability insights for flat pattern."""
        analysis = analyzer.analyze(flat_usage_data)
        insights = analyzer.get_plan_suitability_insights(analysis)

        assert "seasonal" in insights
        assert (
            "consistent" in insights["seasonal"].lower()
            or "any rate" in insights["seasonal"].lower()
        )

    def test_plan_suitability_insights_increasing_trend(
        self, analyzer: UsageAnalyzer, increasing_trend_data: list[Any]
    ) -> None:
        """Test insights for increasing usage trend."""
        analysis = analyzer.analyze(increasing_trend_data)
        insights = analyzer.get_plan_suitability_insights(analysis)

        assert "trend" in insights
        assert "increasing" in insights["trend"].lower()

    def test_annual_usage_estimation(self, analyzer: UsageAnalyzer) -> None:
        """Test that annual usage is estimated correctly from partial data."""
        customer_id = uuid4()
        data = []

        # 6 months of 1000 kWh each
        for month in range(1, 7):
            usage = SimpleNamespace()
            usage.id = uuid4()
            usage.customer_id = customer_id
            usage.usage_date = date(2024, month, 1)
            usage.kwh_usage = Decimal("1000")
            data.append(usage)

        analysis = analyzer.analyze(data)

        # Total should be 6000, but annual estimate should be ~12000
        assert analysis.total_annual_kwh == Decimal("6000")
        # The analyzer should identify this as high consumption based on annualized rate
        assert analysis.is_high_consumer is True
