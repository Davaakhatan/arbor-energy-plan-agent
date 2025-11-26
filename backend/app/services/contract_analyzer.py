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
    MARGINAL_BENEFIT = "marginal_benefit"  # Savings exist but minimal


class NotBeneficialReason(str, Enum):
    """Reasons why switching may not be beneficial."""

    NEW_PLAN_MORE_EXPENSIVE = "new_plan_more_expensive"
    SAVINGS_TOO_SMALL = "savings_too_small"
    BREAK_EVEN_TOO_LONG = "break_even_too_long"
    ETF_EXCEEDS_ANNUAL_SAVINGS = "etf_exceeds_annual_savings"
    CONTRACT_TOO_SHORT = "contract_too_short"
    RATE_VOLATILITY_RISK = "rate_volatility_risk"


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

    # Not beneficial analysis
    not_beneficial_reason: NotBeneficialReason | None = None
    confidence_score: float = 1.0  # 0-1 confidence in recommendation

    # Explanation
    explanation: str = ""
    details: dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class ContractAnalyzer:
    """Analyzes contract timing for optimal switching decisions."""

    # Thresholds for determining benefit worthiness
    MIN_ANNUAL_SAVINGS_THRESHOLD = Decimal("50")  # Minimum $50/year to be worthwhile
    MIN_MONTHLY_SAVINGS_THRESHOLD = Decimal("5")  # Minimum $5/month
    MAX_BREAK_EVEN_MONTHS = 18  # Maximum months to recover ETF
    MARGINAL_SAVINGS_THRESHOLD = Decimal("100")  # Below this is marginal benefit

    def analyze_switch_timing(
        self,
        current_contract_end: date | None,
        early_termination_fee: Decimal,
        current_plan_monthly_cost: Decimal,
        new_plan_monthly_cost: Decimal,
        new_plan_contract_months: int = 12,
        today: date | None = None,
    ) -> ContractAnalysis:
        """Analyze the optimal timing for switching plans.

        Args:
            current_contract_end: End date of current contract (None if month-to-month)
            early_termination_fee: Fee for early termination
            current_plan_monthly_cost: Current plan's monthly cost
            new_plan_monthly_cost: New plan's monthly cost
            new_plan_contract_months: Length of new plan contract in months
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
        annual_savings = monthly_savings * 12

        # Check for various not-beneficial scenarios
        not_beneficial_result = self._check_not_beneficial(
            monthly_savings=monthly_savings,
            annual_savings=annual_savings,
            early_termination_fee=early_termination_fee,
            has_active_contract=has_active_contract,
            days_until_end=days_until_end,
            new_plan_contract_months=new_plan_contract_months,
            current_contract_end=current_contract_end,
        )

        if not_beneficial_result:
            return ContractAnalysis(
                has_active_contract=has_active_contract,
                contract_end_date=current_contract_end,
                days_until_contract_end=days_until_end,
                early_termination_fee=early_termination_fee,
                switch_recommendation=not_beneficial_result["recommendation"],
                optimal_switch_date=not_beneficial_result.get("optimal_date"),
                break_even_months=not_beneficial_result.get("break_even_months"),
                remaining_contract_cost=Decimal("0"),
                new_plan_cost_same_period=Decimal("0"),
                immediate_switch_savings=monthly_savings,
                wait_to_switch_savings=annual_savings
                if annual_savings > 0
                else Decimal("0"),
                not_beneficial_reason=not_beneficial_result["reason"],
                confidence_score=not_beneficial_result["confidence"],
                explanation=not_beneficial_result["explanation"],
                details=not_beneficial_result["details"],
            )

        # Calculate break-even point (months to recover ETF)
        break_even_months = None
        if monthly_savings > 0 and early_termination_fee > 0:
            break_even_months = (
                int((early_termination_fee / monthly_savings).to_integral_value()) + 1
            )

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
            if (
                break_even_months
                and months_remaining
                and break_even_months <= months_remaining
            ):
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

    def _check_not_beneficial(
        self,
        monthly_savings: Decimal,
        annual_savings: Decimal,
        early_termination_fee: Decimal,
        has_active_contract: bool,
        days_until_end: int | None,
        new_plan_contract_months: int,
        current_contract_end: date | None,
    ) -> dict | None:
        """Check if switching is not beneficial and return details.

        Returns None if switching IS beneficial, otherwise returns a dict with:
        - recommendation: SwitchRecommendation
        - reason: NotBeneficialReason
        - confidence: float (0-1)
        - explanation: str
        - details: dict
        """
        # Scenario 1: New plan is more expensive
        if monthly_savings <= 0:
            return {
                "recommendation": SwitchRecommendation.NOT_BENEFICIAL,
                "reason": NotBeneficialReason.NEW_PLAN_MORE_EXPENSIVE,
                "confidence": 1.0,
                "explanation": (
                    f"The new plan costs ${abs(monthly_savings):.2f} more per month. "
                    "You would lose money by switching."
                ),
                "details": {
                    "monthly_difference": str(monthly_savings),
                    "annual_loss": str(monthly_savings * 12),
                },
            }

        # Scenario 2: Savings are too small to be worth the hassle
        if annual_savings < self.MIN_ANNUAL_SAVINGS_THRESHOLD:
            return {
                "recommendation": SwitchRecommendation.NOT_BENEFICIAL,
                "reason": NotBeneficialReason.SAVINGS_TOO_SMALL,
                "confidence": 0.9,
                "explanation": (
                    f"Annual savings of ${annual_savings:.2f} may not justify the effort "
                    f"of switching. Minimum recommended savings: ${self.MIN_ANNUAL_SAVINGS_THRESHOLD}."
                ),
                "details": {
                    "annual_savings": str(annual_savings),
                    "threshold": str(self.MIN_ANNUAL_SAVINGS_THRESHOLD),
                    "monthly_savings": str(monthly_savings),
                },
            }

        # Scenario 3: ETF exceeds annual savings (takes over a year to break even)
        if early_termination_fee > 0 and early_termination_fee > annual_savings:
            break_even_months = (
                int((early_termination_fee / monthly_savings).to_integral_value()) + 1
            )

            if break_even_months > self.MAX_BREAK_EVEN_MONTHS:
                return {
                    "recommendation": SwitchRecommendation.NOT_BENEFICIAL,
                    "reason": NotBeneficialReason.ETF_EXCEEDS_ANNUAL_SAVINGS,
                    "confidence": 0.95,
                    "explanation": (
                        f"The ${early_termination_fee} early termination fee would take "
                        f"{break_even_months} months to recover through savings. "
                        f"This exceeds the recommended maximum of {self.MAX_BREAK_EVEN_MONTHS} months."
                    ),
                    "details": {
                        "etf": str(early_termination_fee),
                        "annual_savings": str(annual_savings),
                        "break_even_months": break_even_months,
                        "max_recommended": self.MAX_BREAK_EVEN_MONTHS,
                    },
                    "break_even_months": break_even_months,
                }

        # Scenario 4: Break-even period exceeds new contract length
        if early_termination_fee > 0 and monthly_savings > 0:
            break_even_months = (
                int((early_termination_fee / monthly_savings).to_integral_value()) + 1
            )

            if break_even_months > new_plan_contract_months:
                return {
                    "recommendation": SwitchRecommendation.NOT_BENEFICIAL,
                    "reason": NotBeneficialReason.BREAK_EVEN_TOO_LONG,
                    "confidence": 0.85,
                    "explanation": (
                        f"It would take {break_even_months} months to recover the "
                        f"${early_termination_fee} ETF, but the new plan contract is "
                        f"only {new_plan_contract_months} months. You wouldn't benefit "
                        "within this contract period."
                    ),
                    "details": {
                        "break_even_months": break_even_months,
                        "new_contract_months": new_plan_contract_months,
                        "etf": str(early_termination_fee),
                    },
                    "break_even_months": break_even_months,
                }

        # Scenario 5: Current contract ending very soon - marginal benefit
        if (
            has_active_contract
            and days_until_end
            and days_until_end <= 14
            and early_termination_fee > 0
        ):
            # Contract ends in 2 weeks, might not be worth ETF hassle
            two_week_savings = monthly_savings / 2
            if early_termination_fee > two_week_savings * 3:  # ETF > 6 weeks savings
                return {
                    "recommendation": SwitchRecommendation.MARGINAL_BENEFIT,
                    "reason": NotBeneficialReason.CONTRACT_TOO_SHORT,
                    "confidence": 0.7,
                    "explanation": (
                        f"Your contract ends in only {days_until_end} days. "
                        f"Paying the ${early_termination_fee} ETF for such a short period "
                        "provides minimal benefit. Consider waiting."
                    ),
                    "details": {
                        "days_remaining": days_until_end,
                        "etf": str(early_termination_fee),
                        "potential_savings_remaining": str(two_week_savings),
                    },
                    "optimal_date": current_contract_end,
                }

        # Scenario 6: Marginal savings - worth it but barely
        if annual_savings < self.MARGINAL_SAVINGS_THRESHOLD:
            return {
                "recommendation": SwitchRecommendation.MARGINAL_BENEFIT,
                "reason": NotBeneficialReason.SAVINGS_TOO_SMALL,
                "confidence": 0.6,
                "explanation": (
                    f"Annual savings of ${annual_savings:.2f} are relatively modest. "
                    "Switching is beneficial but the impact is limited. "
                    "Consider if other factors (renewable energy, customer service) "
                    "are important to you."
                ),
                "details": {
                    "annual_savings": str(annual_savings),
                    "marginal_threshold": str(self.MARGINAL_SAVINGS_THRESHOLD),
                },
            }

        # Switching appears beneficial
        return None

    def calculate_total_cost_of_switching(
        self,
        early_termination_fee: Decimal,
        months_remaining_current: int,
        current_monthly_cost: Decimal,
        new_monthly_cost: Decimal,
        new_contract_months: int,
    ) -> dict:
        """Calculate comprehensive cost analysis for switching.

        Returns a detailed breakdown of costs for switching now vs waiting.
        """
        # Cost if staying on current plan until end + new plan after
        stay_cost = current_monthly_cost * months_remaining_current
        then_new_cost = new_monthly_cost * new_contract_months
        total_stay_then_switch = stay_cost + then_new_cost

        # Cost if switching now (with ETF)
        switch_now_cost = early_termination_fee + new_monthly_cost * (
            months_remaining_current + new_contract_months
        )

        # Which is better?
        savings_switching_now = total_stay_then_switch - switch_now_cost

        return {
            "stay_on_current_cost": stay_cost,
            "new_plan_cost_after": then_new_cost,
            "total_stay_then_switch": total_stay_then_switch,
            "switch_now_total_cost": switch_now_cost,
            "etf_included": early_termination_fee,
            "savings_if_switch_now": savings_switching_now,
            "recommendation": ("switch_now" if savings_switching_now > 0 else "wait"),
        }
