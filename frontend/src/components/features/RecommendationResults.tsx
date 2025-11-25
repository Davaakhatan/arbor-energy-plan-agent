"use client";

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
} from "lucide-react";
import type { Recommendation, RecommendationSet } from "@/types";

interface RecommendationResultsProps {
  recommendations: RecommendationSet;
  onStartOver: () => void;
}

export function RecommendationResults({
  recommendations,
  onStartOver,
}: RecommendationResultsProps) {
  const { recommendations: plans, best_savings, processing_time_ms, warnings } = recommendations;

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

      {/* Recommendation cards */}
      <ul className="space-y-4" aria-label="Recommended plans">
        {plans.map((rec) => (
          <li key={rec.id}>
            <RecommendationCard recommendation={rec} />
          </li>
        ))}
      </ul>

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

function RecommendationCard({ recommendation }: { recommendation: Recommendation }) {
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
            <Button variant="outline" size="sm" className="flex-1 sm:flex-none">
              View Details
            </Button>
            <Button size="sm" className="flex-1 sm:flex-none">
              Select Plan
            </Button>
          </div>
        </div>
      </CardFooter>
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
