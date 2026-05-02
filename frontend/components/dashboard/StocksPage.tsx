"use client";

import { useEffect, useMemo, useState } from "react";

import { apiRequest } from "../../lib/api";
import type { Asset, AssetPricePoint, AssetPricesResponse } from "../../types/stock";

const priceFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
});

const volumeFormatter = new Intl.NumberFormat("en-US");
const STOCKS_STORAGE_KEY = "ai-stock-lab-stocks-state";

interface StoredStocksState {
  endDate?: string;
  selectedSymbol?: string | null;
  startDate?: string;
}

function formatDateForApi(date: Date) {
  return date.toISOString().slice(0, 10);
}

function getDefaultDateRange() {
  const end = new Date();
  const start = new Date();
  start.setMonth(end.getMonth() - 1);

  return {
    endDate: formatDateForApi(end),
    startDate: formatDateForApi(start),
  };
}

function formatDateForDisplay(value: string | null | undefined) {
  if (!value) {
    return "-";
  }

  const [year, month, day] = value.split("-");
  if (!year || !month || !day) {
    return value;
  }

  return `${year}/${Number(month)}/${Number(day)}`;
}

function readStoredStocksState(): StoredStocksState | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    const storedValue = window.localStorage.getItem(STOCKS_STORAGE_KEY);
    if (!storedValue) {
      return null;
    }

    const parsed = JSON.parse(storedValue) as Record<string, unknown>;
    return {
      endDate: typeof parsed.endDate === "string" ? parsed.endDate : undefined,
      selectedSymbol: typeof parsed.selectedSymbol === "string" ? parsed.selectedSymbol : null,
      startDate: typeof parsed.startDate === "string" ? parsed.startDate : undefined,
    };
  } catch {
    return null;
  }
}

function buildPricePath(symbol: string, startDate: string, endDate: string) {
  const params = new URLSearchParams();
  if (startDate) {
    params.set("start", startDate);
  }
  if (endDate) {
    params.set("end", endDate);
  }

  return `/api/assets/${encodeURIComponent(symbol)}/prices?${params.toString()}`;
}

function formatPrice(value: string | null | undefined) {
  if (!value) {
    return "-";
  }

  return priceFormatter.format(Number(value));
}

