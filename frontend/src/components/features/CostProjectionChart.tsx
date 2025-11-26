"use client";

import { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils";
import {
  TrendingUp,
  Calendar,
  DollarSign,
} from "lucide-react";
import type { Recommendation, UsageAnalysis } from "@/types";

interface CostProjectionChartProps {
  recommendations: Recommendation[];
  usageAnalysis?: UsageAnalysis;
  currentAnnualCost?: number;
}

interface MonthlyProjection {
  month: string;
  monthIndex: number;
  costs: Record<string, number>;
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

const PLAN_COLORS = [
  { bg: "bg-arbor-primary", text: "text-arbor-primary", light: "bg-arbor-light" },
  { bg: "bg-blue-500", text: "text-blue-600", light: "bg-blue-100" },
  { bg: "bg-purple-500", text: "text-purple-600", light: "bg-purple-100" },
];

export function CostProjectionChart({
  recommendations,
  usageAnalysis,
  currentAnnualCost,
}: CostProjectionChartProps) {
  const [selectedPlan, setSelectedPlan] = useState<string | null>(
    recommendations[0]?.id || null
  );
  const [viewMode, setViewMode] = useState<"monthly" | "cumulative">("monthly");

  const projections = useMemo(() => {
    const currentMonth = new Date().getMonth();
    const monthlyData: MonthlyProjection[] = [];

    for (let i = 0; i < 12; i++) {
      const monthIndex = (currentMonth + i) % 12;
      const month = MONTHS[monthIndex];

      const costs: Record<string, number> = {};

      recommendations.forEach((rec) => {
        const annualCost = Number(rec.projected_annual_cost);
        let monthlyMultiplier = 1;

        if (usageAnalysis) {
          const isPeakMonth = usageAnalysis.peak_months.includes(monthIndex + 1);
          const isLowMonth = usageAnalysis.low_months.includes(monthIndex + 1);
          const seasonalVariation = Number(usageAnalysis.seasonal_variation_percent) / 100;

          if (isPeakMonth) {
            monthlyMultiplier = 1 + seasonalVariation * 0.5;
          } else if (isLowMonth) {
            monthlyMultiplier = 1 - seasonalVariation * 0.5;
          }
        }

        costs[rec.id] = (annualCost / 12) * monthlyMultiplier;
      });

      if (currentAnnualCost) {
        let multiplier = 1;
        if (usageAnalysis) {
          const isPeakMonth = usageAnalysis.peak_months.includes(monthIndex + 1);
          const isLowMonth = usageAnalysis.low_months.includes(monthIndex + 1);
          const seasonalVariation = Number(usageAnalysis.seasonal_variation_percent) / 100;

          if (isPeakMonth) {
            multiplier = 1 + seasonalVariation * 0.5;
          } else if (isLowMonth) {
            multiplier = 1 - seasonalVariation * 0.5;
          }
        }
        costs["current"] = (currentAnnualCost / 12) * multiplier;
      }

      monthlyData.push({ month, monthIndex, costs });
    }

    return monthlyData;
  }, [recommendations, usageAnalysis, currentAnnualCost]);

  const cumulativeData = useMemo(() => {
    const runningTotals: Record<string, number> = {};
    recommendations.forEach((rec) => {
      runningTotals[rec.id] = 0;
    });
    if (currentAnnualCost) {
      runningTotals["current"] = 0;
    }

    return projections.map((proj) => {
      const newCosts: Record<string, number> = {};
      Object.keys(proj.costs).forEach((key) => {
        runningTotals[key] = (runningTotals[key] || 0) + proj.costs[key];
        newCosts[key] = runningTotals[key];
      });
      return { ...proj, costs: newCosts };
    });
  }, [projections, recommendations, currentAnnualCost]);

  const displayData = viewMode === "monthly" ? projections : cumulativeData;

  const maxCost = useMemo(() => {
    let max = 0;
    displayData.forEach((proj) => {
      Object.values(proj.costs).forEach((cost) => {
        if (cost > max) max = cost;
      });
    });
    return max;
  }, [displayData]);

  const totalSavings = useMemo(() => {
    if (!currentAnnualCost || !selectedPlan) return null;
    const selectedRec = recommendations.find((r) => r.id === selectedPlan);
    if (!selectedRec) return null;
    return currentAnnualCost - Number(selectedRec.projected_annual_cost);
  }, [currentAnnualCost, selectedPlan, recommendations]);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
            12-Month Cost Projection
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant={viewMode === "monthly" ? "primary" : "outline"}
              size="sm"
              onClick={() => setViewMode("monthly")}
            >
              <Calendar className="w-4 h-4 mr-1" aria-hidden="true" />
              Monthly
            </Button>
            <Button
              variant={viewMode === "cumulative" ? "primary" : "outline"}
              size="sm"
              onClick={() => setViewMode("cumulative")}
            >
              <DollarSign className="w-4 h-4 mr-1" aria-hidden="true" />
              Cumulative
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Plan selector */}
        <div className="flex flex-wrap gap-2 mb-6">
          {recommendations.map((rec, idx) => (
            <button
              key={rec.id}
              onClick={() => setSelectedPlan(rec.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selectedPlan === rec.id
                  ? `${PLAN_COLORS[idx % PLAN_COLORS.length].bg} text-white`
                  : `${PLAN_COLORS[idx % PLAN_COLORS.length].light} ${PLAN_COLORS[idx % PLAN_COLORS.length].text} hover:opacity-80`
              }`}
            >
              {rec.plan.name}
            </button>
          ))}
          {currentAnnualCost && (
            <button
              onClick={() => setSelectedPlan("current")}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selectedPlan === "current"
                  ? "bg-gray-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:opacity-80"
              }`}
            >
              Current Plan
            </button>
          )}
        </div>

        {/* Chart */}
        <div className="relative h-64 mb-4">
          <div className="absolute inset-0 flex items-end justify-between gap-1">
            {displayData.map((proj, idx) => {
              const selectedCost = selectedPlan
                ? proj.costs[selectedPlan] || 0
                : Object.values(proj.costs)[0] || 0;
              const heightPercent = maxCost > 0 ? (selectedCost / maxCost) * 100 : 0;

              const planIndex = recommendations.findIndex(
                (r) => r.id === selectedPlan
              );
              const colorClass =
                selectedPlan === "current"
                  ? "bg-gray-400"
                  : PLAN_COLORS[planIndex % PLAN_COLORS.length]?.bg || "bg-arbor-primary";

              return (
                <div
                  key={proj.month}
                  className="flex-1 flex flex-col items-center"
                >
                  <div className="w-full relative group">
                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                      <div className="bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                        {formatCurrency(selectedCost)}
                      </div>
                    </div>
                    {/* Bar */}
                    <div
                      className={`w-full ${colorClass} rounded-t transition-all duration-300 hover:opacity-80`}
                      style={{
                        height: `${Math.max(heightPercent * 2.4, 4)}px`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 mt-1">
                    {idx % 2 === 0 ? proj.month : ""}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Y-axis labels */}
        <div className="flex justify-between text-xs text-gray-400 border-t pt-2">
          <span>{formatCurrency(0)}</span>
          <span>{formatCurrency(maxCost / 2)}</span>
          <span>{formatCurrency(maxCost)}</span>
        </div>

        {/* Summary stats */}
        {selectedPlan && selectedPlan !== "current" && (
          <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t">
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">
                {viewMode === "monthly" ? "Avg Monthly" : "Year Total"}
              </div>
              <div className="font-semibold text-gray-900">
                {viewMode === "monthly"
                  ? formatCurrency(
                      (recommendations.find((r) => r.id === selectedPlan)
                        ?.projected_annual_cost || 0) / 12
                    )
                  : formatCurrency(
                      recommendations.find((r) => r.id === selectedPlan)
                        ?.projected_annual_cost || 0
                    )}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">Annual Savings</div>
              <div className="font-semibold text-green-600">
                {formatCurrency(
                  recommendations.find((r) => r.id === selectedPlan)
                    ?.projected_annual_savings || 0
                )}
              </div>
            </div>
            {totalSavings !== null && (
              <>
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">
                    vs Current Plan
                  </div>
                  <div
                    className={`font-semibold ${
                      totalSavings > 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {totalSavings > 0 ? "+" : ""}
                    {formatCurrency(totalSavings)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">
                    Monthly Savings
                  </div>
                  <div
                    className={`font-semibold ${
                      totalSavings > 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {totalSavings > 0 ? "+" : ""}
                    {formatCurrency(totalSavings / 12)}
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
