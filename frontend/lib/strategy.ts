import { apiRequest } from "./api";

// 1. Define the strict config ruleset (This matches StrategyConfigSerializer)
export interface StrategyConfig {
  rebalance_frequency: "daily" | "weekly" | "monthly" | "quarterly";
  ranking_metric: "conviction";
  portfolio_size: number;
  sizing: "equal_weight" | "conviction_weighted";
  sector_cap_pct: number;
  exit_on_signal_flip: boolean;
}

// 2. Define the main Strategy object returned by the backend
export interface Strategy {
  id: number;
  owner: number;
  name: string;
  description: string;
  config: StrategyConfig;
  source: "manual" | "ai";
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

// 3. API Binding: Function to call our new Django endpoint
export async function generateAiStrategy(prompt: string): Promise<Strategy> {
  return apiRequest<Strategy>("/strategies/generate_ai", {
    method: "POST",
    body: { prompt },
  });
}

// 4. API Binding: Fetch user's strategies
export async function getStrategies(): Promise<Strategy[]> {
  return apiRequest<Strategy[]>("/strategies");
}