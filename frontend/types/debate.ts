export interface DebateMessage {
  id: number;
  session: number;
  agent_name: string;
  agent_role: "bullish" | "bearish" | "judge";
  round_number: number;
  content: string;
  created_at: string;
}

export interface StockSignal {
  id: number;
  user: number;
  asset: number;
  ticker: string;
  debate_session: number;
  action: "BUY" | "SELL" | "HOLD";
  conviction: number;
  bull_thesis: string;
  bear_thesis: string;
  judge_reasoning: string;
  timestamp: string;
}

export interface DebateSession {
  id: number;
  user: number;
  stock: number | null;
  topic: string;
  status: "pending" | "running" | "completed" | "failed";
  summary: string;
  created_at: string;
  updated_at: string;
}

export interface DebateSessionDetail extends DebateSession {
  messages: DebateMessage[];
  signal: StockSignal | null;
}
