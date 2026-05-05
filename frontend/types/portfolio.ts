export interface PortfolioHolding {
  id: number;
  portfolio?: number;
  asset: number;
  asset_symbol: string;
  asset_name: string;
  target_weight: string;
  quantity: string | null;
  average_cost: string | null;
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
  target_weight: string;
  quantity?: string;
  average_cost?: string;
}
