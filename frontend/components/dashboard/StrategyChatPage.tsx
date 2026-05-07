import StrategyManager from "../strategies/StrategyManager";

interface StrategyChatPageProps {
  title: string;
  chatId?: string;
  onChatCreated?: (id: string) => void;
}

export function StrategyChatPage({ title, chatId, onChatCreated }: StrategyChatPageProps) {
  return (
    <section className="chat-workspace">
      <header className="chat-header">
        <div>
          <p className="eyebrow">Strategy</p>
          <h1>{title}</h1>
          <p className="muted">
            Translate natural language trading ideas into strict, deterministic JSON rules using AI.
          </p>
        </div>
      </header>

      <StrategyManager chatId={chatId} onChatCreated={onChatCreated} />
    </section>
  );
}