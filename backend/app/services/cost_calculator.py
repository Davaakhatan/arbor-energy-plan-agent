"""Cost calculation service for energy plans."""

from decimal import Decimal
from uuid import UUID

from app.models.customer import CustomerUsage
from app.models.plan import EnergyPlan


class CostCalculator:
    """Service for calculating energy costs based on usage patterns."""

    def calculate_annual_cost(
        self,
        usage_data: list[CustomerUsage],
        plan: EnergyPlan,
    ) -> Decimal:
        """Calculate projected annual cost for a plan.

        Args:
            usage_data: Customer's monthly usage data
            plan: Energy plan to calculate cost for

        Returns:
            Projected annual cost in dollars
        """
        if not usage_data:
            return Decimal("0.00")

        # Calculate total usage
        total_kwh = sum(u.kwh_usage for u in usage_data)

        # Annualize if less than 12 months
        months = len(usage_data)
        if months < 12:
            total_kwh = (total_kwh / months) * 12

        # Calculate energy cost
        energy_cost = total_kwh * plan.rate_per_kwh

        # Add monthly fees (12 months)
        monthly_fees = plan.monthly_fee * 12

        return Decimal(str(round(energy_cost + monthly_fees, 2)))

    def calculate_monthly_cost(
        self,
        monthly_usage_kwh: Decimal,
        plan: EnergyPlan,
    ) -> Decimal:
        """Calculate monthly cost for given usage."""
        energy_cost = monthly_usage_kwh * plan.rate_per_kwh
        return Decimal(str(round(energy_cost + plan.monthly_fee, 2)))

    def calculate_all_costs(
        self,
        usage_data: list[CustomerUsage],
        plans: list[EnergyPlan],
    ) -> dict[UUID, dict]:
        """Calculate costs for all plans.

        Returns:
            Dictionary mapping plan ID to cost details
        """
        costs = {}

        # Calculate usage statistics
        total_kwh = sum(u.kwh_usage for u in usage_data)
        months = len(usage_data)
        avg_monthly = total_kwh / months if months > 0 else Decimal("0.00")

        # Annualize
        annual_kwh = (total_kwh / months * 12) if months > 0 else Decimal("0.00")

        for plan in plans:
            annual_cost = self.calculate_annual_cost(usage_data, plan)
            monthly_avg = annual_cost / 12

            # Calculate cost breakdown
            energy_portion = annual_kwh * plan.rate_per_kwh
            fee_portion = plan.monthly_fee * 12

            costs[plan.id] = {
                "annual_cost": annual_cost,
                "monthly_average": monthly_avg,
                "cost_per_kwh_effective": (
                    annual_cost / annual_kwh if annual_kwh > 0 else Decimal("0.00")
                ),
                "breakdown": {
                    "energy_cost": Decimal(str(round(energy_portion, 2))),
                    "monthly_fees": Decimal(str(round(fee_portion, 2))),
                    "total": annual_cost,
                },
                "usage_stats": {
                    "total_kwh": total_kwh,
                    "annual_kwh_projected": annual_kwh,
                    "avg_monthly_kwh": avg_monthly,
                    "months_of_data": months,
                },
            }

        return costs

    def calculate_savings(
        self,
        current_cost: Decimal,
        new_cost: Decimal,
        switching_cost: Decimal = Decimal("0.00"),
    ) -> dict:
        """Calculate savings from switching plans.

        Args:
            current_cost: Current annual cost
            new_cost: New plan annual cost
            switching_cost: One-time switching cost (ETF, etc.)

        Returns:
            Savings breakdown
        """
        annual_savings = current_cost - new_cost
        first_year_net = annual_savings - switching_cost

        # Calculate break-even if switching has a cost
        break_even_months = None
        if switching_cost > 0 and annual_savings > 0:
            monthly_savings = annual_savings / 12
            break_even_months = int(
                (switching_cost / monthly_savings).to_integral_value()
            )

        return {
            "annual_savings": annual_savings,
            "first_year_net_savings": first_year_net,
            "switching_cost": switching_cost,
            "break_even_months": break_even_months,
            "five_year_savings": (annual_savings * 5) - switching_cost,
            "is_beneficial": first_year_net > 0,
        }

    def project_seasonal_costs(
        self,
        usage_data: list[CustomerUsage],
        plan: EnergyPlan,
    ) -> list[dict]:
        """Project monthly costs based on historical usage patterns.

        Useful for showing seasonal variation.
        """
        projections = []

        for usage in sorted(usage_data, key=lambda u: u.usage_date):
            monthly_cost = self.calculate_monthly_cost(usage.kwh_usage, plan)
            projections.append(
                {
                    "month": usage.usage_date.strftime("%Y-%m"),
                    "kwh_usage": usage.kwh_usage,
                    "projected_cost": monthly_cost,
                }
            )

        return projections
