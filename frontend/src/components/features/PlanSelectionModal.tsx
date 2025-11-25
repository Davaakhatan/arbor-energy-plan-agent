"use client";

import { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { feedbackApi } from "@/lib/api";
import {
  formatCurrency,
  formatPercentage,
  getRateTypeLabel,
} from "@/lib/utils";
import {
  CheckCircle,
  Loader2,
  AlertCircle,
  DollarSign,
  Calendar,
  Leaf,
  ExternalLink,
} from "lucide-react";
import type { Recommendation } from "@/types";

interface PlanSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendation: Recommendation;
  customerId: string;
  onPlanSelected?: () => void;
}

export function PlanSelectionModal({
  isOpen,
  onClose,
  recommendation,
  customerId,
  onPlanSelected,
}: PlanSelectionModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { plan } = recommendation;

  const handleConfirmSelection = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await feedbackApi.submit({
        customer_id: customerId,
        plan_id: plan.id,
        feedback_type: "plan_selected",
        switched_to_plan: true,
        metadata: {
          recommendation_id: recommendation.id,
          plan_name: plan.name,
          supplier_name: plan.supplier?.name,
          projected_annual_savings: recommendation.projected_annual_savings,
          selected_at: new Date().toISOString(),
        },
      });

      setIsSuccess(true);
      onPlanSelected?.();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to record plan selection"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setIsSuccess(false);
      setError(null);
      onClose();
    }
  };

  if (isSuccess) {
    return (
      <Modal isOpen={isOpen} onClose={handleClose} title="Plan Selected!" size="md">
        <div className="text-center py-6">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Great Choice!
          </h3>
          <p className="text-gray-600 mb-4">
            You&apos;ve selected <span className="font-medium">{plan.name}</span> from{" "}
            <span className="font-medium">{plan.supplier?.name}</span>.
          </p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-green-800 text-sm">
              Your projected annual savings:{" "}
              <span className="font-bold text-lg">
                {formatCurrency(recommendation.projected_annual_savings)}
              </span>
            </p>
          </div>
          <div className="space-y-3">
            <p className="text-sm text-gray-500">
              Next steps: Contact {plan.supplier?.name} to finalize your switch.
            </p>
            {plan.supplier?.website && (
              <Button
                variant="primary"
                className="w-full"
                onClick={() => window.open(plan.supplier?.website, "_blank")}
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Visit {plan.supplier?.name} Website
              </Button>
            )}
            <Button variant="outline" className="w-full" onClick={handleClose}>
              Close
            </Button>
          </div>
        </div>
      </Modal>
    );
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Confirm Plan Selection"
      size="md"
    >
      <div className="space-y-6">
        {/* Plan summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-1">{plan.name}</h3>
          <p className="text-sm text-gray-600 mb-3">
            {plan.supplier?.name} • {getRateTypeLabel(plan.rate_type)}
          </p>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-gray-500">Rate</p>
                <p className="font-medium">${plan.rate_per_kwh}/kWh</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-gray-500">Contract</p>
                <p className="font-medium">{plan.contract_length_months} mo</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Leaf className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-gray-500">Renewable</p>
                <p className="font-medium">
                  {formatPercentage(plan.renewable_percentage)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Savings highlight */}
        <div className="bg-arbor-primary/5 border border-arbor-primary/20 rounded-lg p-4 text-center">
          <p className="text-sm text-arbor-primary mb-1">
            Projected Annual Savings
          </p>
          <p className="text-3xl font-bold text-arbor-primary">
            {formatCurrency(recommendation.projected_annual_savings)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            First year net savings:{" "}
            {formatCurrency(recommendation.net_first_year_savings)}
          </p>
        </div>

        {/* Important notes */}
        <div className="text-sm text-gray-600">
          <p className="font-medium text-gray-900 mb-2">Important Notes:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              This selection records your intent to switch to this plan
            </li>
            <li>
              You&apos;ll need to contact {plan.supplier?.name} directly to complete
              the switch
            </li>
            {plan.early_termination_fee > 0 && (
              <li>
                Early termination fee:{" "}
                {formatCurrency(plan.early_termination_fee)}
              </li>
            )}
          </ul>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            className="flex-1"
            onClick={handleConfirmSelection}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Confirming...
              </>
            ) : (
              "Confirm Selection"
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
