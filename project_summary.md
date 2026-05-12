# LLM-Powered Trading System — Project Summary

## What the project does

Two independent modules:

**Module A — Stock Rater:** Given a ticker, a Bull and Bear LLM debate its merits, a Judge LLM renders a verdict (BUY / SELL / HOLD) with a conviction score. Human approves before any action.

**Module B — Portfolio Backtester:** A portfolio allocation strategy is expressed as a deterministic ruleset that defines how capital is distributed across asset classes (e.g. tech stocks, commodities, ETFs) and under what conditions the allocation shifts. The strategy can be authored in two ways: **(1)** a human describes their idea in natural language and an LLM converts it into deterministic rules, or **(2)** an LLM proposes the entire strategy — allocation idea and rules — from scratch. Either way, the result is a deterministic ruleset that is then backtested on historical price data to answer: *"If I had followed this strategy for the past N years, how much money would I have made?"*

**Modules A and B are fully independent.** Module A rates individual stocks using LLM debates. Module B tests allocation strategies over historical data using only price data and deterministic rules — it does not consume signals from Module A.

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

### Person 3 — Individual Stock Rater (Module A)
- The debate system: Bull opens → Bear opens → Bear rebuts → Bull rebuts → Judge decides
- Output per stock: `{ action, conviction, bull_thesis, bear_thesis, judge_reasoning, timestamp }`
- This output gets written to the DB for the user to review
- Keep structured JSON outputs — this is load-bearing
- Optional: feed real news headlines or an earnings summary into agent prompts before debate starts

### Person 4 — Strategy Manager (Module B)
- LLM proposes a portfolio allocation strategy in natural language, which is then hardcoded into a deterministic ruleset before backtesting
- The strategy operates over **asset classes or groups** (e.g. tech stocks, commodities, ETFs), not individual stock picks
- See strategy design constraints below

### Person 5 — Backtester (Module B)
- Takes the deterministic ruleset from Person 4
- Runs it over historical price data for representative assets in each class
- See backtesting constraints below

---

## Data flow

```
MODULE A (Stock Rater) — standalone

  User input (ticker)
          │
          ▼
  Person 3: Stock Rater
    → Bull/Bear debate → Judge verdict
    → output: { ticker, action, conviction, reasoning, timestamp }
          │
          ▼
  Person 1: DB stores signal
  Person 2: Frontend displays debate + lets user approve/reject


MODULE B (Portfolio Backtester) — standalone

  Option A: User describes strategy idea in natural language
  Option B: User asks the LLM to propose a strategy from scratch
          │
          ▼
  Person 4: Strategy Manager
    → Option A: LLM translates user's idea into deterministic rules
    → Option B: LLM generates both the allocation idea AND the rules
    → output: deterministic ruleset (asset class weights, rebalance conditions)
          │
          ▼
  Person 5: Backtester
    → replays allocation rules over historical price data
    → outputs: P&L, Sharpe, max drawdown, equity curve
          │
          ▼
  Person 2: Frontend displays backtest results
  Person 1: DB stores everything
```

---

## Strategy design (Person 4)

The Strategy Manager supports two modes of strategy creation. In both cases, the LLM does not run during backtesting — it runs once to generate the rules.

### Mode 1: Human-authored strategy

The user describes their strategy idea in natural language. The LLM's job is to translate it into a structured, deterministic ruleset.

Examples of what the user might type:

> "Hold 20% tech stocks, 50% commodities, 30% ETFs. Rebalance monthly."

> "Hold 20% tech, 50% commodities, 30% ETFs. When a war starts, shift commodities to 80% and reduce tech to 5% and ETFs to 15%."

> "60% S&P 500 ETF, 40% bonds. When the VIX crosses above 30, flip to 80% bonds and 20% S&P 500."

> "Equal weight across 5 sector ETFs. Rebalance quarterly."

### Mode 2: LLM-generated strategy

The user asks the LLM to propose a strategy from scratch. The LLM generates both the allocation idea and the deterministic rules. The user can optionally provide constraints or goals.

Examples of what the user might type:

> "Generate a defensive portfolio strategy for someone worried about a recession."

> "Propose a growth-oriented allocation using tech and emerging market ETFs."

> "Come up with a strategy that would have performed well during the 2020 COVID crash."

The LLM responds with a complete strategy (name, description, allocation weights, conditional rules) in the same JSON format as Mode 1. The user reviews it before backtesting — they can approve, modify, or reject it.

### What the deterministic ruleset looks like

The LLM output should be a JSON config the backtester can mechanically execute:

```json
{
  "strategy_name": "War-Adjusted Commodity Tilt",
  "description": "Base allocation across tech/commodities/ETFs with a conditional shift into commodities during geopolitical crises.",
  "base_allocation": {
    "tech": 0.20,
    "commodities": 0.50,
    "etf": 0.30
  },
  "rebalance_frequency": "monthly",
  "conditional_rules": [
    {
      "trigger": "geopolitical_crisis",
      "allocation_override": {
        "tech": 0.05,
        "commodities": 0.80,
        "etf": 0.15
      }
    }
  ]
}
```

