"use client";

import { Modal } from "@/components/ui/Modal";
import {
  formatCurrency,
  formatPercentage,
  getRateTypeLabel,
  getSeverityColor,
} from "@/lib/utils";
import {
  Leaf,
  Clock,
  Star,
  AlertTriangle,
  DollarSign,
  Calendar,
  Building2,
  TrendingDown,
} from "lucide-react";
import type { Recommendation } from "@/types";

interface PlanDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendation: Recommendation;
}

export function PlanDetailsModal({
  isOpen,
  onClose,
  recommendation,
}: PlanDetailsModalProps) {
  const { plan, explanation, risk_flags, confidence_level } = recommendation;
  const supplier = plan.supplier;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={plan.name} size="lg">
      <div className="space-y-6">
        {/* Supplier Info */}
        <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-arbor-primary/10">
            <Building2 className="w-6 h-6 text-arbor-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {supplier?.name || "Unknown Supplier"}
            </h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Star className="w-4 h-4 text-yellow-500" />
              <span>{supplier?.rating ? Number(supplier.rating).toFixed(1) : "N/A"} rating</span>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <MetricCard
            icon={<DollarSign className="w-5 h-5 text-green-600" />}
            label="Rate"
            value={`$${plan.rate_per_kwh}/kWh`}
          />
          <MetricCard
            icon={<Calendar className="w-5 h-5 text-blue-600" />}
            label="Monthly Fee"
            value={formatCurrency(plan.monthly_fee)}
          />
          <MetricCard
            icon={<Clock className="w-5 h-5 text-purple-600" />}
            label="Contract"
            value={`${plan.contract_length_months} months`}
          />
          <MetricCard
            icon={<Leaf className="w-5 h-5 text-green-600" />}
            label="Renewable"
            value={formatPercentage(plan.renewable_percentage)}
          />
        </div>

        {/* Savings Summary */}
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-5 h-5 text-green-600" />
            <h4 className="font-semibold text-green-800">Projected Savings</h4>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-green-700">Annual Savings</p>
              <p className="text-2xl font-bold text-green-800">
                {formatCurrency(recommendation.projected_annual_savings)}
              </p>
            </div>
            <div>
              <p className="text-sm text-green-700">First Year (Net)</p>
              <p className="text-2xl font-bold text-green-800">
                {formatCurrency(recommendation.net_first_year_savings)}
              </p>
            </div>
          </div>
        </div>

        {/* Plan Details */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-3">Plan Details</h4>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
            <DetailRow label="Plan Type" value={getRateTypeLabel(plan.rate_type)} />
            <DetailRow
              label="Early Termination Fee"
              value={plan.early_termination_fee ? formatCurrency(plan.early_termination_fee) : "None"}
            />
            <DetailRow
              label="Cancellation Fee"
              value={plan.cancellation_fee ? formatCurrency(plan.cancellation_fee) : "None"}
            />
            <DetailRow
              label="Status"
              value={plan.is_active ? "Active" : "Inactive"}
            />
          </dl>
        </div>

        {/* Why This Plan */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">Why This Plan?</h4>
          <p className="text-sm text-gray-600 bg-gray-50 p-4 rounded-lg">
            {explanation}
          </p>
        </div>

        {/* Score Breakdown */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-3">Score Breakdown</h4>
          <div className="space-y-2">
            <ScoreBar label="Cost Score" score={recommendation.cost_score} />
            <ScoreBar label="Flexibility Score" score={recommendation.flexibility_score} />
            <ScoreBar label="Renewable Score" score={recommendation.renewable_score} />
            <ScoreBar label="Rating Score" score={recommendation.rating_score} />
          </div>
        </div>

        {/* Risk Flags */}
        {risk_flags.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-600" />
              Things to Consider
            </h4>
            <div className="space-y-2">
              {risk_flags.map((flag, i) => (
                <div
                  key={i}
                  className={`text-sm px-4 py-3 rounded-lg border ${getSeverityColor(flag.severity)}`}
                >
                  <span className="font-medium">{flag.code}:</span>{" "}
                  {flag.message}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Confidence */}
        <div className="text-center pt-4 border-t">
          <span className="text-sm text-gray-500">
            Confidence Level:{" "}
            <span className="font-medium capitalize">{confidence_level}</span>
          </span>
        </div>
      </div>
    </Modal>
  );
}

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="p-3 bg-gray-50 rounded-lg text-center">
      <div className="flex justify-center mb-1">{icon}</div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="font-semibold text-gray-900">{value}</p>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-100">
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900">{value}</dd>
    </div>
  );
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const percentage = Math.round(score * 100);
  const color =
    percentage >= 70
      ? "bg-green-500"
      : percentage >= 40
        ? "bg-yellow-500"
        : "bg-red-500";

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600 w-32">{label}</span>
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-900 w-12 text-right">
        {percentage}%
      </span>
    </div>
  );
}
