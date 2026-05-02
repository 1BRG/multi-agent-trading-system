"use client";

import { useEffect, useMemo, useState } from "react";

import type { User } from "../../types/auth";
import { Sidebar } from "../layout/Sidebar";
import type { ChatCategory, ChatHistoryItem, WorkspaceMode } from "../layout/Sidebar";
import { MainContent } from "./MainContent";

const initialDebateChats: ChatHistoryItem[] = [
  {
    id: "debate-aapl",
    title: "AAPL buy or hold",
    subtitle: "Two-agent stock debate",
  },
  {
    id: "debate-nvda",
    title: "NVDA valuation debate",
    subtitle: "Bullish vs bearish agents",
  },
];

const initialStrategyChats: ChatHistoryItem[] = [
  {
    id: "strategy-rsi",
    title: "RSI mean reversion",
    subtitle: "Single-agent strategy chat",
  },
  {
    id: "strategy-ma",
    title: "Moving average crossover",
    subtitle: "Entry and exit idea",
  },
];

const WORKSPACE_STORAGE_KEY = "ai-stock-lab-workspace-state";

interface StoredWorkspaceState {
  activeDebateChatId?: string | null;
  activeMode?: WorkspaceMode;
  activeStrategyChatId?: string | null;
  chatCategory?: ChatCategory;
  debateChats?: ChatHistoryItem[];
  strategyChats?: ChatHistoryItem[];
}

interface DashboardWorkspaceProps {
  initialMode?: WorkspaceMode;
  user: User | null;
  onLogout: () => void;
}

function isWorkspaceMode(value: unknown): value is WorkspaceMode {
  return (
    value === "stocks" ||
    value === "backtesting" ||
    value === "strategy" ||
    value === "debate" ||
    value === "profile" ||
    value === "settings"
  );
}

function isChatCategory(value: unknown): value is ChatCategory {
  return value === "debate" || value === "strategy";
}

function isChatHistory(value: unknown): value is ChatHistoryItem[] {
  return (
    Array.isArray(value) &&
    value.every((item) => (
      item &&
      typeof item === "object" &&
      typeof (item as ChatHistoryItem).id === "string" &&
      typeof (item as ChatHistoryItem).title === "string" &&
      typeof (item as ChatHistoryItem).subtitle === "string"
    ))
  );
}

function readStoredWorkspaceState(): StoredWorkspaceState | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    const storedValue = window.localStorage.getItem(WORKSPACE_STORAGE_KEY);
    if (!storedValue) {
      return null;
    }

    const parsed = JSON.parse(storedValue) as Record<string, unknown>;
    return {
      activeDebateChatId:
        typeof parsed.activeDebateChatId === "string" ? parsed.activeDebateChatId : null,
      activeMode: isWorkspaceMode(parsed.activeMode) ? parsed.activeMode : undefined,
      activeStrategyChatId:
        typeof parsed.activeStrategyChatId === "string" ? parsed.activeStrategyChatId : null,
      chatCategory: isChatCategory(parsed.chatCategory) ? parsed.chatCategory : undefined,
      debateChats: isChatHistory(parsed.debateChats) ? parsed.debateChats : undefined,
      strategyChats: isChatHistory(parsed.strategyChats) ? parsed.strategyChats : undefined,
    };
  } catch {
    return null;
  }
}

