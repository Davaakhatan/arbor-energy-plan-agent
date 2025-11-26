"use client";

import { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { formatCurrency } from "@/lib/utils";
import {
  Calculator,
  Zap,
  TrendingUp,
  TrendingDown,
  Minus,
  Info,
} from "lucide-react";
import type { Recommendation } from "@/types";

interface SavingsCalculatorProps {
  recommendations: Recommendation[];
  initialMonthlyUsage?: number;
}

export function SavingsCalculator({
  recommendations,
  initialMonthlyUsage = 1000,
}: SavingsCalculatorProps) {
  const [monthlyUsage, setMonthlyUsage] = useState(initialMonthlyUsage);
  const [usageChange, setUsageChange] = useState(0);
  const [selectedPlanId, setSelectedPlanId] = useState<string>(
    recommendations[0]?.id || ""
  );

  const adjustedUsage = useMemo(() => {
    return monthlyUsage * (1 + usageChange / 100);
  }, [monthlyUsage, usageChange]);

  const calculations = useMemo(() => {
    const selectedPlan = recommendations.find((r) => r.id === selectedPlanId);
    if (!selectedPlan) return null;

    const annualUsage = adjustedUsage * 12;
    const rate = Number(selectedPlan.plan.rate_per_kwh);
    const monthlyFee = Number(selectedPlan.plan.monthly_fee);

    const annualEnergyCost = annualUsage * rate;
    const annualFees = monthlyFee * 12;
    const totalAnnualCost = annualEnergyCost + annualFees;

    const originalAnnualCost = Number(selectedPlan.projected_annual_cost);
    const originalSavings = Number(selectedPlan.projected_annual_savings);

    const newSavings = originalSavings + (originalAnnualCost - totalAnnualCost);

    const savingsPerMonth = newSavings / 12;
    const savingsPercentage = originalAnnualCost > 0
      ? ((originalAnnualCost - totalAnnualCost) / originalAnnualCost) * 100
      : 0;

    const breakEvenMonths = selectedPlan.switching_cost > 0 && savingsPerMonth > 0
      ? Math.ceil(Number(selectedPlan.switching_cost) / savingsPerMonth)
      : null;

    return {
      annualUsage,
      annualEnergyCost,
      annualFees,
      totalAnnualCost,
      originalAnnualCost,
      newSavings,
      savingsPerMonth,
      savingsPercentage,
      breakEvenMonths,
      plan: selectedPlan,
    };
  }, [recommendations, selectedPlanId, adjustedUsage]);

  const usagePresets = [
    { label: "Low (500 kWh)", value: 500 },
    { label: "Average (1000 kWh)", value: 1000 },
    { label: "High (1500 kWh)", value: 1500 },
    { label: "Very High (2000 kWh)", value: 2000 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
          Savings Calculator
        </CardTitle>
        <p className="text-sm text-gray-500 mt-1">
          Adjust your usage to see how it affects your savings
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Controls */}
          <div className="space-y-6">
            {/* Plan Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Plan
              </label>
              <select
                value={selectedPlanId}
                onChange={(e) => setSelectedPlanId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-arbor-primary focus:border-arbor-primary"
              >
                {recommendations.map((rec) => (
                  <option key={rec.id} value={rec.id}>
                    {rec.plan.name} - ${Number(rec.plan.rate_per_kwh).toFixed(4)}/kWh
                  </option>
                ))}
              </select>
            </div>

            {/* Monthly Usage */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Monthly Usage: {Math.round(monthlyUsage)} kWh
              </label>
              <input
                type="range"
                min={200}
                max={3000}
                step={50}
                value={monthlyUsage}
                onChange={(e) => setMonthlyUsage(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-arbor-primary"
              />
              <div className="flex justify-between mt-2">
                {usagePresets.map((preset) => (
                  <button
                    key={preset.value}
                    onClick={() => setMonthlyUsage(preset.value)}
                    className={`text-xs px-2 py-1 rounded ${
                      monthlyUsage === preset.value
                        ? "bg-arbor-primary text-white"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Usage Change Scenario */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What if usage changes: {usageChange > 0 ? "+" : ""}{usageChange}%
              </label>
              <input
                type="range"
                min={-50}
                max={50}
                step={5}
                value={usageChange}
                onChange={(e) => setUsageChange(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-arbor-primary"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>-50% (reduce usage)</span>
                <button
                  onClick={() => setUsageChange(0)}
                  className="text-arbor-primary hover:underline"
                >
                  Reset
                </button>
                <span>+50% (more usage)</span>
              </div>
            </div>

            {/* Effective Usage Display */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-gray-500" aria-hidden="true" />
                <span className="text-sm font-medium text-gray-700">
                  Effective Monthly Usage
                </span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-gray-900">
                  {Math.round(adjustedUsage).toLocaleString()}
                </span>
                <span className="text-gray-500">kWh/month</span>
                {usageChange !== 0 && (
                  <span
                    className={`text-sm flex items-center gap-1 ${
                      usageChange > 0 ? "text-red-600" : "text-green-600"
                    }`}
                  >
                    {usageChange > 0 ? (
                      <TrendingUp className="w-3 h-3" aria-hidden="true" />
                    ) : (
                      <TrendingDown className="w-3 h-3" aria-hidden="true" />
                    )}
                    {Math.abs(usageChange)}%
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {Math.round(adjustedUsage * 12).toLocaleString()} kWh annually
              </div>
            </div>
          </div>

          {/* Results */}
          {calculations && (
            <div className="space-y-4">
              {/* Cost Breakdown */}
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">
                  Cost Breakdown for {calculations.plan.plan.name}
                </h4>
                <dl className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <dt className="text-gray-600">Energy Cost</dt>
                    <dd className="font-medium">
                      {formatCurrency(calculations.annualEnergyCost)}/yr
                    </dd>
                  </div>
                  <div className="flex justify-between text-sm">
                    <dt className="text-gray-600">Monthly Fees</dt>
                    <dd className="font-medium">
                      {formatCurrency(calculations.annualFees)}/yr
                    </dd>
                  </div>
                  <div className="flex justify-between text-sm pt-2 border-t">
                    <dt className="text-gray-900 font-medium">Total Annual Cost</dt>
                    <dd className="font-bold text-gray-900">
                      {formatCurrency(calculations.totalAnnualCost)}
                    </dd>
                  </div>
                </dl>
              </div>

              {/* Savings Summary */}
              <div
                className={`rounded-lg p-4 ${
                  calculations.newSavings > 0
                    ? "bg-green-50 border border-green-200"
                    : calculations.newSavings < 0
                      ? "bg-red-50 border border-red-200"
                      : "bg-gray-50 border border-gray-200"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {calculations.newSavings > 0 ? (
                    <TrendingUp className="w-5 h-5 text-green-600" aria-hidden="true" />
                  ) : calculations.newSavings < 0 ? (
                    <TrendingDown className="w-5 h-5 text-red-600" aria-hidden="true" />
                  ) : (
                    <Minus className="w-5 h-5 text-gray-500" aria-hidden="true" />
                  )}
                  <span
                    className={`font-medium ${
                      calculations.newSavings > 0
                        ? "text-green-800"
                        : calculations.newSavings < 0
                          ? "text-red-800"
                          : "text-gray-700"
                    }`}
                  >
                    {calculations.newSavings > 0
                      ? "Estimated Savings"
                      : calculations.newSavings < 0
                        ? "Additional Cost"
                        : "No Change"}
                  </span>
                </div>
                <div
                  className={`text-3xl font-bold ${
                    calculations.newSavings > 0
                      ? "text-green-700"
                      : calculations.newSavings < 0
                        ? "text-red-700"
                        : "text-gray-700"
                  }`}
                >
                  {calculations.newSavings > 0 ? "+" : ""}
                  {formatCurrency(Math.abs(calculations.newSavings))}
                  <span className="text-lg font-normal">/year</span>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {calculations.newSavings > 0 ? "+" : ""}
                  {formatCurrency(calculations.savingsPerMonth)}/month
                </div>
              </div>

              {/* Additional Info */}
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" aria-hidden="true" />
                  <div className="text-sm text-blue-800">
                    {calculations.breakEvenMonths && (
                      <p className="mb-2">
                        With switching costs of{" "}
                        {formatCurrency(Number(calculations.plan.switching_cost))}, you&apos;ll
                        break even in{" "}
                        <strong>{calculations.breakEvenMonths} months</strong>.
                      </p>
                    )}
                    <p>
                      Rate: ${Number(calculations.plan.plan.rate_per_kwh).toFixed(4)}/kWh
                      {" + "}
                      {formatCurrency(Number(calculations.plan.plan.monthly_fee))}/month fee
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
