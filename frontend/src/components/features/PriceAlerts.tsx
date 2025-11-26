"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  Bell,
  TrendingDown,
  Mail,
  Check,
  X,
  DollarSign,
  Percent,
} from "lucide-react";

interface PriceAlertsProps {
  currentRate?: number;
  currentPlanName?: string;
}

interface AlertSettings {
  email: string;
  targetRate: number;
  alertType: "fixed" | "percent";
  percentBelow: number;
  isActive: boolean;
  createdAt: string;
}

export function PriceAlerts({ currentRate, currentPlanName }: PriceAlertsProps) {
  const [email, setEmail] = useState("");
  const [alertType, setAlertType] = useState<"fixed" | "percent">("percent");
  const [targetRate, setTargetRate] = useState(currentRate ? currentRate * 0.9 : 0.10);
  const [percentBelow, setPercentBelow] = useState(10);
  const [showForm, setShowForm] = useState(false);
  const [savedAlert, setSavedAlert] = useState<AlertSettings | null>(null);

  // Load saved alert from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("priceAlert");
    if (saved) {
      setSavedAlert(JSON.parse(saved));
    }
  }, []);

  // Update target rate when currentRate changes
  useEffect(() => {
    if (currentRate && alertType === "percent") {
      setTargetRate(currentRate * (1 - percentBelow / 100));
    }
  }, [currentRate, percentBelow, alertType]);

  const handleSaveAlert = () => {
    if (!email) return;

    const alertData: AlertSettings = {
      email,
      targetRate: alertType === "fixed" ? targetRate : currentRate! * (1 - percentBelow / 100),
      alertType,
      percentBelow,
      isActive: true,
      createdAt: new Date().toISOString(),
    };

    localStorage.setItem("priceAlert", JSON.stringify(alertData));
    setSavedAlert(alertData);
    setShowForm(false);
  };

  const handleDeleteAlert = () => {
    localStorage.removeItem("priceAlert");
    setSavedAlert(null);
    setEmail("");
  };

  const displayRate = currentRate || 0.12;
  const calculatedTargetRate = alertType === "fixed"
    ? targetRate
    : displayRate * (1 - percentBelow / 100);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingDown className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
          Price Drop Alerts
        </CardTitle>
        <p className="text-sm text-gray-500 mt-1">
          Get notified when energy rates drop below your target
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current Rate Display */}
        {currentRate && (
          <div className="p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              {currentPlanName ? `${currentPlanName}: ` : "Current Rate: "}
              <span className="font-semibold text-gray-900">
                ${currentRate.toFixed(4)}/kWh
              </span>
            </p>
          </div>
        )}

        {/* Saved Alert Display */}
        {savedAlert ? (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <Bell className="w-5 h-5 text-green-600 mt-0.5" aria-hidden="true" />
                <div>
                  <p className="font-medium text-green-800">
                    Alert Active
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    We&apos;ll email {savedAlert.email} when rates drop to{" "}
                    <span className="font-semibold">${savedAlert.targetRate.toFixed(4)}/kWh</span>
                    {savedAlert.alertType === "percent" && (
                      <span> ({savedAlert.percentBelow}% below current)</span>
                    )}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDeleteAlert}
                className="text-gray-500 hover:text-red-500"
              >
                <X className="w-4 h-4" aria-hidden="true" />
              </Button>
            </div>
          </div>
        ) : showForm ? (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            {/* Email */}
            <div>
              <label htmlFor="alert-email" className="block text-sm font-medium text-gray-700 mb-1">
                Email for alerts
              </label>
              <input
                id="alert-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-arbor-primary focus:border-transparent"
              />
            </div>

            {/* Alert Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Alert me when rates are:
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setAlertType("percent")}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    alertType === "percent"
                      ? "border-arbor-primary bg-arbor-light"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <Percent className="w-4 h-4 mb-1" aria-hidden="true" />
                  <span className="text-sm font-medium block">% Below Current</span>
                </button>
                <button
                  type="button"
                  onClick={() => setAlertType("fixed")}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    alertType === "fixed"
                      ? "border-arbor-primary bg-arbor-light"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <DollarSign className="w-4 h-4 mb-1" aria-hidden="true" />
                  <span className="text-sm font-medium block">Fixed Rate Target</span>
                </button>
              </div>
            </div>

            {/* Target Selection */}
            {alertType === "percent" ? (
              <div>
                <label htmlFor="percent-slider" className="block text-sm font-medium text-gray-700 mb-2">
                  Alert when rates drop by:
                </label>
                <div className="flex items-center gap-4">
                  <input
                    id="percent-slider"
                    type="range"
                    min="5"
                    max="30"
                    step="5"
                    value={percentBelow}
                    onChange={(e) => setPercentBelow(Number(e.target.value))}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-arbor-primary"
                  />
                  <span className="w-12 text-center font-medium">{percentBelow}%</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Target: ${calculatedTargetRate.toFixed(4)}/kWh
                </p>
              </div>
            ) : (
              <div>
                <label htmlFor="target-rate" className="block text-sm font-medium text-gray-700 mb-1">
                  Target rate ($/kWh):
                </label>
                <input
                  id="target-rate"
                  type="number"
                  step="0.001"
                  min="0.01"
                  max="0.50"
                  value={targetRate}
                  onChange={(e) => setTargetRate(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-arbor-primary focus:border-transparent"
                />
              </div>
            )}

            {/* Preview */}
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-700">
                <Check className="w-4 h-4 inline mr-1" aria-hidden="true" />
                You&apos;ll be notified when plans are available at{" "}
                <span className="font-semibold">
                  ${calculatedTargetRate.toFixed(4)}/kWh or lower
                </span>
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button
                onClick={handleSaveAlert}
                disabled={!email}
                className="flex-1"
              >
                <Bell className="w-4 h-4 mr-2" aria-hidden="true" />
                Create Alert
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button
            variant="outline"
            onClick={() => setShowForm(true)}
            className="w-full"
          >
            <Mail className="w-4 h-4 mr-2" aria-hidden="true" />
            Set Up Price Alert
          </Button>
        )}

        {/* Info */}
        <p className="text-xs text-gray-500">
          We check rates daily and will notify you when better deals become available.
          Alerts are stored locally on this device.
        </p>
      </CardContent>
    </Card>
  );
}
