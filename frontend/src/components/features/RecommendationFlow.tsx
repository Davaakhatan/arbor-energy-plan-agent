"use client";

import { useState, useEffect } from "react";
import { HelpCircle } from "lucide-react";
import { UsageInputForm } from "./UsageInputForm";
import { PreferenceForm } from "./PreferenceForm";
import { RecommendationResults } from "./RecommendationResults";
import { OnboardingTutorial, useOnboardingStatus } from "./OnboardingTutorial";
import { Button } from "@/components/ui/Button";
import type { CustomerPreference, RecommendationSet } from "@/types";

type Step = "usage" | "preferences" | "results";

export function RecommendationFlow() {
  const [step, setStep] = useState<Step>("usage");
  const [customerId, setCustomerId] = useState<string | null>(null);
  const [_preferences, setPreferences] = useState<CustomerPreference | null>(
    null
  );
  const [recommendations, setRecommendations] =
    useState<RecommendationSet | null>(null);
  const [showTutorial, setShowTutorial] = useState(false);
  const { shouldShowOnboarding } = useOnboardingStatus();

  // Auto-show tutorial for first-time visitors
  useEffect(() => {
    if (shouldShowOnboarding) {
      // Slight delay to let the page render first
      const timer = setTimeout(() => setShowTutorial(true), 500);
      return () => clearTimeout(timer);
    }
  }, [shouldShowOnboarding]);

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

  const stepNumber = step === "usage" ? 1 : step === "preferences" ? 2 : 3;

  return (
    <section
      className="py-8 sm:py-12 px-4 sm:px-6 lg:px-8"
      id="get-started"
      aria-labelledby="flow-heading"
    >
      <h2 id="flow-heading" className="sr-only">
        Energy Plan Recommendation Process
      </h2>

      {/* Onboarding Tutorial Modal */}
      <OnboardingTutorial
        isOpen={showTutorial}
        onClose={() => setShowTutorial(false)}
      />

      <div className="mx-auto max-w-3xl">
        {/* Help button for tutorial */}
        <div className="flex justify-end mb-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowTutorial(true)}
            className="text-gray-600 hover:text-arbor-primary"
          >
            <HelpCircle className="w-4 h-4 mr-1" />
            How It Works
          </Button>
        </div>

        {/* Progress indicator - responsive */}
        <nav aria-label="Progress" className="mb-6 sm:mb-8">
          {/* Mobile: Simple text indicator */}
          <div className="sm:hidden text-center mb-4">
            <span className="text-sm font-medium text-arbor-primary">
              Step {stepNumber} of 3
            </span>
            <div className="mt-1 text-xs text-gray-500">
              {step === "usage" && "Enter Usage Data"}
              {step === "preferences" && "Set Preferences"}
              {step === "results" && "View Results"}
            </div>
          </div>

          {/* Mobile: Progress bar */}
          <div className="sm:hidden">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-arbor-primary transition-all duration-300"
                style={{ width: `${(stepNumber / 3) * 100}%` }}
                role="progressbar"
                aria-valuenow={stepNumber}
                aria-valuemin={1}
                aria-valuemax={3}
              />
            </div>
          </div>

          {/* Desktop: Step indicators */}
          <ol className="hidden sm:flex items-center justify-center space-x-4">
            <StepIndicator
              step={1}
              label="Usage Data"
              isActive={step === "usage"}
              isComplete={step !== "usage"}
            />
            <li className="h-px w-8 md:w-12 bg-gray-300" aria-hidden="true" />
            <StepIndicator
              step={2}
              label="Preferences"
              isActive={step === "preferences"}
              isComplete={step === "results"}
            />
            <li className="h-px w-8 md:w-12 bg-gray-300" aria-hidden="true" />
            <StepIndicator
              step={3}
              label="Results"
              isActive={step === "results"}
              isComplete={false}
            />
          </ol>
        </nav>

        {/* Step content with live region for screen readers */}
        <div aria-live="polite" aria-atomic="true">
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
    <li className="flex flex-col items-center">
      <div
        className={`
          flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium
          transition-colors duration-200
          ${
            isActive
              ? "bg-arbor-primary text-white"
              : isComplete
                ? "bg-arbor-accent text-white"
                : "bg-gray-200 text-gray-500"
          }
        `}
        aria-current={isActive ? "step" : undefined}
      >
        {isComplete ? (
          <span aria-hidden="true">✓</span>
        ) : (
          step
        )}
        <span className="sr-only">
          {isComplete ? `${label} completed` : isActive ? `${label} current` : label}
        </span>
      </div>
      <span
        className={`mt-2 text-xs hidden md:block ${
          isActive ? "text-arbor-primary font-medium" : "text-gray-500"
        }`}
        aria-hidden="true"
      >
        {label}
      </span>
    </li>
  );
}
