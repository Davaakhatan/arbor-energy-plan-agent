"use client";

import { useState } from "react";
import { UsageInputForm } from "./UsageInputForm";
import { PreferenceForm } from "./PreferenceForm";
import { RecommendationResults } from "./RecommendationResults";
import type { CustomerPreference, RecommendationSet } from "@/types";

type Step = "usage" | "preferences" | "results";

export function RecommendationFlow() {
  const [step, setStep] = useState<Step>("usage");
  const [customerId, setCustomerId] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<CustomerPreference | null>(
    null
  );
  const [recommendations, setRecommendations] =
    useState<RecommendationSet | null>(null);

  const handleUsageSubmit = (id: string) => {
    setCustomerId(id);
    setStep("preferences");
  };

  const handlePreferencesSubmit = (
    prefs: CustomerPreference,
    recs: RecommendationSet
  ) => {
    setPreferences(prefs);
    setRecommendations(recs);
    setStep("results");
  };

  const handleStartOver = () => {
    setStep("usage");
    setCustomerId(null);
    setPreferences(null);
    setRecommendations(null);
  };

  return (
    <section className="py-12 px-4 sm:px-6 lg:px-8" id="get-started">
      <div className="mx-auto max-w-3xl">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            <StepIndicator
              step={1}
              label="Usage Data"
              isActive={step === "usage"}
              isComplete={step !== "usage"}
            />
            <div className="h-px w-12 bg-gray-300" />
            <StepIndicator
              step={2}
              label="Preferences"
              isActive={step === "preferences"}
              isComplete={step === "results"}
            />
            <div className="h-px w-12 bg-gray-300" />
            <StepIndicator
              step={3}
              label="Results"
              isActive={step === "results"}
              isComplete={false}
            />
          </div>
        </div>

        {/* Step content */}
        {step === "usage" && <UsageInputForm onSubmit={handleUsageSubmit} />}

        {step === "preferences" && customerId && (
          <PreferenceForm
            customerId={customerId}
            onSubmit={handlePreferencesSubmit}
            onBack={() => setStep("usage")}
          />
        )}

        {step === "results" && recommendations && (
          <RecommendationResults
            recommendations={recommendations}
            onStartOver={handleStartOver}
          />
        )}
      </div>
    </section>
  );
}

function StepIndicator({
  step,
  label,
  isActive,
  isComplete,
}: {
  step: number;
  label: string;
  isActive: boolean;
  isComplete: boolean;
}) {
  return (
    <div className="flex flex-col items-center">
      <div
        className={`
          flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium
          ${
            isActive
              ? "bg-arbor-primary text-white"
              : isComplete
                ? "bg-arbor-accent text-white"
                : "bg-gray-200 text-gray-500"
          }
        `}
      >
        {isComplete ? "✓" : step}
      </div>
      <span
        className={`mt-2 text-xs ${isActive ? "text-arbor-primary font-medium" : "text-gray-500"}`}
      >
        {label}
      </span>
    </div>
  );
}
