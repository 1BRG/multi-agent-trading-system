"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";

import { apiRequest } from "../../../../lib/api";
import { setAccessToken } from "../../../../lib/auth";
import type { AuthResponse } from "../../../../types/auth";

export default function SocialAuthCallbackPage() {
  const params = useParams<{ provider: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function completeSocialLogin() {
      const provider = params.provider;
      const code = searchParams.get("code");
      const state = searchParams.get("state");
      const providerError = searchParams.get("error");

      if (providerError) {
        setError(providerError);
        return;
      }

      if (!code || !state) {
        setError("Social login callback is missing code or state.");
        return;
      }

      const storedState = window.sessionStorage.getItem(`ai_stock_lab_oauth_${provider}_state`);
      if (storedState !== state) {
        setError("Social login state does not match. Please try again.");
        return;
      }

      try {
        const response = await apiRequest<AuthResponse>(`/auth/social/${provider}/callback`, {
          method: "POST",
          auth: false,
          body: { code, state },
        });
        window.sessionStorage.removeItem(`ai_stock_lab_oauth_${provider}_state`);
        setAccessToken(response.access_token);
        router.replace("/dashboard");
        router.refresh();
      } catch (caughtError) {
        setError(caughtError instanceof Error ? caughtError.message : "Social login failed.");
      }
    }

    void completeSocialLogin();
  }, [params.provider, router, searchParams]);

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">AI Stock Lab</p>
        <h1>Social login</h1>
        {error ? <p className="form-error">{error}</p> : <p className="muted">Signing you in...</p>}
      </section>
    </main>
  );
}
