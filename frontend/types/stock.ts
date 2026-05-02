export interface Asset {
  id: number;
  symbol: string;
  name: string;
  asset_type: "stock" | "etf" | "commodity";
  sector: string;
  exchange: string;
  currency: string;
  is_active: boolean;
  latest_price: AssetPricePoint | null;
}

export interface AssetPricePoint {
  asset_id: number;
  symbol: string;
  date: string;
  open: string;
  high: string;
  low: string;
  close: string;
  adjusted_close: string | null;
  volume: number;
  source: string;
}

export interface AssetPricesResponse {
  asset: Asset;
  prices: AssetPricePoint[];
}

export type Stock = Asset;
export type StockPricePoint = AssetPricePoint;
