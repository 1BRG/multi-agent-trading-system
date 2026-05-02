interface DebatePageProps {
  title: string;
}

export function DebatePage({ title }: DebatePageProps) {
  return (
    <section className="workspace-panel debate-panel">
      <div>
        <p className="eyebrow">Debate</p>
        <h1>{title}</h1>
        <p className="muted">
          Two agents discussing whether a stock is a good buy, sell, or hold idea.
        </p>
      </div>

      <label className="stock-search">
        <span>Stock symbol</span>
        <input placeholder="AAPL" type="text" />
      </label>

      <div className="debate-agents-grid">
        <article className="agent-panel">
          <p className="eyebrow">Agent 1</p>
          <h2>Bullish agent</h2>
          <p className="muted">
            Placeholder argument for why the selected stock could be a good buy.
          </p>
        </article>
        <article className="agent-panel">
          <p className="eyebrow">Agent 2</p>
          <h2>Bearish agent</h2>
          <p className="muted">
            Placeholder argument for risks, weak signals, or reasons to avoid the stock.
          </p>
        </article>
      </div>
    </section>
  );
}
