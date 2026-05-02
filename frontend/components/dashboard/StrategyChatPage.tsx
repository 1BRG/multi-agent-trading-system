interface StrategyChatPageProps {
  title: string;
}

export function StrategyChatPage({ title }: StrategyChatPageProps) {
  return (
    <section className="chat-workspace">
      <header className="chat-header">
        <div>
          <p className="eyebrow">Strategy</p>
          <h1>{title}</h1>
          <p className="muted">
            Strategy chat placeholder. One user talks with one AI agent about a strategy or
            trading idea.
          </p>
        </div>
      </header>

      <div className="chat-thread">
        <article className="chat-message assistant">
          <strong>Strategy agent</strong>
          <p>Placeholder response for a strategy conversation.</p>
        </article>
        <article className="chat-message user">
          <strong>You</strong>
          <p>Ask about a trading idea, rules, signals, or risk management.</p>
        </article>
      </div>

      <form className="chat-composer">
        <input disabled placeholder="Strategy chat input placeholder" type="text" />
        <button disabled type="button">
          Send
        </button>
      </form>
    </section>
  );
}
