import { BacktestingPage } from "./BacktestingPage";
import { DebatePage } from "./DebatePage";
import { PortfolioPage } from "./PortfolioPage";
import { SettingsPlaceholderPage } from "./SettingsPlaceholderPage";
import { StocksPage } from "./StocksPage";
import { StrategyChatPage } from "./StrategyChatPage";
import { AccountPanel } from "../auth/AccountPanel";
import type { ChatHistoryItem, WorkspaceMode } from "../layout/Sidebar";

interface MainContentProps {
  activeChat: ChatHistoryItem | null;
  activeMode: WorkspaceMode;
  onChatCreated?: (id: string) => void;
}

export function MainContent({ activeChat, activeMode, onChatCreated }: MainContentProps) {
  if (activeMode === "stocks") return <StocksPage />;
  if (activeMode === "backtesting") return <BacktestingPage />;
  if (activeMode === "portfolio") return <PortfolioPage />;
  if (activeMode === "debate") return <DebatePage title={activeChat?.title ?? "Debate mode placeholder."} />;
  if (activeMode === "profile") return <AccountPanel embedded />;
  if (activeMode === "settings") return <SettingsPlaceholderPage />;

  return (
    <StrategyChatPage 
      title={activeChat?.title ?? "New Strategy"} 
      chatId={activeChat?.id} 
      onChatCreated={onChatCreated} 
    />
  );
}