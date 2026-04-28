export interface Strategy {
  id: string;
  name: string;
  description?: string;
}

export interface StrategyConfig {
  strategyId: string;
  parameters: Record<string, unknown>;
}
