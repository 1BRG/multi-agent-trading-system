import type { BacktestRun } from "../../types/backtest";
import { BacktestMetricsTable } from "./BacktestMetricsTable";

interface BacktestResultCardProps {
  run: BacktestRun;
}

const moneyFormatter = new Intl.NumberFormat("en-US", {
  currency: "USD",
  maximumFractionDigits: 2,
  style: "currency",
});

function formatDate(value: string | undefined) {
  if (!value) return "-";
  const [year, month, day] = value.split("-");
  if (!year || !month || !day) return value;
  return `${day}/${month}/${year}`;
}

function formatMode(value: string | undefined) {
  if (!value) return "-";
  return value.replaceAll("_", " ");
}

export function BacktestResultCard({ run }: BacktestResultCardProps) {
  const curvePreview = run.equity_curve.slice(-8);
  const tradesPreview = run.trades.slice(-6).reverse();

  return (
    <section className="backtest-result">
      <div className="backtest-result-header">
        <div>
          <p className="eyebrow">Latest result</p>
          <h2>{run.metrics.strategy_name ?? "Backtest run"}</h2>
          <p className="muted">
            {run.metrics.symbol ?? "Asset"} - {formatMode(run.metrics.mode)} - {formatDate(run.metrics.start_date)} to {formatDate(run.metrics.end_date)}
          </p>
        </div>
        <strong className={run.status === "completed" ? "status-pill success" : "status-pill danger"}>
          {run.status}
        </strong>
      </div>

      {run.status === "failed" ? (
        <p className="form-error">{run.error_message || "Backtest failed."}</p>
      ) : null}

      {run.status === "completed" ? (
        <>
          <div className="backtest-kpis">
            <div>
              <span>Final equity</span>
              <strong>{moneyFormatter.format(run.metrics.final_equity ?? 0)}</strong>
            </div>
            <div>
              <span>Total return</span>
              <strong>{run.metrics.total_return_pct ?? 0}%</strong>
            </div>
            <div>
              <span>Sharpe</span>
              <strong>{run.metrics.sharpe_ratio ?? 0}</strong>
            </div>
          </div>

          <BacktestMetricsTable metrics={run.metrics} />

          <div className="backtest-preview-grid">
            <div className="backtest-preview-panel">
              <h3>Equity curve</h3>
              <div className="stocks-table-wrap compact">
                <table className="stocks-table backtest-small-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Equity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {curvePreview.map((point) => (
                      <tr key={point.date}>
                        <td>{formatDate(point.date)}</td>
                        <td>{moneyFormatter.format(point.equity)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="backtest-preview-panel">
              <h3>Trades</h3>
              {tradesPreview.length === 0 ? (
                <p className="muted">No trades were generated.</p>
              ) : (
                <div className="stocks-table-wrap compact">
                  <table className="stocks-table backtest-small-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Side</th>
                        <th>Price</th>
                        <th>Shares</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tradesPreview.map((trade) => (
                        <tr key={`${trade.date}-${trade.action}-${trade.price}`}>
                          <td>{formatDate(trade.date)}</td>
                          <td>{trade.action}</td>
                          <td>{moneyFormatter.format(trade.price)}</td>
                          <td>{trade.shares}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </>
      ) : null}
    </section>
  );
}
