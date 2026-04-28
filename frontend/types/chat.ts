export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface ChatThread {
  id: string;
  title: string;
}
