import { BacktestingPage } from "./BacktestingPage";
import { DebatePage } from "./DebatePage";
import { PortfolioPage } from "./PortfolioPage";
import { SettingsPage } from "./SettingsPage";
import { StocksPage } from "./StocksPage";
import { StrategyChatPage } from "./StrategyChatPage";
import type { User } from "../../types/auth";
import type { ChatHistoryItem, WorkspaceMode } from "../layout/Sidebar";

interface MainContentProps {
  activeChat: ChatHistoryItem | null;
  activeMode: WorkspaceMode;
  onChatCreated?: (id: string) => void;
  onUserUpdated: (user: User) => void;
}

export function MainContent({ activeChat, activeMode, onChatCreated, onUserUpdated }: MainContentProps) {
  if (activeMode === "stocks") return <StocksPage />;
  if (activeMode === "backtesting") return <BacktestingPage />;
  if (activeMode === "portfolio") return <PortfolioPage />;
  if (activeMode === "debate") return <DebatePage title={activeChat?.title ?? "Debate mode placeholder."} />;
  if (activeMode === "profile") return <SettingsPage onUserUpdated={onUserUpdated} />;
  if (activeMode === "settings") return <SettingsPage onUserUpdated={onUserUpdated} />;

  return (
    <StrategyChatPage 
      title={activeChat?.title ?? "New Strategy"} 
      chatId={activeChat?.id} 
      onChatCreated={onChatCreated} 
    />
  );
}