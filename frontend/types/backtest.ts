export interface BacktestRun {
  id: number;
  user: number;
  strategy: number;
  stock: number;
  start_date: string;
  end_date: string;
  initial_cash: string;
  status: "pending" | "running" | "completed" | "failed";
  metrics: BacktestMetrics;
  equity_curve: EquityCurvePoint[];
  trades: BacktestTrade[];
  error_message: string;
  created_at: string;
  updated_at: string;
}

export interface BacktestMetrics {
  strategy_name?: string;
  symbol?: string;
  mode?: string;
  start_date?: string;
  end_date?: string;
  initial_cash?: number;
  final_equity?: number;
  total_return_pct?: number;
  annualized_return_pct?: number;
  benchmark_return_pct?: number;
  max_drawdown_pct?: number;
  sharpe_ratio?: number;
  volatility_pct?: number;
  trade_count?: number;
  win_rate_pct?: number;
  price_rows?: number;
  config?: Record<string, unknown>;
}

export interface EquityCurvePoint {
  date: string;
  equity: number;
}

export interface BacktestTrade {
  date: string;
  action: "BUY" | "SELL";
  price: number;
  shares: number;
  cash_after: number;
  equity_after: number;
  reason: string;
}
