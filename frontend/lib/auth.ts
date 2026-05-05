const TOKEN_STORAGE_KEY = "ai_stock_lab_access_token";
const WORKSPACE_STORAGE_KEY = "ai-stock-lab-workspace-state";
const STOCKS_STORAGE_KEY = "ai-stock-lab-stocks-state";


export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setAccessToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearAccessToken(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function clearStoredAppState(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(WORKSPACE_STORAGE_KEY);
  window.localStorage.removeItem(STOCKS_STORAGE_KEY);
}
