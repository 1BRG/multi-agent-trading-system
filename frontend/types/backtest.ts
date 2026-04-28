export interface BacktestRun {
  id: string;
  strategyId: string;
  status: "pending" | "completed" | "failed";
}

export interface BacktestMetrics {
  totalReturn: number;
  sharpeRatio: number;
}
