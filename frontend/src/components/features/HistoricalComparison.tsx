"use client";

import { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  History,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  DollarSign,
  BarChart3,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import type { Recommendation, UsageAnalysis } from "@/types";

interface HistoricalComparisonProps {
  recommendations: Recommendation[];
  usageAnalysis?: UsageAnalysis;
  currentAnnualCost?: number;
}

// Simulated historical rate data (in a real app, this would come from the API)
const HISTORICAL_RATES: { month: string; avgRate: number; lowestRate: number }[] = [
  { month: "Jan 2024", avgRate: 0.128, lowestRate: 0.095 },
  { month: "Feb 2024", avgRate: 0.125, lowestRate: 0.092 },
  { month: "Mar 2024", avgRate: 0.118, lowestRate: 0.088 },
  { month: "Apr 2024", avgRate: 0.115, lowestRate: 0.085 },
  { month: "May 2024", avgRate: 0.122, lowestRate: 0.091 },
  { month: "Jun 2024", avgRate: 0.135, lowestRate: 0.102 },
  { month: "Jul 2024", avgRate: 0.145, lowestRate: 0.112 },
  { month: "Aug 2024", avgRate: 0.148, lowestRate: 0.115 },
  { month: "Sep 2024", avgRate: 0.138, lowestRate: 0.105 },
  { month: "Oct 2024", avgRate: 0.125, lowestRate: 0.095 },
  { month: "Nov 2024", avgRate: 0.120, lowestRate: 0.090 },
  { month: "Dec 2024", avgRate: 0.118, lowestRate: 0.088 },
];

type TimeRange = "3m" | "6m" | "12m";

export function HistoricalComparison({
  recommendations,
  usageAnalysis,
  currentAnnualCost: _currentAnnualCost,
}: HistoricalComparisonProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>("12m");
  const [showDetails, setShowDetails] = useState(false);

  const topRecommendation = recommendations[0];
  const currentRate = topRecommendation
    ? Number(topRecommendation.plan.rate_per_kwh)
    : null;

  const filteredHistory = useMemo(() => {
    const monthsToShow = timeRange === "3m" ? 3 : timeRange === "6m" ? 6 : 12;
    return HISTORICAL_RATES.slice(-monthsToShow);
  }, [timeRange]);

  const stats = useMemo(() => {
    const rates = filteredHistory.map((h) => h.avgRate);
    const lowestRates = filteredHistory.map((h) => h.lowestRate);

    const avgRate = rates.reduce((a, b) => a + b, 0) / rates.length;
    const minAvgRate = Math.min(...rates);
    const maxAvgRate = Math.max(...rates);
    const minLowestRate = Math.min(...lowestRates);

    // Calculate if current recommendation is a good deal
    const currentVsAvg = currentRate ? ((avgRate - currentRate) / avgRate) * 100 : 0;
    const currentVsHistoricLow = currentRate
      ? ((minLowestRate - currentRate) / minLowestRate) * 100
      : 0;

    return {
      avgRate,
      minAvgRate,
      maxAvgRate,
      minLowestRate,
      currentVsAvg,
      currentVsHistoricLow,
      isGoodDeal: currentRate !== null && currentRate <= avgRate,
      isGreatDeal: currentRate !== null && currentRate <= minLowestRate * 1.05,
    };
  }, [filteredHistory, currentRate]);

  // Calculate what the user would have paid historically
  const historicalCostComparison = useMemo(() => {
    if (!usageAnalysis) return null;

    const annualKwh = Number(usageAnalysis.total_annual_kwh);
    const monthlyFee = topRecommendation ? Number(topRecommendation.plan.monthly_fee) : 0;

    return {
      atAvgRate: annualKwh * stats.avgRate + monthlyFee * 12,
      atMinRate: annualKwh * stats.minLowestRate + monthlyFee * 12,
      atMaxRate: annualKwh * stats.maxAvgRate + monthlyFee * 12,
      atCurrentRate: currentRate
        ? annualKwh * currentRate + monthlyFee * 12
        : null,
    };
  }, [usageAnalysis, stats, topRecommendation, currentRate]);

  const maxBarHeight = Math.max(...filteredHistory.map((h) => h.avgRate));

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
            Historical Rate Comparison
          </CardTitle>
          <div className="flex gap-2">
            {(["3m", "6m", "12m"] as TimeRange[]).map((range) => (
              <Button
                key={range}
                variant={timeRange === range ? "primary" : "outline"}
                size="sm"
                onClick={() => setTimeRange(range)}
              >
                {range === "3m" ? "3 Mo" : range === "6m" ? "6 Mo" : "1 Year"}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Deal Assessment */}
        {currentRate && (
          <div className={`p-4 rounded-lg ${
            stats.isGreatDeal
              ? "bg-green-50 border border-green-200"
              : stats.isGoodDeal
                ? "bg-blue-50 border border-blue-200"
                : "bg-yellow-50 border border-yellow-200"
          }`}>
            <div className="flex items-start gap-3">
              {stats.isGreatDeal ? (
                <TrendingDown className="w-5 h-5 text-green-600 mt-0.5" aria-hidden="true" />
              ) : stats.isGoodDeal ? (
                <Minus className="w-5 h-5 text-blue-600 mt-0.5" aria-hidden="true" />
              ) : (
                <TrendingUp className="w-5 h-5 text-yellow-600 mt-0.5" aria-hidden="true" />
              )}
              <div>
                <p className={`font-medium ${
                  stats.isGreatDeal ? "text-green-800" :
                  stats.isGoodDeal ? "text-blue-800" : "text-yellow-800"
                }`}>
                  {stats.isGreatDeal
                    ? "Excellent Deal! Near historic lows"
                    : stats.isGoodDeal
                      ? "Good Deal - Below average rates"
                      : "Above average - Consider waiting"}
                </p>
                <p className="text-sm mt-1 text-gray-600">
                  Your recommended rate of ${currentRate.toFixed(4)}/kWh is{" "}
                  {stats.currentVsAvg > 0 ? (
                    <span className="text-green-600 font-medium">
                      {Math.abs(stats.currentVsAvg).toFixed(1)}% below
                    </span>
                  ) : (
                    <span className="text-yellow-600 font-medium">
                      {Math.abs(stats.currentVsAvg).toFixed(1)}% above
                    </span>
                  )}{" "}
                  the {timeRange === "12m" ? "yearly" : `${timeRange.replace("m", "-month")}`} average.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Rate Chart */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Rate History</span>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-gray-300" /> Avg Market
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-green-500" /> Best Available
              </span>
              {currentRate && (
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded bg-arbor-primary" /> Your Plan
                </span>
              )}
            </div>
          </div>

          <div className="flex items-end justify-between gap-1 h-40 pt-4">
            {filteredHistory.map((data) => {
              const avgHeight = (data.avgRate / maxBarHeight) * 100;
              const lowHeight = (data.lowestRate / maxBarHeight) * 100;

              return (
                <div
                  key={data.month}
                  className="flex-1 flex flex-col items-center gap-1"
                >
                  <div className="w-full flex items-end justify-center gap-0.5 h-32">
                    {/* Average rate bar */}
                    <div
                      className="w-2 bg-gray-300 rounded-t"
                      style={{ height: `${avgHeight}%` }}
                      title={`Avg: $${data.avgRate.toFixed(3)}/kWh`}
                    />
                    {/* Lowest rate bar */}
                    <div
                      className="w-2 bg-green-500 rounded-t"
                      style={{ height: `${lowHeight}%` }}
                      title={`Low: $${data.lowestRate.toFixed(3)}/kWh`}
                    />
                  </div>
                  <span className="text-[10px] text-gray-500 -rotate-45 origin-left whitespace-nowrap">
                    {data.month.split(" ")[0]}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Current rate line */}
          {currentRate && (
            <div className="relative h-0 -mt-32">
              <div
                className="absolute w-full border-t-2 border-dashed border-arbor-primary"
                style={{ bottom: `${(currentRate / maxBarHeight) * 128}px` }}
              >
                <span className="absolute right-0 -top-5 text-xs bg-arbor-light text-arbor-primary px-1 rounded">
                  ${currentRate.toFixed(3)}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Avg Rate</p>
            <p className="text-lg font-semibold">${stats.avgRate.toFixed(3)}</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Lowest Ever</p>
            <p className="text-lg font-semibold text-green-600">${stats.minLowestRate.toFixed(3)}</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Highest Avg</p>
            <p className="text-lg font-semibold text-red-500">${stats.maxAvgRate.toFixed(3)}</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Your Rate</p>
            <p className={`text-lg font-semibold ${
              stats.isGoodDeal ? "text-green-600" : "text-yellow-600"
            }`}>
              {currentRate ? `$${currentRate.toFixed(3)}` : "N/A"}
            </p>
          </div>
        </div>

        {/* Cost Comparison */}
        {historicalCostComparison && (
          <div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
              className="w-full text-gray-600"
            >
              <BarChart3 className="w-4 h-4 mr-2" aria-hidden="true" />
              {showDetails ? "Hide" : "Show"} Cost Comparison
            </Button>

            {showDetails && (
              <div className="mt-4 space-y-3">
                <p className="text-sm text-gray-600 mb-2">
                  Based on your annual usage of{" "}
                  {usageAnalysis?.total_annual_kwh?.toLocaleString()} kWh:
                </p>

                <div className="space-y-2">
                  {historicalCostComparison.atCurrentRate && (
                    <div className="flex justify-between items-center p-2 bg-arbor-light rounded">
                      <span className="text-sm">At your recommended rate</span>
                      <span className="font-semibold text-arbor-primary">
                        {formatCurrency(historicalCostComparison.atCurrentRate)}/yr
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-sm">At average market rate</span>
                    <span className="font-medium text-gray-700">
                      {formatCurrency(historicalCostComparison.atAvgRate)}/yr
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                    <span className="text-sm">At historic lowest</span>
                    <span className="font-medium text-green-700">
                      {formatCurrency(historicalCostComparison.atMinRate)}/yr
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                    <span className="text-sm">At peak rates</span>
                    <span className="font-medium text-red-600">
                      {formatCurrency(historicalCostComparison.atMaxRate)}/yr
                    </span>
                  </div>
                </div>

                {historicalCostComparison.atCurrentRate && (
                  <p className="text-sm text-gray-600 pt-2">
                    You&apos;re saving{" "}
                    <span className="font-semibold text-green-600">
                      {formatCurrency(
                        historicalCostComparison.atAvgRate -
                          historicalCostComparison.atCurrentRate
                      )}
                    </span>{" "}
                    compared to average market rates.
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Timing Tips */}
        <div className="text-xs text-gray-500 space-y-1 pt-2 border-t">
          <p>
            <Calendar className="w-3 h-3 inline mr-1" aria-hidden="true" />
            <strong>Best time to lock in rates:</strong> Spring (March-May) typically has lowest rates
          </p>
          <p>
            <DollarSign className="w-3 h-3 inline mr-1" aria-hidden="true" />
            <strong>Peak rate season:</strong> Summer (June-August) when demand is highest
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
