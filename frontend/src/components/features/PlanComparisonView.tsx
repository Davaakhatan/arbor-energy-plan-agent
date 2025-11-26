"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  formatCurrency,
  formatPercentage,
  getRateTypeLabel,
} from "@/lib/utils";
import {
  ArrowLeftRight,
  Check,
  X,
  Trophy,
  Leaf,
  Clock,
  Star,
  DollarSign,
  AlertTriangle,
} from "lucide-react";
import type { Recommendation } from "@/types";

interface PlanComparisonViewProps {
  recommendations: Recommendation[];
  onClose: () => void;
}

interface ComparisonItem {
  label: string;
  getValue: (rec: Recommendation) => string | number | React.ReactNode;
  highlight?: "lowest" | "highest" | "none";
  format?: "currency" | "percentage" | "number" | "text";
}

export function PlanComparisonView({
  recommendations,
  onClose,
}: PlanComparisonViewProps) {
  const [selectedPlans, setSelectedPlans] = useState<string[]>(
    recommendations.slice(0, Math.min(3, recommendations.length)).map((r) => r.id)
  );

  const togglePlan = (planId: string) => {
    if (selectedPlans.includes(planId)) {
      if (selectedPlans.length > 2) {
        setSelectedPlans(selectedPlans.filter((id) => id !== planId));
      }
    } else if (selectedPlans.length < 3) {
      setSelectedPlans([...selectedPlans, planId]);
    }
  };

  const selectedRecommendations = recommendations.filter((r) =>
    selectedPlans.includes(r.id)
  );

  const comparisonItems: ComparisonItem[] = [
    {
      label: "Rate per kWh",
      getValue: (rec) => `$${Number(rec.plan.rate_per_kwh).toFixed(4)}`,
      highlight: "lowest",
    },
    {
      label: "Monthly Fee",
      getValue: (rec) => formatCurrency(rec.plan.monthly_fee),
      highlight: "lowest",
    },
    {
      label: "Projected Annual Cost",
      getValue: (rec) => formatCurrency(rec.projected_annual_cost),
      highlight: "lowest",
    },
    {
      label: "Annual Savings",
      getValue: (rec) => formatCurrency(rec.projected_annual_savings),
      highlight: "highest",
    },
    {
      label: "Contract Length",
      getValue: (rec) => `${rec.plan.contract_length_months} months`,
      highlight: "lowest",
    },
    {
      label: "Early Termination Fee",
      getValue: (rec) => formatCurrency(rec.plan.early_termination_fee),
      highlight: "lowest",
    },
    {
      label: "Renewable Energy",
      getValue: (rec) => formatPercentage(rec.plan.renewable_percentage),
      highlight: "highest",
    },
    {
      label: "Rate Type",
      getValue: (rec) => getRateTypeLabel(rec.plan.rate_type),
      highlight: "none",
    },
    {
      label: "Overall Score",
      getValue: (rec) => `${Math.round(Number(rec.overall_score) * 100)}%`,
      highlight: "highest",
    },
    {
      label: "Cost Score",
      getValue: (rec) => renderScoreBar(Number(rec.cost_score)),
      highlight: "none",
    },
    {
      label: "Flexibility Score",
      getValue: (rec) => renderScoreBar(Number(rec.flexibility_score)),
      highlight: "none",
    },
    {
      label: "Green Score",
      getValue: (rec) => renderScoreBar(Number(rec.renewable_score)),
      highlight: "none",
    },
    {
      label: "Rating Score",
      getValue: (rec) => renderScoreBar(Number(rec.rating_score)),
      highlight: "none",
    },
    {
      label: "Confidence",
      getValue: (rec) => (
        <span
          className={`capitalize ${
            rec.confidence_level === "high"
              ? "text-green-600"
              : rec.confidence_level === "medium"
                ? "text-yellow-600"
                : "text-red-600"
          }`}
        >
          {rec.confidence_level}
        </span>
      ),
      highlight: "none",
    },
    {
      label: "Risk Flags",
      getValue: (rec) =>
        rec.risk_flags.length === 0 ? (
          <span className="text-green-600 flex items-center gap-1">
            <Check className="w-4 h-4" aria-hidden="true" />
            None
          </span>
        ) : (
          <span className="text-orange-600 flex items-center gap-1">
            <AlertTriangle className="w-4 h-4" aria-hidden="true" />
            {rec.risk_flags.length} warning{rec.risk_flags.length > 1 ? "s" : ""}
          </span>
        ),
      highlight: "none",
    },
  ];

  const getHighlightClass = (
    item: ComparisonItem,
    rec: Recommendation,
    allRecs: Recommendation[]
  ): string => {
    if (item.highlight === "none") return "";

    const values = allRecs.map((r) => {
      const value = item.getValue(r);
      if (typeof value === "string") {
        const num = parseFloat(value.replace(/[^0-9.-]/g, ""));
        return isNaN(num) ? 0 : num;
      }
      return 0;
    });

    const currentValue = (() => {
      const value = item.getValue(rec);
      if (typeof value === "string") {
        const num = parseFloat(value.replace(/[^0-9.-]/g, ""));
        return isNaN(num) ? 0 : num;
      }
      return 0;
    })();

    if (item.highlight === "lowest" && currentValue === Math.min(...values)) {
      return "bg-green-50 text-green-700 font-semibold";
    }
    if (item.highlight === "highest" && currentValue === Math.max(...values)) {
      return "bg-green-50 text-green-700 font-semibold";
    }

    return "";
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <ArrowLeftRight className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
            Plan Comparison
          </CardTitle>
          <Button variant="outline" size="sm" onClick={onClose}>
            <X className="w-4 h-4" aria-hidden="true" />
          </Button>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Compare up to 3 plans side by side. Select plans below to compare.
        </p>
      </CardHeader>
      <CardContent>
        {/* Plan selection */}
        <div className="flex flex-wrap gap-2 mb-6 pb-4 border-b">
          {recommendations.map((rec) => (
            <button
              key={rec.id}
              onClick={() => togglePlan(rec.id)}
              className={`px-3 py-2 rounded-lg border text-sm transition-colors ${
                selectedPlans.includes(rec.id)
                  ? "bg-arbor-primary text-white border-arbor-primary"
                  : "bg-white text-gray-700 border-gray-300 hover:border-arbor-primary"
              }`}
              disabled={
                !selectedPlans.includes(rec.id) && selectedPlans.length >= 3
              }
            >
              {rec.rank === 1 && (
                <Trophy className="w-3 h-3 inline mr-1" aria-hidden="true" />
              )}
              {rec.plan.name}
            </button>
          ))}
        </div>

        {/* Comparison table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-500 min-w-[140px]">
                  Feature
                </th>
                {selectedRecommendations.map((rec) => (
                  <th
                    key={rec.id}
                    className="text-center py-3 px-2 min-w-[150px]"
                  >
                    <div className="flex flex-col items-center gap-1">
                      {rec.rank === 1 && (
                        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                          Best Match
                        </span>
                      )}
                      <span className="font-semibold text-gray-900 text-sm">
                        {rec.plan.name}
                      </span>
                      <span className="text-xs text-gray-500">
                        {rec.plan.supplier?.name}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {comparisonItems.map((item, idx) => (
                <tr
                  key={item.label}
                  className={idx % 2 === 0 ? "bg-gray-50" : ""}
                >
                  <td className="py-3 px-2 text-sm text-gray-600 font-medium">
                    {getItemIcon(item.label)}
                    {item.label}
                  </td>
                  {selectedRecommendations.map((rec) => (
                    <td
                      key={rec.id}
                      className={`py-3 px-2 text-center text-sm ${getHighlightClass(
                        item,
                        rec,
                        selectedRecommendations
                      )}`}
                    >
                      {item.getValue(rec)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Summary */}
        <div className="mt-6 pt-4 border-t">
          <h4 className="font-semibold text-gray-900 mb-3">Quick Summary</h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {selectedRecommendations.map((rec) => (
              <div
                key={rec.id}
                className={`p-4 rounded-lg border ${
                  rec.rank === 1
                    ? "border-arbor-primary bg-arbor-light"
                    : "border-gray-200"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {rec.rank === 1 && (
                    <Trophy className="w-4 h-4 text-yellow-600" aria-hidden="true" />
                  )}
                  <span className="font-semibold text-gray-900 text-sm">
                    {rec.plan.name}
                  </span>
                </div>
                <p className="text-xs text-gray-600 line-clamp-3">
                  {rec.explanation}
                </p>
                <div className="mt-3 text-lg font-bold text-arbor-primary">
                  Save {formatCurrency(rec.projected_annual_savings)}/yr
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function renderScoreBar(score: number): React.ReactNode {
  const percentage = Math.round(score * 100);
  const color =
    percentage >= 70
      ? "bg-green-500"
      : percentage >= 40
        ? "bg-yellow-500"
        : "bg-red-500";

  return (
    <div className="flex items-center gap-2 justify-center">
      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-gray-600 w-8">{percentage}%</span>
    </div>
  );
}

function getItemIcon(label: string): React.ReactNode {
  const iconClass = "w-4 h-4 inline mr-2 text-gray-400";

  switch (label) {
    case "Rate per kWh":
    case "Monthly Fee":
    case "Projected Annual Cost":
    case "Annual Savings":
    case "Early Termination Fee":
      return <DollarSign className={iconClass} aria-hidden="true" />;
    case "Contract Length":
      return <Clock className={iconClass} aria-hidden="true" />;
    case "Renewable Energy":
    case "Green Score":
      return <Leaf className={iconClass} aria-hidden="true" />;
    case "Rating Score":
      return <Star className={iconClass} aria-hidden="true" />;
    default:
      return null;
  }
}
