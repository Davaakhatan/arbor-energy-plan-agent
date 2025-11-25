import axios from "axios";
import type {
  Customer,
  CustomerPreference,
  EnergyPlan,
  RecommendationSet,
  UsageFormData,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Customer API
export const customerApi = {
  create: async (data: UsageFormData): Promise<Customer> => {
    const response = await api.post<Customer>("/customers", data);
    return response.data;
  },

  get: async (customerId: string): Promise<Customer> => {
    const response = await api.get<Customer>(`/customers/${customerId}`);
    return response.data;
  },

  getByExternalId: async (externalId: string): Promise<Customer> => {
    const response = await api.get<Customer>(`/customers/external/${externalId}`);
    return response.data;
  },

  delete: async (customerId: string): Promise<void> => {
    await api.delete(`/customers/${customerId}`);
  },
};

// Plans API
export const plansApi = {
  list: async (filters?: {
    active_only?: boolean;
    supplier_id?: string;
    min_renewable?: number;
  }): Promise<EnergyPlan[]> => {
    const response = await api.get<EnergyPlan[]>("/plans", { params: filters });
    return response.data;
  },

  get: async (planId: string): Promise<EnergyPlan> => {
    const response = await api.get<EnergyPlan>(`/plans/${planId}`);
    return response.data;
  },
};

// Preferences API
export const preferencesApi = {
  get: async (customerId: string): Promise<CustomerPreference> => {
    const response = await api.get<CustomerPreference>(
      `/preferences/${customerId}`
    );
    return response.data;
  },

  upsert: async (
    customerId: string,
    preferences: CustomerPreference
  ): Promise<CustomerPreference> => {
    const response = await api.put<CustomerPreference>(
      `/preferences/${customerId}`,
      preferences
    );
    return response.data;
  },
};

// Recommendations API
export const recommendationsApi = {
  generate: async (
    customerId: string,
    preferences?: CustomerPreference
  ): Promise<RecommendationSet> => {
    const response = await api.post<RecommendationSet>("/recommendations", {
      customer_id: customerId,
      preferences,
      include_switching_analysis: true,
    });
    return response.data;
  },

  getCached: async (customerId: string): Promise<RecommendationSet> => {
    const response = await api.get<RecommendationSet>(
      `/recommendations/${customerId}`
    );
    return response.data;
  },

  invalidate: async (customerId: string): Promise<void> => {
    await api.delete(`/recommendations/${customerId}`);
  },
};

// Health API
export const healthApi = {
  check: async (): Promise<{ status: string; version: string }> => {
    const response = await api.get("/health");
    return response.data;
  },
};
