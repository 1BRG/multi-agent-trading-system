# API Routes

## Overview

This document tracks the current Django REST API route surface.

The frontend should use `NEXT_PUBLIC_API_BASE_URL` as the backend base URL. In local Docker development this is usually `http://localhost:8000`.

## Authentication

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | No | Creates a new user with `username`, `email`, `password`, optional `full_name`; returns JWT tokens and the user. |
| `POST` | `/auth/login` | No | Validates `identifier` plus `password`; `identifier` can be username or email. Also accepts `email` temporarily for compatibility. |
| `POST` | `/auth/social/{provider}/start` | No | Starts OAuth login for `google` or `github`; returns an authorization URL and state when provider credentials are configured. |
| `POST` | `/auth/social/{provider}/callback` | No | Exchanges an OAuth authorization code for app JWT tokens. |
| `GET` | `/auth/me` | Bearer token | Returns the currently authenticated user. |

### Login payload

```json
{
  "identifier": "email_or_username",
  "password": "password"
}
```

### Register payload

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "password123",
  "full_name": "Admin User"
}
```

### Social auth providers

Supported providers:

- `google`
- `github`

Required environment variables are documented in `.env.example`.

## Users

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/users/me` | Bearer token | Returns the current user's profile. |
| `PATCH` | `/users/me` | Bearer token | Updates current user's `username`, `email`, `full_name` and/or `profile_photo`. |
| `PATCH` | `/users/me/password` | Bearer token | Changes the current user's password. |
| `DELETE` | `/users/me` | Bearer token | Deactivates the current user's account. |
| `GET` | `/users` | Admin bearer token | Lists users. |
| `POST` | `/users` | Admin bearer token | Creates a user as admin. |
| `GET` | `/users/{user_id}` | Admin bearer token | Returns a user by id. |
| `PATCH` | `/users/{user_id}` | Admin bearer token | Updates a user as admin. |
| `DELETE` | `/users/{user_id}` | Admin bearer token | Deactivates a user as admin. |

Profile photo upload should be sent as multipart form data.

## Market Data

Market prices are served from PostgreSQL. The API does not call external market data providers during normal reads.

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/assets` | No | Lists active assets. Each asset includes `latest_price` when price data exists. |
| `GET` | `/api/assets/{symbol}/prices?start=YYYY-MM-DD&end=YYYY-MM-DD` | No | Returns daily OHLCV price rows from PostgreSQL for charting and backtests. |

Example:

```http
GET /api/assets/AAPL/prices?start=2024-01-01&end=2024-01-31
```

Response shape:

```json
{
  "asset": {
    "id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "asset_type": "stock",
    "currency": "USD"
  },
  "prices": [
    {
      "asset_id": 1,
      "symbol": "AAPL",
      "date": "2024-01-02",
      "open": "187.149994",
      "high": "188.440002",
      "low": "183.889999",
      "close": "185.639999",
      "adjusted_close": "183.731293",
      "volume": 82488700,
      "source": "yahoo"
    }
  ]
}
```

The frontend Stocks page uses the last month as its default selected date range to avoid loading all historical prices by default.

The backend also applies safety limits:

- If `start` or `end` is missing, the API defaults to the latest one-month window.
- A single request cannot exceed `5 years`.
- Asset symbols are validated before querying.
- Price reads use Django ORM filters, not raw SQL.

## Router Endpoints

These endpoints are registered through DRF's router without trailing slash.

| Prefix | Auth | Description |
| --- | --- | --- |
| `/assets` | Read public, write admin | Asset CRUD for available symbols. |
| `/asset-prices` | Read public, write admin | Historical OHLCV prices, filterable by `symbol`. |
| `/strategies` | Bearer token | User-owned strategies plus public strategies. |
| `/backtests` | Bearer token | Current user's backtest runs and JSON results. |
| `/chats` | Bearer token | Current user's chat threads. |
| `/chat-messages` | Bearer token | Messages scoped to current user's chats. |
| `/debates` | Bearer token | Current user's AI debate sessions. |
| `/debate-messages` | Bearer token | Messages scoped to current user's debates. |
| `/users` | Admin bearer token | Admin user management. |

## Utility Routes

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Returns `{ "status": "ok" }`. |
| `GET` | `/admin/` | Django admin login | Django admin interface. |

## Notes

- Historical prices are imported by Django management commands.
- Backtesting should use stored PostgreSQL prices from `asset_prices`.
- External market APIs should be used only by import/update jobs, not by normal API reads or backtest runs.
