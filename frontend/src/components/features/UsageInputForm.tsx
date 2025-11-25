"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Upload, FileText } from "lucide-react";
import { customerApi } from "@/lib/api";
import type { CustomerUsage } from "@/types";

interface UsageInputFormProps {
  onSubmit: (customerId: string) => void;
}

export function UsageInputForm({ onSubmit }: UsageInputFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [usageData, setUsageData] = useState<CustomerUsage[]>([]);
  const [externalId, setExternalId] = useState("");

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
  };

  const handleSubmit = async () => {
    if (usageData.length === 0) {
      setError("Please add usage data or use sample data");
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
                  disabled
                  type="button"
                  aria-label="Upload CSV file (coming soon)"
                >
                  <Upload className="w-4 h-4 mr-2" aria-hidden="true" />
                  Upload CSV
                </Button>
              </div>
              <p id="sample-data-hint" className="sr-only">
                Generates 12 months of sample usage data for demonstration
              </p>
            </fieldset>

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
