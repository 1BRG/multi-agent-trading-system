"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "../../lib/api";
import { clearAccessToken } from "../../lib/auth";
import type {
  UpdatePasswordPayload,
  UpdateProfilePayload,
  User,
} from "../../types/auth";

export function AccountPanel() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingPassword, setIsSavingPassword] = useState(false);

  useEffect(() => {
    async function loadUser() {
      try {
        const currentUser = await apiRequest<User>("/users/me");
        setUser(currentUser);
        setUsername(currentUser.username);
        setEmail(currentUser.email);
        setFullName(currentUser.full_name);
      } catch {
        clearAccessToken();
        router.replace("/login");
      } finally {
        setIsLoading(false);
      }
    }

    void loadUser();
  }, [router]);

  async function handleProfileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSavingProfile(true);

    const payload: UpdateProfilePayload = {
      username,
      email,
      full_name: fullName.trim(),
    };

    try {
      const updatedUser = await apiRequest<User>("/users/me", {
        method: "PATCH",
        body: payload,
      });
      setUser(updatedUser);
      setMessage("Profilul a fost actualizat.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Update failed.");
    } finally {
      setIsSavingProfile(false);
    }
  }

  async function handlePasswordSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSavingPassword(true);

    const payload: UpdatePasswordPayload = {
      current_password: currentPassword,
      new_password: newPassword,
    };

    try {
      await apiRequest<void>("/users/me/password", {
        method: "PATCH",
        body: payload,
      });
      setCurrentPassword("");
      setNewPassword("");
      setMessage("Parola a fost schimbata.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Password update failed.");
    } finally {
      setIsSavingPassword(false);
    }
  }

  async function handleDeactivateAccount() {
    setError(null);
    setMessage(null);

    try {
      await apiRequest<void>("/users/me", { method: "DELETE" });
      clearAccessToken();
      router.replace("/register");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Account deletion failed.");
    }
  }

  function handleLogout() {
    clearAccessToken();
    router.replace("/login");
  }

  if (isLoading) {
    return <main className="page-shell">Loading...</main>;
  }

  return (
    <main className="page-shell">
      <section className="account-header">
        <div>
          <p className="eyebrow">Account</p>
          <h1>{user?.full_name || user?.username || user?.email}</h1>
          <p className="muted">Role: {user?.role}</p>
        </div>
        <button className="secondary-button" onClick={handleLogout} type="button">
          Logout
        </button>
      </section>

      <section className="account-grid">
        <form className="panel-form" onSubmit={handleProfileSubmit}>
          <h2>Profile</h2>
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
          <button className="primary-button" disabled={isSavingProfile} type="submit">
            {isSavingProfile ? "Saving..." : "Save profile"}
          </button>
        </form>

        <form className="panel-form" onSubmit={handlePasswordSubmit}>
          <h2>Password</h2>
          <label className="field">
            <span>Current password</span>
            <input
              autoComplete="current-password"
              name="current_password"
              onChange={(event) => setCurrentPassword(event.target.value)}
              required
              type="password"
              value={currentPassword}
            />
          </label>
          <label className="field">
            <span>New password</span>
            <input
              autoComplete="new-password"
              minLength={8}
              name="new_password"
              onChange={(event) => setNewPassword(event.target.value)}
              required
              type="password"
              value={newPassword}
            />
          </label>
          <button className="primary-button" disabled={isSavingPassword} type="submit">
            {isSavingPassword ? "Saving..." : "Change password"}
          </button>
        </form>
      </section>

      {message ? <p className="form-success">{message}</p> : null}
      {error ? <p className="form-error">{error}</p> : null}

      <section className="danger-zone">
        <h2>Deactivate account</h2>
        <button className="danger-button" onClick={handleDeactivateAccount} type="button">
          Deactivate my account
        </button>
      </section>
    </main>
  );
}
