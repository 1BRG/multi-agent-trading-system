import { BacktestingPage } from "./BacktestingPage";
import { DebatePage } from "./DebatePage";
import { SettingsPlaceholderPage } from "./SettingsPlaceholderPage";
import { StocksPage } from "./StocksPage";
import { StrategyChatPage } from "./StrategyChatPage";
import { AccountPanel } from "../auth/AccountPanel";
import type { ChatHistoryItem, WorkspaceMode } from "../layout/Sidebar";

interface MainContentProps {
  activeChat: ChatHistoryItem | null;
  activeMode: WorkspaceMode;
}

export function MainContent({ activeChat, activeMode }: MainContentProps) {
  if (activeMode === "stocks") {
    return <StocksPage />;
  }

  if (activeMode === "backtesting") {
    return <BacktestingPage />;
  }

  if (activeMode === "debate") {
    return <DebatePage title={activeChat?.title ?? "Debate mode placeholder."} />;
  }

  if (activeMode === "profile") {
    return <AccountPanel embedded />;
  }

  if (activeMode === "settings") {
    return <SettingsPlaceholderPage />;
  }

  return <StrategyChatPage title={activeChat?.title ?? "Strategy chat placeholder."} />;
}
