# Architecture

## Overview

AI Stock Lab is a Docker-based web application with:

- Next.js frontend on port `3000`.
- Django REST Framework backend on port `8000`.
- PostgreSQL database on port `5432`.
- Optional local Ollama service on port `11434`.

The current implementation uses Django models and Django migrations for schema management. FastAPI, SQLAlchemy and Alembic are no longer part of the active backend.

## Runtime Services

| Service | Technology | Purpose |
| --- | --- | --- |
| `frontend` | Next.js / React | User interface, auth screens, sidebar workspace, Stocks UI. |
| `backend` | Django REST Framework | Auth, CRUD APIs, market data APIs, domain APIs. |
| `postgres` | PostgreSQL 15 | Stores users, assets, prices, portfolios, strategies, backtests and conversations. |
| `ollama` | Ollama | Actively powers the local LLM workflows (Llama3) for the Debate System and Strategy Generation. |

## Backend

The backend is organized into Django apps:

- `accounts`: custom user model, register/login, JWT auth, profile updates, password changes, Google/GitHub OAuth callbacks.
- `market`: assets and daily OHLCV market prices.
- `portfolios`: user portfolios and holdings linked to supported assets.
- `strategies`: user-owned or public strategy definitions.
- `backtests`: backtest run records and JSON result storage.
- `conversations`: strategy chats and debate sessions/messages.

Authentication uses JWT bearer tokens. Login accepts an `identifier` field, which can be either username or email.

## Market Data Flow

Market data is stored in PostgreSQL.

The active flow is:

1. Django migrations create the `assets` and `asset_prices` tables.
2. A data migration seeds the supported asset list.
3. `import_historical_market_data` downloads historical daily OHLCV prices from `2010-01-01` until today.
4. `update_market_data` downloads only missing rows after the latest stored date for each asset.
5. API endpoints read prices from PostgreSQL.
6. Future backtests should read local database prices and should not call external market APIs during a run.

## Frontend

The frontend talks to the backend through `NEXT_PUBLIC_API_BASE_URL`.

Implemented workspace areas:

- Landing page.
- Login/register pages.
- Auth callback pages for Google/GitHub OAuth.
- Logged-in dashboard with persistent left sidebar.
- Stocks page with asset list and selected-asset price details.
- Portfolio page for creating user portfolios and managing holdings.
- Interactive interface for Strategy formulation and historical chat memory.
- Fully implemented Debate Mode UI showing agent transcripts and conviction ring charts.
- Backtesting page for running approved strategies on stored OHLCV data and reviewing metrics, equity curve previews and trades.
- Placeholder page for Settings.
Profile page embedded through the sidebar user menu.

The sidebar state is persisted after refresh. The Stocks page keeps the selected asset, but the default date range is the last month to avoid loading all historical prices by default.

## API Surface

The backend exposes:

- Explicit auth endpoints under `/auth/...`.
- Explicit market data endpoints under `/api/assets...`.
- DRF router endpoints for assets, asset prices, portfolios, portfolio holdings, strategies, backtests, chats, debate sessions and admin user management.

See `docs/api_routes.md` for route details.

## Pending Architecture Work

- Multi-asset backtesting engine and richer strategy allocation rules.
- Scheduled market data update runner, for example cron or Celery Beat.
- Production Docker images and production static/media handling.
