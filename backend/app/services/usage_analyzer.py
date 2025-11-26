"""Usage pattern analysis module for seasonal detection and consumption patterns."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from statistics import mean, stdev

from app.models.customer import CustomerUsage


class SeasonalPattern(str, Enum):
    """Types of seasonal usage patterns."""

    SUMMER_PEAK = "summer_peak"  # Higher usage in summer (AC)
    WINTER_PEAK = "winter_peak"  # Higher usage in winter (heating)
    DUAL_PEAK = "dual_peak"  # High in both summer and winter
    FLAT = "flat"  # Relatively consistent usage
    UNKNOWN = "unknown"  # Not enough data to determine


class UsageTrend(str, Enum):
    """Overall usage trend direction."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    UNKNOWN = "unknown"


@dataclass
class UsageAnalysis:
    """Results of usage pattern analysis."""

    # Basic statistics
    total_annual_kwh: Decimal
    average_monthly_kwh: Decimal
    min_monthly_kwh: Decimal
    max_monthly_kwh: Decimal
    standard_deviation: Decimal

    # Seasonal analysis
    seasonal_pattern: SeasonalPattern
    seasonal_variation_percent: Decimal  # How much usage varies seasonally
    peak_months: list[int]  # 1-12
    low_months: list[int]  # 1-12

    # Trend analysis
    usage_trend: UsageTrend
    trend_percent_change: Decimal  # Year-over-year if available

    # Time-of-use insights
    is_high_consumer: bool  # Above average household
    consumption_tier: str  # low, medium, high, very_high

    # Data quality
    months_of_data: int
    data_quality_score: Decimal  # 0-1, based on completeness and consistency
    has_gaps: bool
    gap_months: list[int]


