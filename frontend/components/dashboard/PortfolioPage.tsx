"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../../lib/api";
import type {
  Portfolio,
  CreatePortfolioHoldingPayload,
  CreatePortfolioPayload,
  HoldingPriceSource,
  ResolvedHoldingPrice,
} from "../../types/portfolio";
import type { Asset } from "../../types/stock";

const moneyFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 0,
});

const PRICE_SOURCE_LABELS: Record<HoldingPriceSource, string> = {
  market_close: "Market close",
  previous_close: "Previous close",
  manual: "Custom price",
  unknown: "Unknown",
};

function formatMoney(value: string | null | undefined, currency = "USD") {
  const numberValue = Number(value ?? 0);
  if (!Number.isFinite(numberValue)) {
    return "-";
  }

  return `${moneyFormatter.format(numberValue)} ${currency}`;
}

function formatPercentRatio(value: number | null) {
  if (value === null || !Number.isFinite(value)) {
    return "-";
  }

  return `${percentFormatter.format(value * 100)}%`;
}

function formatPriceSource(source: HoldingPriceSource) {
  return PRICE_SOURCE_LABELS[source] ?? source;
}

function numericPreview(value: number | null, currency = "USD") {
  if (value === null || !Number.isFinite(value)) {
    return "-";
  }

  return formatMoney(value.toFixed(6), currency);
}

function parseDisplayDate(value: string) {
  const match = value.trim().match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (!match) {
    return null;
  }

  const [, dayText, monthText, yearText] = match;
  const day = Number(dayText);
  const month = Number(monthText);
  const year = Number(yearText);
  const date = new Date(Date.UTC(year, month - 1, day));

  if (
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== month - 1 ||
    date.getUTCDate() !== day
  ) {
    return null;
  }

  return `${yearText}-${monthText}-${dayText}`;
}

function formatDateForDisplay(value: string | null | undefined) {
  if (!value) {
    return "-";
  }

  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) {
    return value;
  }

  const [, year, month, day] = match;
  return `${day}/${month}/${year}`;
}

function normalizeDisplayDateInput(value: string) {
  const digits = value.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) {
    return digits;
  }
  if (digits.length <= 4) {
    return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  }
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

function formatIsoDateForDisplay(value: string) {
  if (!value) {
    return "";
  }
  return formatDateForDisplay(value);
}

function safeNumber(value: string | number | null | undefined) {
  const numberValue = Number(value ?? 0);
  return Number.isFinite(numberValue) ? numberValue : 0;
}

