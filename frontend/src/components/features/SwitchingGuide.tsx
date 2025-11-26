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
  CheckCircle,
  Circle,
  ArrowRight,
  FileText,
  Phone,
  Clock,
  AlertTriangle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import type { Recommendation } from "@/types";

interface SwitchingGuideProps {
  recommendation: Recommendation;
  contractEndDate?: string;
  earlyTerminationFee?: number;
}

interface Step {
  id: string;
  title: string;
  description: string;
  details: string[];
  tips?: string[];
  warning?: string;
  estimatedTime?: string;
}

const SWITCHING_STEPS: Step[] = [
  {
    id: "review",
    title: "Review Your Current Contract",
    description: "Check your existing contract for important dates and terms",
    details: [
      "Find your current contract end date",
      "Note any early termination fees",
      "Check for automatic renewal clauses",
      "Locate your account number and meter ID",
    ],
    tips: [
      "Most contracts auto-renew 30-60 days before expiration",
      "Some providers waive ETF if you switch within a grace period",
    ],
    estimatedTime: "15 minutes",
  },
  {
    id: "compare",
    title: "Compare the Plans",
    description: "Ensure the new plan meets your needs",
    details: [
      "Verify the rate per kWh and any monthly fees",
      "Confirm the contract length works for you",
      "Check renewable energy percentage",
      "Review customer service ratings",
    ],
    tips: [
      "Consider your seasonal usage patterns",
      "Factor in any signup bonuses or promotions",
    ],
    estimatedTime: "10 minutes",
  },
  {
    id: "signup",
    title: "Sign Up for New Plan",
    description: "Enroll with your chosen energy provider",
    details: [
      "Visit the provider's website or call them",
      "Have your meter ID/ESI ID ready",
      "Provide a valid ID and proof of residence",
      "Choose your start date (usually within 1-2 weeks)",
    ],
    tips: [
      "Ask about any current promotions",
      "Request confirmation in writing",
    ],
    warning: "Never cancel your old plan before enrolling in the new one",
    estimatedTime: "20-30 minutes",
  },
  {
    id: "confirm",
    title: "Confirm Enrollment",
    description: "Verify your switch is scheduled correctly",
    details: [
      "You should receive a confirmation email within 24 hours",
      "Check the start date matches your expected date",
      "Verify the rate and terms match what you agreed to",
      "Save all documentation for your records",
    ],
    tips: [
      "Mark your calendar for the switch date",
      "Set a reminder to check your first bill",
    ],
    estimatedTime: "5 minutes",
  },
  {
    id: "transition",
    title: "Transition Complete",
    description: "Your service will switch automatically",
    details: [
      "No action needed on switch day - it happens automatically",
      "Your power will NOT be interrupted",
      "Final bill from old provider will arrive within 2 weeks",
      "First bill from new provider will reflect the new rate",
    ],
    tips: [
      "Compare your first new bill against projected costs",
      "Contact provider if the rate doesn't match",
    ],
    estimatedTime: "No action needed",
  },
];

