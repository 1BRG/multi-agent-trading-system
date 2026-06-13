export type HoldingPriceSource = "market_close" | "previous_close" | "manual" | "unknown";

export interface PortfolioHolding {
  id: number;
  portfolio?: number;
  asset: number;
  asset_symbol: string;
  asset_name: string;
  asset_currency: string;
  target_weight: string;
  quantity: string | null;
  average_cost: string | null;
  purchase_date: string | null;
  price_date: string | null;
  price_source: HoldingPriceSource;
  created_at: string;
  updated_at: string;
}

export interface Portfolio {
  id: number;
  user: number;
  name: string;
  cash: string;
  base_currency: string;
  description: string;
  holdings: PortfolioHolding[];
  created_at: string;
  updated_at: string;
}

export interface CreatePortfolioPayload {
  name: string;
  cash: string;
  base_currency: string;
  description: string;
}

export interface CreatePortfolioHoldingPayload {
  portfolio: number;
  asset: number;
  price_source: HoldingPriceSource;
  purchase_date?: string;
  quantity?: string;
  average_cost?: string;
}

export interface ResolvedHoldingPrice {
  asset: number;
  asset_symbol: string;
  purchase_date: string;
  price_date: string;
  price_source: HoldingPriceSource;
  average_cost: string;
}
