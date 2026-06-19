import Link from "next/link";

export default function HomePage() {
  return (
    <div className="landing-shell">
      <div className="landing-noise" aria-hidden="true" />
      <header className="landing-header">
        <Link className="landing-logo" href="/">
          AI Stock Lab
        </Link>
        <nav className="landing-nav" aria-label="Main navigation">
          <Link href="/login">Login</Link>
          <Link className="landing-register" href="/register">
            Register
          </Link>
        </nav>
      </header>

      <main className="landing-main">
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <p className="landing-eyebrow">Algorithmic intelligence for traders</p>
            <h1>Build, debate, and backtest AI trading ideas in one command center.</h1>
            <p className="landing-copy">
              AI Stock Lab combina analiza cuantitativa, dezbateri Bull vs Bear si
              strategii deterministe intr-o experienta moderna pentru dezvoltare si
              decizii de investitii.
            </p>
            <div className="landing-actions">
              <Link className="landing-primary" href="/register">
                Start Free
              </Link>
              <Link className="landing-secondary" href="/login">
                Open Dashboard
              </Link>
            </div>
            <div className="landing-metrics" aria-label="Platform metrics">
              <article>
                <span>Signals generated</span>
                <strong>12.8K+</strong>
              </article>
              <article>
                <span>Strategies tested</span>
                <strong>3.4K+</strong>
              </article>
              <article>
                <span>Assets tracked</span>
                <strong>500+</strong>
              </article>
            </div>
          </div>

          <div className="landing-product-preview" aria-label="AI Stock Lab dashboard preview">
            <div className="preview-topbar">
              <span />
              <span />
              <span />
              <strong>Live workspace</strong>
            </div>
            <div className="preview-market-row">
              <article>
                <span>NVDA</span>
                <strong>$141.28</strong>
                <small>+2.84%</small>
              </article>
              <article>
                <span>MSFT</span>
                <strong>$468.72</strong>
                <small>+1.12%</small>
              </article>
              <article>
                <span>TSLA</span>
                <strong>$182.39</strong>
                <small className="is-negative">-0.64%</small>
              </article>
            </div>
            <div className="preview-chart-card">
              <div className="preview-card-header">
                <span>Strategy equity curve</span>
                <strong>+18.6%</strong>
              </div>
              <div className="preview-chart" aria-hidden="true">
                <span style={{ height: "34%" }} />
                <span style={{ height: "48%" }} />
                <span style={{ height: "42%" }} />
                <span style={{ height: "63%" }} />
                <span style={{ height: "56%" }} />
                <span style={{ height: "78%" }} />
                <span style={{ height: "68%" }} />
                <span style={{ height: "88%" }} />
              </div>
            </div>
            <div className="preview-insight-grid">
              <article className="preview-verdict">
                <span>AI debate verdict</span>
                <strong>Bullish</strong>
                <p>Momentum remains strong while risk stays inside the strategy guardrails.</p>
              </article>
              <article className="preview-json">
                <span>{"{"}</span>
                <code>{'"rule": "buy_dip"'}</code>
                <code>{'"risk": "medium"'}</code>
                <code>{'"confidence": 0.82'}</code>
                <span>{"}"}</span>
              </article>
            </div>
          </div>
        </section>

        <section className="landing-grid" aria-label="Feature highlights">
          <article className="landing-card">
            <h2>Multi-Agent Debate</h2>
            <p>
              Doua perspective AI opuse, un verdict final si un conviction score
              usor de integrat in strategii.
            </p>
          </article>
          <article className="landing-card">
            <h2>Deterministic Rules</h2>
            <p>
              Ideile in limbaj natural sunt convertite in JSON validat strict,
              gata de aprobare si executie in backtests.
            </p>
          </article>
          <article className="landing-card">
            <h2>Research Workspace</h2>
            <p>
              Urmareste active, construieste portofolii si itereaza rapid pe
              strategii intr-un singur workspace.
            </p>
          </article>
        </section>
      </main>
    </div>
  );
}
