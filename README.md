# AI Stock Lab

AI Stock Lab is an AI-assisted stock analysis and backtesting platform.

The application is built with a Next.js frontend, a Django REST Framework backend, a PostgreSQL database, JWT authentication, optional Google/GitHub OAuth login, and planned local Ollama integration for AI-assisted stock analysis workflows.

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

### 4. Open the application

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Django admin: `http://localhost:8000/admin`

### 5. Create an admin user

If needed, create a Django admin user:

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Importing Historical Market Data

The database tables and the supported asset list are created through Django migrations, but historical price data is not downloaded automatically.

On a new machine or with an empty database, run:

```bash
docker compose exec backend python manage.py import_historical_market_data
```

This imports daily OHLCV market data from `2010-01-01` until today for all supported symbols. The process may take some time.

To import data for a single symbol:

```bash
docker compose exec backend python manage.py import_historical_market_data --symbol AAPL
```

To update only missing prices after the latest stored date:

```bash
docker compose exec backend python manage.py update_market_data
```

To update one symbol:

```bash
docker compose exec backend python manage.py update_market_data --symbol AAPL
```

Recommended update strategy: run `update_market_data` as a scheduled job after market close, either daily or weekly.

Do not run the update command on every login, because it can slow down authentication and may hit external API limits.

---

## Implemented Features

### Backend and Database

- Django REST Framework backend.
- PostgreSQL database running through Docker.
- Django migrations for database schema management.
- Custom user model based on `AbstractUser`.
- JWT authentication using `djangorestframework-simplejwt`.
- Database tables for:
  - users/accounts
  - assets
  - asset prices
  - strategies
  - backtest runs
  - chat threads/messages
  - debate sessions/messages

### Authentication and Accounts

- User registration.
- Login with email or username.
- JWT-based authenticated requests.
- Frontend logout.
- Current user endpoint.
- Profile page accessible from the sidebar user menu.
- Username/profile update support.
- Password update support.
- Profile photo field/support.
- Admin user support through Django admin.
- Optional Google OAuth login.
- Optional GitHub OAuth login.

### Layout and Frontend

- Main landing page.
- Login and register forms.
- Persistent ChatGPT-like left sidebar after login.
- Sidebar sections:
  - Stocks
  - Backtesting
  - Debate history
  - Strategy history
  - User menu with Profile, Settings, and Log out
- Separate placeholder pages for:
  - Backtesting
  - Strategy chat
  - Debate mode
  - Settings
- Sidebar state persists after refresh.
- Placeholder chat history for Strategy and Debate sections.
- Right-click delete support for placeholder conversations.

### Market Data and Stocks

- Supported assets:
  - Stocks: `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `NVDA`, `TSLA`, `META`, `JPM`, `KO`, `WMT`
  - ETFs: `SPY`, `QQQ`, `GLD`
  - Commodity-related: `GC=F`
- `assets` table.
- `asset_prices` table.
- Unique constraint on `asset_id + date`.
- Historical import script starting from `2010-01-01`.
- Incremental update script for missing prices.
- Backend reads stored market data from PostgreSQL.
- Stocks UI lists all supported assets.
- Selecting an asset opens a details panel.
- Date range selector for price data.
- Details panel can be closed with a small `x` button.
- Dates are displayed as `YYYY/M/D`.
- OHLCV rows are prepared for future line charts and candlestick charts.

---

## API Endpoints

Important implemented endpoints:

```http
POST   /auth/register
POST   /auth/login
GET    /auth/me
GET    /users/me
PATCH  /users/me
DELETE /users/me
GET    /api/assets
GET    /api/assets/{symbol}/prices?start=YYYY-MM-DD&end=YYYY-MM-DD
```

More route details are available in:

```text
docs/api_routes.md
```

---

## Planned Features

### Market Data and Charting

- Candlestick chart component.
- Line chart for close/adjusted close prices.
- Better empty-state messages for missing prices.
- Scheduled market data update runner, for example using cron or Celery Beat.
- Optional admin UI for adding/removing supported assets.

### Backtesting

- Real backtesting engine.
- Strategy configuration form.
- Backtest execution endpoint.
- Results dashboard with:
  - total return
  - Sharpe ratio
  - maximum drawdown
  - win rate
  - equity curve
  - trade list
- Backtesting must use PostgreSQL price data, not external API calls.

### AI Features

- Real Strategy chat integration with an LLM.
- Strategy generation from chat.
- Debate mode with two AI agents discussing a selected stock.
- Real chat history persisted in the database instead of placeholder history.
- Ollama/OpenAI-compatible provider integration through the backend.

### User Experience

- Improved settings page.
- Improved profile photo upload UI.
- Loading skeletons for market data.
- Better error handling for OAuth failures.
- Responsive polish for small screens.

### Production Readiness

- Proper secrets management.
- Production Docker image builds.
- Static files handling for Django admin and media files.
- CI checks for backend tests and frontend type checking.
- Scheduled database backups.
- Rate-limit protection for authentication and external market data imports.

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