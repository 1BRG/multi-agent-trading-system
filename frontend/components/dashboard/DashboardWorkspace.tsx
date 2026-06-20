"use client";

import { useEffect, useState, useCallback } from "react";
import type { User } from "../../types/auth";
import { Sidebar, type ChatCategory, type WorkspaceMode, type ChatHistoryItem } from "../layout/Sidebar";
import { MainContent } from "./MainContent";
import { getChatThreads, deleteChatThread } from "../../lib/chat";
import { deleteDebateSession, getDebateSessions } from "../../lib/debate";

interface DashboardWorkspaceProps {
  initialMode?: WorkspaceMode;
  user: User | null;
  onLogout: () => void;
  onUserUpdated: (user: User) => void;
}

export function DashboardWorkspace({ initialMode = "strategy", user, onLogout, onUserUpdated }: DashboardWorkspaceProps) {
  const [activeMode, setActiveMode] = useState<WorkspaceMode>(initialMode);
  const [chatCategory, setChatCategory] = useState<ChatCategory>("strategy");
  
  const [strategyThreads, setStrategyThreads] = useState<ChatHistoryItem[]>([]);
  const [debateThreads, setDebateThreads] = useState<ChatHistoryItem[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  function formatHistoryDate(value: string) {
    const d = new Date(value);
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }

  const loadThreads = useCallback(async () => {
    try {
      const dbThreads = await getChatThreads();
      const mapped = dbThreads.map(t => {
        return {
          id: String(t.id),
          title: t.title,
          subtitle: formatHistoryDate(t.created_at)
        };
      });
      setStrategyThreads(mapped);
      return mapped;
    } catch (err) {
      console.error("Failed to load threads", err);
      return [];
    }
  }, []);

  const loadDebates = useCallback(async () => {
    try {
      const dbDebates = await getDebateSessions();
      const mapped = dbDebates.map((debate) => ({
        id: String(debate.id),
        title: debate.topic || "Stock debate",
        subtitle: debate.status + String.fromCharCode(32, 45, 32) + formatHistoryDate(debate.created_at)
      }));
      setDebateThreads(mapped);
      return mapped;
    } catch (err) {
      console.error("Failed to load debates", err);
      return [];
    }
  }, []);

  useEffect(() => {
    loadThreads().then((mapped) => {
      if (mapped.length > 0 && chatCategory === "strategy" && activeChatId === null) {
        setActiveChatId(mapped[0].id);
      }
    });
    loadDebates().then((mapped) => {
      if (mapped.length > 0 && chatCategory === "debate" && activeChatId === null) {
        setActiveChatId(mapped[0].id);
      }
    });
  }, [loadThreads, loadDebates, chatCategory]); 

  function handleNewChat() {
    if (chatCategory === "debate") {
      setActiveChatId(null);
      setActiveMode("debate");
      return;
    }
    
    setActiveChatId(null);
    setActiveMode("strategy");
  }

  const handleChatCreated = async (newId: string) => {
    await loadThreads();
    setActiveChatId(newId);
  };

  const handleDebateCreated = async (newId: string) => {
    await loadDebates();
    setActiveChatId(newId);
    setChatCategory("debate");
    setActiveMode("debate");
  };

  async function handleDeleteChat(chatId: string) {
    try {
      if (chatCategory === "debate") {
        await deleteDebateSession(Number(chatId));
        const nextThreads = debateThreads.filter((chat) => chat.id < chatId || chat.id > chatId);
        setDebateThreads(nextThreads);
        if (activeChatId === chatId) setActiveChatId(nextThreads[0]?.id ?? null);
        return;
      }

      await deleteChatThread(Number(chatId));
      const nextThreads = strategyThreads.filter((chat) => chat.id < chatId || chat.id > chatId);
      setStrategyThreads(nextThreads);
      if (activeChatId === chatId) setActiveChatId(nextThreads[0]?.id ?? null);
    } catch (err) {
      console.error("Failed to delete chat", err);
    }
  }

  const visibleHistory = chatCategory === "strategy" ? strategyThreads : debateThreads;
  const activeChat = visibleHistory.find((chat) => chat.id === activeChatId) ?? null;

  return (
    <div className="workspace-layout">
      <Sidebar
        activeChatId={activeChatId}
        activeMode={activeMode}
        chatCategory={chatCategory}
        historyItems={visibleHistory} 
        onChatCategoryChange={(c) => { 
          setChatCategory(c); 
          setActiveMode(c);
          setActiveChatId(c === "strategy" && strategyThreads.length > 0 ? strategyThreads[0].id : debateThreads[0]?.id ?? null);
        }}
        onDeleteChat={handleDeleteChat}
        onLogout={onLogout}
        onModeChange={setActiveMode}
        onNewChat={handleNewChat}
        onSelectChat={(id) => { setActiveChatId(id); setActiveMode(chatCategory); }}
        user={user}
      />
      <main className="workspace-main">
        {/*  */}
        <MainContent 
          activeChat={activeChat} 
          activeMode={activeMode} 
          onUserUpdated={onUserUpdated}
          onChatCreated={handleChatCreated} 
          onDebateCreated={handleDebateCreated}
        />
      </main>
    </div>
  );
}