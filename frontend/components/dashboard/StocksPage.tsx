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

  return `${day.padStart(2, "0")}/${month.padStart(2, "0")}/${year}`;
}

function parseDisplayDate(value: string) {
  const trimmedValue = value.trim();
  if (!trimmedValue) {
    return "";
  }

  const match = trimmedValue.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (!match) {
    return null;
  }

  const [, day, month, year] = match;
  const dayNumber = Number(day);
  const monthNumber = Number(month);
  const yearNumber = Number(year);
  const parsedDate = new Date(yearNumber, monthNumber - 1, dayNumber);

  if (
    parsedDate.getFullYear() !== yearNumber ||
    parsedDate.getMonth() !== monthNumber - 1 ||
    parsedDate.getDate() !== dayNumber
  ) {
    return null;
  }

  return `${year}-${String(monthNumber).padStart(2, "0")}-${String(dayNumber).padStart(2, "0")}`;
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

function readStoredSelectedSymbol() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(STOCKS_STORAGE_KEY);
}

interface DatePickerFieldProps {
  label: string;
  onChange: (value: string) => void;
  value: string;
}

function DatePickerField({ label, onChange, value }: DatePickerFieldProps) {
  const [displayValue, setDisplayValue] = useState(formatDateForDisplay(value));

  useEffect(() => {
    setDisplayValue(formatDateForDisplay(value));
  }, [value]);

  function handleTextChange(nextValue: string) {
    setDisplayValue(nextValue);
    const parsedDate = parseDisplayDate(nextValue);
    if (parsedDate !== null) {
      onChange(parsedDate);
    }
  }

  function handleBlur() {
    const parsedDate = parseDisplayDate(displayValue);
    if (parsedDate) {
      setDisplayValue(formatDateForDisplay(parsedDate));
      return;
    }

    if (!displayValue.trim()) {
      onChange("");
      return;
    }

    onChange("");
  }

  return (
    <label>
      <span>{label}</span>
      <div className="date-picker-control">
        <input
          aria-label={label}
          inputMode="numeric"
          onBlur={handleBlur}
          onChange={(event) => handleTextChange(event.target.value)}
          placeholder="zz/ll/aaaa"
          type="text"
          value={displayValue}
        />
        <span className="date-picker-calendar" title="Open calendar">
          <svg
            aria-hidden="true"
            focusable="false"
            viewBox="0 0 16 16"
          >
            <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5M1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z" />
          </svg>
          <input
            aria-label={`${label} calendar`}
            lang="ro-RO"
            onChange={(event) => onChange(event.target.value)}
            tabIndex={-1}
            type="date"
            value={value}
          />
        </span>
      </div>
    </label>
  );
}

export function StocksPage() {
  const defaultDateRange = useMemo(getDefaultDateRange, []);
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
    if (typeof window !== "undefined") {
      setSelectedSymbol(readStoredSelectedSymbol());
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (selectedSymbol) {
      window.localStorage.setItem(STOCKS_STORAGE_KEY, selectedSymbol);
      return;
    }

    window.localStorage.removeItem(STOCKS_STORAGE_KEY);
  }, [selectedSymbol]);

  useEffect(() => {
    if (!selectedSymbol) {
      setSelectedPrices([]);
      setPricesError(null);
      return;
    }

    if (!startDate || !endDate) {
      setSelectedPrices([]);
      setPricesError("Use date format zz/ll/aaaa.");
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
  const activeDateRange = `${formatDateForDisplay(startDate)} - ${formatDateForDisplay(endDate)}`;
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
      <div className="workspace-hero">
        <div>
          <p className="eyebrow">Stocks</p>
          <h1>Market data terminal</h1>
          <p className="muted">
            Explore equities, ETFs, and commodity proxies stored in PostgreSQL. Select an asset
            to inspect its recent trend, OHLCV history, and custom date window.
          </p>
        </div>

        <div className="workspace-stats">
          <div className="stat-card">
            <span>Assets loaded</span>
            <strong>{assets.length}</strong>
          </div>
          <div className="stat-card">
            <span>Selected asset</span>
            <strong>{selectedAsset?.symbol ?? "None"}</strong>
          </div>
          <div className="stat-card">
            <span>Date window</span>
            <strong>{activeDateRange}</strong>
          </div>
        </div>
      </div>

      <div className="workspace-card">
        <label className="stock-search">
          <span>Search asset</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search AAPL, SPY, GLD, GC=F..."
            type="search"
            value={query}
          />
        </label>
      </div>

      {isLoading ? <p className="muted">Loading assets...</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <div className="workspace-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Asset universe</p>
            <h2>Available instruments</h2>
          </div>
          <p className="muted">Click a row to open its price history.</p>
        </div>

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
              Choose a day or range to read OHLCV data from the local database. The default range
              is the last month.
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
            <DatePickerField label="Start date" onChange={setStartDate} value={startDate} />
            <DatePickerField label="End date" onChange={setEndDate} value={endDate} />
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
