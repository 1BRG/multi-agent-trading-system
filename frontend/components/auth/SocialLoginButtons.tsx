"use client";

import { useState } from "react";

import { apiRequest } from "../../lib/api";
import type { SocialAuthStartResponse } from "../../types/auth";

const providers = [
  { id: "google", label: "Continue with Google" },
  { id: "github", label: "Continue with GitHub" },
];

export function SocialLoginButtons() {
  const [error, setError] = useState<string | null>(null);
  const [activeProvider, setActiveProvider] = useState<string | null>(null);

  async function handleSocialLogin(provider: string) {
    setError(null);
    setActiveProvider(provider);

    try {
      const response = await apiRequest<SocialAuthStartResponse>(
        `/auth/social/${provider}/start`,
        {
          method: "POST",
          auth: false,
        },
      );
      window.sessionStorage.setItem(`ai_stock_lab_oauth_${provider}_state`, response.state);
      window.location.assign(response.authorization_url);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Social login failed.");
      setActiveProvider(null);
    }
  }

  return (
    <div className="social-login">
      <div className="auth-divider">
        <span>or</span>
      </div>
      <div className="social-login-buttons">
        {providers.map((provider) => (
          <button
            className="secondary-button social-login-button"
            disabled={activeProvider !== null}
            key={provider.id}
            onClick={() => handleSocialLogin(provider.id)}
            type="button"
          >
            {activeProvider === provider.id ? "Redirecting..." : provider.label}
          </button>
        ))}
      </div>
      {error ? <p className="form-error">{error}</p> : null}
    </div>
  );
}
