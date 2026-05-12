export interface ChatMessage {
  id: number;
  thread: number;
  role: "user" | "assistant";
  content: string;
  metadata?: Record<string, any>;
}

export interface ChatThread {
  id: number;
  title: string;
  created_at: string;
}
