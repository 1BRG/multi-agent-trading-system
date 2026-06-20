# AI Stock Lab

AI Stock Lab is an AI-assisted stock analysis and backtesting platform.

The application is built with a Next.js frontend, a Django REST Framework backend, a PostgreSQL database, JWT authentication, optional Google/GitHub OAuth login, and local Ollama integration for AI-assisted stock analysis workflows.

---

## Local Setup

### 1. Copy the environment template

```bash
cp .env.example .env
```

### 2. Configure environment variables

Open `.env` and set at least:

```env
DJANGO_SECRET_KEY=your-local-django-secret
JWT_SECRET_KEY=your-local-jwt-secret
```

For local development, the PostgreSQL values from `.env.example` can remain unchanged. Google and GitHub OAuth variables are optional.

### 3. Start the application with Docker

```bash
docker compose up --build
```

The backend container automatically installs dependencies, runs Django migrations, and starts the API server.

### 4. Download the Local AI Model (Ollama)
The application uses a local LLM via Docker. To download the Llama3 model into your running Ollama container, open a new terminal window and run:
```bash
docker exec -it ai-stock-lab-ollama ollama pull llama3
```
*(Wait for the download to say "success" before trying to use the AI in the app).*

### 5. Open the application

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Django admin: `http://localhost:8000/admin`

---

## Importing Historical Market Data

The database tables and the supported asset list are created through Django migrations, but historical price data is not downloaded automatically.

On a new machine or with an empty database, run:

```bash
docker compose exec backend python manage.py import_historical_market_data
```

This imports daily OHLCV market data from `2010-01-01` until today for all supported symbols.

To update only missing prices after the latest stored date:

```bash
docker compose exec backend python manage.py update_market_data
```

---

## Implemented Features

### 1. AI Stock Rater & Debate System
A fully integrated multi-agent LLM debate system to evaluate individual stocks.
- **The Debate Flow:** A "Bull" LLM and "Bear" LLM engage in a multi-round debate over a specific ticker (Opening → Rebuttal).
- **The Verdict:** An impartial "Judge" LLM reviews the debate transcript and outputs a rigid JSON verdict (`BUY/SELL/HOLD`) alongside a mathematical **Conviction Score** (0.0 to 1.0).
- **Data Persistence:** The qualitative debate and the quantitative conviction score are saved to the database to be consumed by the Strategy Manager.

### 2. AI Strategy Generation (Portfolio Construction)
An interactive AI Strategy Manager that translates qualitative natural-language trading ideas into strict, deterministic, mathematical JSON rulesets ready for backtesting.
- **Context-Aware Memory:** The Strategy LLM retains chat history. Users can iteratively refine their strategies (e.g., *"Change the portfolio size to 8 and make it equal weighted"*) without the AI losing previous context.
- **The Factor Bridge:** The AI configures a `min_conviction_score` parameter, acting as a direct bridge to the Debate System's outputs.
- **Strict Validation Firewall:** The Django backend strictly validates the LLM's output against a rigid schema. Any AI hallucinations (e.g., inventing a "yearly" rebalance frequency) are blocked and rejected before they can break the backtesting engine.
- **The "Frozen Rule" & Approval Workflow:** To prevent Lookahead Bias, the generated ruleset is saved as a `DRAFT`. The user must manually review the JSON rules and click **"Approve Strategy"** before the backtester is allowed to execute it.

### 3. Backend and Database Architecture
- Django REST Framework backend with PostgreSQL database running through Docker.
- Custom user model, JWT authentication, and user portfolios.
- Backend reads stored market data directly from PostgreSQL to prevent live-API calls during backtesting (ensuring temporal accuracy and preventing lookahead bias).

### 4. Layout and Frontend
- Persistent sidebar with real chat history persisted in PostgreSQL.
- Dedicated workspaces for Stocks, Portfolios, Debates, Strategy Formulation, and Backtesting.
- Stocks UI listing all supported assets (`AAPL`, `MSFT`, `SPY`, `GLD`, etc.) with date range selectors.

### 5. Portfolio Tracking and Backtesting
- Portfolio workspace for creating portfolios, adding holdings, resolving historical buy prices, and viewing dynamic position weights.
- Backtesting workspace for approved strategies using stored PostgreSQL OHLCV data.
- Backtest results include final equity, total return, annualized return, benchmark return, max drawdown, volatility, Sharpe ratio, equity curve and trade history.

---

## API Endpoints

Important implemented endpoints:

```http
POST   /auth/register
POST   /auth/login
GET    /api/assets
GET    /api/assets/{symbol}/prices?start=YYYY-MM-DD&end=YYYY-MM-DD
GET    /portfolios
POST   /debates/run_debate           (Executes the 5-round Bull/Bear/Judge workflow)
POST   /strategies/generate_ai       (Generates AI JSON ruleset with chat history)
PATCH  /strategies/{id}/approve      (Approves a Draft strategy for backtesting)
POST   /backtests                    (Runs an approved strategy on stored OHLCV data)
```

---

## Planned Features (Future Work)

### 1. Backtesting Engine Upgrade
- Optional future migration from the current custom deterministic engine to `vectorbt`.
- Multi-asset portfolio allocation backtests consuming the full approved `Strategy.config` JSON and `StockSignal` conviction scores.
- Strict enforcement of local PostgreSQL price data usage for all future multi-asset strategies.

### 2. Institutional Trading Metrics
To scale the backtester to production hedge-fund standards, future iterations will include:
- **Transaction Costs & Slippage:** Simulating real-world broker fees on high-frequency rebalances.
- **Advanced Exit Logic:** Hardcoded Stop-Loss and Take-Profit limits independent of signal flips.
- **Long/Short Capabilities:** Allowing the strategy JSON to dictate short-selling the lowest conviction stocks.

---

## Testing & Checks

Run backend tests:
```bash
docker compose exec backend python manage.py test accounts market strategies backtests conversations portfolios
```

Run Django system checks:
```bash
docker compose exec backend python manage.py check
```

Run frontend type checking:
```bash
docker compose exec frontend npx tsc --noEmit
```


## Documentation

- Database schema: `docs/database_schema.md`
- API routes: `docs/api_routes.md`
- Architecture notes: `docs/architecture.md`

---

## MDS Grading Evidence

The repository evidence for the MDS laboratory grading rubric is tracked in:

- Grading checklist: `docs/grading_evidence.md`
- Architecture and workflow diagrams: `docs/diagrams.md`
- AI development usage report: `docs/ai_usage_report.md`
- Portfolio bug report handled on the grading branch: `docs/bug_report_portfolio.md`
- Product backlog, user stories, and issues: [Linear workspace](https://linear.app/multi-agent-trading-system/team/MUL/overview)
- Demo video: [YouTube demo](https://www.youtube.com/watch?v=88_VAOaR9uM)

Note: Linear may require workspace access.
