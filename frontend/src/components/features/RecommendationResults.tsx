"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import {
  formatCurrency,
  formatPercentage,
  getRateTypeLabel,
  getSeverityColor,
  getConfidenceColor,
} from "@/lib/utils";
import {
  Trophy,
  Leaf,
  Clock,
  Star,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  MessageSquare,
  TrendingUp,
  TrendingDown,
  Minus,
  Sun,
  Snowflake,
  Zap,
  BarChart3,
  XCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { FeedbackForm } from "./FeedbackForm";
import { PlanDetailsModal } from "./PlanDetailsModal";
import { PlanSelectionModal } from "./PlanSelectionModal";
import type { Recommendation, RecommendationSet, UsageAnalysis, FilteredPlan } from "@/types";

interface RecommendationResultsProps {
  recommendations: RecommendationSet;
  onStartOver: () => void;
}

export function RecommendationResults({
  recommendations,
  onStartOver,
}: RecommendationResultsProps) {
  const { recommendations: plans, best_savings, processing_time_ms, warnings, usage_analysis, filtered_plans } = recommendations;
  const [showFiltered, setShowFiltered] = useState(false);

  return (
    <div className="space-y-4 sm:space-y-6" role="region" aria-label="Recommendation Results">
      {/* Summary header */}
      <header className="text-center">
        <div
          className="inline-flex items-center gap-2 bg-green-100 text-green-800 px-3 sm:px-4 py-2 rounded-full text-sm font-medium mb-3 sm:mb-4"
          role="status"
        >
          <CheckCircle className="w-4 h-4" aria-hidden="true" />
          <span>Found {plans.length} plans for you</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
          Your Top Recommendations
        </h2>
        <p className="text-gray-600 mt-2 text-sm sm:text-base">
          Potential savings up to{" "}
          <span className="text-arbor-primary font-semibold">
            {formatCurrency(best_savings)}/year
          </span>
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Generated in {processing_time_ms}ms
        </p>
      </header>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div
          className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 sm:p-4"
          role="alert"
          aria-label="Warnings"
        >
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
            <div className="text-sm text-yellow-800">
              {warnings.map((warning, i) => (
                <p key={i}>{warning}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Usage Insights */}
      {usage_analysis && <UsageInsightsCard analysis={usage_analysis} />}

      {/* Recommendation cards */}
      <ul className="space-y-4" aria-label="Recommended plans">
        {plans.map((rec) => (
          <li key={rec.id}>
            <RecommendationCard
              recommendation={rec}
              customerId={recommendations.customer_id}
            />
          </li>
        ))}
      </ul>

      {/* Filtered Plans - "Why Not" Section */}
      {filtered_plans && filtered_plans.length > 0 && (
        <FilteredPlansSection
          filteredPlans={filtered_plans}
          isExpanded={showFiltered}
          onToggle={() => setShowFiltered(!showFiltered)}
        />
      )}

      {/* Actions */}
      <div className="flex justify-center pt-2">
        <Button variant="outline" onClick={onStartOver}>
          <RefreshCw className="w-4 h-4 mr-2" aria-hidden="true" />
          Start Over
        </Button>
      </div>
    </div>
  );
}

function RecommendationCard({
  recommendation,
  customerId,
}: {
  recommendation: Recommendation;
  customerId: string;
}) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [showSelection, setShowSelection] = useState(false);
  const [isSelected, setIsSelected] = useState(false);
  const { rank, plan, explanation, risk_flags, confidence_level } = recommendation;
  const isTop = rank === 1;

  return (
    <Card variant={isTop ? "highlight" : "default"}>
      <CardHeader>
        {/* Mobile: Stack layout, Desktop: Row layout */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div className="flex items-center gap-3">
            {isTop && (
              <div
                className="flex items-center justify-center w-8 h-8 bg-yellow-100 rounded-full flex-shrink-0"
                aria-label="Top recommendation"
              >
                <Trophy className="w-4 h-4 text-yellow-600" aria-hidden="true" />
              </div>
            )}
            <div className="min-w-0">
              <CardTitle className="flex flex-wrap items-center gap-2">
                <span className="truncate">{plan.name}</span>
                {isTop && (
                  <span className="text-xs bg-arbor-primary text-white px-2 py-0.5 rounded-full whitespace-nowrap">
                    Best Match
                  </span>
                )}
              </CardTitle>
              <p className="text-sm text-gray-500">
                {plan.supplier?.name} • {getRateTypeLabel(plan.rate_type)}
              </p>
            </div>
          </div>
          <div className="text-left sm:text-right flex-shrink-0">
            <div className="text-xl sm:text-2xl font-bold text-arbor-primary">
              {formatCurrency(recommendation.projected_annual_savings)}
            </div>
            <div className="text-xs text-gray-500">annual savings</div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Scores grid - 2x2 on mobile, 4 columns on larger screens */}
        <div
          className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-4"
          role="group"
          aria-label="Plan scores"
        >
          <ScoreItem
            icon={<span className="text-lg" aria-hidden="true">💰</span>}
            label="Cost"
            score={recommendation.cost_score}
          />
          <ScoreItem
            icon={<Clock className="w-4 h-4" aria-hidden="true" />}
            label="Flexibility"
            score={recommendation.flexibility_score}
          />
          <ScoreItem
            icon={<Leaf className="w-4 h-4" aria-hidden="true" />}
            label="Green"
            score={recommendation.renewable_score}
          />
          <ScoreItem
            icon={<Star className="w-4 h-4" aria-hidden="true" />}
            label="Rating"
            score={recommendation.rating_score}
          />
        </div>

        {/* Plan details - 2x2 grid on mobile */}
        <dl className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 text-sm bg-gray-50 rounded-lg p-3 mb-4">
          <div>
            <dt className="text-gray-500">Rate</dt>
            <dd className="font-medium">${plan.rate_per_kwh}/kWh</dd>
          </div>
          <div>
            <dt className="text-gray-500">Monthly Fee</dt>
            <dd className="font-medium">{formatCurrency(plan.monthly_fee)}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Contract</dt>
            <dd className="font-medium">{plan.contract_length_months} months</dd>
          </div>
          <div>
            <dt className="text-gray-500">Renewable</dt>
            <dd className="font-medium">
              {formatPercentage(plan.renewable_percentage)}
            </dd>
          </div>
        </dl>

        {/* Explanation */}
        <p className="text-sm text-gray-600 mb-4">{explanation}</p>

        {/* Risk flags */}
        {risk_flags.length > 0 && (
          <div className="space-y-2" role="list" aria-label="Risk warnings">
            {risk_flags.map((flag, i) => (
              <div
                key={i}
                className={`text-xs px-3 py-2 rounded border ${getSeverityColor(flag.severity)}`}
                role="listitem"
              >
                <AlertTriangle className="w-3 h-3 inline mr-1" aria-hidden="true" />
                <span>{flag.message}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      <CardFooter>
        {/* Mobile: Stack buttons, Desktop: Row layout */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between w-full gap-3">
          <span
            className={`text-xs ${getConfidenceColor(confidence_level)} order-2 sm:order-1 text-center sm:text-left`}
          >
            {confidence_level.charAt(0).toUpperCase() + confidence_level.slice(1)}{" "}
            confidence
          </span>
          <div className="flex gap-2 order-1 sm:order-2 justify-center sm:justify-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFeedback(!showFeedback)}
              aria-expanded={showFeedback}
            >
              <MessageSquare className="w-4 h-4 mr-1" aria-hidden="true" />
              Feedback
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="flex-1 sm:flex-none"
              onClick={() => setShowDetails(true)}
            >
              View Details
            </Button>
            <Button
              size="sm"
              className="flex-1 sm:flex-none"
              onClick={() => setShowSelection(true)}
              disabled={isSelected}
            >
              {isSelected ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-1" aria-hidden="true" />
                  Selected
                </>
              ) : (
                "Select Plan"
              )}
            </Button>
          </div>
        </div>
      </CardFooter>

      {/* Feedback form */}
      {showFeedback && (
        <div className="px-6 pb-6">
          <FeedbackForm
            customerId={customerId}
            recommendation={recommendation}
            onSubmitted={() => setShowFeedback(false)}
          />
        </div>
      )}

      {/* Plan details modal */}
      <PlanDetailsModal
        isOpen={showDetails}
        onClose={() => setShowDetails(false)}
        recommendation={recommendation}
      />

      {/* Plan selection modal */}
      <PlanSelectionModal
        isOpen={showSelection}
        onClose={() => setShowSelection(false)}
        recommendation={recommendation}
        customerId={customerId}
        onPlanSelected={() => setIsSelected(true)}
      />
    </Card>
  );
}

function ScoreItem({
  icon,
  label,
  score,
}: {
  icon: React.ReactNode;
  label: string;
  score: number;
}) {
  const percentage = Math.round(score * 100);
  const color =
    percentage >= 70
      ? "text-green-600"
      : percentage >= 40
        ? "text-yellow-600"
        : "text-red-600";

  return (
    <div className="text-center p-2 sm:p-0">
      <div className="flex justify-center text-gray-400 mb-1">{icon}</div>
      <div className={`text-sm font-semibold ${color}`} aria-label={`${label}: ${percentage}%`}>
        {percentage}%
      </div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

function UsageInsightsCard({ analysis }: { analysis: UsageAnalysis }) {
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  const getSeasonalIcon = () => {
    switch (analysis.seasonal_pattern) {
      case "summer_peak":
        return <Sun className="w-5 h-5 text-orange-500" aria-hidden="true" />;
      case "winter_peak":
        return <Snowflake className="w-5 h-5 text-blue-500" aria-hidden="true" />;
      case "dual_peak":
        return <Zap className="w-5 h-5 text-purple-500" aria-hidden="true" />;
      default:
        return <Minus className="w-5 h-5 text-gray-500" aria-hidden="true" />;
    }
  };

  const getSeasonalLabel = () => {
    switch (analysis.seasonal_pattern) {
      case "summer_peak":
        return "Summer Peak";
      case "winter_peak":
        return "Winter Peak";
      case "dual_peak":
        return "Dual Peak (Summer & Winter)";
      default:
        return "Flat Usage";
    }
  };

  const getTrendIcon = () => {
    switch (analysis.usage_trend) {
      case "increasing":
        return <TrendingUp className="w-5 h-5 text-red-500" aria-hidden="true" />;
      case "decreasing":
        return <TrendingDown className="w-5 h-5 text-green-500" aria-hidden="true" />;
      default:
        return <Minus className="w-5 h-5 text-gray-500" aria-hidden="true" />;
    }
  };

  const getTrendLabel = () => {
    const change = Math.abs(Number(analysis.trend_percent_change)).toFixed(1);
    switch (analysis.usage_trend) {
      case "increasing":
        return `Increasing (+${change}%)`;
      case "decreasing":
        return `Decreasing (-${change}%)`;
      default:
        return "Stable";
    }
  };

  const getTierColor = () => {
    switch (analysis.consumption_tier) {
      case "low":
        return "bg-green-100 text-green-800";
      case "medium":
        return "bg-blue-100 text-blue-800";
      case "high":
        return "bg-orange-100 text-orange-800";
      case "very_high":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getTierLabel = () => {
    switch (analysis.consumption_tier) {
      case "low":
        return "Low Consumer";
      case "medium":
        return "Average Consumer";
      case "high":
        return "High Consumer";
      case "very_high":
        return "Very High Consumer";
      default:
        return analysis.consumption_tier;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
          Your Usage Profile
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Key metrics */}
        <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <dt className="text-xs text-gray-500 mb-1">Annual Usage</dt>
            <dd className="text-lg font-semibold text-gray-900">
              {Number(analysis.total_annual_kwh).toLocaleString()} kWh
            </dd>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <dt className="text-xs text-gray-500 mb-1">Monthly Avg</dt>
            <dd className="text-lg font-semibold text-gray-900">
              {Math.round(Number(analysis.average_monthly_kwh)).toLocaleString()} kWh
            </dd>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <dt className="text-xs text-gray-500 mb-1">Data Quality</dt>
            <dd className="text-lg font-semibold text-gray-900">
              {Math.round(Number(analysis.data_quality_score) * 100)}%
            </dd>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <dt className="text-xs text-gray-500 mb-1">Months Analyzed</dt>
            <dd className="text-lg font-semibold text-gray-900">
              {analysis.months_of_data}
            </dd>
          </div>
        </dl>

        {/* Pattern summary */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
          {/* Seasonal Pattern */}
          <div className="flex items-center gap-3 p-3 border rounded-lg">
            {getSeasonalIcon()}
            <div>
              <div className="text-xs text-gray-500">Seasonal Pattern</div>
              <div className="font-medium text-sm">{getSeasonalLabel()}</div>
              {Number(analysis.seasonal_variation_percent) > 0 && (
                <div className="text-xs text-gray-400">
                  ±{Number(analysis.seasonal_variation_percent).toFixed(0)}% variation
                </div>
              )}
            </div>
          </div>

          {/* Usage Trend */}
          <div className="flex items-center gap-3 p-3 border rounded-lg">
            {getTrendIcon()}
            <div>
              <div className="text-xs text-gray-500">Usage Trend</div>
              <div className="font-medium text-sm">{getTrendLabel()}</div>
            </div>
          </div>

          {/* Consumption Tier */}
          <div className="flex items-center gap-3 p-3 border rounded-lg">
            <div className={`px-2 py-1 rounded text-xs font-medium ${getTierColor()}`}>
              {getTierLabel()}
            </div>
          </div>
        </div>

        {/* Peak and Low months */}
        {(analysis.peak_months.length > 0 || analysis.low_months.length > 0) && (
          <div className="grid grid-cols-2 gap-3 mb-4">
            {analysis.peak_months.length > 0 && (
              <div className="p-3 bg-red-50 rounded-lg">
                <div className="text-xs text-red-600 font-medium mb-1">Peak Usage Months</div>
                <div className="text-sm text-red-800">
                  {analysis.peak_months.map(m => monthNames[m - 1]).join(", ")}
                </div>
              </div>
            )}
            {analysis.low_months.length > 0 && (
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="text-xs text-green-600 font-medium mb-1">Low Usage Months</div>
                <div className="text-sm text-green-800">
                  {analysis.low_months.map(m => monthNames[m - 1]).join(", ")}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Personalized Insights */}
        {Object.keys(analysis.insights).length > 0 && (
          <div className="bg-arbor-light rounded-lg p-4">
            <h4 className="text-sm font-semibold text-arbor-primary mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4" aria-hidden="true" />
              Personalized Insights
            </h4>
            <ul className="space-y-2">
              {Object.entries(analysis.insights).map(([key, value]) => (
                <li key={key} className="text-sm text-gray-700 flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-arbor-primary flex-shrink-0 mt-0.5" aria-hidden="true" />
                  <span>{value}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function FilteredPlansSection({
  filteredPlans,
  isExpanded,
  onToggle,
}: {
  filteredPlans: FilteredPlan[];
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const getFilterIcon = (code: string) => {
    switch (code) {
      case "LOW_RENEWABLE":
        return <Leaf className="w-4 h-4 text-gray-400" aria-hidden="true" />;
      case "LONG_CONTRACT":
        return <Clock className="w-4 h-4 text-gray-400" aria-hidden="true" />;
      case "VARIABLE_RATE":
        return <TrendingUp className="w-4 h-4 text-gray-400" aria-hidden="true" />;
      default:
        return <XCircle className="w-4 h-4 text-gray-400" aria-hidden="true" />;
    }
  };

  const getFilterBadgeColor = (code: string) => {
    switch (code) {
      case "LOW_RENEWABLE":
        return "bg-green-100 text-green-700";
      case "LONG_CONTRACT":
        return "bg-blue-100 text-blue-700";
      case "VARIABLE_RATE":
        return "bg-orange-100 text-orange-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const getFilterLabel = (code: string) => {
    switch (code) {
      case "LOW_RENEWABLE":
        return "Low Renewable";
      case "LONG_CONTRACT":
        return "Long Contract";
      case "VARIABLE_RATE":
        return "Variable Rate";
      default:
        return code;
    }
  };

  return (
    <Card>
      <button
        onClick={onToggle}
        className="w-full px-4 sm:px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors rounded-lg"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-2">
          <XCircle className="w-5 h-5 text-gray-400" aria-hidden="true" />
          <span className="font-medium text-gray-700">
            Why not these {filteredPlans.length} plans?
          </span>
          <span className="text-sm text-gray-500">
            (Filtered based on your preferences)
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" aria-hidden="true" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" aria-hidden="true" />
        )}
      </button>

      {isExpanded && (
        <CardContent className="pt-0">
          <ul className="divide-y divide-gray-100">
            {filteredPlans.map((plan) => (
              <li key={plan.plan_id} className="py-3 first:pt-0 last:pb-0">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <div className="flex items-start gap-3">
                    {getFilterIcon(plan.filter_code)}
                    <div>
                      <div className="font-medium text-gray-900">{plan.plan_name}</div>
                      {plan.supplier_name && (
                        <div className="text-sm text-gray-500">{plan.supplier_name}</div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-7 sm:ml-0">
                    <span className={`text-xs px-2 py-1 rounded-full ${getFilterBadgeColor(plan.filter_code)}`}>
                      {getFilterLabel(plan.filter_code)}
                    </span>
                  </div>
                </div>
                <p className="mt-2 ml-7 text-sm text-gray-600">{plan.filter_reason}</p>
              </li>
            ))}
          </ul>
        </CardContent>
      )}
    </Card>
  );
}