export function SwitchingGuide({
  recommendation,
  contractEndDate,
  earlyTerminationFee,
}: SwitchingGuideProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleStepComplete = (stepId: string) => {
    setCompletedSteps((prev) =>
      prev.includes(stepId)
        ? prev.filter((id) => id !== stepId)
        : [...prev, stepId]
    );
  };

  const isStepComplete = (stepId: string) => completedSteps.includes(stepId);

  const daysUntilContractEnd = contractEndDate
    ? Math.ceil(
        (new Date(contractEndDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
      )
    : null;

  const shouldWait =
    daysUntilContractEnd !== null &&
    daysUntilContractEnd > 0 &&
    daysUntilContractEnd <= 30 &&
    earlyTerminationFee &&
    earlyTerminationFee > 50;

  return (
    <Card>
      <CardHeader>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between"
        >
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
            Switching Guide for {recommendation.plan.name}
          </CardTitle>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" aria-hidden="true" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" aria-hidden="true" />
          )}
        </button>
      </CardHeader>

      {isExpanded && (
        <CardContent>
          {/* Contract Warning */}
          {daysUntilContractEnd !== null && (
            <div
              className={`mb-6 p-4 rounded-lg ${
                shouldWait
                  ? "bg-yellow-50 border border-yellow-200"
                  : "bg-green-50 border border-green-200"
              }`}
            >
              <div className="flex items-start gap-3">
                {shouldWait ? (
                  <Clock className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
                ) : (
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
                )}
                <div>
                  <p className={`font-medium ${shouldWait ? "text-yellow-800" : "text-green-800"}`}>
                    {daysUntilContractEnd > 0
                      ? `${daysUntilContractEnd} days until your contract ends`
                      : "Your contract has ended - no termination fee!"}
                  </p>
                  {shouldWait && earlyTerminationFee && (
                    <p className="text-sm text-yellow-700 mt-1">
                      Consider waiting {daysUntilContractEnd} days to avoid the{" "}
                      {formatCurrency(earlyTerminationFee)} early termination fee.
                    </p>
                  )}
                  {!shouldWait && daysUntilContractEnd > 0 && earlyTerminationFee && (
                    <p className="text-sm text-green-700 mt-1">
                      Early termination fee: {formatCurrency(earlyTerminationFee)}.
                      Your projected savings outweigh this cost.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Provider Info */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">
              Contact {recommendation.plan.supplier?.name}
            </h4>
            <div className="flex flex-wrap gap-4 text-sm">
              {recommendation.plan.supplier?.website && (
                <a
                  href={recommendation.plan.supplier.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-arbor-primary hover:underline"
                >
                  <ExternalLink className="w-4 h-4" aria-hidden="true" />
                  Visit Website
                </a>
              )}
              <span className="flex items-center gap-1 text-gray-600">
                <Phone className="w-4 h-4" aria-hidden="true" />
                Check website for phone
              </span>
            </div>
          </div>

          {/* Progress */}
          <div className="mb-6">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-600">Progress</span>
              <span className="font-medium">
                {completedSteps.length} of {SWITCHING_STEPS.length} steps completed
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-arbor-primary transition-all duration-300"
                style={{
                  width: `${(completedSteps.length / SWITCHING_STEPS.length) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Steps */}
          <div className="space-y-4">
            {SWITCHING_STEPS.map((step, index) => {
              const isActive = index === currentStep;
              const isComplete = isStepComplete(step.id);

              return (
                <div
                  key={step.id}
                  className={`border rounded-lg overflow-hidden transition-colors ${
                    isActive
                      ? "border-arbor-primary bg-arbor-light"
                      : isComplete
                        ? "border-green-200 bg-green-50"
                        : "border-gray-200"
                  }`}
                >
                  <button
                    onClick={() => setCurrentStep(index)}
                    className="w-full p-4 flex items-start gap-3 text-left"
                  >
                    <div
                      className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        isComplete
                          ? "bg-green-500 text-white"
                          : isActive
                            ? "bg-arbor-primary text-white"
                            : "bg-gray-200 text-gray-500"
                      }`}
                    >
                      {isComplete ? (
                        <CheckCircle className="w-5 h-5" aria-hidden="true" />
                      ) : (
                        <span className="text-sm font-medium">{index + 1}</span>
                      )}
                    </div>
                    <div className="flex-1">
                      <h4
                        className={`font-medium ${
                          isActive ? "text-arbor-primary" : "text-gray-900"
                        }`}
                      >
                        {step.title}
                      </h4>
                      <p className="text-sm text-gray-500">{step.description}</p>
                    </div>
                    {step.estimatedTime && (
                      <span className="text-xs text-gray-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" aria-hidden="true" />
                        {step.estimatedTime}
                      </span>
                    )}
                  </button>

                  {isActive && (
                    <div className="px-4 pb-4 pt-0">
                      <div className="ml-11">
                        <ul className="space-y-2 mb-4">
                          {step.details.map((detail, i) => (
                            <li
                              key={i}
                              className="text-sm text-gray-700 flex items-start gap-2"
                            >
                              <Circle className="w-2 h-2 mt-1.5 text-gray-400 flex-shrink-0" aria-hidden="true" />
                              {detail}
                            </li>
                          ))}
                        </ul>

                        {step.tips && (
                          <div className="bg-blue-50 rounded-lg p-3 mb-4">
                            <p className="text-xs font-medium text-blue-800 mb-1">
                              Tips
                            </p>
                            {step.tips.map((tip, i) => (
                              <p key={i} className="text-sm text-blue-700">
                                {tip}
                              </p>
                            ))}
                          </div>
                        )}

                        {step.warning && (
                          <div className="bg-red-50 rounded-lg p-3 mb-4 flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
                            <p className="text-sm text-red-700">{step.warning}</p>
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <Button
                            variant={isComplete ? "outline" : "primary"}
                            size="sm"
                            onClick={() => toggleStepComplete(step.id)}
                          >
                            {isComplete ? (
                              "Mark Incomplete"
                            ) : (
                              <>
                                <CheckCircle className="w-4 h-4 mr-1" aria-hidden="true" />
                                Mark Complete
                              </>
                            )}
                          </Button>
                          {index < SWITCHING_STEPS.length - 1 && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setCurrentStep(index + 1)}
                            >
                              Next Step
                              <ArrowRight className="w-4 h-4 ml-1" aria-hidden="true" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Completion */}
          {completedSteps.length === SWITCHING_STEPS.length && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg text-center">
              <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" aria-hidden="true" />
              <p className="font-medium text-green-800">
                All steps completed! Your switch is on track.
              </p>
              <p className="text-sm text-green-700 mt-1">
                Remember to check your first bill from the new provider.
              </p>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
