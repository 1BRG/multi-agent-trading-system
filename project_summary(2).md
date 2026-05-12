# LLM-Powered Trading System — Project Summary

## What the project does

Two independent modules:

**Module A — Stock Rater:** Given a ticker, a Bull and Bear LLM debate its merits, a Judge LLM renders a verdict (BUY / SELL / HOLD) with a conviction score. Human approves before any action.

**Module B — Portfolio Manager:** An LLM proposes a portfolio strategy over a universe of stocks using signals from Module A. The strategy is expressed as a deterministic ruleset, then backtested on historical data.

The claim of alpha generation is a hypothesis to test, not a guarantee. The backtest either supports it or it doesn't.

---

## Team split

### Person 1 — Database & Auth
- User accounts, authentication (JWT or session-based)
- Storage: user portfolios, saved strategies, backtest results, stock signal history
- **Critical:** price data must be stored with ingestion timestamps, not just dates. Point-in-time integrity matters for the backtester.
- Stack: PostgreSQL, SQLAlchemy or Prisma depending on backend language

### Person 2 — Frontend
- Three views: Stock Rater (debate output + human approval), Portfolio Dashboard (current allocations), Backtest Results (performance charts)
- Backtest results view is the most important to get right — needs equity curve, drawdown chart, and benchmark comparison (not just final return)
- Can be built mostly independently once the API contracts are agreed

### Person 3 — Individual Stock Rater
- The debate system: Bull opens → Bear opens → Bear rebuts → Bull rebuts → Judge decides
- Output per stock: `{ action, conviction, bull_thesis, bear_thesis, judge_reasoning, timestamp }`
- This output gets written to the DB so Person 4 can aggregate across stocks
- Keep structured JSON outputs — this is load-bearing
- Optional: feed real news headlines or an earnings summary into agent prompts before debate starts

### Person 4 — Strategy Manager
- Takes a universe of stock signals from Person 3's DB table
- LLM proposes a portfolio strategy in natural language, which is then hardcoded into a deterministic ruleset before backtesting
- See strategy design constraints below

### Person 5 — Backtester
- Takes the deterministic ruleset from Person 4
- Runs it over historical price data with strict temporal discipline
- See backtesting constraints below

---

## Data flow

```
User input (ticker list)
        │
        ▼
Person 3: Stock Rater
  → signals: { ticker, action, conviction, timestamp }
        │
        ▼ (stored in DB)
        │
Person 4: Strategy Manager
  → reads signals, LLM proposes strategy
  → strategy expressed as deterministic rules
        │
        ▼
Person 5: Backtester
  → replays rules over historical data
  → outputs: Sharpe, alpha, max drawdown, equity curve
        │
        ▼
Person 2: Frontend displays results
Person 1: DB stores everything
```

---

## Strategy design (Person 4)

The LLM's job is to propose the strategy structure, not to optimize parameters. Example of what this looks like:

> "Each week, rank all stocks by conviction score. Go long the top 5, equal-weighted. Exit any position that drops to HOLD or SELL. Maximum 20% in any single sector."

This becomes a hardcoded ruleset the backtester can replay. The LLM is not re-run during backtesting — it runs once to generate the rules.

**Why this matters:** if the LLM were run on historical data to generate signals that are then tested on the same historical data, that is a form of overfitting. The strategy structure must be fixed before touching the test data.

Reasonable strategy primitives to expose:
- Ranking metric (conviction score, or conviction × analyst score)
- Portfolio size (top N stocks)
- Rebalancing frequency (weekly, monthly)
- Position sizing (equal weight, conviction-weighted, volatility-scaled)
- Exit rules (signal flip, stop-loss on price)
- Sector concentration cap

---

## Backtesting constraints (Person 5)

### Minimising lookahead bias

**Rule: at rebalance date T, only use data available before T.**

Concretely:
- Price data: use closing prices of day T-1 to make decisions on day T. Never use T's close to enter at T's open.
- Earnings data: use announcement date, not fiscal period end. A Q1 report released on May 10 is not available on April 30.
- Signals from Person 3: each signal has a timestamp. A signal generated on May 10 cannot be used in a backtest decision on May 9.
- Rebalancing: if you rebalance on the first trading day of each month, your input features must be from the last day of the previous month or earlier.

**Unavoidable limitation to acknowledge:** The LLMs themselves were trained on data that includes the backtest period. A model trained through 2024 has implicitly "seen" 2022 market events. This cannot be fully eliminated — it should be stated as a limitation in the report.

### Minimising overfitting

- **No parameter search on the test set.** If the strategy has tunable parameters (e.g., top N stocks), fix them before looking at results. If you must tune, use a validation set, keep a held-out test set untouched until final evaluation.
- **Walk-forward validation** over a single train/test split:
  - Split your data: train (years 1–3), validation (year 4), test (year 5)
  - Develop and tune on train+validation only
  - Report test period results as the honest number
- **Keep the strategy simple.** The more degrees of freedom the strategy has, the more likely a good backtest result is noise. A 2-rule strategy that works is more credible than a 10-rule strategy.
- **Benchmark against SPY.** Alpha = your strategy return minus SPY return. A strategy that returns 12% when SPY returns 14% is not generating alpha.

### Metrics to report
- Annualised return vs benchmark
- Sharpe ratio (use daily returns, annualise)
- Maximum drawdown
- Calmar ratio (return / max drawdown)
- Win rate per trade (optional)

### Stack
`vectorbt` is the fastest to get running for this use case. `backtrader` is more flexible but has a steeper learning curve. Recommend vectorbt for the time constraint.

---

## Interface contracts (agree these early)

Person 3 → Person 4:
```json
{
  "ticker": "NVDA",
  "action": "BUY",
  "conviction": 0.78,
  "timestamp": "2024-11-01T14:32:00Z"
}
```

Person 4 → Person 5:
```json
{
  "strategy_id": "s_001",
  "rebalance_frequency": "weekly",
  "ranking_metric": "conviction",
  "portfolio_size": 5,
  "sizing": "equal_weight",
  "sector_cap_pct": 20,
  "exit_on_signal_flip": true
}
```

These two JSON shapes need to be agreed by week 1. Everything else can be built in parallel.

---

## What to be honest about in the report

- LLM training data lookahead is unavoidable and should be stated
- "Alpha generation" is the hypothesis; the backtest result is the answer
- The debate system produces qualitative reasoning, not quantitative forecasts — the connection between conviction score and actual returns is an assumption that should be tested
- Backtest results on a single historical period are not proof of future performance
