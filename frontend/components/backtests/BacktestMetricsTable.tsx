import type { BacktestMetrics } from "../../types/backtest";

interface BacktestMetricsTableProps {
  metrics: BacktestMetrics;
}

function formatNumber(value: number | undefined, suffix = "") {
  if (value === undefined || Number.isNaN(value)) {
    return "-";
  }

  return `${new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(value)}${suffix}`;
}

export function BacktestMetricsTable({ metrics }: BacktestMetricsTableProps) {
  const rows = [
    ["Total return", formatNumber(metrics.total_return_pct, "%")],
    ["Annualized return", formatNumber(metrics.annualized_return_pct, "%")],
    ["Benchmark return", formatNumber(metrics.benchmark_return_pct, "%")],
    ["Max drawdown", formatNumber(metrics.max_drawdown_pct, "%")],
    ["Sharpe ratio", formatNumber(metrics.sharpe_ratio)],
    ["Volatility", formatNumber(metrics.volatility_pct, "%")],
    ["Trades", formatNumber(metrics.trade_count)],
    ["Price rows", formatNumber(metrics.price_rows)],
  ];

  return (
    <div className="stocks-table-wrap backtest-metrics-wrap">
      <table className="stocks-table backtest-metrics-table">
        <tbody>
          {rows.map(([label, value]) => (
            <tr key={label}>
              <th>{label}</th>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
