// frontend/lib/debate.ts

import { apiRequest } from "./api";
import type { DebateSession, DebateSessionDetail } from "../types/debate";

export async function runDebate(ticker: string): Promise<DebateSessionDetail> {
  return apiRequest<DebateSessionDetail>("/debates/run_debate", {
    method: "POST",
    body: { ticker },
  });
}

export async function getDebateSessions(): Promise<DebateSession[]> {
  return apiRequest<DebateSession[]>("/debates");
}

export async function getDebateSession(id: number): Promise<DebateSessionDetail> {
  return apiRequest<DebateSessionDetail>(`/debates/${id}`);
}
