export type Theme = "light" | "dark";

const THEME_STORAGE_KEY = "app-theme";
const DEFAULT_THEME: Theme = "dark";

export function getStoredTheme(): Theme {
  if (typeof window === "undefined") return DEFAULT_THEME;
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    return stored === "light" || stored === "dark" ? stored : DEFAULT_THEME;
  } catch {
    return DEFAULT_THEME;
  }
}

export function setStoredTheme(theme: Theme): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // Ignore storage errors
  }
}

export function applyTheme(theme: Theme): void {
  if (typeof document === "undefined") return;
  document.documentElement.setAttribute("data-theme", theme);
  document.documentElement.style.colorScheme = theme;
}

export function initializeTheme(): Theme {
  const theme = getStoredTheme();
  applyTheme(theme);
  return theme;
}
