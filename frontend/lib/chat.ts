// frontend/lib/chat.ts

import { apiRequest } from "./api";
import type { ChatThread, ChatMessage, ChatMessageMetadata } from "../types/chat";

export async function getChatThreads(): Promise<ChatThread[]> {
  return apiRequest<ChatThread[]>("/chats");
}

export async function createChatThread(title: string): Promise<ChatThread> {
  return apiRequest<ChatThread>("/chats", {
    method: "POST",
    body: { title },
  });
}

export async function deleteChatThread(id: number): Promise<void> {
  return apiRequest<void>(`/chats/${id}`, { method: "DELETE" });
}

export async function getChatMessages(): Promise<ChatMessage[]> {
  return apiRequest<ChatMessage[]>("/chat-messages");
}

export async function createChatMessage(
  threadId: number,
  role: ChatMessage["role"],
  content: string,
  metadata: ChatMessageMetadata = {}
): Promise<ChatMessage> {
  return apiRequest<ChatMessage>("/chat-messages", {
    method: "POST",
    body: { thread: threadId, role, content, metadata },
  });
}