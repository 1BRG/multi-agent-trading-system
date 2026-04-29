"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { apiRequest } from "../../lib/api";
import { setAccessToken } from "../../lib/auth";
import type { AuthResponse, RegisterPayload } from "../../types/auth";

export function RegisterForm() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const payload: RegisterPayload = {
      identifier: username,
      username,
      email,
      password,
      full_name: fullName.trim() || undefined,
    };

    try {
      const response = await apiRequest<AuthResponse>("/auth/register", {
        method: "POST",
        auth: false,
        body: payload,
      });
      setAccessToken(response.access_token);
      router.push("/dashboard");
      router.refresh();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Registration failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="field">
        <span>Username</span>
        <input
          autoComplete="username"
          maxLength={150}
          name="username"
          onChange={(event) => setUsername(event.target.value)}
          required
          type="text"
          value={username}
        />
      </label>

      <label className="field">
        <span>Full name</span>
        <input
          autoComplete="name"
          maxLength={255}
          name="full_name"
          onChange={(event) => setFullName(event.target.value)}
          type="text"
          value={fullName}
        />
      </label>

      <label className="field">
        <span>Email</span>
        <input
          autoComplete="email"
          name="email"
          onChange={(event) => setEmail(event.target.value)}
          required
          type="email"
          value={email}
        />
      </label>

      <label className="field">
        <span>Password</span>
        <input
          autoComplete="new-password"
          minLength={8}
          name="password"
          onChange={(event) => setPassword(event.target.value)}
          required
          type="password"
          value={password}
        />
      </label>

      {error ? <p className="form-error">{error}</p> : null}

      <button className="primary-button" disabled={isSubmitting} type="submit">
        {isSubmitting ? "Creating account..." : "Create account"}
      </button>

      <p className="form-footer">
        Ai deja cont? <Link href="/login">Intra in cont</Link>
      </p>
    </form>
  );
}
