"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../../lib/api";
import { createBacktest, getBacktests } from "../../lib/backtest";
import { getStrategies, type Strategy } from "../../lib/strategy";
import type { BacktestRun } from "../../types/backtest";
import type { Asset } from "../../types/stock";
import { BacktestResultCard } from "../backtests/BacktestResultCard";

function dateYearsAgo(years: number) {
  const date = new Date();
  date.setFullYear(date.getFullYear() - years);
  return date.toISOString().slice(0, 10);
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function formatDate(value: string) {
  const [year, month, day] = value.split("-");
  if (!year || !month || !day) return value;
  return `${day}/${month}/${year}`;
}

export function BacktestingPage() {
  const defaultStart = useMemo(() => dateYearsAgo(3), []);
  const defaultEnd = useMemo(today, []);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [runs, setRuns] = useState<BacktestRun[]>([]);
  const [selectedStrategyId, setSelectedStrategyId] = useState("");
  const [selectedAssetId, setSelectedAssetId] = useState("");
  const [startDate, setStartDate] = useState(defaultStart);
  const [endDate, setEndDate] = useState(defaultEnd);
  const [initialCash, setInitialCash] = useState("10000.00");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      setError(null);
      try {
        const [assetResponse, strategyResponse, runResponse] = await Promise.all([
          apiRequest<Asset[]>("/api/assets", { auth: false }),
          getStrategies(),
          getBacktests(),
        ]);
        setAssets(assetResponse);
        setStrategies(strategyResponse);
        setRuns(runResponse);
        setSelectedAssetId(String(assetResponse[0]?.id ?? ""));
        setSelectedStrategyId(String(strategyResponse.find((strategy) => strategy.status === "approved" || strategy.is_public)?.id ?? ""));
      } catch (caughtError) {
        setError(caughtError instanceof Error ? caughtError.message : "Could not load backtesting data.");
      } finally {
        setIsLoading(false);
      }
    }

    void loadData();
  }, []);

  const runnableStrategies = strategies.filter((strategy) => strategy.status === "approved" || strategy.is_public);
  const latestRun = runs[0] ?? null;
  const approvedStrategyCount = runnableStrategies.length;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);

    if (!selectedStrategyId || !selectedAssetId) {
      setError("Choose a strategy and an asset before running the backtest.");
      return;
    }

    if (startDate > endDate) {
      setError("Start date must be before end date.");
      return;
    }

    setIsSubmitting(true);
    try {
      const run = await createBacktest({
        strategy: Number(selectedStrategyId),
        stock: Number(selectedAssetId),
        start_date: startDate,
        end_date: endDate,
        initial_cash: initialCash,
      });
      setRuns((currentRuns) => [run, ...currentRuns.filter((item) => item.id !== run.id)]);
      setMessage(run.status === "completed" ? "Backtest completed." : "Backtest saved with a failure message.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not run backtest.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-panel backtesting-panel">
      <div className="workspace-hero">
        <div>
          <p className="eyebrow">Backtesting</p>
          <h1>Strategy lab</h1>
          <p className="muted">
            Simulate approved strategies against historical OHLCV data stored in PostgreSQL and
            inspect equity, trades, and risk metrics in one place.
          </p>
        </div>

        <div className="workspace-stats">
          <div className="stat-card">
            <span>Approved strategies</span>
            <strong>{approvedStrategyCount}</strong>
          </div>
          <div className="stat-card">
            <span>Saved runs</span>
            <strong>{runs.length}</strong>
          </div>
          <div className="stat-card">
            <span>Lookback</span>
            <strong>{formatDate(defaultStart)} - {formatDate(defaultEnd)}</strong>
          </div>
        </div>
      </div>

      {isLoading ? <p className="muted">Loading backtesting workspace...</p> : null}
      {message ? <p className="form-success">{message}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <div className="workspace-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Run</p>
            <h2>Backtest parameters</h2>
          </div>
          <p className="muted">Pick a strategy, market, and date window.</p>
        </div>

        <form className="panel-form backtest-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Strategy</span>
            <select
              disabled={isLoading || isSubmitting}
              onChange={(event) => setSelectedStrategyId(event.target.value)}
              value={selectedStrategyId}
            >
              <option value="">Choose strategy</option>
              {runnableStrategies.map((strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name} {strategy.is_public ? "(public)" : ""}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Asset</span>
            <select
              disabled={isLoading || isSubmitting}
              onChange={(event) => setSelectedAssetId(event.target.value)}
              value={selectedAssetId}
            >
              <option value="">Choose asset</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} - {asset.name}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Start date</span>
            <input
              disabled={isSubmitting}
              onChange={(event) => setStartDate(event.target.value)}
              type="date"
              value={startDate}
            />
          </label>

          <label className="field">
            <span>End date</span>
            <input
              disabled={isSubmitting}
              onChange={(event) => setEndDate(event.target.value)}
              type="date"
              value={endDate}
            />
          </label>

          <label className="field">
            <span>Initial cash</span>
            <input
              disabled={isSubmitting}
              min="1"
              onChange={(event) => setInitialCash(event.target.value)}
              step="0.01"
              type="number"
              value={initialCash}
            />
          </label>

          <button className="primary-button" disabled={isSubmitting || isLoading} type="submit">
            {isSubmitting ? "Running..." : "Run backtest"}
          </button>
        </form>
      </div>

      {runnableStrategies.length === 0 && !isLoading ? (
        <p className="form-error">Approve a strategy before running a backtest.</p>
      ) : null}

      {latestRun ? <BacktestResultCard run={latestRun} /> : null}

      <section className="backtest-history">
        <h2>Recent runs</h2>
        {runs.length === 0 ? (
          <p className="muted">No backtests have been run yet.</p>
        ) : (
          <div className="stocks-table-wrap compact">
            <table className="stocks-table backtest-history-table">
              <thead>
                <tr>
                  <th>Created</th>
                  <th>Strategy</th>
                  <th>Symbol</th>
                  <th>Status</th>
                  <th>Return</th>
                  <th>Final equity</th>
                </tr>
              </thead>
              <tbody>
                {runs.slice(0, 8).map((run) => (
                  <tr key={run.id}>
                    <td>{formatDate(run.created_at.slice(0, 10))}</td>
                    <td>{run.metrics.strategy_name ?? `#${run.strategy}`}</td>
                    <td>{run.metrics.symbol ?? `#${run.stock}`}</td>
                    <td>{run.status}</td>
                    <td>{run.metrics.total_return_pct !== undefined ? `${run.metrics.total_return_pct}%` : "-"}</td>
                    <td>{run.metrics.final_equity !== undefined ? `$${run.metrics.final_equity.toLocaleString()}` : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}
