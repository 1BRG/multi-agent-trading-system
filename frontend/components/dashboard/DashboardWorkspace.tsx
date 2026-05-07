"use client";

import { useEffect, useState, useCallback } from "react";
import type { User } from "../../types/auth";
import { Sidebar, type ChatCategory, type WorkspaceMode, type ChatHistoryItem } from "../layout/Sidebar";
import { MainContent } from "./MainContent";
import { getChatThreads, deleteChatThread } from "../../lib/chat";

interface DashboardWorkspaceProps {
  initialMode?: WorkspaceMode;
  user: User | null;
  onLogout: () => void;
}

export function DashboardWorkspace({ initialMode = "strategy", user, onLogout }: DashboardWorkspaceProps) {
  const [activeMode, setActiveMode] = useState<WorkspaceMode>(initialMode);
  const [chatCategory, setChatCategory] = useState<ChatCategory>("strategy");
  
  const [strategyThreads, setStrategyThreads] = useState<ChatHistoryItem[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  const loadThreads = useCallback(async () => {
    try {
      const dbThreads = await getChatThreads();
      const mapped = dbThreads.map(t => {
        const d = new Date(t.created_at);
        // Formats to nice strings like "May 6" or "Oct 12"
        const dateStr = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        
        return {
          id: String(t.id),
          title: t.title,
          subtitle: dateStr
        };
      });
      setStrategyThreads(mapped);
      return mapped;
    } catch (err) {
      console.error("Failed to load threads", err);
      return [];
    }
  }, []);

  useEffect(() => {
    loadThreads().then((mapped) => {
      if (mapped.length > 0 && chatCategory === "strategy" && !activeChatId) {
        setActiveChatId(mapped[0].id);
      }
    });
  }, [loadThreads, chatCategory]); 

  function handleNewChat() {
    if (chatCategory === "debate") {
      alert("Debate AI is handled by another module!");
      return;
    }
    
    setActiveChatId(null);
    setActiveMode("strategy");
  }

  
  const handleChatCreated = async (newId: string) => {
    await loadThreads();
    setActiveChatId(newId);
  };

  async function handleDeleteChat(chatId: string) {
    if (chatCategory === "debate") return;
    try {
      await deleteChatThread(Number(chatId));
      const nextThreads = strategyThreads.filter((chat) => chat.id !== chatId);
      setStrategyThreads(nextThreads);
      if (activeChatId === chatId) setActiveChatId(nextThreads[0]?.id ?? null);
    } catch (err) {
      console.error("Failed to delete chat", err);
    }
  }

  const visibleHistory = chatCategory === "strategy" ? strategyThreads : [];
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
          setActiveChatId(c === "strategy" && strategyThreads.length > 0 ? strategyThreads[0].id : null);
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
          onChatCreated={handleChatCreated} 
        />
      </main>
    </div>
  );
}