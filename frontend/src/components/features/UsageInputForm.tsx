"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { customerApi, ingestionApi } from "@/lib/api";
import type { CustomerUsage } from "@/types";

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
  const fileInputRef = useRef<HTMLInputElement>(null);

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
            </fieldset>

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
