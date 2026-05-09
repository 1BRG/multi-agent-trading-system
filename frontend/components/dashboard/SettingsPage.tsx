"use client";

import { useEffect, useState } from "react";
import type { User } from "../../types/auth";
import { applyTheme, getStoredTheme, setStoredTheme, type Theme } from "../../lib/theme";
import { AccountPanel } from "../auth/AccountPanel";

interface SettingsPageProps {
  onUserUpdated: (user: User) => void;
}

export function SettingsPage({ onUserUpdated }: SettingsPageProps) {
  const [theme, setTheme] = useState<Theme>("dark");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const currentTheme = getStoredTheme();
    setTheme(currentTheme);
    setIsLoading(false);
  }, []);

  function handleThemeChange(newTheme: Theme) {
    setTheme(newTheme);
    setStoredTheme(newTheme);
    applyTheme(newTheme);
  }

  if (isLoading) {
    return (
      <section className="workspace-panel">
        <p className="muted">Loading settings...</p>
      </section>
    );
  }

  return (
    <section className="workspace-panel settings-panel">
      <div className="workspace-hero">
        <div>
          <p className="eyebrow">Settings</p>
          <h1>Preferences and profile</h1>
          <p className="muted">Manage appearance and your account in one place.</p>
        </div>
      </div>

      <div className="workspace-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">Appearance</p>
            <h2>Theme</h2>
          </div>
          <p className="muted">Choose between light and dark mode.</p>
        </div>

        <div className="theme-selector">
          <label className="theme-option">
            <input
              checked={theme === "light"}
              onChange={() => handleThemeChange("light")}
              type="radio"
              value="light"
            />
            <span className="theme-label">
              <span className="theme-icon">☀️</span>
              <span className="theme-text">
                <strong>Light</strong>
                <span className="theme-desc">Bright and clean interface</span>
              </span>
            </span>
          </label>

          <label className="theme-option">
            <input
              checked={theme === "dark"}
              onChange={() => handleThemeChange("dark")}
              type="radio"
              value="dark"
            />
            <span className="theme-label">
              <span className="theme-icon">🌙</span>
              <span className="theme-text">
                <strong>Dark</strong>
                <span className="theme-desc">Easy on the eyes</span>
              </span>
            </span>
          </label>
        </div>
      </div>

      <AccountPanel embedded onUserUpdated={onUserUpdated} />
    </section>
  );
}
