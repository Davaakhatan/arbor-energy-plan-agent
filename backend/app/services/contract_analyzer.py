"""Contract timing analysis module for switching recommendations."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum


class SwitchRecommendation(str, Enum):
    """Recommendation for when to switch plans."""

    SWITCH_NOW = "switch_now"
    WAIT_FOR_CONTRACT_END = "wait_for_contract_end"
    NOT_BENEFICIAL = "not_beneficial"
    SWITCH_SOON = "switch_soon"  # Within 30 days recommended


@dataclass
class ContractAnalysis:
    """Analysis of contract timing for switching."""

    # Current contract status
    has_active_contract: bool
    contract_end_date: date | None
    days_until_contract_end: int | None
    early_termination_fee: Decimal

    # Switching analysis
    switch_recommendation: SwitchRecommendation
    optimal_switch_date: date | None
    break_even_months: int | None

    # Financial analysis
    remaining_contract_cost: Decimal  # Cost to stay on current plan
    new_plan_cost_same_period: Decimal  # Cost of new plan for same period
    immediate_switch_savings: Decimal  # Savings if switch now (including ETF)
    wait_to_switch_savings: Decimal  # Savings if wait for contract end

    # Explanation
    explanation: str
    details: dict


class ContractAnalyzer:
    """Analyzes contract timing for optimal switching decisions."""

    def analyze_switch_timing(
        self,
        current_contract_end: date | None,
        early_termination_fee: Decimal,
        current_plan_monthly_cost: Decimal,
        new_plan_monthly_cost: Decimal,
        today: date | None = None,
    ) -> ContractAnalysis:
        """Analyze the optimal timing for switching plans.

        Args:
            current_contract_end: End date of current contract (None if month-to-month)
            early_termination_fee: Fee for early termination
            current_plan_monthly_cost: Current plan's monthly cost
            new_plan_monthly_cost: New plan's monthly cost
            today: Optional override for today's date (for testing)
        """
        if today is None:
            today = date.today()

        # Calculate days until contract end
        has_active_contract = False
        days_until_end = None

        if current_contract_end and current_contract_end > today:
            has_active_contract = True
            days_until_end = (current_contract_end - today).days

        # Calculate monthly savings
        monthly_savings = current_plan_monthly_cost - new_plan_monthly_cost

        # If new plan is more expensive, not beneficial
        if monthly_savings <= 0:
            return ContractAnalysis(
                has_active_contract=has_active_contract,
                contract_end_date=current_contract_end,
                days_until_contract_end=days_until_end,
                early_termination_fee=early_termination_fee,
                switch_recommendation=SwitchRecommendation.NOT_BENEFICIAL,
                optimal_switch_date=None,
                break_even_months=None,
                remaining_contract_cost=Decimal("0"),
                new_plan_cost_same_period=Decimal("0"),
                immediate_switch_savings=monthly_savings,
                wait_to_switch_savings=Decimal("0"),
                explanation=(
                    "The new plan would not save you money compared to your current plan."
                ),
                details={
                    "monthly_difference": str(monthly_savings),
                    "reason": "new_plan_more_expensive",
                },
            )

        # Calculate break-even point (months to recover ETF)
        break_even_months = None
        if monthly_savings > 0 and early_termination_fee > 0:
            break_even_months = int(
                (early_termination_fee / monthly_savings).to_integral_value()
            ) + 1

        # No active contract - switch immediately
        if not has_active_contract:
            annual_savings = monthly_savings * 12
            return ContractAnalysis(
                has_active_contract=False,
                contract_end_date=current_contract_end,
                days_until_contract_end=None,
                early_termination_fee=Decimal("0"),
                switch_recommendation=SwitchRecommendation.SWITCH_NOW,
                optimal_switch_date=today,
                break_even_months=0,
                remaining_contract_cost=Decimal("0"),
                new_plan_cost_same_period=Decimal("0"),
                immediate_switch_savings=annual_savings,
                wait_to_switch_savings=annual_savings,
                explanation=(
                    f"No contract restrictions. Switch now to save ${annual_savings:.2f} per year."
                ),
                details={
                    "monthly_savings": str(monthly_savings),
                    "annual_savings": str(annual_savings),
                },
            )

        # Active contract - analyze switching options
        months_remaining = days_until_end // 30 if days_until_end else 0

        # Cost to stay on current plan for remaining contract
        remaining_contract_cost = current_plan_monthly_cost * months_remaining

        # Cost of new plan for same period
        new_plan_cost_same_period = new_plan_monthly_cost * months_remaining

        # Savings if switch now (factoring in ETF)
        immediate_switch_savings = (
            remaining_contract_cost - new_plan_cost_same_period - early_termination_fee
        )

        # Savings if wait for contract to end (just ongoing savings)
        annual_savings_after_contract = monthly_savings * 12
        wait_to_switch_savings = annual_savings_after_contract

        # Determine recommendation
        if immediate_switch_savings > 0:
            # Switching now still saves money even with ETF
            if days_until_end and days_until_end <= 30:
                recommendation = SwitchRecommendation.SWITCH_SOON
                optimal_date = current_contract_end
                explanation = (
                    f"Your contract ends in {days_until_end} days. "
                    f"Wait to avoid the ${early_termination_fee} fee, "
                    f"then switch to save ${annual_savings_after_contract:.2f}/year."
                )
            else:
                recommendation = SwitchRecommendation.SWITCH_NOW
                optimal_date = today
                explanation = (
                    f"Even with the ${early_termination_fee} early termination fee, "
                    f"switching now saves ${immediate_switch_savings:.2f} over your "
                    f"remaining contract, plus ${annual_savings_after_contract:.2f}/year ongoing."
                )
        else:
            # ETF makes immediate switch not worthwhile
            if break_even_months and months_remaining and break_even_months <= months_remaining:
                # Would break even before contract ends anyway
                recommendation = SwitchRecommendation.WAIT_FOR_CONTRACT_END
                optimal_date = current_contract_end
                explanation = (
                    f"Wait for your contract to end in {days_until_end} days. "
                    f"The ${early_termination_fee} fee exceeds potential savings. "
                    f"After contract ends, you'll save ${annual_savings_after_contract:.2f}/year."
                )
            else:
                recommendation = SwitchRecommendation.WAIT_FOR_CONTRACT_END
                optimal_date = current_contract_end
                explanation = (
                    f"Wait {days_until_end} days for your contract to end. "
                    f"Then switch to save ${annual_savings_after_contract:.2f}/year."
                )

        return ContractAnalysis(
            has_active_contract=True,
            contract_end_date=current_contract_end,
            days_until_contract_end=days_until_end,
            early_termination_fee=early_termination_fee,
            switch_recommendation=recommendation,
            optimal_switch_date=optimal_date,
            break_even_months=break_even_months,
            remaining_contract_cost=remaining_contract_cost,
            new_plan_cost_same_period=new_plan_cost_same_period,
            immediate_switch_savings=immediate_switch_savings,
            wait_to_switch_savings=wait_to_switch_savings,
            explanation=explanation,
            details={
                "months_remaining": months_remaining,
                "monthly_savings": str(monthly_savings),
                "annual_savings": str(annual_savings_after_contract),
                "break_even_months": break_even_months,
            },
        )

    def get_switching_windows(
        self,
        contract_end_date: date | None,
        today: date | None = None,
    ) -> dict[str, date | None]:
        """Get key dates for switching decisions."""
        if today is None:
            today = date.today()

        windows = {
            "today": today,
            "contract_end": contract_end_date,
            "optimal_notice_date": None,  # When to start shopping
            "final_switch_date": None,  # Last day to switch before renewal
        }

        if contract_end_date and contract_end_date > today:
            # Typically want to start shopping 30-60 days before contract ends
            windows["optimal_notice_date"] = contract_end_date - timedelta(days=60)
            # Don't wait until the last day
            windows["final_switch_date"] = contract_end_date - timedelta(days=7)

            # If optimal notice date is in the past, use today
            if windows["optimal_notice_date"] < today:
                windows["optimal_notice_date"] = today

        return windows
