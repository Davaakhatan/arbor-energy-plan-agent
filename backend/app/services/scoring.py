"""MCDA Scoring Engine for plan recommendations."""

from decimal import Decimal
from uuid import UUID

from app.models.plan import EnergyPlan
from app.models.preference import CustomerPreference


class ScoringEngine:
    """Multi-Criteria Decision Analysis (MCDA) scoring engine.

    Implements a weighted scoring system to rank energy plans based on
    customer preferences across multiple criteria.
    """

    def score_plans(
        self,
        plans: list[EnergyPlan],
        costs: dict[UUID, dict],
        preferences: CustomerPreference,
    ) -> list[dict]:
        """Score all plans using MCDA.

        Args:
            plans: List of energy plans to score
            costs: Pre-calculated costs for each plan
            preferences: Customer preference weights

        Returns:
            List of scored plans with individual and overall scores
        """
        if not plans:
            return []

        # Calculate min/max values for normalization
        cost_values = [costs[p.id]["annual_cost"] for p in plans]
        min_cost = min(cost_values)
        max_cost = max(cost_values)

        contract_lengths = [p.contract_length_months for p in plans]
        min_contract = min(contract_lengths)
        max_contract = max(contract_lengths)

        renewable_values = [p.renewable_percentage for p in plans]
        max_renewable = max(renewable_values)

        rating_values = [
            float(p.supplier.rating) if p.supplier and p.supplier.rating else 0.0
            for p in plans
        ]
        max_rating = max(rating_values) if rating_values else 5.0

        scored_plans = []
        for plan in plans:
            # Calculate individual scores (0.0 to 1.0)
            cost_score = self._normalize_inverse(
                costs[plan.id]["annual_cost"],
                min_cost,
                max_cost,
            )

            flexibility_score = self._normalize_inverse(
                Decimal(plan.contract_length_months),
                Decimal(min_contract),
                Decimal(max_contract),
            )

            renewable_score = self._normalize(
                Decimal(plan.renewable_percentage),
                Decimal(0),
                Decimal(max_renewable) if max_renewable > 0 else Decimal(100),
            )

            supplier_rating = (
                float(plan.supplier.rating)
                if plan.supplier and plan.supplier.rating
                else 3.0
            )
            rating_score = self._normalize(
                Decimal(str(supplier_rating)),
                Decimal(0),
                Decimal(str(max_rating)) if max_rating > 0 else Decimal(5),
            )

            # Calculate weighted overall score (default to equal weights if None)
            cost_weight = float(preferences.cost_savings_weight or Decimal("0.25"))
            flexibility_weight = float(
                preferences.flexibility_weight or Decimal("0.25")
            )
            renewable_weight = float(preferences.renewable_weight or Decimal("0.25"))
            rating_weight = float(preferences.supplier_rating_weight or Decimal("0.25"))

            overall_score = (
                cost_weight * cost_score
                + flexibility_weight * flexibility_score
                + renewable_weight * renewable_score
                + rating_weight * rating_score
            )

            scored_plans.append(
                {
                    "plan": plan,
                    "plan_id": plan.id,
                    "cost_score": round(cost_score, 4),
                    "flexibility_score": round(flexibility_score, 4),
                    "renewable_score": round(renewable_score, 4),
                    "rating_score": round(rating_score, 4),
                    "overall_score": round(overall_score, 4),
                    "weights_applied": {
                        "cost": cost_weight,
                        "flexibility": flexibility_weight,
                        "renewable": renewable_weight,
                        "rating": rating_weight,
                    },
                }
            )

        return scored_plans

    def _normalize(
        self,
        value: Decimal,
        min_val: Decimal,
        max_val: Decimal,
    ) -> float:
        """Normalize value to 0-1 range (higher is better)."""
        if max_val == min_val:
            return 1.0
        return float((value - min_val) / (max_val - min_val))

    def _normalize_inverse(
        self,
        value: Decimal,
        min_val: Decimal,
        max_val: Decimal,
    ) -> float:
        """Normalize value to 0-1 range (lower is better)."""
        if max_val == min_val:
            return 1.0
        return float((max_val - value) / (max_val - min_val))

    def explain_score(
        self,
        scored_plan: dict,
        _preferences: CustomerPreference,
    ) -> str:
        """Generate explanation of why a plan received its score."""
        parts = []

        # Analyze each component
        if scored_plan["cost_score"] > 0.8:
            parts.append("excellent cost efficiency")
        elif scored_plan["cost_score"] > 0.5:
            parts.append("competitive pricing")

        if scored_plan["flexibility_score"] > 0.8:
            parts.append("high flexibility with short contract terms")
        elif scored_plan["flexibility_score"] < 0.3:
            parts.append("longer contract commitment required")

        if scored_plan["renewable_score"] > 0.8:
            parts.append("strong renewable energy content")
        elif scored_plan["renewable_score"] > 0.5:
            parts.append("moderate renewable energy mix")

        if scored_plan["rating_score"] > 0.8:
            parts.append("highly rated supplier")

        if not parts:
            return "This plan provides a balanced option across your criteria."

        return f"This plan scores well due to: {', '.join(parts)}."