export function DashboardWorkspace({
  initialMode = "strategy",
  user,
  onLogout,
}: DashboardWorkspaceProps) {
  const [hasLoadedStoredState, setHasLoadedStoredState] = useState(false);
  const [activeMode, setActiveMode] = useState<WorkspaceMode>(initialMode);
  const [chatCategory, setChatCategory] = useState<ChatCategory>("strategy");
  const [debateChats, setDebateChats] = useState<ChatHistoryItem[]>(initialDebateChats);
  const [strategyChats, setStrategyChats] = useState<ChatHistoryItem[]>(initialStrategyChats);
  const [activeDebateChatId, setActiveDebateChatId] = useState<string | null>(
    initialDebateChats[0]?.id ?? null,
  );
  const [activeStrategyChatId, setActiveStrategyChatId] = useState<string | null>(
    initialStrategyChats[0]?.id ?? null,
  );

  const visibleHistory = chatCategory === "debate" ? debateChats : strategyChats;
  const visibleActiveChatId =
    chatCategory === "debate" ? activeDebateChatId : activeStrategyChatId;
  const activeChat = useMemo(() => {
    const chats = activeMode === "debate" ? debateChats : strategyChats;
    const activeId = activeMode === "debate" ? activeDebateChatId : activeStrategyChatId;
    return chats.find((chat) => chat.id === activeId) ?? chats[0] ?? null;
  }, [activeDebateChatId, activeMode, activeStrategyChatId, debateChats, strategyChats]);

  useEffect(() => {
    const storedState = readStoredWorkspaceState();
    if (storedState) {
      if (storedState.activeMode) {
        setActiveMode(storedState.activeMode);
      }
      if (storedState.chatCategory) {
        setChatCategory(storedState.chatCategory);
      }
      if (storedState.debateChats) {
        setDebateChats(storedState.debateChats);
      }
      if (storedState.strategyChats) {
        setStrategyChats(storedState.strategyChats);
      }
      setActiveDebateChatId(storedState.activeDebateChatId ?? null);
      setActiveStrategyChatId(storedState.activeStrategyChatId ?? null);
    }
    setHasLoadedStoredState(true);
  }, []);

  useEffect(() => {
    if (!hasLoadedStoredState) {
      return;
    }

    window.localStorage.setItem(
      WORKSPACE_STORAGE_KEY,
      JSON.stringify({
        activeDebateChatId,
        activeMode,
        activeStrategyChatId,
        chatCategory,
        debateChats,
        strategyChats,
      }),
    );
  }, [
    activeDebateChatId,
    activeMode,
    activeStrategyChatId,
    chatCategory,
    debateChats,
    hasLoadedStoredState,
    strategyChats,
  ]);

  function handleChatCategoryChange(category: ChatCategory) {
    setChatCategory(category);
    setActiveMode(category);
  }

  function handleNewChat() {
    const createdAt = new Date();
    const timeLabel = createdAt.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    if (chatCategory === "debate") {
      const newChat: ChatHistoryItem = {
        id: `debate-${createdAt.getTime()}`,
        title: "New debate chat",
        subtitle: `Created at ${timeLabel}`,
      };
      setDebateChats((currentChats) => [newChat, ...currentChats]);
      setActiveDebateChatId(newChat.id);
      setActiveMode("debate");
      return;
    }

    const newChat: ChatHistoryItem = {
      id: `strategy-${createdAt.getTime()}`,
      title: "New strategy chat",
      subtitle: `Created at ${timeLabel}`,
    };
    setStrategyChats((currentChats) => [newChat, ...currentChats]);
    setActiveStrategyChatId(newChat.id);
    setActiveMode("strategy");
  }

  function handleSelectChat(chatId: string) {
    if (chatCategory === "debate") {
      setActiveDebateChatId(chatId);
      setActiveMode("debate");
      return;
    }

    setActiveStrategyChatId(chatId);
    setActiveMode("strategy");
  }

  function handleDeleteChat(chatId: string) {
    if (chatCategory === "debate") {
      const nextChats = debateChats.filter((chat) => chat.id !== chatId);
      setDebateChats(nextChats);
      if (activeDebateChatId === chatId) {
        setActiveDebateChatId(nextChats[0]?.id ?? null);
      }
      return;
    }

    const nextChats = strategyChats.filter((chat) => chat.id !== chatId);
    setStrategyChats(nextChats);
    if (activeStrategyChatId === chatId) {
      setActiveStrategyChatId(nextChats[0]?.id ?? null);
    }
  }

  return (
    <div className="workspace-layout">
      <Sidebar
        activeChatId={visibleActiveChatId}
        activeMode={activeMode}
        chatCategory={chatCategory}
        historyItems={visibleHistory}
        onChatCategoryChange={handleChatCategoryChange}
        onDeleteChat={handleDeleteChat}
        onLogout={onLogout}
        onModeChange={setActiveMode}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        user={user}
      />
      <main className="workspace-main">
        <MainContent activeChat={activeChat} activeMode={activeMode} />
      </main>
    </div>
  );
}
