export interface Stock {
  symbol: string;
  name: string;
}

export interface StockPricePoint {
  date: string;
  close: number;
}
