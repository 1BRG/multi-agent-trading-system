"use client";

import { useEffect, useState } from "react";
import type { Asset } from "../../types/stock";
import type { DebateSessionDetail } from "../../types/debate";
import { apiRequest } from "../../lib/api";
import { runDebate } from "../../lib/debate";
import { DebateMessage } from "../debates/DebateMessage";
import { DebatePanel } from "../debates/DebatePanel";

interface DebatePageProps {
  title: string;
}

export function DebatePage({ title }: DebatePageProps) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DebateSessionDetail | null>(null);

  useEffect(() => {
    async function loadAssets() {
      try {
        const data = await apiRequest<Asset[]>("/api/assets", { auth: false });
        // Only show stocks (not ETFs or commodities) for debate
        const stocks = data.filter(
          (a) => a.asset_type === "stock" && a.is_active
        );
        setAssets(stocks);
        if (stocks.length > 0) setSelectedTicker(stocks[0].symbol);
      } catch {
        /* assets will be empty */
      }
    }
    void loadAssets();
  }, []);

  async function handleRunDebate() {
    if (!selectedTicker) return;
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const debateResult = await runDebate(selectedTicker);
      setResult(debateResult);
    } catch (err: any) {
      setError(err.message || "Failed to run debate.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="workspace-panel debate-page-panel">
      <div>
        <p className="eyebrow">Stock Rater</p>
        <h1>{title}</h1>
        <p className="muted">
          Two AI agents debate whether a stock is a BUY, SELL, or HOLD. A Judge
          renders the final verdict with a conviction score.
        </p>
      </div>

      <div className="debate-controls">
        <label className="field">
          <span>Select stock</span>
          <select
            value={selectedTicker}
            onChange={(e) => {
              setSelectedTicker(e.target.value);
              setResult(null);
              setError(null);
            }}
            disabled={isLoading}
          >
            {assets.map((a) => (
              <option key={a.symbol} value={a.symbol}>
                {a.symbol} — {a.name}
              </option>
            ))}
          </select>
        </label>

        <button
          className="primary-button debate-run-button"
          onClick={handleRunDebate}
          disabled={isLoading || !selectedTicker}
          type="button"
        >
          {isLoading ? "Running debate…" : "Run Debate"}
        </button>
      </div>

      {isLoading && (
        <div className="debate-loading">
          <div className="debate-loading-spinner" />
          <p>
            Running 5-round debate for <strong>{selectedTicker}</strong>…
          </p>
          <p className="muted">
            This may take 1–3 minutes with a local LLM.
          </p>
        </div>
      )}

      {error && (
        <div className="form-error">{error}</div>
      )}

      {result && result.signal && (
        <DebatePanel signal={result.signal} />
      )}

      {result && result.messages && result.messages.length > 0 && (
        <div className="debate-transcript">
          <p className="eyebrow">Debate Transcript</p>
          <div className="debate-messages-list">
            {result.messages.map((msg) => (
              <DebateMessage key={msg.id} message={msg} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
