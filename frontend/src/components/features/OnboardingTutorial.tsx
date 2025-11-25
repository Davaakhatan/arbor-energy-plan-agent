"use client";

import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import {
  FileText,
  Sliders,
  Award,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Upload,
  BarChart3,
  Leaf,
  DollarSign,
  Clock,
  ThumbsUp,
  HelpCircle,
} from "lucide-react";

interface OnboardingTutorialProps {
  isOpen: boolean;
  onClose: () => void;
}

const tutorialSteps = [
  {
    title: "Welcome to Arbor Energy!",
    icon: HelpCircle,
    content: (
      <div className="space-y-4">
        <p className="text-gray-600">
          We help you find the <strong>perfect energy plan</strong> for your
          needs using AI-powered recommendations.
        </p>
        <div className="bg-arbor-primary/5 rounded-lg p-4">
          <h4 className="font-semibold text-arbor-primary mb-2">
            Here&apos;s what you&apos;ll do:
          </h4>
          <ol className="space-y-2 text-sm text-gray-600">
            <li className="flex items-center gap-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-arbor-primary text-white text-xs">
                1
              </span>
              Enter your energy usage data
            </li>
            <li className="flex items-center gap-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-arbor-primary text-white text-xs">
                2
              </span>
              Set your preferences (cost, green energy, flexibility)
            </li>
            <li className="flex items-center gap-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-arbor-primary text-white text-xs">
                3
              </span>
              Get personalized plan recommendations
            </li>
          </ol>
        </div>
      </div>
    ),
  },
  {
    title: "Step 1: Enter Usage Data",
    icon: FileText,
    content: (
      <div className="space-y-4">
        <p className="text-gray-600">
          You have <strong>two options</strong> to provide your energy usage:
        </p>
        <div className="grid gap-4">
          <div className="border rounded-lg p-4 bg-blue-50 border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h4 className="font-semibold text-blue-800">Use Sample Data</h4>
            </div>
            <p className="text-sm text-blue-700">
              Click &quot;Use Sample Data&quot; to see how the app works with example
              usage patterns. Perfect for trying out the app!
            </p>
          </div>
          <div className="border rounded-lg p-4 bg-green-50 border-green-200">
            <div className="flex items-center gap-2 mb-2">
              <Upload className="w-5 h-5 text-green-600" />
              <h4 className="font-semibold text-green-800">
                Upload Your CSV File
              </h4>
            </div>
            <p className="text-sm text-green-700">
              Upload a CSV file with your actual monthly usage. Your file should
              have columns for <code className="bg-green-100 px-1 rounded">date</code> and{" "}
              <code className="bg-green-100 px-1 rounded">kwh</code> (or similar names).
            </p>
          </div>
        </div>
      </div>
    ),
  },
  {
    title: "Step 2: Set Your Preferences",
    icon: Sliders,
    content: (
      <div className="space-y-4">
        <p className="text-gray-600">
          Use the sliders to tell us what matters most to you:
        </p>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <DollarSign className="w-5 h-5 text-green-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Cost Priority</h4>
              <p className="text-sm text-gray-600">
                How much do you want to prioritize saving money? Higher = focus
                on lowest cost plans.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Leaf className="w-5 h-5 text-green-500 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Renewable Priority</h4>
              <p className="text-sm text-gray-600">
                Want green energy? Higher = prefer plans with more renewable
                energy sources.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Clock className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900">Flexibility Priority</h4>
              <p className="text-sm text-gray-600">
                Prefer shorter contracts? Higher = favor plans with no long-term
                commitment.
              </p>
            </div>
          </div>
        </div>
      </div>
    ),
  },
  {
    title: "Step 3: Get Recommendations",
    icon: Award,
    content: (
      <div className="space-y-4">
        <p className="text-gray-600">
          Our AI analyzes your data and returns the <strong>top 3 plans</strong>{" "}
          that best match your needs:
        </p>
        <div className="space-y-3">
          <div className="border rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">
              Each recommendation shows:
            </h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Plan name, rate, and supplier info
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Projected annual savings
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Score breakdown (cost, flexibility, renewable, rating)
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Risk flags and warnings to consider
              </li>
            </ul>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p className="text-sm text-yellow-800">
              <strong>Tip:</strong> Click &quot;View Details&quot; on any plan to see the
              full breakdown, then &quot;Select This Plan&quot; when you find the right
              one!
            </p>
          </div>
        </div>
      </div>
    ),
  },
  {
    title: "After Selection",
    icon: ThumbsUp,
    content: (
      <div className="space-y-4">
        <p className="text-gray-600">
          Once you select a plan, here&apos;s what happens:
        </p>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-green-800">
                Your choice is recorded
              </h4>
              <p className="text-sm text-green-700">
                We track which plans you&apos;re interested in to improve our
                recommendations.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <ArrowRight className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-800">Next steps</h4>
              <p className="text-sm text-blue-700">
                Contact the supplier directly to sign up for your chosen plan.
                We provide all the details you need!
              </p>
            </div>
          </div>
        </div>
        <div className="mt-4 p-4 bg-arbor-primary/5 rounded-lg">
          <p className="text-center text-arbor-primary font-medium">
            Ready to find your perfect energy plan?
          </p>
        </div>
      </div>
    ),
  },
];