### Strategy primitives to expose

- **Asset class weights** — percentage allocation to each asset class (tech, commodities, ETFs, bonds, etc.)
- **Representative tickers** — which specific ticker represents each asset class for price data (e.g., QQQ for tech, GLD for commodities, SPY for broad market)
- **Rebalancing frequency** — daily, weekly, monthly, quarterly
- **Conditional rules** — triggers that shift the allocation (volatility spikes, drawdown thresholds, or flagged macro events)
- **Position sizing** — equal weight across classes, or custom weights

### Handling conditional triggers in backtests

Some triggers (like "when a war starts") are not directly observable from price data. Two approaches:

1. **Price-derived proxies:** Use observable market signals as stand-ins. For example, "geopolitical crisis" ≈ VIX > 30, or gold price spike > 10% in a month, or a specific commodity index crossing a threshold. The LLM should propose the proxy when generating rules.
2. **Manual event flags:** Maintain a simple table of historical events with date ranges (e.g., `{ event: "Russia-Ukraine War", start: "2022-02-24", end: "2023-12-31" }`). The backtester checks if the current date falls within an event window.

Approach 1 is more rigorous for backtesting. Approach 2 is simpler to implement and good enough for a demo.

---

## Backtesting constraints (Person 5)

### What the backtester actually does

At its core, the backtester is a simulation loop:

1. Start with initial cash (e.g. $10,000)
2. On day 1, buy assets according to the base allocation weights
3. On each rebalance date, check if any conditional rules fire; if so, use the override allocation
4. Sell/buy to rebalance the portfolio to the target weights
5. Track the total portfolio value (cash + holdings) every day → this is the equity curve
6. At the end, calculate how much money was made or lost

### Minimising lookahead bias

**Rule: at rebalance date T, only use data available before T.**

Concretely:
- Price data: use closing prices of day T-1 to make decisions on day T. Never use T's close to enter at T's open.
- Rebalancing: if you rebalance on the first trading day of each month, your input features must be from the last day of the previous month or earlier.

### Minimising overfitting

- **No parameter search on the test set.** If the strategy has tunable parameters, fix them before looking at results.
- **Walk-forward validation** over a single train/test split:
  - Split your data: train (years 1–3), validation (year 4), test (year 5)
  - Develop and tune on train+validation only
  - Report test period results as the honest number
- **Keep the strategy simple.** The more degrees of freedom the strategy has, the more likely a good backtest result is noise.
- **Benchmark against SPY.** Alpha = your strategy return minus SPY return. A strategy that returns 12% when SPY returns 14% is not generating alpha.

### Metrics to report
- Total P&L (dollar amount gained/lost)
- Total return (%) vs benchmark
- Annualised return vs benchmark
- Sharpe ratio (use daily returns, annualise)
- Maximum drawdown
- Calmar ratio (return / max drawdown)
- Equity curve chart

### Stack
`vectorbt` is the fastest to get running for this use case. `backtrader` is more flexible but has a steeper learning curve. Recommend vectorbt for the time constraint.

---

## Interface contracts (agree these early)

Person 4 → Person 5 (Strategy → Backtester):
```json
{
  "strategy_id": "s_001",
  "strategy_name": "Commodity Tilt",
  "base_allocation": {
    "QQQ": 0.20,
    "GLD": 0.50,
    "SPY": 0.30
  },
  "rebalance_frequency": "monthly",
  "conditional_rules": [
    {
      "trigger_type": "vix_above",
      "trigger_value": 30,
      "allocation_override": {
        "QQQ": 0.05,
        "GLD": 0.80,
        "SPY": 0.15
      }
    }
  ]
}
```

Person 5 → Frontend (Backtest Results):
```json
{
  "strategy_id": "s_001",
  "start_date": "2019-01-01",
  "end_date": "2024-12-31",
  "initial_cash": 10000,
  "final_equity": 14523.80,
  "total_pnl": 4523.80,
  "total_return_pct": 45.24,
  "annualized_return_pct": 7.73,
  "benchmark_return_pct": 52.10,
  "sharpe_ratio": 0.65,
  "max_drawdown_pct": -18.30,
  "calmar_ratio": 0.42,
  "equity_curve": [
    { "date": "2019-01-02", "equity": 10000.00 },
    { "date": "2019-01-03", "equity": 10045.20 }
  ],
  "trades": [
    {
      "date": "2019-02-01",
      "action": "REBALANCE",
      "reason": "Monthly rebalance — no conditional triggers active",
      "allocations": { "QQQ": 0.20, "GLD": 0.50, "SPY": 0.30 }
    }
  ]
}
```

---

## What to be honest about in the report

- "Alpha generation" is the hypothesis; the backtest result is the answer
- Backtest results on a single historical period are not proof of future performance
- Conditional triggers based on manually flagged events (like "war starts") are not predictive — the backtest only shows what would have happened *if you had known the event was occurring*
- Transaction costs and slippage are not modelled (unless you add them), so real returns would be lower
- The two modules (Stock Rater and Portfolio Backtester) are independent demonstrations of LLM-assisted trading tools, not a single integrated system
