import { ApiError, apiRequest } from "./api";

// 1. Define the strict config ruleset (This matches StrategyConfigSerializer)
export interface StrategyConfig {
  signal_rule?: "moving_average_crossover";
  short_window?: number;
  long_window?: number;
  rebalance_frequency: "daily" | "weekly" | "monthly" | "quarterly";
  ranking_metric: "conviction";
  portfolio_size: number;
  sizing: "equal_weight" | "conviction_weighted";
  sector_cap_pct: number;
  exit_on_signal_flip: boolean;
  min_conviction_score: number;
}

// 2. Define the main Strategy object returned by the backend
export interface Strategy {
  id: number;
  owner: number;
  name: string;
  description: string;
  config: StrategyConfig;
  status: "draft" | "approved" | "archived";
  source: "manual" | "ai";
  is_public: boolean;
  created_at: string;
  updated_at: string;
  
}

// 3. API Binding: Function to call our new Django endpoint
export async function generateAiStrategy(prompt: string, threadId?: number): Promise<Strategy> {
  const requestBody = { prompt, thread_id: threadId };

  try {
    return await apiRequest<Strategy>("/strategies/generate_ai", {
      method: "POST",
      body: requestBody,
    });
  } catch (error) {
    const message = error instanceof ApiError ? error.message.toLowerCase() : "";
    const shouldRetryForDeterministicConfig =
      error instanceof ApiError &&
      error.status === 400 &&
      (message.includes("rebalance_frequency") || message.includes("not a valid choice"));

    if (!shouldRetryForDeterministicConfig) {
      throw error;
    }

    const retryPrompt = `${prompt}\n\nImportant: return only valid deterministic values. rebalance_frequency must be exactly one of: daily, weekly, monthly, quarterly.`;

    return apiRequest<Strategy>("/strategies/generate_ai", {
      method: "POST",
      body: { prompt: retryPrompt, thread_id: threadId },
    });
  }
}

export async function approveStrategy(strategyId: number): Promise<Strategy> {
  return apiRequest<Strategy>(`/strategies/${strategyId}/approve`, {
    method: "PATCH",
  });
}

// 4. API Binding: Fetch user's strategies
export async function getStrategies(): Promise<Strategy[]> {
  return apiRequest<Strategy[]>("/strategies");
}
