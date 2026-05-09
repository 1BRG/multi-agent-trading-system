export interface ChatMessageMetadata {
  strategyConfig?: unknown;
  strategyName?: string;
  strategyId?: number;
  strategyStatus?: "draft" | "approved" | "archived";
}

export interface ChatMessage {
  id: number;
  thread: number;
  role: "user" | "assistant";
  content: string;
  metadata?: ChatMessageMetadata;
}

export interface ChatThread {
  id: number;
  title: string;
  created_at: string;
}
