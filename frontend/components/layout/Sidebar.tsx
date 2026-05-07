"use client";

import { useEffect, useState } from "react";
import type { MouseEvent } from "react";

import type { User } from "../../types/auth";
import { UserMenu } from "./UserMenu";

export type WorkspaceMode =
  | "stocks"
  | "portfolio"
  | "backtesting"
  | "strategy"
  | "debate"
  | "profile"
  | "settings";
export type ChatCategory = "debate" | "strategy";

export interface ChatHistoryItem {
  id: string;
  title: string;
  subtitle: string;
}

interface SidebarProps {
  activeChatId: string | null;
  activeMode: WorkspaceMode;
  chatCategory: ChatCategory;
  historyItems: ChatHistoryItem[];
  user: User | null;
  onChatCategoryChange: (category: ChatCategory) => void;
  onDeleteChat: (chatId: string) => void;
  onLogout: () => void;
  onModeChange: (mode: WorkspaceMode) => void;
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
}

export function Sidebar({
  activeChatId,
  activeMode,
  chatCategory,
  historyItems,
  user,
  onChatCategoryChange,
  onDeleteChat,
  onLogout,
  onModeChange,
  onNewChat,
  onSelectChat,
}: SidebarProps) {
  const [contextMenu, setContextMenu] = useState<{
    chatId: string;
    x: number;
    y: number;
  } | null>(null);

  useEffect(() => {
    function closeContextMenu() {
      setContextMenu(null);
    }

    window.addEventListener("click", closeContextMenu);
    window.addEventListener("keydown", closeContextMenu);
    return () => {
      window.removeEventListener("click", closeContextMenu);
      window.removeEventListener("keydown", closeContextMenu);
    };
  }, []);

  function handleChatContextMenu(event: MouseEvent<HTMLButtonElement>, chatId: string) {
    event.preventDefault();
    setContextMenu({
      chatId,
      x: Math.min(event.clientX, window.innerWidth - 190),
      y: Math.min(event.clientY, window.innerHeight - 54),
    });
  }

  function handleDeleteChat() {
    if (!contextMenu) {
      return;
    }

    onDeleteChat(contextMenu.chatId);
    setContextMenu(null);
  }

  return (
    <aside className="app-sidebar">
      <div className="sidebar-top">
        <div className="sidebar-brand">AI Stock Lab</div>
        <button className="new-chat-button" onClick={onNewChat} type="button">
          <span aria-hidden="true">+</span>
          New Chat
        </button>
      </div>

      <nav className="sidebar-section" aria-label="Main navigation">
        <button
          className={activeMode === "stocks" ? "sidebar-nav-item active" : "sidebar-nav-item"}
          onClick={() => onModeChange("stocks")}
          type="button"
        >
          Stocks
        </button>
        <button
          className={activeMode === "portfolio" ? "sidebar-nav-item active" : "sidebar-nav-item"}
          onClick={() => onModeChange("portfolio")}
          type="button"
        >
          Portfolio
        </button>
        <button
          className={activeMode === "backtesting" ? "sidebar-nav-item active" : "sidebar-nav-item"}
          onClick={() => onModeChange("backtesting")}
          type="button"
        >
          Backtesting
        </button>
      </nav>

      <section className="sidebar-history" aria-label="Chat history">
        <p className="sidebar-section-title">History</p>
        
        {/* We force Flexbox scrolling here! */}
        <div className="history-list" style={{ display: "flex", flexDirection: "column", overflowY: "auto" }}>
          {historyItems.length > 0 ? (
            historyItems.map((item) => (
              <button
                className={activeChatId === item.id ? "history-item active" : "history-item"}
                key={item.id}
                onContextMenu={(event) => handleChatContextMenu(event, item.id)}
                onClick={() => onSelectChat(item.id)}
                type="button"
                style={{ flexShrink: 0 }} // This prevents the button from squishing!
              >
                <span>{item.title}</span>
                <small>{item.subtitle}</small>
              </button>
            ))
          ) : (
            <p className="history-empty">No chats yet.</p>
          )}
        </div>
        {contextMenu ? (
          <div
            className="history-context-menu"
            style={{ left: contextMenu.x, top: contextMenu.y }}
          >
            <button onClick={handleDeleteChat} type="button">
              Delete conversation
            </button>
          </div>
        ) : null}
      </section>

      <div className="sidebar-bottom">
        <div className="history-toggle" aria-label="Chat mode selector">
          <button
            className={chatCategory === "debate" ? "active" : ""}
            onClick={() => onChatCategoryChange("debate")}
            type="button"
          >
            Debate
          </button>
          <button
            className={chatCategory === "strategy" ? "active" : ""}
            onClick={() => onChatCategoryChange("strategy")}
            type="button"
          >
            Strategy
          </button>
        </div>
        <UserMenu
          onLogout={onLogout}
          onOpenProfile={() => onModeChange("profile")}
          onOpenSettings={() => onModeChange("settings")}
          user={user}
        />
      </div>
    </aside>
  );
}
