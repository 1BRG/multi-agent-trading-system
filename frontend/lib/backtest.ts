import { apiRequest } from "./api";
import type { BacktestRun } from "../types/backtest";

export interface CreateBacktestPayload {
  strategy: number;
  stock: number;
  start_date: string;
  end_date: string;
  initial_cash: string;
}

export async function getBacktests(): Promise<BacktestRun[]> {
  return apiRequest<BacktestRun[]>("/backtests");
}

export async function createBacktest(payload: CreateBacktestPayload): Promise<BacktestRun> {
  return apiRequest<BacktestRun>("/backtests", {
    method: "POST",
    body: payload,
  });
}