export function OnboardingTutorial({ isOpen, onClose }: OnboardingTutorialProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [dontShowAgain, setDontShowAgain] = useState(false);

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === tutorialSteps.length - 1;
  const step = tutorialSteps[currentStep];
  const StepIcon = step.icon;

  const handleNext = () => {
    if (isLastStep) {
      handleClose();
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    setCurrentStep((prev) => Math.max(0, prev - 1));
  };

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem("arbor-onboarding-completed", "true");
    }
    setCurrentStep(0);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title=""
      size="lg"
    >
      <div className="space-y-6">
        {/* Step header */}
        <div className="text-center">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-arbor-primary/10 mb-4">
            <StepIcon className="h-7 w-7 text-arbor-primary" />
          </div>
          <h3 className="text-xl font-bold text-gray-900">{step.title}</h3>
        </div>

        {/* Progress dots */}
        <div className="flex justify-center gap-2">
          {tutorialSteps.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentStep(index)}
              className={`h-2 rounded-full transition-all ${
                index === currentStep
                  ? "w-6 bg-arbor-primary"
                  : "w-2 bg-gray-300 hover:bg-gray-400"
              }`}
              aria-label={`Go to step ${index + 1}`}
            />
          ))}
        </div>

        {/* Step content */}
        <div className="min-h-[280px]">{step.content}</div>

        {/* Don't show again checkbox */}
        {isLastStep && (
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={dontShowAgain}
              onChange={(e) => setDontShowAgain(e.target.checked)}
              className="rounded border-gray-300 text-arbor-primary focus:ring-arbor-primary"
            />
            Don&apos;t show this tutorial again
          </label>
        )}

        {/* Navigation buttons */}
        <div className="flex justify-between pt-4 border-t">
          <Button
            variant="outline"
            onClick={handlePrev}
            disabled={isFirstStep}
            className={isFirstStep ? "invisible" : ""}
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back
          </Button>
          <Button onClick={handleNext}>
            {isLastStep ? (
              <>
                Get Started
                <CheckCircle className="w-4 h-4 ml-1" />
              </>
            ) : (
              <>
                Next
                <ArrowRight className="w-4 h-4 ml-1" />
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

// Hook to check if user should see onboarding
export function useOnboardingStatus() {
  const [shouldShowOnboarding, setShouldShowOnboarding] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem("arbor-onboarding-completed");
    setShouldShowOnboarding(!completed);
  }, []);

  const resetOnboarding = () => {
    localStorage.removeItem("arbor-onboarding-completed");
    setShouldShowOnboarding(true);
  };

  return { shouldShowOnboarding, resetOnboarding };
}
