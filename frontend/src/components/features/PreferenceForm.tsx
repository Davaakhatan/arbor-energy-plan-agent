"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ArrowLeft } from "lucide-react";
import { recommendationsApi } from "@/lib/api";
import type { CustomerPreference, RecommendationSet } from "@/types";

interface PreferenceFormProps {
  customerId: string;
  onSubmit: (preferences: CustomerPreference, recommendations: RecommendationSet) => void;
  onBack: () => void;
}

export function PreferenceForm({ customerId, onSubmit, onBack }: PreferenceFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Preference state (weights should sum to 1.0)
  const [preferences, setPreferences] = useState<CustomerPreference>({
    cost_savings_weight: 0.4,
    flexibility_weight: 0.2,
    renewable_weight: 0.2,
    supplier_rating_weight: 0.2,
    min_renewable_percentage: 0,
    max_contract_months: undefined,
    avoid_variable_rates: false,
  });

  const updateWeight = (key: keyof CustomerPreference, value: number) => {
    // Adjust other weights proportionally to keep sum at 1.0
    const weightKeys = [
      "cost_savings_weight",
      "flexibility_weight",
      "renewable_weight",
      "supplier_rating_weight",
    ] as const;

    const otherKeys = weightKeys.filter((k) => k !== key);
    const oldValue = preferences[key] as number;
    const diff = value - oldValue;
    const otherSum = otherKeys.reduce(
      (sum, k) => sum + (preferences[k] as number),
      0
    );

    const newPrefs = { ...preferences, [key]: value };

    // Distribute the difference among other weights
    if (otherSum > 0) {
      otherKeys.forEach((k) => {
        const proportion = (preferences[k] as number) / otherSum;
        const newVal = Math.max(0, (preferences[k] as number) - diff * proportion);
        (newPrefs[k] as number) = Math.round(newVal * 100) / 100;
      });
    }

    setPreferences(newPrefs);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const recommendations = await recommendationsApi.generate(
        customerId,
        preferences
      );
      onSubmit(preferences, recommendations);
    } catch (err) {
      setError("Failed to generate recommendations. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={onBack}>
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <CardTitle>Set Your Preferences</CardTitle>
            <p className="text-sm text-gray-600 mt-1">
              Adjust the sliders to reflect what matters most to you.
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Weight sliders */}
          <div className="space-y-4">
            <PreferenceSlider
              label="Cost Savings"
              description="Prioritize lower monthly bills"
              value={preferences.cost_savings_weight}
              onChange={(v) => updateWeight("cost_savings_weight", v)}
            />
            <PreferenceSlider
              label="Flexibility"
              description="Prefer shorter contracts"
              value={preferences.flexibility_weight}
              onChange={(v) => updateWeight("flexibility_weight", v)}
            />
            <PreferenceSlider
              label="Renewable Energy"
              description="Higher green energy percentage"
              value={preferences.renewable_weight}
              onChange={(v) => updateWeight("renewable_weight", v)}
            />
            <PreferenceSlider
              label="Supplier Rating"
              description="Better customer reviews"
              value={preferences.supplier_rating_weight}
              onChange={(v) => updateWeight("supplier_rating_weight", v)}
            />
          </div>

          {/* Additional constraints */}
          <div className="border-t pt-4 space-y-4">
            <h4 className="text-sm font-medium text-gray-700">
              Additional Constraints
            </h4>

            <div>
              <label className="flex items-center justify-between text-sm">
                <span>Minimum Renewable %</span>
                <span className="font-medium">
                  {preferences.min_renewable_percentage}%
                </span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                step="10"
                value={preferences.min_renewable_percentage}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    min_renewable_percentage: Number(e.target.value),
                  })
                }
                className="w-full mt-2"
              />
            </div>

            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={preferences.avoid_variable_rates}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    avoid_variable_rates: e.target.checked,
                  })
                }
                className="rounded border-gray-300"
              />
              <span>Avoid variable rate plans</span>
            </label>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {error}
            </div>
          )}

          <Button
            onClick={handleSubmit}
            isLoading={isLoading}
            className="w-full"
            size="lg"
          >
            Get My Recommendations
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function PreferenceSlider({
  label,
  description,
  value,
  onChange,
}: {
  label: string;
  description: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1">
        <div>
          <span className="font-medium">{label}</span>
          <span className="text-gray-500 ml-2">{description}</span>
        </div>
        <span className="font-medium text-arbor-primary">
          {Math.round(value * 100)}%
        </span>
      </div>
      <input
        type="range"
        min="0"
        max="0.8"
        step="0.05"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
      />
    </div>
  );
}
