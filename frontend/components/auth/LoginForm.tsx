"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { ApiError, apiRequest } from "../../lib/api";
import { clearStoredAppState, setAccessToken } from "../../lib/auth";
import type { AuthResponse, LoginPayload } from "../../types/auth";
import { SocialLoginButtons } from "./SocialLoginButtons";

export function LoginForm() {
  const router = useRouter();
  const [identifier, setIdentifier] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload: LoginPayload = {
      identifier,
      password: String(formData.get("password") ?? ""),
    };

    try {
      const response = await apiRequest<AuthResponse>("/auth/login", {
        method: "POST",
        auth: false,
        body: payload,
      });
      clearStoredAppState();
      setAccessToken(response.access_token);
      router.push("/dashboard");
      router.refresh();
    } catch (caughtError) {
      if (caughtError instanceof ApiError && caughtError.status === 401) {
        setError("Invalid username/email or password.");
      } else {
        setError(caughtError instanceof Error ? caughtError.message : "Login failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="field">
        <span>Email or username</span>
        <input
          autoComplete="username"
          name="identifier"
          onChange={(event) => setIdentifier(event.target.value)}
          required
          type="text"
          value={identifier}
        />
      </label>

      <label className="field">
        <span>Password</span>
        <input
          autoComplete="current-password"
          name="password"
          required
          type="password"
        />
      </label>

      {error ? <p className="form-error">{error}</p> : null}

      <button className="primary-button" disabled={isSubmitting} type="submit">
        {isSubmitting ? "Signing in..." : "Sign in"}
      </button>

      <SocialLoginButtons />

      <p className="form-footer">
        No account yet? <Link href="/register">Create one</Link>
      </p>
    </form>
  );
}
