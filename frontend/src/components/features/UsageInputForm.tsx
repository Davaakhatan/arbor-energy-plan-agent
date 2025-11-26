"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Upload, FileText, CheckCircle, AlertCircle, Calculator, ChevronDown, ChevronUp } from "lucide-react";
import { customerApi, ingestionApi, plansApi } from "@/lib/api";
import { SmartDefaults } from "./SmartDefaults";
import type { CustomerUsage, EnergyPlan } from "@/types";

interface UsageInputFormProps {
  onSubmit: (customerId: string) => void;
}

export function UsageInputForm({ onSubmit }: UsageInputFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string } | null>(null);
  const [usageData, setUsageData] = useState<CustomerUsage[]>([]);
  const [externalId, setExternalId] = useState("");
  const [uploadedCustomerId, setUploadedCustomerId] = useState<string | null>(null);
  const [showSmartDefaults, setShowSmartDefaults] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Current plan state
  const [showCurrentPlan, setShowCurrentPlan] = useState(false);
  const [availablePlans, setAvailablePlans] = useState<EnergyPlan[]>([]);
  const [currentPlanId, setCurrentPlanId] = useState<string>("");
  const [contractEndDate, setContractEndDate] = useState<string>("");
  const [earlyTerminationFee, setEarlyTerminationFee] = useState<string>("");

  // Fetch available plans when component mounts
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const plans = await plansApi.list({ active_only: true });
        setAvailablePlans(plans);
      } catch (err) {
        console.error("Failed to fetch plans:", err);
      }
    };
    fetchPlans();
  }, []);

  // Handle smart defaults generated data
  const handleSmartDefaultsGenerate = (data: CustomerUsage[]) => {
    setUsageData(data);
    setExternalId(`estimate-${Date.now()}`);
    setUploadedCustomerId(null);
    setUploadResult({ success: true, message: "Usage estimated based on your home profile" });
    setShowSmartDefaults(false);
  };

  // Generate sample 12-month usage data
  const generateSampleData = () => {
    const data: CustomerUsage[] = [];
    const baseUsage = 900;
    const now = new Date();

    for (let i = 11; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      // Simulate seasonal variation
      const month = date.getMonth();
      const seasonalFactor =
        month >= 5 && month <= 8
          ? 1.3 // Summer peak
          : month >= 11 || month <= 1
            ? 1.2 // Winter peak
            : 1.0;

      const randomVariation = 0.9 + Math.random() * 0.2;
      const kwh = Math.round(baseUsage * seasonalFactor * randomVariation);

      data.push({
        usage_date: date.toISOString().split("T")[0],
        kwh_usage: kwh,
      });
    }

    setUsageData(data);
    setExternalId(`demo-${Date.now()}`);
    setUploadedCustomerId(null);
    setUploadResult(null);
  };

  // Handle CSV file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".csv")) {
      setError("Please upload a CSV file");
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const result = await ingestionApi.uploadCsv(file);

      if (result.ingestion_result.success) {
        // Convert customer usage data to the format we need
        const uploadedUsage: CustomerUsage[] = result.customer.usage_data.map((u: CustomerUsage) => ({
          usage_date: u.usage_date,
          kwh_usage: Number(u.kwh_usage),
        }));

        setUsageData(uploadedUsage);
        setUploadedCustomerId(result.customer.id);
        setExternalId(result.customer.external_id);
        setUploadResult({
          success: true,
          message: `Successfully uploaded ${result.ingestion_result.records_processed} months of data`,
        });
      } else {
        setError(result.ingestion_result.errors.join(", ") || "Failed to process CSV file");
      }
    } catch (err) {
      setError("Failed to upload CSV file. Please check the format and try again.");
      console.error(err);
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleSubmit = async () => {
    if (usageData.length === 0) {
      setError("Please add usage data or use sample data");
      return;
    }

    // If customer was already created via CSV upload, use that ID
    if (uploadedCustomerId) {
      onSubmit(uploadedCustomerId);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const customer = await customerApi.create({
        external_id: externalId || `user-${Date.now()}`,
        usage_data: usageData,
        current_plan_id: currentPlanId || undefined,
        contract_end_date: contractEndDate || undefined,
        early_termination_fee: earlyTerminationFee ? parseFloat(earlyTerminationFee) : undefined,
      });

      onSubmit(customer.id);
    } catch (err) {
      setError("Failed to submit usage data. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const totalUsage = usageData.reduce((sum, u) => sum + u.kwh_usage, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle id="usage-form-title">Enter Your Energy Usage</CardTitle>
        <p className="text-sm text-gray-600 mt-1" id="usage-form-desc">
          We need 12 months of usage data to provide accurate recommendations.
        </p>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          aria-labelledby="usage-form-title"
          aria-describedby="usage-form-desc"
        >
          {/* Usage data display */}
          {usageData.length > 0 && (
            <div
              className="mb-6 p-4 bg-gray-50 rounded-lg"
              role="region"
              aria-label="Monthly usage data"
            >
              <h4 className="text-sm font-medium text-gray-700 mb-3" id="usage-data-heading">
                Usage Data ({usageData.length} months)
              </h4>
              <div
                className="grid grid-cols-3 sm:grid-cols-4 gap-2 text-xs"
                role="list"
                aria-labelledby="usage-data-heading"
              >
                {usageData.map((usage) => (
                  <div
                    key={usage.usage_date}
                    className="bg-white p-2 rounded border"
                    role="listitem"
                  >
                    <div className="text-gray-500">
                      {new Date(usage.usage_date).toLocaleDateString("en-US", {
                        month: "short",
                        year: "2-digit",
                      })}
                    </div>
                    <div className="font-medium" aria-label={`${usage.kwh_usage} kilowatt hours`}>
                      {usage.kwh_usage} kWh
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3 text-sm text-gray-600" aria-live="polite">
                Total: <span aria-label={`${totalUsage.toLocaleString()} kilowatt hours per year`}>
                  {totalUsage.toLocaleString()} kWh/year
                </span>
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="space-y-4">
            <fieldset>
              <legend className="sr-only">Data input options</legend>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={generateSampleData}
                  className="flex-1"
                  type="button"
                  aria-describedby="sample-data-hint"
                >
                  <FileText className="w-4 h-4 mr-2" aria-hidden="true" />
                  Use Sample Data
                </Button>
                <Button
                  variant="secondary"
                  className="flex-1"
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  aria-label="Upload CSV file"
                >
                  <Upload className="w-4 h-4 mr-2" aria-hidden="true" />
                  {isUploading ? "Uploading..." : "Upload CSV"}
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                  aria-label="CSV file input"
                />
              </div>
              <p id="sample-data-hint" className="sr-only">
                Generates 12 months of sample usage data for demonstration
              </p>
              <p className="text-xs text-gray-500 mt-2">
                CSV format: date,kwh (e.g., 2024-01-01,1050)
              </p>
              <div className="mt-3 pt-3 border-t">
                <Button
                  variant="ghost"
                  type="button"
                  onClick={() => setShowSmartDefaults(!showSmartDefaults)}
                  className="w-full text-gray-600"
                >
                  <Calculator className="w-4 h-4 mr-2" aria-hidden="true" />
                  {showSmartDefaults ? "Hide Estimator" : "Don't have your data? Estimate based on home"}
                </Button>
              </div>
            </fieldset>

            {/* Smart Defaults Estimator */}
            {showSmartDefaults && (
              <SmartDefaults onGenerate={handleSmartDefaultsGenerate} />
            )}

            {/* Current Plan Section */}
            <div className="border-t pt-4">
              <button
                type="button"
                onClick={() => setShowCurrentPlan(!showCurrentPlan)}
                className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 hover:text-gray-900"
                aria-expanded={showCurrentPlan}
              >
                <span>Do you have a current energy plan?</span>
                {showCurrentPlan ? (
                  <ChevronUp className="w-4 h-4" aria-hidden="true" />
                ) : (
                  <ChevronDown className="w-4 h-4" aria-hidden="true" />
                )}
              </button>
              <p className="text-xs text-gray-500 mt-1">
                Adding your current plan allows us to calculate your potential savings
              </p>

              {showCurrentPlan && (
                <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <label htmlFor="current-plan" className="block text-sm font-medium text-gray-700 mb-1">
                      Select Your Current Plan
                    </label>
                    <select
                      id="current-plan"
                      value={currentPlanId}
                      onChange={(e) => setCurrentPlanId(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    >
                      <option value="">Select a plan...</option>
                      {availablePlans.map((plan) => (
                        <option key={plan.id} value={plan.id}>
                          {plan.supplier?.name || "Unknown"} - {plan.name} (${plan.rate_per_kwh}/kWh)
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="contract-end" className="block text-sm font-medium text-gray-700 mb-1">
                      Contract End Date
                    </label>
                    <input
                      type="date"
                      id="contract-end"
                      value={contractEndDate}
                      onChange={(e) => setContractEndDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">When does your current contract expire?</p>
                  </div>

                  <div>
                    <label htmlFor="etf" className="block text-sm font-medium text-gray-700 mb-1">
                      Early Termination Fee ($)
                    </label>
                    <input
                      type="number"
                      id="etf"
                      value={earlyTerminationFee}
                      onChange={(e) => setEarlyTerminationFee(e.target.value)}
                      placeholder="0.00"
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Fee charged if you switch before contract ends</p>
                  </div>
                </div>
              )}
            </div>

            {uploadResult && (
              <div
                className={`p-3 rounded-lg text-sm flex items-center gap-2 ${
                  uploadResult.success
                    ? "bg-green-50 border border-green-200 text-green-700"
                    : "bg-red-50 border border-red-200 text-red-600"
                }`}
                role="status"
                aria-live="polite"
              >
                {uploadResult.success ? (
                  <CheckCircle className="w-4 h-4" aria-hidden="true" />
                ) : (
                  <AlertCircle className="w-4 h-4" aria-hidden="true" />
                )}
                {uploadResult.message}
              </div>
            )}

            {error && (
              <div
                className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600"
                role="alert"
                aria-live="assertive"
              >
                {error}
              </div>
            )}

            <Button
              type="submit"
              isLoading={isLoading}
              loadingText="Submitting usage data..."
              disabled={usageData.length === 0}
              className="w-full"
              size="lg"
              aria-describedby={usageData.length === 0 ? "submit-hint" : undefined}
            >
              Continue to Preferences
            </Button>
            {usageData.length === 0 && (
              <p id="submit-hint" className="text-sm text-gray-500 text-center">
                Please add usage data to continue
              </p>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