export function StocksPage() {
  const defaultDateRange = useMemo(getDefaultDateRange, []);
  const [hasLoadedStoredState, setHasLoadedStoredState] = useState(false);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [startDate, setStartDate] = useState(defaultDateRange.startDate);
  const [endDate, setEndDate] = useState(defaultDateRange.endDate);
  const [selectedPrices, setSelectedPrices] = useState<AssetPricePoint[]>([]);
  const [pricesError, setPricesError] = useState<string | null>(null);
  const [isLoadingPrices, setIsLoadingPrices] = useState(false);

  useEffect(() => {
    async function loadAssets() {
      try {
        const response = await apiRequest<Asset[]>("/api/assets", { auth: false });
        setAssets(response);
      } catch (caughtError) {
        setError(caughtError instanceof Error ? caughtError.message : "Could not load assets.");
      } finally {
        setIsLoading(false);
      }
    }

    void loadAssets();
  }, []);

  useEffect(() => {
    const storedState = readStoredStocksState();
    if (storedState) {
      setSelectedSymbol(storedState.selectedSymbol ?? null);
      if (storedState.startDate) {
        setStartDate(storedState.startDate);
      }
      if (storedState.endDate) {
        setEndDate(storedState.endDate);
      }
    }
    setHasLoadedStoredState(true);
  }, []);

  useEffect(() => {
    if (!selectedSymbol) {
      setSelectedPrices([]);
      setPricesError(null);
      return;
    }

    if (!startDate || !endDate) {
      setSelectedPrices([]);
      setPricesError("Use date format YYYY/M/D.");
      return;
    }

    if (startDate && endDate && startDate > endDate) {
      setSelectedPrices([]);
      setPricesError("Start date must be before end date.");
      return;
    }

    const symbol = selectedSymbol;
    let ignore = false;

    async function loadSelectedPrices() {
      setIsLoadingPrices(true);
      setPricesError(null);

      try {
        const response = await apiRequest<AssetPricesResponse>(
          buildPricePath(symbol, startDate, endDate),
          { auth: false },
        );
        if (!ignore) {
          setSelectedPrices(response.prices);
        }
      } catch (caughtError) {
        if (!ignore) {
          setSelectedPrices([]);
          setPricesError(
            caughtError instanceof Error ? caughtError.message : "Could not load prices.",
          );
        }
      } finally {
        if (!ignore) {
          setIsLoadingPrices(false);
        }
      }
    }

    void loadSelectedPrices();

    return () => {
      ignore = true;
    };
  }, [endDate, selectedSymbol, startDate]);

  useEffect(() => {
    if (!hasLoadedStoredState) {
      return;
    }

    window.localStorage.setItem(
      STOCKS_STORAGE_KEY,
      JSON.stringify({
        endDate,
        selectedSymbol,
        startDate,
      }),
    );
  }, [endDate, hasLoadedStoredState, selectedSymbol, startDate]);

  const filteredAssets = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return assets;
    }

    return assets.filter((asset) => (
      asset.symbol.toLowerCase().includes(normalizedQuery) ||
      asset.name.toLowerCase().includes(normalizedQuery) ||
      asset.asset_type.toLowerCase().includes(normalizedQuery)
    ));
  }, [assets, query]);

  const selectedAsset = assets.find((asset) => asset.symbol === selectedSymbol) ?? null;
  const visiblePrices = selectedPrices.slice().reverse();

  function handleSelectAsset(symbol: string) {
    setSelectedSymbol(symbol);
  }

  function handleCloseDetails() {
    setSelectedSymbol(null);
    setSelectedPrices([]);
    setPricesError(null);
  }

  return (
    <section className="workspace-panel stocks-panel">
      <div>
        <p className="eyebrow">Stocks</p>
        <h1>Market data</h1>
        <p className="muted">
          Stocks, ETFs, and gold-related instruments stored in PostgreSQL. Select an asset to see
          price details for the day or date range you choose.
        </p>
      </div>

      <label className="stock-search">
        <span>Search asset</span>
        <input
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search AAPL, SPY, GLD, GC=F..."
          type="search"
          value={query}
        />
      </label>

      {isLoading ? <p className="muted">Loading assets...</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <div className="stocks-table-wrap">
        <table className="stocks-table selectable">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Type</th>
              <th>Exchange</th>
              <th>Last date</th>
              <th>Close</th>
              <th>Volume</th>
              <th>Currency</th>
            </tr>
          </thead>
          <tbody>
            {filteredAssets.map((asset) => (
              <tr
                className={asset.symbol === selectedSymbol ? "selected" : ""}
                key={asset.symbol}
                onClick={() => handleSelectAsset(asset.symbol)}
              >
                <td>{asset.symbol}</td>
                <td>{asset.name}</td>
                <td>{asset.asset_type}</td>
                <td>{asset.exchange || "-"}</td>
                <td>{asset.latest_price ? formatDateForDisplay(asset.latest_price.date) : "No prices yet"}</td>
                <td>{formatPrice(asset.latest_price?.close)}</td>
                <td>
                  {asset.latest_price ? volumeFormatter.format(asset.latest_price.volume) : "-"}
                </td>
                <td>{asset.currency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedAsset ? (
        <div className="stock-price-panel">
          <button
            aria-label="Close stock details"
            className="stock-detail-close"
            onClick={handleCloseDetails}
            type="button"
          >
            x
          </button>

          <div>
            <p className="eyebrow">Selected asset</p>
            <h2>{`${selectedAsset.symbol} details`}</h2>
            <p className="muted">
              Choose a day or range to read OHLCV data from the local database.
            </p>
          </div>

            <div className="stock-detail-summary">
              <div>
                <span>Latest close</span>
                <strong>{formatPrice(selectedAsset.latest_price?.close)}</strong>
              </div>
              <div>
                <span>Latest date</span>
                <strong>{formatDateForDisplay(selectedAsset.latest_price?.date)}</strong>
              </div>
              <div>
                <span>Asset type</span>
                <strong>{selectedAsset.asset_type}</strong>
              </div>
            </div>

            <div className="stock-date-controls">
              <label>
                <span>Start date</span>
                <input
                  onChange={(event) => setStartDate(event.target.value)}
                  type="date"
                  value={startDate}
                />
              </label>
              <label>
                <span>End date</span>
                <input
                  onChange={(event) => setEndDate(event.target.value)}
                  type="date"
                  value={endDate}
                />
              </label>
            </div>

          {isLoadingPrices ? <p className="muted">Loading prices...</p> : null}
          {pricesError ? <p className="form-error">{pricesError}</p> : null}

          {!isLoadingPrices && visiblePrices.length === 0 ? (
            <p className="muted">
              No price rows were found for {selectedAsset.symbol} in this interval.
            </p>
          ) : null}

          {visiblePrices.length > 0 ? (
            <div className="stocks-table-wrap compact">
              <table className="stocks-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Open</th>
                    <th>High</th>
                    <th>Low</th>
                    <th>Close</th>
                    <th>Adj close</th>
                    <th>Volume</th>
                    <th>Source</th>
                  </tr>
                </thead>
                <tbody>
                  {visiblePrices.map((price) => (
                    <tr key={price.date}>
                      <td>{formatDateForDisplay(price.date)}</td>
                      <td>{formatPrice(price.open)}</td>
                      <td>{formatPrice(price.high)}</td>
                      <td>{formatPrice(price.low)}</td>
                      <td>{formatPrice(price.close)}</td>
                      <td>{formatPrice(price.adjusted_close)}</td>
                      <td>{volumeFormatter.format(price.volume)}</td>
                      <td>{price.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
