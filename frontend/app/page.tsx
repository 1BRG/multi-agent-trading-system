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
