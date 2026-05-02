"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "../../lib/api";
import { clearAccessToken } from "../../lib/auth";
import type { User } from "../../types/auth";
import { DashboardWorkspace } from "../dashboard/DashboardWorkspace";
import type { WorkspaceMode } from "../layout/Sidebar";

interface DashboardHomeProps {
  initialMode?: WorkspaceMode;
}

export function DashboardHome({ initialMode = "strategy" }: DashboardHomeProps) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const currentUser = await apiRequest<User>("/users/me");
        setUser(currentUser);
      } catch {
        clearAccessToken();
        router.replace("/login");
      } finally {
        setIsLoading(false);
      }
    }

    void loadUser();
  }, [router]);

  function handleLogout() {
    clearAccessToken();
    router.replace("/");
  }

  return (
    <DashboardWorkspace
      initialMode={initialMode}
      onLogout={handleLogout}
      user={isLoading ? null : user}
    />
  );
}
