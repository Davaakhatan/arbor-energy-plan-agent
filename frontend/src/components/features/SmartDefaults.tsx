"use client";

import { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  Home,
  Users,
  Thermometer,
  Zap,
  Calculator,
  Info,
} from "lucide-react";
import type { CustomerUsage } from "@/types";

interface SmartDefaultsProps {
  onGenerate: (usageData: CustomerUsage[]) => void;
}

type HomeType = "apartment" | "townhouse" | "house_small" | "house_medium" | "house_large";
type ClimateZone = "mild" | "hot_summer" | "cold_winter" | "extreme";

interface HomeOption {
  value: HomeType;
  label: string;
  icon: string;
  basekWh: number;
}

const HOME_OPTIONS: HomeOption[] = [
  { value: "apartment", label: "Apartment", icon: "🏢", basekWh: 600 },
  { value: "townhouse", label: "Townhouse", icon: "🏘️", basekWh: 800 },
  { value: "house_small", label: "Small House (<1500 sqft)", icon: "🏠", basekWh: 900 },
  { value: "house_medium", label: "Medium House (1500-2500 sqft)", icon: "🏡", basekWh: 1100 },
  { value: "house_large", label: "Large House (>2500 sqft)", icon: "🏰", basekWh: 1400 },
];

const CLIMATE_OPTIONS: { value: ClimateZone; label: string; factor: number }[] = [
  { value: "mild", label: "Mild (moderate temps year-round)", factor: 0.85 },
  { value: "hot_summer", label: "Hot Summers (heavy AC use)", factor: 1.15 },
  { value: "cold_winter", label: "Cold Winters (heavy heating)", factor: 1.1 },
  { value: "extreme", label: "Extreme (hot summers & cold winters)", factor: 1.3 },
];

const APPLIANCE_FACTORS: { id: string; label: string; factor: number }[] = [
  { id: "ev", label: "Electric Vehicle", factor: 0.25 },
  { id: "pool", label: "Pool/Hot Tub", factor: 0.15 },
  { id: "solar", label: "Solar Panels", factor: -0.3 },
  { id: "old_appliances", label: "Older Appliances (10+ years)", factor: 0.15 },
  { id: "smart_home", label: "Smart Home/Energy Management", factor: -0.1 },
];

