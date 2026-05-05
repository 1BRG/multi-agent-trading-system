"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../../lib/api";
import type { Portfolio, CreatePortfolioHoldingPayload, CreatePortfolioPayload } from "../../types/portfolio";
import type { Asset } from "../../types/stock";

const moneyFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 0,
});

function formatMoney(value: string | null | undefined, currency = "USD") {
  const numberValue = Number(value ?? 0);
  if (!Number.isFinite(numberValue)) {
    return "-";
  }

  return `${moneyFormatter.format(numberValue)} ${currency}`;
}

function formatPercent(value: string | null | undefined) {
  const numberValue = Number(value ?? 0) * 100;
  if (!Number.isFinite(numberValue)) {
    return "-";
  }

  return `${percentFormatter.format(numberValue)}%`;
}

function normalizeDecimalInput(value: FormDataEntryValue | null) {
  return String(value ?? "").trim();
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

  const selectedPortfolio = portfolios.find((portfolio) => portfolio.id === selectedPortfolioId) ?? null;
  const totalTargetWeight = useMemo(() => (
    selectedPortfolio?.holdings.reduce((sum, holding) => sum + Number(holding.target_weight), 0) ?? 0
  ), [selectedPortfolio]);

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

  async function handleCreatePortfolio(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsCreatingPortfolio(true);

    const form = event.currentTarget;
    const formData = new FormData(form);
    const payload: CreatePortfolioPayload = {
      name: String(formData.get("name") ?? "").trim(),
      cash: normalizeDecimalInput(formData.get("cash")) || "0.00",
      base_currency: String(formData.get("base_currency") ?? "USD").trim().toUpperCase() || "USD",
      description: String(formData.get("description") ?? "").trim(),
    };

    try {
      const createdPortfolio = await apiRequest<Portfolio>("/portfolios", {
        method: "POST",
        body: payload,
      });
      form.reset();
      setPortfolios((currentPortfolios) => [...currentPortfolios, createdPortfolio]);
      setSelectedPortfolioId(createdPortfolio.id);
      setMessage("Portofoliul a fost creat.");
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
    setIsAddingHolding(true);

    const form = event.currentTarget;
    const formData = new FormData(form);
    const targetPercent = Number(formData.get("target_weight_percent"));

    if (!Number.isFinite(targetPercent) || targetPercent < 0 || targetPercent > 100) {
      setError("Target weight must be between 0 and 100.");
      setIsAddingHolding(false);
      return;
    }

    const quantity = normalizeDecimalInput(formData.get("quantity"));
    const averageCost = normalizeDecimalInput(formData.get("average_cost"));
    const payload: CreatePortfolioHoldingPayload = {
      portfolio: selectedPortfolio.id,
      asset: Number(formData.get("asset")),
      target_weight: (targetPercent / 100).toFixed(4),
    };

    if (quantity) {
      payload.quantity = quantity;
    }
    if (averageCost) {
      payload.average_cost = averageCost;
    }

    try {
      await apiRequest("/portfolio-holdings", {
        method: "POST",
        body: payload,
      });
      form.reset();
      await loadPortfolios();
      setMessage("Holding-ul a fost adaugat.");
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
      setMessage("Holding-ul a fost sters.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not delete holding.");
    }
  }

  async function handleDeletePortfolio(portfolioId: number) {
    if (!window.confirm("Stergi portofoliul selectat?")) {
      return;
    }

    setError(null);
    setMessage(null);

    try {
      await apiRequest<void>(`/portfolios/${portfolioId}`, { method: "DELETE" });
      await loadPortfolios();
      setMessage("Portofoliul a fost sters.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Could not delete portfolio.");
    }
  }

  return (
    <section className="workspace-panel portfolio-panel">
      <div>
        <p className="eyebrow">Portfolio</p>
        <h1>Portfolios</h1>
      </div>

      {isLoading ? <p className="muted">Loading portfolios...</p> : null}
      {message ? <p className="form-success">{message}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <div className="portfolio-grid">
        <section className="portfolio-column">
          <form className="panel-form portfolio-form" onSubmit={handleCreatePortfolio}>
            <h2>Create portfolio</h2>
            <label className="field">
              <span>Name</span>
              <input maxLength={255} name="name" required type="text" />
            </label>
            <div className="portfolio-form-row">
              <label className="field">
                <span>Cash</span>
                <input min="0" name="cash" placeholder="10000.00" step="0.01" type="number" />
              </label>
              <label className="field">
                <span>Currency</span>
                <input defaultValue="USD" maxLength={10} name="base_currency" required type="text" />
              </label>
            </div>
            <label className="field">
              <span>Description</span>
              <input maxLength={500} name="description" type="text" />
            </label>
            <button className="primary-button" disabled={isCreatingPortfolio} type="submit">
              {isCreatingPortfolio ? "Creating..." : "Create"}
            </button>
          </form>

          <div className="portfolio-list" aria-label="Portfolio list">
            {portfolios.length > 0 ? (
              portfolios.map((portfolio) => (
                <button
                  className={portfolio.id === selectedPortfolioId ? "portfolio-list-item active" : "portfolio-list-item"}
                  key={portfolio.id}
                  onClick={() => setSelectedPortfolioId(portfolio.id)}
                  type="button"
                >
                  <span>{portfolio.name}</span>
                  <small>{`${formatMoney(portfolio.cash, portfolio.base_currency)} cash`}</small>
                </button>
              ))
            ) : (
              <p className="muted">No portfolios yet.</p>
            )}
          </div>
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
                  className="secondary-button compact-button"
                  onClick={() => handleDeletePortfolio(selectedPortfolio.id)}
                  type="button"
                >
                  Delete
                </button>
              </div>

              <div className="portfolio-summary">
                <div>
                  <span>Cash</span>
                  <strong>{formatMoney(selectedPortfolio.cash, selectedPortfolio.base_currency)}</strong>
                </div>
                <div>
                  <span>Holdings</span>
                  <strong>{selectedPortfolio.holdings.length}</strong>
                </div>
                <div>
                  <span>Target weight</span>
                  <strong>{formatPercent(String(totalTargetWeight))}</strong>
                </div>
              </div>

              <form className="portfolio-holding-form" onSubmit={handleAddHolding}>
                <label className="field">
                  <span>Asset</span>
                  <select name="asset" required>
                    <option value="">Select asset</option>
                    {assets.map((asset) => (
                      <option key={asset.id} value={asset.id}>
                        {asset.symbol} - {asset.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="field">
                  <span>Target %</span>
                  <input max="100" min="0" name="target_weight_percent" required step="0.01" type="number" />
                </label>
                <label className="field">
                  <span>Quantity</span>
                  <input min="0" name="quantity" step="0.00000001" type="number" />
                </label>
                <label className="field">
                  <span>Avg cost</span>
                  <input min="0" name="average_cost" step="0.000001" type="number" />
                </label>
                <button className="primary-button" disabled={isAddingHolding} type="submit">
                  {isAddingHolding ? "Adding..." : "Add"}
                </button>
              </form>

              <div className="stocks-table-wrap portfolio-holdings-wrap">
                <table className="stocks-table portfolio-holdings-table">
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>Name</th>
                      <th>Target</th>
                      <th>Quantity</th>
                      <th>Avg cost</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPortfolio.holdings.map((holding) => (
                      <tr key={holding.id}>
                        <td>{holding.asset_symbol}</td>
                        <td>{holding.asset_name}</td>
                        <td>{formatPercent(holding.target_weight)}</td>
                        <td>{holding.quantity ?? "-"}</td>
                        <td>{holding.average_cost ? formatMoney(holding.average_cost, selectedPortfolio.base_currency) : "-"}</td>
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
                        <td colSpan={6}>No holdings yet.</td>
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
