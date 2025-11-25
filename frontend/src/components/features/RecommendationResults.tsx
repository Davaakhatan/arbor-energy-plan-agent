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
    <div className="space-y-6">
      {/* Summary header */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium mb-4">
          <CheckCircle className="w-4 h-4" />
          Found {plans.length} plans for you
        </div>
        <h2 className="text-2xl font-bold text-gray-900">
          Your Top Recommendations
        </h2>
        <p className="text-gray-600 mt-2">
          Potential savings up to{" "}
          <span className="text-arbor-primary font-semibold">
            {formatCurrency(best_savings)}/year
          </span>
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Generated in {processing_time_ms}ms
        </p>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-800">
              {warnings.map((warning, i) => (
                <p key={i}>{warning}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recommendation cards */}
      <div className="space-y-4">
        {plans.map((rec) => (
          <RecommendationCard key={rec.id} recommendation={rec} />
        ))}
      </div>

      {/* Actions */}
      <div className="flex justify-center">
        <Button variant="outline" onClick={onStartOver}>
          <RefreshCw className="w-4 h-4 mr-2" />
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
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {isTop && (
              <div className="flex items-center justify-center w-8 h-8 bg-yellow-100 rounded-full">
                <Trophy className="w-4 h-4 text-yellow-600" />
              </div>
            )}
            <div>
              <CardTitle className="flex items-center gap-2">
                {plan.name}
                {isTop && (
                  <span className="text-xs bg-arbor-primary text-white px-2 py-0.5 rounded-full">
                    Best Match
                  </span>
                )}
              </CardTitle>
              <p className="text-sm text-gray-500">
                {plan.supplier?.name} • {getRateTypeLabel(plan.rate_type)}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-arbor-primary">
              {formatCurrency(recommendation.projected_annual_savings)}
            </div>
            <div className="text-xs text-gray-500">annual savings</div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Scores grid */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          <ScoreItem
            icon={<span className="text-lg">💰</span>}
            label="Cost"
            score={recommendation.cost_score}
          />
          <ScoreItem
            icon={<Clock className="w-4 h-4" />}
            label="Flexibility"
            score={recommendation.flexibility_score}
          />
          <ScoreItem
            icon={<Leaf className="w-4 h-4" />}
            label="Green"
            score={recommendation.renewable_score}
          />
          <ScoreItem
            icon={<Star className="w-4 h-4" />}
            label="Rating"
            score={recommendation.rating_score}
          />
        </div>

        {/* Plan details */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm bg-gray-50 rounded-lg p-3 mb-4">
          <div>
            <span className="text-gray-500">Rate</span>
            <div className="font-medium">${plan.rate_per_kwh}/kWh</div>
          </div>
          <div>
            <span className="text-gray-500">Monthly Fee</span>
            <div className="font-medium">{formatCurrency(plan.monthly_fee)}</div>
          </div>
          <div>
            <span className="text-gray-500">Contract</span>
            <div className="font-medium">{plan.contract_length_months} months</div>
          </div>
          <div>
            <span className="text-gray-500">Renewable</span>
            <div className="font-medium">
              {formatPercentage(plan.renewable_percentage)}
            </div>
          </div>
        </div>

        {/* Explanation */}
        <p className="text-sm text-gray-600 mb-4">{explanation}</p>

        {/* Risk flags */}
        {risk_flags.length > 0 && (
          <div className="space-y-2">
            {risk_flags.map((flag, i) => (
              <div
                key={i}
                className={`text-xs px-3 py-2 rounded border ${getSeverityColor(flag.severity)}`}
              >
                <AlertTriangle className="w-3 h-3 inline mr-1" />
                {flag.message}
              </div>
            ))}
          </div>
        )}
      </CardContent>

      <CardFooter>
        <div className="flex items-center justify-between w-full">
          <span className={`text-xs ${getConfidenceColor(confidence_level)}`}>
            {confidence_level.charAt(0).toUpperCase() + confidence_level.slice(1)}{" "}
            confidence
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              View Details
            </Button>
            <Button size="sm">Select Plan</Button>
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
    <div className="text-center">
      <div className="flex justify-center text-gray-400 mb-1">{icon}</div>
      <div className={`text-sm font-semibold ${color}`}>{percentage}%</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
