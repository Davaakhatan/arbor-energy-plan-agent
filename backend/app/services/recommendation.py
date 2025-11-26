"""Recommendation service implementing MCDA-based plan recommendations."""

import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.redis import CacheService
from app.models.customer import Customer
from app.models.plan import EnergyPlan
from app.models.preference import CustomerPreference
from app.repositories.plan import PlanRepository
from app.repositories.preference import PreferenceRepository
from app.schemas.preference import CustomerPreferenceCreate
from app.schemas.recommendation import (
    FilteredPlanResponse,
    RecommendationResponse,
    RecommendationSetResponse,
    RiskFlag,
    UsageAnalysisResponse,
)
from app.services.cached_plan_service import CachedPlanService
from app.services.cost_calculator import CostCalculator
from app.services.scoring import ScoringEngine
from app.services.usage_analyzer import UsageAnalyzer

logger = get_logger(__name__)


class RecommendationService:
    """Service for generating personalized energy plan recommendations."""

    def __init__(self, db: AsyncSession, cache: CacheService) -> None:
        """Initialize service with database and cache."""
        self.db = db
        self.cache = cache
        self.plan_repo = PlanRepository(db)
        self.cached_plans = CachedPlanService(db, cache)
        self.pref_repo = PreferenceRepository(db)
        self.cost_calculator = CostCalculator()
        self.scoring_engine = ScoringEngine()
        self.usage_analyzer = UsageAnalyzer()

    async def generate_recommendations(
        self,
        customer: Customer,
        preferences_override: CustomerPreferenceCreate | None = None,
        include_switching_analysis: bool = True,
    ) -> RecommendationSetResponse:
        """Generate top 3 plan recommendations for a customer.

        Performance target: < 2 seconds.
        """
        start_time = time.perf_counter()

        # Get or create preferences
        preferences = await self._get_preferences(customer.id, preferences_override)

        # Get all active plans (cached)
        plans = await self.cached_plans.get_all_active_plans()

        # Filter plans based on hard constraints
        eligible_plans, filtered_plans = self._filter_by_constraints(plans, preferences)

        # Calculate costs for each plan
        plan_costs = self.cost_calculator.calculate_all_costs(
            customer.usage_data,
            eligible_plans,
        )

        # Calculate current plan cost if available (cached)
        current_cost = None
        if customer.current_plan_id:
            current_plan = await self.cached_plans.get_plan_by_id(customer.current_plan_id)
            if current_plan:
                current_cost = self.cost_calculator.calculate_annual_cost(
                    customer.usage_data,
                    current_plan,
                )

        # Score all plans using MCDA
        scored_plans = self.scoring_engine.score_plans(
            eligible_plans,
            plan_costs,
            preferences,
        )

        # Select top 3
        top_3 = sorted(scored_plans, key=lambda x: x["overall_score"], reverse=True)[:3]

        # Generate recommendations with explanations
        recommendations = []
        for rank, scored in enumerate(top_3, 1):
            plan = scored["plan"]
            cost = plan_costs[plan.id]

            # Calculate savings
            savings = (
                current_cost - cost["annual_cost"] if current_cost else Decimal("0.00")
            )

            # Calculate switching cost
            switching_cost = self._calculate_switching_cost(
                customer,
                include_switching_analysis,
            )

            # Generate risk flags
            risk_flags = self._assess_risks(
                plan,
                customer,
                cost,
                scored,
            )

            # Generate explanation
            explanation, details = self._generate_explanation(
                plan,
                scored,
                savings,
                preferences,
            )

            recommendations.append(
                RecommendationResponse(
                    id=plan.id,  # Using plan ID as recommendation ID for now
                    rank=rank,
                    plan=plan,
                    overall_score=Decimal(str(scored["overall_score"])),
                    cost_score=Decimal(str(scored["cost_score"])),
                    flexibility_score=Decimal(str(scored["flexibility_score"])),
                    renewable_score=Decimal(str(scored["renewable_score"])),
                    rating_score=Decimal(str(scored["rating_score"])),
                    projected_annual_cost=cost["annual_cost"],
                    projected_annual_savings=savings,
                    switching_cost=switching_cost,
                    net_first_year_savings=savings - switching_cost,
                    explanation=explanation,
                    explanation_details=details,
                    risk_flags=risk_flags,
                    confidence_level=self._determine_confidence(customer, risk_flags),
                    created_at=datetime.now(UTC),
                    expires_at=datetime.now(UTC) + timedelta(hours=1),
                )
            )

        # Calculate processing time
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Perform usage pattern analysis
        usage_analysis = self._analyze_usage_patterns(customer)

        # Build response
        response = RecommendationSetResponse(
            customer_id=customer.id,
            recommendations=recommendations,
            filtered_plans=filtered_plans,
            usage_analysis=usage_analysis,
            current_annual_cost=current_cost,
            best_savings=max(r.projected_annual_savings for r in recommendations)
            if recommendations
            else Decimal("0.00"),
            generated_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            processing_time_ms=processing_time_ms,
            warnings=self._generate_warnings(customer, plans, eligible_plans),
        )

        # Cache the response
        await self._cache_recommendations(customer.id, response)

        logger.info(
            "Generated recommendations",
            customer_id=str(customer.id),
            num_plans_evaluated=len(plans),
            processing_time_ms=processing_time_ms,
        )

        return response

    async def get_cached_recommendations(
        self,
        customer_id: UUID,
    ) -> RecommendationSetResponse | None:
        """Get cached recommendations if available."""
        cached = await self.cache.get(f"recommendations:{customer_id}")
        if cached:
            return RecommendationSetResponse.model_validate(cached)
        return None

    async def _get_preferences(
        self,
        customer_id: UUID,
        override: CustomerPreferenceCreate | None,
    ) -> CustomerPreference:
        """Get customer preferences, using override or stored values."""
        if override:
            # Create temporary preference object from override
            return CustomerPreference(
                customer_id=customer_id,
                cost_savings_weight=override.cost_savings_weight,
                flexibility_weight=override.flexibility_weight,
                renewable_weight=override.renewable_weight,
                supplier_rating_weight=override.supplier_rating_weight,
                min_renewable_percentage=override.min_renewable_percentage,
                max_contract_months=override.max_contract_months,
                avoid_variable_rates=override.avoid_variable_rates,
            )

        stored = await self.pref_repo.get_by_customer_id(customer_id)
        if stored:
            return stored

        # Return default preferences
        return CustomerPreference(customer_id=customer_id)

    def _filter_by_constraints(
        self,
        plans: list[EnergyPlan],
        preferences: CustomerPreference,
    ) -> tuple[list[EnergyPlan], list[FilteredPlanResponse]]:
        """Filter plans based on hard constraints.

        Returns:
            Tuple of (eligible_plans, filtered_out_plans_with_reasons)
        """
        eligible = []
        filtered_out = []

        for plan in plans:
            supplier_name = plan.supplier.name if plan.supplier else None

            # Check renewable minimum
            if plan.renewable_percentage < preferences.min_renewable_percentage:
                filtered_out.append(
                    FilteredPlanResponse(
                        plan_id=plan.id,
                        plan_name=plan.name,
                        supplier_name=supplier_name,
                        filter_code="LOW_RENEWABLE",
                        filter_reason=f"Renewable energy is {plan.renewable_percentage}%, below your {preferences.min_renewable_percentage}% minimum requirement.",
                        details={
                            "plan_renewable": plan.renewable_percentage,
                            "required_renewable": preferences.min_renewable_percentage,
                        },
                    )
                )
                continue

            # Check contract length maximum
            if (
                preferences.max_contract_months
                and plan.contract_length_months > preferences.max_contract_months
            ):
                filtered_out.append(
                    FilteredPlanResponse(
                        plan_id=plan.id,
                        plan_name=plan.name,
                        supplier_name=supplier_name,
                        filter_code="LONG_CONTRACT",
                        filter_reason=f"Contract length is {plan.contract_length_months} months, exceeding your {preferences.max_contract_months}-month maximum.",
                        details={
                            "plan_contract_months": plan.contract_length_months,
                            "max_contract_months": preferences.max_contract_months,
                        },
                    )
                )
                continue

            # Check variable rate avoidance
            if preferences.avoid_variable_rates and plan.rate_type in [
                "variable",
                "indexed",
            ]:
                rate_label = "variable" if plan.rate_type == "variable" else "indexed"
                filtered_out.append(
                    FilteredPlanResponse(
                        plan_id=plan.id,
                        plan_name=plan.name,
                        supplier_name=supplier_name,
                        filter_code="VARIABLE_RATE",
                        filter_reason=f"This plan has a {rate_label} rate, which you've chosen to avoid.",
                        details={"rate_type": plan.rate_type},
                    )
                )
                continue

            eligible.append(plan)

        return eligible, filtered_out

    def _calculate_switching_cost(
        self,
        customer: Customer,
        include_analysis: bool,
    ) -> Decimal:
        """Calculate the cost of switching from current plan."""
        if not include_analysis:
            return Decimal("0.00")

        if not customer.early_termination_fee:
            return Decimal("0.00")

        # Check if contract has ended
        if customer.contract_end_date and customer.contract_end_date <= datetime.now(UTC).date():
            return Decimal("0.00")

        return customer.early_termination_fee

    def _assess_risks(
        self,
        plan: EnergyPlan,
        customer: Customer,
        _cost: dict,
        _scored: dict,
    ) -> list[RiskFlag]:
        """Assess risks associated with a recommendation."""
        risks = []

        # Variable rate risk
        if plan.rate_type in ["variable", "indexed"]:
            risks.append(
                RiskFlag(
                    code="VARIABLE_RATE",
                    severity="medium",
                    message="This plan has a variable rate that may fluctuate with market conditions.",
                    details={"rate_type": plan.rate_type},
                )
            )

        # Long contract risk
        contract_months = plan.contract_length_months or 12
        if contract_months >= 24:
            risks.append(
                RiskFlag(
                    code="LONG_CONTRACT",
                    severity="low",
                    message=f"This plan requires a {contract_months}-month commitment.",
                    details={"months": contract_months},
                )
            )

        # High ETF risk
        etf = plan.early_termination_fee or Decimal("0.00")
        if etf >= Decimal("200.00"):
            risks.append(
                RiskFlag(
                    code="HIGH_ETF",
                    severity="medium",
                    message=f"Early termination fee of ${etf} applies.",
                    details={"etf": str(etf)},
                )
            )

        # Insufficient data warning
        if len(customer.usage_data) < 12:
            risks.append(
                RiskFlag(
                    code="INSUFFICIENT_DATA",
                    severity="low",
                    message=f"Only {len(customer.usage_data)} months of usage data available. Projections may be less accurate.",
                    details={"months_available": len(customer.usage_data)},
                )
            )

        return risks

    def _determine_confidence(
        self,
        customer: Customer,
        risks: list[RiskFlag],
    ) -> str:
        """Determine confidence level based on data quality and risks."""
        if len(customer.usage_data) < 6:
            return "low"
        if len(customer.usage_data) < 12:
            return "medium"
        if any(r.severity == "high" for r in risks):
            return "medium"
        return "high"

    def _generate_explanation(
        self,
        plan: EnergyPlan,
        scored: dict,
        savings: Decimal,
        _preferences: CustomerPreference,
    ) -> tuple[str, dict]:
        """Generate plain language explanation for recommendation."""
        parts = []

        # Lead with strongest benefit
        if scored["cost_score"] > 0.8:
            parts.append(f"offers excellent value with projected annual savings of ${savings:.2f}")
        elif savings > 0:
            parts.append(f"could save you ${savings:.2f} per year")

        # Mention renewable if significant
        if plan.renewable_percentage >= 50:
            parts.append(f"includes {plan.renewable_percentage}% renewable energy")

        # Mention flexibility if relevant
        if plan.contract_length_months <= 6:
            parts.append("offers flexible month-to-month or short-term commitment")

        # Mention supplier rating
        if plan.supplier and plan.supplier.rating and plan.supplier.rating >= Decimal("4.0"):
            parts.append(f"from {plan.supplier.name}, a highly-rated supplier")

        explanation = f"This plan {', '.join(parts)}." if parts else "This plan matches your preferences."

        details = {
            "cost_ranking": "top" if scored["cost_score"] > 0.8 else "competitive",
            "renewable_level": "high" if plan.renewable_percentage >= 50 else "standard",
            "flexibility": "high" if plan.contract_length_months <= 6 else "standard",
            "projected_savings": str(savings),
        }

        return explanation, details

    def _generate_warnings(
        self,
        customer: Customer,
        all_plans: list[EnergyPlan],
        eligible_plans: list[EnergyPlan],
    ) -> list[str]:
        """Generate general warnings about the recommendations."""
        warnings = []

        if len(eligible_plans) < 3:
            warnings.append(
                f"Only {len(eligible_plans)} plans match your criteria. "
                "Consider relaxing constraints for more options."
            )

        if len(customer.usage_data) < 12:
            warnings.append(
                f"Projections based on {len(customer.usage_data)} months of data. "
                "12 months recommended for accurate estimates."
            )

        filtered_count = len(all_plans) - len(eligible_plans)
        if filtered_count > len(eligible_plans):
            warnings.append(
                f"{filtered_count} plans were filtered out based on your preferences."
            )

        return warnings

    def _analyze_usage_patterns(
        self,
        customer: Customer,
    ) -> UsageAnalysisResponse | None:
        """Analyze customer usage patterns."""
        if not customer.usage_data:
            return None

        analysis = self.usage_analyzer.analyze(customer.usage_data)
        insights = self.usage_analyzer.get_plan_suitability_insights(analysis)

        return UsageAnalysisResponse(
            total_annual_kwh=analysis.total_annual_kwh,
            average_monthly_kwh=analysis.average_monthly_kwh,
            min_monthly_kwh=analysis.min_monthly_kwh,
            max_monthly_kwh=analysis.max_monthly_kwh,
            seasonal_pattern=analysis.seasonal_pattern.value,
            seasonal_variation_percent=analysis.seasonal_variation_percent,
            peak_months=analysis.peak_months,
            low_months=analysis.low_months,
            usage_trend=analysis.usage_trend.value,
            trend_percent_change=analysis.trend_percent_change,
            consumption_tier=analysis.consumption_tier,
            is_high_consumer=analysis.is_high_consumer,
            months_of_data=analysis.months_of_data,
            data_quality_score=analysis.data_quality_score,
            insights=insights,
        )

    async def _cache_recommendations(
        self,
        customer_id: UUID,
        response: RecommendationSetResponse,
    ) -> None:
        """Cache recommendations for future retrieval."""
        await self.cache.set(
            f"recommendations:{customer_id}",
            response.model_dump(mode="json"),
            ttl=3600,  # 1 hour
        )
