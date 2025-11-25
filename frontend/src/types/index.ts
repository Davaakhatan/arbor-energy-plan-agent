// Customer types
export interface CustomerUsage {
  usage_date: string;
  kwh_usage: number;
}

export interface Customer {
  id: string;
  external_id: string;
  current_plan_id?: string;
  contract_end_date?: string;
  early_termination_fee?: number;
  created_at: string;
  updated_at: string;
  usage_data: CustomerUsage[];
}

// Preference types
export interface CustomerPreference {
  cost_savings_weight: number;
  flexibility_weight: number;
  renewable_weight: number;
  supplier_rating_weight: number;
  min_renewable_percentage: number;
  max_contract_months?: number;
  avoid_variable_rates: boolean;
}

// Plan types
export interface Supplier {
  id: string;
  name: string;
  rating?: number;
  website?: string;
  customer_service_rating?: number;
  is_active: boolean;
}

export interface EnergyPlan {
  id: string;
  supplier_id: string;
  name: string;
  description?: string;
  rate_type: "fixed" | "variable" | "indexed" | "time_of_use";
  rate_per_kwh: number;
  monthly_fee: number;
  contract_length_months: number;
  early_termination_fee: number;
  cancellation_fee: number;
  renewable_percentage: number;
  is_active: boolean;
  supplier?: Supplier;
}

// Recommendation types
export interface RiskFlag {
  code: string;
  severity: "low" | "medium" | "high";
  message: string;
  details: Record<string, unknown>;
}

export interface Recommendation {
  id: string;
  rank: number;
  plan: EnergyPlan;
  overall_score: number;
  cost_score: number;
  flexibility_score: number;
  renewable_score: number;
  rating_score: number;
  projected_annual_cost: number;
  projected_annual_savings: number;
  switching_cost: number;
  net_first_year_savings: number;
  explanation: string;
  explanation_details: Record<string, unknown>;
  risk_flags: RiskFlag[];
  confidence_level: "high" | "medium" | "low";
  created_at: string;
  expires_at?: string;
}

export interface RecommendationSet {
  customer_id: string;
  recommendations: Recommendation[];
  current_annual_cost?: number;
  best_savings: number;
  generated_at: string;
  expires_at: string;
  processing_time_ms: number;
  warnings: string[];
}

// Form types
export interface UsageFormData {
  external_id: string;
  usage_data: CustomerUsage[];
  current_plan_id?: string;
  contract_end_date?: string;
  early_termination_fee?: number;
}

export interface PreferenceFormData extends CustomerPreference {}
