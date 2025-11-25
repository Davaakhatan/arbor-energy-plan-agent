import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export function formatPercentage(value: number, decimals = 0): string {
  return `${value.toFixed(decimals)}%`;
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function getRateTypeLabel(rateType: string): string {
  const labels: Record<string, string> = {
    fixed: "Fixed Rate",
    variable: "Variable Rate",
    indexed: "Indexed Rate",
    time_of_use: "Time of Use",
  };
  return labels[rateType] || rateType;
}

export function getConfidenceColor(level: string): string {
  const colors: Record<string, string> = {
    high: "text-green-600",
    medium: "text-yellow-600",
    low: "text-red-600",
  };
  return colors[level] || "text-gray-600";
}

export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    low: "bg-yellow-100 text-yellow-800 border-yellow-200",
    medium: "bg-orange-100 text-orange-800 border-orange-200",
    high: "bg-red-100 text-red-800 border-red-200",
  };
  return colors[severity] || "bg-gray-100 text-gray-800";
}