export function PortfolioPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingPortfolio, setIsCreatingPortfolio] = useState(false);
  const [isAddingHolding, setIsAddingHolding] = useState(false);
  const [holdingAssetId, setHoldingAssetId] = useState("");
  const [holdingQuantity, setHoldingQuantity] = useState("");
  const [purchaseDate, setPurchaseDate] = useState("");
  const [manualPrice, setManualPrice] = useState("");
  const [priceSource, setPriceSource] = useState<HoldingPriceSource>("previous_close");
  const [resolvedPrice, setResolvedPrice] = useState<ResolvedHoldingPrice | null>(null);
  const [priceLookupError, setPriceLookupError] = useState<string | null>(null);
  const [isResolvingPrice, setIsResolvingPrice] = useState(false);

  const selectedPortfolio = portfolios.find((portfolio) => portfolio.id === selectedPortfolioId) ?? null;
  const assetsById = useMemo(() => new Map(assets.map((asset) => [asset.id, asset])), [assets]);
  const selectedMetrics = useMemo(() => {
    const investedCost = selectedPortfolio?.holdings.reduce((sum, holding) => {
      const quantity = safeNumber(holding.quantity);
      const averageCost = safeNumber(holding.average_cost);
      return sum + quantity * averageCost;
    }, 0) ?? 0;
    const marketValue = selectedPortfolio?.holdings.reduce((sum, holding) => {
      const quantity = safeNumber(holding.quantity);
      const latestClose = safeNumber(assetsById.get(holding.asset)?.latest_price?.close);
      return sum + quantity * latestClose;
    }, 0) ?? 0;

    return {
      investedCost,
      marketValue,
      unrealizedPnL: marketValue - investedCost,
    };
  }, [assetsById, selectedPortfolio]);
  const totalPortfolioValue = useMemo(() => (
    portfolios.reduce((portfolioSum, portfolio) => {
      const marketValue = portfolio.holdings.reduce((holdingSum, holding) => {
        const quantity = safeNumber(holding.quantity);
        const latestClose = safeNumber(assetsById.get(holding.asset)?.latest_price?.close);
        return holdingSum + quantity * latestClose;
      }, 0);
      return portfolioSum + marketValue;
    }, 0)
  ), [assetsById, portfolios]);
  const selectedAsset = assetsById.get(Number(holdingAssetId)) ?? null;
  const selectedAssetAlreadyHeld = Boolean(
    selectedPortfolio?.holdings.some((holding) => String(holding.asset) === holdingAssetId),
  );
  const quantityNumber = Number(holdingQuantity);
  const hasPreviewQuantity = Number.isFinite(quantityNumber) && quantityNumber > 0;
  const effectivePrice = priceSource === "manual"
    ? Number(manualPrice)
    : Number(resolvedPrice?.average_cost ?? NaN);
  const latestPrice = Number(selectedAsset?.latest_price?.close ?? NaN);
  const investedAmount = hasPreviewQuantity && Number.isFinite(effectivePrice)
    ? quantityNumber * effectivePrice
    : null;
  const currentValue = hasPreviewQuantity && Number.isFinite(latestPrice)
    ? quantityNumber * latestPrice
    : null;
  const unrealizedPnL = investedAmount !== null && currentValue !== null
    ? currentValue - investedAmount
    : null;

  async function loadPortfolios() {
    const response = await apiRequest<Portfolio[]>("/portfolios");
    setPortfolios(response);
    setSelectedPortfolioId((currentId) => {
      if (currentId && response.some((portfolio) => portfolio.id === currentId)) {
        return currentId;
      }

      return response[0]?.id ?? null;
    });
  }

  const resetHoldingForm = useCallback(() => {
    setHoldingAssetId("");
    setHoldingQuantity("");
    setPurchaseDate("");
    setManualPrice("");
    setPriceSource("previous_close");
    setResolvedPrice(null);
    setPriceLookupError(null);
  }, []);

  useEffect(() => {
    let ignore = false;

    async function loadData() {
      try {
        const [portfolioResponse, assetResponse] = await Promise.all([
          apiRequest<Portfolio[]>("/portfolios"),
          apiRequest<Asset[]>("/api/assets", { auth: false }),
        ]);

        if (!ignore) {
          setPortfolios(portfolioResponse);
          setAssets(assetResponse);
          setSelectedPortfolioId(portfolioResponse[0]?.id ?? null);
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(caughtError instanceof Error ? caughtError.message : "Could not load portfolios.");
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadData();

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    let ignore = false;

    async function resolvePrice() {
      if (priceSource === "manual") {
        setResolvedPrice(null);
        setPriceLookupError(null);
        setIsResolvingPrice(false);
        return;
      }

      if (!holdingAssetId || !purchaseDate) {
        setResolvedPrice(null);
        setPriceLookupError(null);
        setIsResolvingPrice(false);
        return;
      }

      const parsedPurchaseDate = parseDisplayDate(purchaseDate);
      if (!parsedPurchaseDate) {
        setResolvedPrice(null);
        setPriceLookupError("Use date format dd/mm/yyyy.");
        setIsResolvingPrice(false);
        return;
      }

      setIsResolvingPrice(true);
      setResolvedPrice(null);
      setPriceLookupError(null);

      try {
        const params = new URLSearchParams({
          asset: holdingAssetId,
          purchase_date: parsedPurchaseDate,
          price_source: priceSource,
        });
        const response = await apiRequest<ResolvedHoldingPrice>(
          `/portfolio-holdings/resolve-price?${params.toString()}`,
        );
        if (!ignore) {
          setResolvedPrice(response);
        }
      } catch (caughtError) {
        if (!ignore) {
          setPriceLookupError(
            caughtError instanceof Error ? caughtError.message : "Could not resolve purchase price.",
          );
        }
      } finally {
        if (!ignore) {
          setIsResolvingPrice(false);
        }
      }
    }

    void resolvePrice();

    return () => {
      ignore = true;
    };
  }, [holdingAssetId, purchaseDate, priceSource]);

  async function handleCreatePortfolio(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);

    const form = event.currentTarget;
    const formData = new FormData(form);
    const payload: CreatePortfolioPayload = {
      name: String(formData.get("name") ?? "").trim(),
      cash: "0.00",
      base_currency: String(formData.get("base_currency") ?? "USD").trim().toUpperCase() || "USD",
      description: String(formData.get("description") ?? "").trim(),
    };

    if (!payload.name) {
      setError("Portfolio name is required.");
      return;
    }
    if (portfolios.some((portfolio) => portfolio.name.trim().toLowerCase() === payload.name.toLowerCase())) {
      setError("You already have a portfolio with this name.");
      return;
    }
    if (payload.base_currency !== "USD") {
      setError("Only USD portfolios are supported right now.");
      return;
    }

    setIsCreatingPortfolio(true);

    try {
      const createdPortfolio = await apiRequest<Portfolio>("/portfolios", {
        method: "POST",
        body: payload,
      });
      form.reset();
      setPortfolios((currentPortfolios) => [...currentPortfolios, createdPortfolio]);
      setSelectedPortfolioId(createdPortfolio.id);
      resetHoldingForm();
      setMessage("Portfolio created.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not create portfolio.");
    } finally {
      setIsCreatingPortfolio(false);
    }
  }

  async function handleAddHolding(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPortfolio) {
      return;
    }

    setError(null);
    setMessage(null);

    const assetId = Number(holdingAssetId);
    const quantity = Number(holdingQuantity);

    if (!assetId || !selectedAsset) {
      setError("Select an asset.");
      return;
    }
    if (selectedAssetAlreadyHeld) {
      setError("This asset already exists in the selected portfolio.");
      return;
    }
    if (!Number.isFinite(quantity) || quantity <= 0) {
      setError("Quantity must be greater than 0.");
      return;
    }
    const payload: CreatePortfolioHoldingPayload = {
      portfolio: selectedPortfolio.id,
      asset: assetId,
      quantity: quantity.toFixed(8),
      price_source: priceSource,
    };

    if (priceSource === "manual") {
      const customPrice = Number(manualPrice);
      if (!Number.isFinite(customPrice) || customPrice <= 0) {
        setError("Custom price must be greater than 0.");
        return;
      }
      payload.average_cost = customPrice.toFixed(6);
    } else {
      if (!purchaseDate) {
        setError("Purchase date is required for market price lookup.");
        return;
      }
      const parsedPurchaseDate = parseDisplayDate(purchaseDate);
      if (!parsedPurchaseDate) {
        setError("Purchase date must use dd/mm/yyyy format.");
        return;
      }
      if (isResolvingPrice) {
        setError("Wait for the purchase price lookup to finish.");
        return;
      }
      if (!resolvedPrice) {
        setError(priceLookupError ?? "Resolve a market price before adding the position.");
        return;
      }
      payload.purchase_date = parsedPurchaseDate;
    }

    setIsAddingHolding(true);

    try {
      await apiRequest("/portfolio-holdings", {
        method: "POST",
        body: payload,
      });
      resetHoldingForm();
      await loadPortfolios();
      setMessage("Position added.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not add holding.");
    } finally {
      setIsAddingHolding(false);
    }
  }

  async function handleDeleteHolding(holdingId: number) {
    setError(null);
    setMessage(null);

    try {
      await apiRequest<void>(`/portfolio-holdings/${holdingId}`, { method: "DELETE" });
      await loadPortfolios();
      setMessage("Holding deleted.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not delete holding.");
    }
  }

  async function handleDeletePortfolio(portfolioId: number) {
    if (!window.confirm("Delete the selected portfolio?")) {
      return;
    }

    setError(null);
    setMessage(null);

    try {
      await apiRequest<void>(`/portfolios/${portfolioId}`, { method: "DELETE" });
      await loadPortfolios();
      resetHoldingForm();
      setMessage("Portfolio deleted.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not delete portfolio.");
    }
  }

  function handlePriceSourceChange(nextSource: HoldingPriceSource) {
    setPriceSource(nextSource);
    setResolvedPrice(null);
    setPriceLookupError(null);

    if (nextSource === "manual") {
      setPurchaseDate("");
      return;
    }

    setManualPrice("");
  }

  function getHoldingInvestedCost(holding: Portfolio["holdings"][number]) {
    return safeNumber(holding.quantity) * safeNumber(holding.average_cost);
  }

  function getHoldingLatestPrice(holding: Portfolio["holdings"][number]) {
    const latestClose = assetsById.get(holding.asset)?.latest_price?.close;
    if (latestClose === null || latestClose === undefined) {
      return null;
    }

    const value = Number(latestClose);
    return Number.isFinite(value) ? value : null;
  }

  function getHoldingMarketValue(holding: Portfolio["holdings"][number]) {
    const latestClose = getHoldingLatestPrice(holding);
    if (latestClose === null) {
      return 0;
    }

    return safeNumber(holding.quantity) * latestClose;
  }

  function getHoldingWeight(holding: Portfolio["holdings"][number]) {
    const denominator = selectedMetrics.investedCost > 0
      ? selectedMetrics.investedCost
      : selectedMetrics.marketValue;
    if (denominator <= 0) {
      return null;
    }

    const value = selectedMetrics.investedCost > 0
      ? getHoldingInvestedCost(holding)
      : getHoldingMarketValue(holding);
    return value / denominator;
  }

  return (
    <section className="workspace-panel portfolio-panel">
      <div className="workspace-hero">
        <div>
          <p className="eyebrow">Portfolio</p>
          <h1>Portfolio workspace</h1>
          <p className="muted">
            Track positions, entry costs, market values, and dynamic investment weights against
            instruments from the local market database.
          </p>
        </div>

        <div className="workspace-stats">
          <div className="stat-card">
            <span>Portfolios</span>
            <strong>{portfolios.length}</strong>
          </div>
          <div className="stat-card">
            <span>Selected holdings</span>
            <strong>{selectedPortfolio?.holdings.length ?? 0}</strong>
          </div>
          <div className="stat-card">
            <span>Total value</span>
            <strong>{formatMoney(String(totalPortfolioValue), selectedPortfolio?.base_currency ?? "USD")}</strong>
          </div>
        </div>
      </div>

      {isLoading ? <p className="muted">Loading portfolios...</p> : null}
      {message ? <p className="form-success">{message}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <div className="portfolio-grid">
        <section className="portfolio-column">
          <section className="workspace-card">
            <div className="section-header">
              <div>
                <p className="eyebrow">Create</p>
                <h2>New portfolio</h2>
              </div>
              <p className="muted">Create the container, then add positions below.</p>
            </div>

            <form className="panel-form portfolio-form" onSubmit={handleCreatePortfolio}>
              <label className="field">
                <span>Name</span>
                <input maxLength={255} name="name" required type="text" />
              </label>
              <label className="field">
                <span>Currency</span>
                <input defaultValue="USD" maxLength={10} name="base_currency" required type="text" />
              </label>
              <label className="field">
                <span>Description</span>
                <input maxLength={500} name="description" type="text" />
              </label>
              <button className="primary-button" disabled={isCreatingPortfolio} type="submit">
                {isCreatingPortfolio ? "Creating..." : "Create portfolio"}
              </button>
            </form>
          </section>

          <section className="workspace-card portfolio-list-card" aria-label="Portfolio list">
            <div className="section-header">
              <div>
                <p className="eyebrow">Select</p>
                <h2>Saved portfolios</h2>
              </div>
              <p className="muted">Switch context with one click.</p>
            </div>

            <div className="portfolio-list">
              {portfolios.length > 0 ? (
                portfolios.map((portfolio) => (
                  <button
                    className={portfolio.id === selectedPortfolioId ? "portfolio-list-item active" : "portfolio-list-item"}
                    key={portfolio.id}
                    onClick={() => {
                      setSelectedPortfolioId(portfolio.id);
                      resetHoldingForm();
                    }}
                    type="button"
                  >
                    <span>{portfolio.name}</span>
                    <small>
                      {`${formatMoney(String(
                        portfolio.holdings.reduce((sum, holding) => {
                          const quantity = safeNumber(holding.quantity);
                          const averageCost = safeNumber(holding.average_cost);
                          return sum + quantity * averageCost;
                        }, 0),
                      ), portfolio.base_currency)} invested`}
                    </small>
                  </button>
                ))
              ) : (
                <p className="muted">No portfolios yet.</p>
              )}
            </div>
          </section>
        </section>

        <section className="portfolio-detail">
          {selectedPortfolio ? (
            <>
              <div className="portfolio-detail-header">
                <div>
                  <p className="eyebrow">Selected portfolio</p>
                  <h2>{selectedPortfolio.name}</h2>
                  <p className="muted">{selectedPortfolio.description || "No description."}</p>
                </div>
                <button
                  className="secondary-button compact-button portfolio-delete-button"
                  onClick={() => handleDeletePortfolio(selectedPortfolio.id)}
                  type="button"
                >
                  Delete
                </button>
              </div>

              <div className="portfolio-summary">
                <div>
                  <span>Invested cost</span>
                  <strong>{formatMoney(String(selectedMetrics.investedCost), selectedPortfolio.base_currency)}</strong>
                </div>
                <div>
                  <span>Market value</span>
                  <strong>{formatMoney(String(selectedMetrics.marketValue), selectedPortfolio.base_currency)}</strong>
                </div>
                <div>
                  <span>Unrealized P/L</span>
                  <strong>{formatMoney(String(selectedMetrics.unrealizedPnL), selectedPortfolio.base_currency)}</strong>
                </div>
                <div>
                  <span>Holdings</span>
                  <strong>{selectedPortfolio.holdings.length}</strong>
                </div>
              </div>

              <form className="portfolio-holding-form" noValidate onSubmit={handleAddHolding}>
                <div className="portfolio-position-grid">
                  <label className="field">
                    <span>Asset</span>
                    <select
                      name="asset"
                      onChange={(event) => setHoldingAssetId(event.target.value)}
                      required
                      value={holdingAssetId}
                    >
                      <option value="">Select asset</option>
                      {assets.map((asset) => {
                        const alreadyHeld = selectedPortfolio.holdings.some((holding) => holding.asset === asset.id);
                        return (
                          <option disabled={alreadyHeld} key={asset.id} value={asset.id}>
                            {asset.symbol} - {asset.name}{alreadyHeld ? " (already added)" : ""}
                          </option>
                        );
                      })}
                    </select>
                  </label>
                  <label className="field">
                    <span>Quantity</span>
                    <input
                      min="0.00000001"
                      onChange={(event) => setHoldingQuantity(event.target.value)}
                      required
                      step="0.00000001"
                      type="number"
                      value={holdingQuantity}
                    />
                  </label>
                  <label className="field">
                    <span>Price mode</span>
                    <select
                      onChange={(event) => handlePriceSourceChange(event.target.value as HoldingPriceSource)}
                      value={priceSource}
                    >
                      <option value="previous_close">Previous close</option>
                      <option value="market_close">Exact close</option>
                      <option value="manual">Custom price</option>
                    </select>
                  </label>
                  {priceSource === "manual" ? (
                    <label className="field">
                      <span>Purchase price</span>
                      <input
                        min="0.000001"
                        onChange={(event) => setManualPrice(event.target.value)}
                        required
                        step="0.000001"
                        type="number"
                        value={manualPrice}
                      />
                    </label>
                  ) : (
                    <label className="field">
                      <span>Purchase date</span>
                      <div className="date-input-row">
                        <input
                          inputMode="numeric"
                          maxLength={10}
                          onChange={(event) => setPurchaseDate(normalizeDisplayDateInput(event.target.value))}
                          placeholder="dd/mm/yyyy"
                          type="text"
                          value={purchaseDate}
                        />
                        <input
                          aria-label="Select purchase date from calendar"
                          className="portfolio-calendar-input"
                          onChange={(event) => setPurchaseDate(formatIsoDateForDisplay(event.target.value))}
                          type="date"
                          value={parseDisplayDate(purchaseDate) ?? ""}
                        />
                      </div>
                    </label>
                  )}
                </div>

                <div className="portfolio-price-status">
                  {isResolvingPrice ? <span>Resolving purchase price...</span> : null}
                  {resolvedPrice ? (
                    <span>
                      Using {formatMoney(resolvedPrice.average_cost, selectedPortfolio.base_currency)} from{" "}
                      {formatDateForDisplay(resolvedPrice.price_date)} ({formatPriceSource(resolvedPrice.price_source)}).
                    </span>
                  ) : null}
                  {priceSource === "manual" && manualPrice ? (
                    <span>Using custom price {formatMoney(manualPrice, selectedPortfolio.base_currency)}.</span>
                  ) : null}
                  {priceLookupError ? <span className="form-error">{priceLookupError}</span> : null}
                </div>

                <div className="portfolio-position-preview">
                  <div>
                    <span>Invested</span>
                    <strong>{numericPreview(investedAmount, selectedPortfolio.base_currency)}</strong>
                  </div>
                  <div>
                    <span>Latest price</span>
                    <strong>{numericPreview(Number.isFinite(latestPrice) ? latestPrice : null, selectedPortfolio.base_currency)}</strong>
                  </div>
                  <div>
                    <span>Current value</span>
                    <strong>{numericPreview(currentValue, selectedPortfolio.base_currency)}</strong>
                  </div>
                  <div>
                    <span>Unrealized P/L</span>
                    <strong>{numericPreview(unrealizedPnL, selectedPortfolio.base_currency)}</strong>
                  </div>
                </div>

                <button className="primary-button" disabled={isAddingHolding || isResolvingPrice} type="submit">
                  {isAddingHolding ? "Adding..." : "Add position"}
                </button>
              </form>

              <div className="stocks-table-wrap portfolio-holdings-wrap">
                <table className="stocks-table portfolio-holdings-table">
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>Name</th>
                      <th>Weight</th>
                      <th>Quantity</th>
                      <th>Buy price</th>
                      <th>Current price</th>
                      <th>Invested cost</th>
                      <th>Current value</th>
                      <th>Price date</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPortfolio.holdings.map((holding) => (
                      <tr key={holding.id}>
                        <td>{holding.asset_symbol}</td>
                        <td>{holding.asset_name}</td>
                        <td>{formatPercentRatio(getHoldingWeight(holding))}</td>
                        <td>{holding.quantity ?? "-"}</td>
                        <td>
                          {holding.average_cost
                            ? `${formatMoney(holding.average_cost, selectedPortfolio.base_currency)} (${formatPriceSource(holding.price_source)})`
                            : "-"}
                        </td>
                        <td>{numericPreview(getHoldingLatestPrice(holding), selectedPortfolio.base_currency)}</td>
                        <td>{formatMoney(String(getHoldingInvestedCost(holding)), selectedPortfolio.base_currency)}</td>
                        <td>{formatMoney(String(getHoldingMarketValue(holding)), selectedPortfolio.base_currency)}</td>
                        <td>{formatDateForDisplay(holding.price_date ?? holding.purchase_date)}</td>
                        <td>
                          <button
                            className="table-action-button"
                            onClick={() => handleDeleteHolding(holding.id)}
                            type="button"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {selectedPortfolio.holdings.length === 0 ? (
                      <tr>
                        <td colSpan={10}>No holdings yet.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="muted">Create a portfolio to add holdings.</p>
          )}
        </section>
      </div>
    </section>
  );
}
