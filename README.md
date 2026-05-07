
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

For local development, the PostgreSQL values from `.env.example` can remain unchanged.

Google and GitHub OAuth variables are optional. They only need to be configured if you want third-party login to work.

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

This imports daily OHLCV market data from `2010-01-01` until today for all supported symbols. The process may take some time.

To update only missing prices after the latest stored date:

```bash
docker compose exec backend python manage.py update_market_data
```

---

## Implemented Features

### AI Strategy Generation (The Strategy Manager)
The platform features a fully integrated **AI Strategy Manager** that translates qualitative natural-language trading ideas into strict, deterministic, mathematical JSON rulesets ready for backtesting.

- **How it works:** 
  1. Navigate to **Strategy** on the sidebar and click **+ New Chat**.
  2. Type a trading idea (e.g., *"Aggressive portfolio holding only the top 3 tech stocks, weighted by conviction, and rebalanced daily"*).
  3. The local LLM processes the prompt and outputs a strict JSON configuration.
  4. The Django backend parses the output through a strict validation "Firewall" to ensure no hallucinations break the backtesting engine.
- **The "Frozen Rule" & Approval Workflow:** To prevent Lookahead Bias during backtesting, the AI is only invoked during this brainstorming phase. The generated ruleset is saved permanently to the database as a `DRAFT`. The user must manually review the JSON rules and click **"Approve Strategy"** before the backtester is allowed to execute it.
- **Persistent Chat History:** Conversations with the Strategy Agent are saved in PostgreSQL, isolated by chat tabs, and auto-named based on your first prompt.
- **Audit Logging:** The raw text output from the LLM is securely logged in the database (`raw_llm_response`) for prompt debugging and safety auditing.

### Backend and Database

- Django REST Framework backend.
- PostgreSQL database running through Docker.
- Django migrations for database schema management.
- Custom user model based on `AbstractUser`.
- JWT authentication using `djangorestframework-simplejwt`.
- Database tables for:
  - users/accounts
  - assets & asset prices
  - user portfolios & portfolio holdings
  - strategies & backtest runs
  - chat threads/messages
  - debate sessions/messages

### Authentication and Accounts

- User registration.
- Login with email or username.
- JWT-based authenticated requests.
- Current user endpoint, profile page, and password updates.

### Layout and Frontend

- Persistent ChatGPT-like left sidebar after login.
- Real chat history persisted in the database for Strategy generation.
- Right-click delete support for conversations.
- Separate pages for Stocks, Portfolio, Backtesting, and Settings.

### Market Data and Stocks

- Supported assets: `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `NVDA`, `TSLA`, `META`, `JPM`, `KO`, `WMT`, `SPY`, `QQQ`, `GLD`, `GC=F`.
- Backend reads stored market data directly from PostgreSQL to prevent live-API calls during backtesting.
- Stocks UI lists all supported assets with date range selectors.

### Portfolios

- Authenticated users can create, update, list and delete their own private portfolios.
- Portfolio holdings are linked to supported assets from the `assets` table.

---

## API Endpoints

Important implemented endpoints:

```http
POST   /auth/register
POST   /auth/login
GET    /api/assets
GET    /api/assets/{symbol}/prices?start=YYYY-MM-DD&end=YYYY-MM-DD
GET    /portfolios
POST   /portfolios
POST   /strategies/generate_ai       (Generates AI JSON ruleset)
PATCH  /strategies/{id}/approve      (Approves a Draft strategy for backtesting)
```

More route details are available in:
```text
docs/api_routes.md
```

---

## Planned Features

### Backtesting Engine
- Real backtesting engine powered by `vectorbt`.
- Backtest execution endpoint consuming the approved `Strategy.config` JSON.
- Results dashboard displaying total return, Sharpe ratio, maximum drawdown, win rate, equity curve, and trade list.
- Strict enforcement of local PostgreSQL price data usage (no external API calls during a run).

### Debate Mode
- Debate mode with two AI agents (Bull vs. Bear) discussing a selected stock.
- A "Judge" LLM that outputs Conviction scores to be consumed by the Strategy Manager.

### Market Data and Charting
- Candlestick chart component.
- Scheduled market data update runner (e.g., cron or Celery Beat).

### Production Readiness
- Production Docker image builds and proper secrets management.
- Static files handling for Django admin and media files.

---

## Testing

Run backend tests:

```bash
docker compose exec backend python manage.py test
```

Run Django system checks:

```bash
docker compose exec backend python manage.py check
```

Run frontend type checking:

```bash
docker compose exec frontend npx tsc --noEmit
```

---

## Documentation

- Database schema: `docs/database_schema.md`
- API routes: `docs/api_routes.md`
- Architecture notes: `docs/architecture.md`
```