class UsageAnalyzer:
    """Analyzes customer usage patterns for better recommendations."""

    # Average US household uses ~10,500 kWh/year
    AVERAGE_ANNUAL_KWH = Decimal("10500")

    # Seasonal months (Northern Hemisphere)
    SUMMER_MONTHS = [6, 7, 8]  # June, July, August
    WINTER_MONTHS = [12, 1, 2]  # December, January, February
    SHOULDER_MONTHS = [3, 4, 5, 9, 10, 11]  # Spring and Fall

    def analyze(self, usage_data: list[CustomerUsage]) -> UsageAnalysis:
        """Perform comprehensive analysis of customer usage patterns."""
        if not usage_data:
            return self._empty_analysis()

        # Sort by date
        sorted_data = sorted(usage_data, key=lambda x: x.usage_date)

        # Extract values
        monthly_values = [float(u.kwh_usage) for u in sorted_data]

        # Basic statistics
        total = sum(monthly_values)
        avg = mean(monthly_values) if monthly_values else 0
        min_val = min(monthly_values) if monthly_values else 0
        max_val = max(monthly_values) if monthly_values else 0
        std_dev = stdev(monthly_values) if len(monthly_values) > 1 else 0

        # Seasonal pattern detection
        seasonal_pattern, peak_months, low_months, seasonal_variation = (
            self._detect_seasonal_pattern(sorted_data)
        )

        # Trend analysis
        trend, trend_change = self._analyze_trend(sorted_data)

        # Consumption tier
        annual_estimate = self._estimate_annual_usage(sorted_data)
        is_high = annual_estimate > self.AVERAGE_ANNUAL_KWH
        tier = self._determine_tier(annual_estimate)

        # Data quality
        quality_score = self._calculate_data_quality(sorted_data)
        has_gaps, gap_months = self._detect_gaps(sorted_data)

        return UsageAnalysis(
            total_annual_kwh=Decimal(str(round(total, 2))),
            average_monthly_kwh=Decimal(str(round(avg, 2))),
            min_monthly_kwh=Decimal(str(round(min_val, 2))),
            max_monthly_kwh=Decimal(str(round(max_val, 2))),
            standard_deviation=Decimal(str(round(std_dev, 2))),
            seasonal_pattern=seasonal_pattern,
            seasonal_variation_percent=seasonal_variation,
            peak_months=peak_months,
            low_months=low_months,
            usage_trend=trend,
            trend_percent_change=trend_change,
            is_high_consumer=is_high,
            consumption_tier=tier,
            months_of_data=len(sorted_data),
            data_quality_score=quality_score,
            has_gaps=has_gaps,
            gap_months=gap_months,
        )

    def _detect_seasonal_pattern(
        self, usage_data: list[CustomerUsage]
    ) -> tuple[SeasonalPattern, list[int], list[int], Decimal]:
        """Detect seasonal usage patterns."""
        if len(usage_data) < 6:
            return SeasonalPattern.UNKNOWN, [], [], Decimal("0")

        # Group usage by season
        summer_usage = []
        winter_usage = []
        shoulder_usage = []

        for usage in usage_data:
            month = usage.usage_date.month
            kwh = float(usage.kwh_usage)

            if month in self.SUMMER_MONTHS:
                summer_usage.append(kwh)
            elif month in self.WINTER_MONTHS:
                winter_usage.append(kwh)
            else:
                shoulder_usage.append(kwh)

        # Calculate averages
        summer_avg = mean(summer_usage) if summer_usage else 0
        winter_avg = mean(winter_usage) if winter_usage else 0
        shoulder_avg = mean(shoulder_usage) if shoulder_usage else 0

        # Calculate overall average for comparison
        overall_avg = mean([float(u.kwh_usage) for u in usage_data])

        # Determine pattern
        summer_ratio = summer_avg / overall_avg if overall_avg > 0 else 1
        winter_ratio = winter_avg / overall_avg if overall_avg > 0 else 1

        # Threshold for significant seasonal variation (20%)
        threshold = 1.20

        peak_months = []
        low_months = []

        if summer_ratio >= threshold and winter_ratio >= threshold:
            pattern = SeasonalPattern.DUAL_PEAK
            peak_months = self.SUMMER_MONTHS + self.WINTER_MONTHS
            low_months = self.SHOULDER_MONTHS
        elif summer_ratio >= threshold:
            pattern = SeasonalPattern.SUMMER_PEAK
            peak_months = self.SUMMER_MONTHS
            low_months = self.WINTER_MONTHS
        elif winter_ratio >= threshold:
            pattern = SeasonalPattern.WINTER_PEAK
            peak_months = self.WINTER_MONTHS
            low_months = self.SUMMER_MONTHS
        else:
            pattern = SeasonalPattern.FLAT
            # Find actual peak/low months from data
            monthly_avgs = self._get_monthly_averages(usage_data)
            if monthly_avgs:
                sorted_months = sorted(monthly_avgs.items(), key=lambda x: x[1])
                low_months = [m for m, _ in sorted_months[:3]]
                peak_months = [m for m, _ in sorted_months[-3:]]

        # Calculate variation percentage
        max_seasonal = max(summer_avg, winter_avg, shoulder_avg)
        min_seasonal = min(
            x for x in [summer_avg, winter_avg, shoulder_avg] if x > 0
        ) if any([summer_avg, winter_avg, shoulder_avg]) else 0

        variation = (
            ((max_seasonal - min_seasonal) / min_seasonal * 100)
            if min_seasonal > 0
            else 0
        )

        return pattern, peak_months, low_months, Decimal(str(round(variation, 1)))

    def _analyze_trend(
        self, usage_data: list[CustomerUsage]
    ) -> tuple[UsageTrend, Decimal]:
        """Analyze usage trend over time."""
        if len(usage_data) < 6:
            return UsageTrend.UNKNOWN, Decimal("0")

        # Split data into two halves
        mid = len(usage_data) // 2
        first_half = [float(u.kwh_usage) for u in usage_data[:mid]]
        second_half = [float(u.kwh_usage) for u in usage_data[mid:]]

        first_avg = mean(first_half)
        second_avg = mean(second_half)

        if first_avg == 0:
            return UsageTrend.UNKNOWN, Decimal("0")

        change_percent = ((second_avg - first_avg) / first_avg) * 100

        # Threshold for significant trend (5%)
        if change_percent > 5:
            trend = UsageTrend.INCREASING
        elif change_percent < -5:
            trend = UsageTrend.DECREASING
        else:
            trend = UsageTrend.STABLE

        return trend, Decimal(str(round(change_percent, 1)))

    def _estimate_annual_usage(self, usage_data: list[CustomerUsage]) -> Decimal:
        """Estimate annual usage from available data."""
        if not usage_data:
            return Decimal("0")

        total = sum(float(u.kwh_usage) for u in usage_data)
        months = len(usage_data)

        # Annualize
        annual_estimate = (total / months) * 12

        return Decimal(str(round(annual_estimate, 2)))

    def _determine_tier(self, annual_kwh: Decimal) -> str:
        """Determine consumption tier based on annual usage."""
        kwh = float(annual_kwh)

        if kwh < 6000:
            return "low"
        elif kwh < 10500:
            return "medium"
        elif kwh < 15000:
            return "high"
        else:
            return "very_high"

    def _calculate_data_quality(self, usage_data: list[CustomerUsage]) -> Decimal:
        """Calculate data quality score based on completeness and consistency."""
        if not usage_data:
            return Decimal("0")

        score = 1.0

        # Penalize for insufficient data
        months = len(usage_data)
        if months < 12:
            score -= (12 - months) * 0.05  # -5% per missing month

        # Penalize for gaps
        has_gaps, gap_count = self._detect_gaps(usage_data)
        if has_gaps:
            score -= len(gap_count) * 0.1  # -10% per gap

        # Penalize for suspicious values (zeros or extreme outliers)
        values = [float(u.kwh_usage) for u in usage_data]
        if values:
            avg = mean(values)
            for val in values:
                if val == 0:
                    score -= 0.05  # -5% per zero
                elif avg > 0 and (val > avg * 3 or val < avg * 0.2):
                    score -= 0.03  # -3% per outlier

        return Decimal(str(max(0, min(1, round(score, 2)))))

    def _detect_gaps(
        self, usage_data: list[CustomerUsage]
    ) -> tuple[bool, list[int]]:
        """Detect gaps in usage data."""
        if len(usage_data) < 2:
            return False, []

        sorted_data = sorted(usage_data, key=lambda x: x.usage_date)
        gap_months = []

        for i in range(1, len(sorted_data)):
            prev_date = sorted_data[i - 1].usage_date
            curr_date = sorted_data[i].usage_date

            # Calculate expected next month
            expected_month = prev_date.month + 1 if prev_date.month < 12 else 1
            expected_year = (
                prev_date.year if prev_date.month < 12 else prev_date.year + 1
            )

            # Check if there's a gap
            if curr_date.month != expected_month or curr_date.year != expected_year:
                # There's a gap
                gap_months.append(expected_month)

        return len(gap_months) > 0, gap_months

    def _get_monthly_averages(
        self, usage_data: list[CustomerUsage]
    ) -> dict[int, float]:
        """Get average usage for each month."""
        monthly_totals: dict[int, list[float]] = {}

        for usage in usage_data:
            month = usage.usage_date.month
            if month not in monthly_totals:
                monthly_totals[month] = []
            monthly_totals[month].append(float(usage.kwh_usage))

        return {month: mean(values) for month, values in monthly_totals.items()}

    def _empty_analysis(self) -> UsageAnalysis:
        """Return empty analysis for missing data."""
        return UsageAnalysis(
            total_annual_kwh=Decimal("0"),
            average_monthly_kwh=Decimal("0"),
            min_monthly_kwh=Decimal("0"),
            max_monthly_kwh=Decimal("0"),
            standard_deviation=Decimal("0"),
            seasonal_pattern=SeasonalPattern.UNKNOWN,
            seasonal_variation_percent=Decimal("0"),
            peak_months=[],
            low_months=[],
            usage_trend=UsageTrend.UNKNOWN,
            trend_percent_change=Decimal("0"),
            is_high_consumer=False,
            consumption_tier="unknown",
            months_of_data=0,
            data_quality_score=Decimal("0"),
            has_gaps=True,
            gap_months=[],
        )

    def get_plan_suitability_insights(
        self, analysis: UsageAnalysis
    ) -> dict[str, str]:
        """Generate insights about plan suitability based on usage patterns."""
        insights = {}

        # Seasonal pattern insights
        if analysis.seasonal_pattern == SeasonalPattern.SUMMER_PEAK:
            insights["seasonal"] = (
                "Your usage peaks in summer, likely from air conditioning. "
                "Consider plans with lower summer rates or time-of-use options."
            )
        elif analysis.seasonal_pattern == SeasonalPattern.WINTER_PEAK:
            insights["seasonal"] = (
                "Your usage peaks in winter, likely from heating. "
                "Look for plans with stable rates or winter discounts."
            )
        elif analysis.seasonal_pattern == SeasonalPattern.DUAL_PEAK:
            insights["seasonal"] = (
                "You have high usage in both summer and winter. "
                "A fixed-rate plan may provide more predictable bills."
            )
        elif analysis.seasonal_pattern == SeasonalPattern.FLAT:
            insights["seasonal"] = (
                "Your usage is relatively consistent throughout the year. "
                "Any rate structure should work well for you."
            )

        # Consumption tier insights
        if analysis.consumption_tier == "very_high":
            insights["consumption"] = (
                "Your usage is well above average. "
                "Focus on the lowest rate per kWh to maximize savings."
            )
        elif analysis.consumption_tier == "high":
            insights["consumption"] = (
                "Your usage is above average. "
                "Rate per kWh will significantly impact your bill."
            )
        elif analysis.consumption_tier == "low":
            insights["consumption"] = (
                "Your usage is below average. "
                "Watch for high monthly fees that can offset low rates."
            )

        # Trend insights
        if analysis.usage_trend == UsageTrend.INCREASING:
            insights["trend"] = (
                f"Your usage has been increasing ({analysis.trend_percent_change}%). "
                "Consider plans with tiered pricing that rewards efficiency."
            )
        elif analysis.usage_trend == UsageTrend.DECREASING:
            insights["trend"] = (
                f"Your usage has been decreasing ({analysis.trend_percent_change}%). "
                "Great job! Shorter contracts give flexibility as needs change."
            )

        # Data quality warning
        if analysis.data_quality_score < Decimal("0.7"):
            insights["data_quality"] = (
                "Limited historical data affects projection accuracy. "
                "Consider a shorter-term plan until more data is available."
            )

        return insights