export function SmartDefaults({ onGenerate }: SmartDefaultsProps) {
  const [homeType, setHomeType] = useState<HomeType>("house_medium");
  const [occupants, setOccupants] = useState(3);
  const [climate, setClimate] = useState<ClimateZone>("hot_summer");
  const [selectedAppliances, setSelectedAppliances] = useState<string[]>([]);

  const toggleAppliance = (id: string) => {
    setSelectedAppliances((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  const estimatedUsage = useMemo(() => {
    const homeOption = HOME_OPTIONS.find((h) => h.value === homeType);
    const climateOption = CLIMATE_OPTIONS.find((c) => c.value === climate);

    if (!homeOption || !climateOption) return 0;

    let baseMonthly = homeOption.basekWh;

    // Adjust for occupants (each person adds ~10%)
    const occupantFactor = 1 + (occupants - 2) * 0.1;
    baseMonthly *= occupantFactor;

    // Adjust for climate
    baseMonthly *= climateOption.factor;

    // Adjust for appliances
    const applianceFactor = selectedAppliances.reduce((acc, id) => {
      const appliance = APPLIANCE_FACTORS.find((a) => a.id === id);
      return acc + (appliance?.factor || 0);
    }, 1);
    baseMonthly *= applianceFactor;

    return Math.round(baseMonthly);
  }, [homeType, occupants, climate, selectedAppliances]);

  const generateUsageData = () => {
    const data: CustomerUsage[] = [];
    const now = new Date();
    const climateOption = CLIMATE_OPTIONS.find((c) => c.value === climate);

    for (let i = 11; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const month = date.getMonth();

      // Apply seasonal variation based on climate
      let seasonalFactor = 1.0;
      if (climateOption?.value === "hot_summer" || climateOption?.value === "extreme") {
        // Summer peak (June-August)
        if (month >= 5 && month <= 8) {
          seasonalFactor = 1.35;
        } else if (month >= 3 && month <= 9) {
          seasonalFactor = 1.15;
        }
      }
      if (climateOption?.value === "cold_winter" || climateOption?.value === "extreme") {
        // Winter peak (Dec-Feb)
        if (month >= 11 || month <= 1) {
          seasonalFactor = Math.max(seasonalFactor, 1.3);
        } else if (month >= 10 || month <= 2) {
          seasonalFactor = Math.max(seasonalFactor, 1.1);
        }
      }

      // Add some random variation (±10%)
      const randomVariation = 0.9 + Math.random() * 0.2;
      const kwh = Math.round(estimatedUsage * seasonalFactor * randomVariation);

      data.push({
        usage_date: date.toISOString().split("T")[0],
        kwh_usage: kwh,
      });
    }

    onGenerate(data);
  };

  const annualEstimate = estimatedUsage * 12;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-arbor-primary" aria-hidden="true" />
          Estimate Your Usage
        </CardTitle>
        <p className="text-sm text-gray-500 mt-1">
          Don&apos;t have your usage data? We&apos;ll estimate based on your home.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Home Type */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
            <Home className="w-4 h-4" aria-hidden="true" />
            Home Type
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {HOME_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setHomeType(option.value)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  homeType === option.value
                    ? "border-arbor-primary bg-arbor-light"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <span className="text-xl" aria-hidden="true">{option.icon}</span>
                <span className="block text-sm font-medium mt-1">{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Occupants */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
            <Users className="w-4 h-4" aria-hidden="true" />
            Number of Occupants
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="1"
              max="8"
              value={occupants}
              onChange={(e) => setOccupants(Number(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-arbor-primary"
              aria-label="Number of occupants"
            />
            <span className="w-12 text-center font-medium text-lg">{occupants}</span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            More people = more energy for lighting, electronics, and hot water
          </p>
        </div>

        {/* Climate */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
            <Thermometer className="w-4 h-4" aria-hidden="true" />
            Climate Zone
          </label>
          <div className="grid grid-cols-2 gap-2">
            {CLIMATE_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setClimate(option.value)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  climate === option.value
                    ? "border-arbor-primary bg-arbor-light"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <span className="text-sm font-medium">{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Additional Factors */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
            <Zap className="w-4 h-4" aria-hidden="true" />
            Additional Factors (optional)
          </label>
          <div className="space-y-2">
            {APPLIANCE_FACTORS.map((appliance) => (
              <label
                key={appliance.id}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                  selectedAppliances.includes(appliance.id)
                    ? "border-arbor-primary bg-arbor-light"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedAppliances.includes(appliance.id)}
                  onChange={() => toggleAppliance(appliance.id)}
                  className="w-4 h-4 text-arbor-primary rounded focus:ring-arbor-primary"
                />
                <span className="text-sm">{appliance.label}</span>
                <span className={`ml-auto text-xs ${appliance.factor > 0 ? "text-red-500" : "text-green-500"}`}>
                  {appliance.factor > 0 ? "+" : ""}{Math.round(appliance.factor * 100)}%
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Estimate Display */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-start gap-2 mb-3">
            <Info className="w-4 h-4 text-gray-400 mt-0.5" aria-hidden="true" />
            <p className="text-xs text-gray-500">
              This is an estimate based on typical usage patterns. Actual usage may vary.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-arbor-primary">{estimatedUsage.toLocaleString()}</p>
              <p className="text-xs text-gray-500">kWh/month (avg)</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{annualEstimate.toLocaleString()}</p>
              <p className="text-xs text-gray-500">kWh/year (est.)</p>
            </div>
          </div>
        </div>

        {/* Generate Button */}
        <Button
          onClick={generateUsageData}
          className="w-full"
          size="lg"
        >
          <Calculator className="w-4 h-4 mr-2" aria-hidden="true" />
          Use This Estimate
        </Button>
      </CardContent>
    </Card>
  );
}
