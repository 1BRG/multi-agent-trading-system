# Database Schema

## Overview

The database is PostgreSQL and the schema is managed by Django models plus Django migrations.

The active backend is Django REST Framework. FastAPI, SQLAlchemy and Alembic are not used by the current implementation.

Historical market prices are stored in PostgreSQL and populated through Django management commands.

## Users

Table: `accounts_user`

Custom user model based on Django `AbstractUser`.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal user id. |
| `username` | varchar(150) | unique, case-insensitive unique constraint | Username and login identifier. |
| `email` | varchar(254) | unique, case-insensitive unique constraint | Normalized lowercase email address. |
| `password` | varchar(128) | not null | Django-managed password hash. |
| `full_name` | varchar(255) | blank allowed | Optional display name. |
| `profile_photo` | varchar(100) | blank allowed | Uploaded profile photo path under Django media storage. |
| `role` | varchar(50) | `user` / `admin` | Application role. |
| `is_active` | boolean | not null | Deactivated users cannot authenticate. |
| `is_staff` | boolean | not null | Django admin access flag. |
| `is_superuser` | boolean | not null | Django superuser flag. |
| `last_login` | timestamp with timezone | nullable | Last successful login timestamp. |
| `date_joined` | timestamp with timezone | not null | Django account creation timestamp. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

Constraints:

- `accounts_user_email_ci_unique`
- `accounts_user_username_ci_unique`

Login accepts either username or email through the `identifier` field.

## Market Data

Tables:

- `assets`
- `asset_prices`

Supported assets seeded by migration:

- Stocks: `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `NVDA`, `TSLA`, `META`, `JPM`, `KO`, `WMT`
- ETFs: `SPY`, `QQQ`, `GLD`
- Commodity-related: `GC=F`

Historical prices are downloaded by Django management commands:

```bash
python manage.py import_historical_market_data
python manage.py update_market_data
```

The importer uses `2010-01-01` as the default historical start date. The update command only downloads missing dates after the latest stored row for each asset.

### `assets`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal asset id. |
| `symbol` | varchar(24) | unique | Provider symbol, normalized uppercase. |
| `name` | varchar(255) | not null | Human-readable asset name. |
| `asset_type` | varchar(20) | `stock` / `etf` / `commodity` | Asset category. |
| `sector` | varchar(100) | blank allowed | Sector for equities when available. |
| `exchange` | varchar(50) | blank allowed | Listing exchange or source venue. |
| `currency` | varchar(10) | default `USD` | Quote currency. |
| `is_active` | boolean | not null | Whether the asset is enabled in the app. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

### `asset_prices`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal price row id. |
| `asset_id` | integer | FK to `assets`, unique with `date` | Asset being priced. |
| `date` | date | unique with `asset_id`, indexed | Trading date. |
| `open` | decimal(18, 6) | not null | Daily open. |
| `high` | decimal(18, 6) | not null | Daily high. |
| `low` | decimal(18, 6) | not null | Daily low. |
| `close` | decimal(18, 6) | not null | Daily close. |
| `adjusted_close` | decimal(18, 6) | nullable | Adjusted daily close. |
| `volume` | bigint | default `0` | Daily volume. |
| `source` | varchar(50) | default `yahoo` | Data provider/source label. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

Constraints and indexes:

- Unique constraint: `asset_prices_asset_date_unique` on `(asset_id, date)`.
- Index: `asset_prices_asset_date_idx` on `(asset_id, date)`.

## Portfolios

Tables:

- `portfolios`
- `portfolio_holdings`

Portfolios are private to the authenticated user that owns them. Holdings reference rows from `assets`, so portfolio data can later be joined with locally stored prices for dashboards and backtests.

### `portfolios`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal portfolio id. |
| `user_id` | integer | FK to `accounts_user`, unique with `name` | Portfolio owner. |
| `name` | varchar(255) | unique with `user_id` | Portfolio name. |
| `cash` | decimal(14, 2) | default `0`, non-negative | Reserved for future cash tracking. The current portfolio UI derives value from holdings, not this column. |
| `base_currency` | varchar(10) | default `USD` | Portfolio reporting currency. |
| `description` | text | blank allowed | Optional description. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

Constraints and indexes:

- Unique constraint: `portfolio_user_name_unique` on `(user_id, name)`.
- Check constraint: `portfolio_cash_non_negative` keeps `cash >= 0`.
- Index: `portfolio_user_name_idx` on `(user_id, name)`.

### `portfolio_holdings`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal holding id. |
| `portfolio_id` | integer | FK to `portfolios`, unique with `asset_id` | Parent portfolio. |
| `asset_id` | integer | FK to `assets`, unique with `portfolio_id` | Held asset. |
| `target_weight` | decimal(6, 4) | between `0` and `1`, default `0` | Legacy/planned target allocation field. The current UI calculates investment weight dynamically from cost basis. |
| `quantity` | decimal(20, 8) | nullable, non-negative | Optional tracked units/shares. |
| `average_cost` | decimal(18, 6) | nullable, non-negative | Average entry cost. For market price modes this is resolved from `asset_prices.close`; for manual mode it is supplied by the user. |
| `purchase_date` | date | nullable | User-provided purchase date used for market price lookup. Empty for custom price mode. |
| `price_date` | date | nullable, `<= purchase_date` | Actual market date used for the cost basis. May be before `purchase_date` when previous close is used. |
| `price_source` | varchar(20) | `market_close` / `previous_close` / `manual` / `unknown` | How `average_cost` was determined. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

Constraints and indexes:

- Unique constraint: `pf_hold_port_asset_uniq` on `(portfolio_id, asset_id)`.
- Check constraint: `pf_hold_weight_range` keeps `target_weight` between `0` and `1`.
- Check constraint: `pf_hold_quantity_non_negative` keeps `quantity >= 0` when present.
- Check constraint: `pf_hold_average_cost_non_negative` keeps `average_cost >= 0` when present.
- Check constraint: `pf_hold_price_date_not_after_purchase` prevents a resolved market price date after the requested purchase date.
- Index: `pf_hold_port_asset_idx` on `(portfolio_id, asset_id)`.

## Strategies

Table: `strategies_strategy`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal strategy id. |
| `owner_id` | integer | FK to `accounts_user` | User that owns the strategy. |
| `name` | varchar(255) | not null | Strategy name. |
| `description` | text | blank allowed | Optional description. |
| `config` | jsonb | default `{}` | Strategy parameters/rules. |
| `source` | varchar(20) | `manual` / `ai` | How the strategy was created. |
| `is_public` | boolean | default `false` | Whether other users can see it. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

Index:

- `strategy_owner_public_idx` on `(owner_id, is_public)`.

## Backtests

Table: `backtests_backtestrun`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal backtest id. |
| `user_id` | integer | FK to `accounts_user` | User that ran the backtest. |
| `strategy_id` | integer | FK to `strategies_strategy` | Strategy being tested. |
| `stock_id` | integer | FK to `assets` | Asset being tested. Field name remains `stock` in code for compatibility. |
| `start_date` | date | not null | Backtest start date. |
| `end_date` | date | not null | Backtest end date. |
| `initial_cash` | decimal(14, 2) | default `10000` | Starting cash amount. |
| `status` | varchar(20) | `pending` / `running` / `completed` / `failed` | Backtest status. |
| `metrics` | jsonb | default `{}` | Summary metrics such as return, Sharpe, drawdown and win rate. |
| `equity_curve` | jsonb | default `[]` | Equity curve points for charting. |
| `trades` | jsonb | default `[]` | Trade records for dashboard display. |
| `error_message` | text | blank allowed | Failure reason if status is `failed`. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

Indexes:

- `backtest_user_status_idx` on `(user_id, status)`.
- `backtest_strategy_stock_idx` on `(strategy_id, stock_id)`.

## Conversations

### `conversations_chatthread`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal chat thread id. |
| `user_id` | integer | FK to `accounts_user` | Owner. |
| `stock_id` | integer | nullable FK to `assets` | Optional asset context. Field name remains `stock` in code for compatibility. |
| `title` | varchar(255) | not null | Thread title. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

### `conversations_chatmessage`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal message id. |
| `thread_id` | integer | FK to `conversations_chatthread` | Parent chat thread. |
| `role` | varchar(20) | `user` / `assistant` / `system` | Message role. |
| `content` | text | not null | Message content. |
| `metadata` | jsonb | default `{}` | Optional structured metadata. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |

### `conversations_debatesession`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal debate id. |
| `user_id` | integer | FK to `accounts_user` | Owner. |
| `stock_id` | integer | nullable FK to `assets` | Optional asset context. Field name remains `stock` in code for compatibility. |
| `topic` | varchar(255) | not null | Debate topic. |
| `status` | varchar(20) | `pending` / `running` / `completed` / `failed` | Debate status. |
| `summary` | text | blank allowed | Optional debate summary. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

### `conversations_debatemessage`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal debate message id. |
| `session_id` | integer | FK to `conversations_debatesession` | Parent debate session. |
| `agent_name` | varchar(100) | not null | Display name of the agent. |
| `agent_role` | varchar(50) | not null | Agent role, for example bullish, bearish or risk. |
| `round_number` | integer | default `1` | Debate round number. |
| `content` | text | not null | Agent message content. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |

### `conversations_stocksignal`

Stores the final quantitative and qualitative verdict from the Judge AI after a Debate session. This table bridges the Stock Rater (Module A) and the Strategy Manager (Module B).

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key | Internal signal id. |
| `user_id` | integer | FK to `accounts_user` | User who generated the signal. |
| `asset_id` | integer | FK to `assets` | The stock being rated. |
| `debate_session_id` | integer | nullable FK to `conversations_debatesession` | Link to the transcript. |
| `action` | varchar(10) | `BUY` / `SELL` / `HOLD` | The Judge's final action. |
| `conviction` | decimal(5, 4) | between `0.0` and `1.0` | Mathematical conviction score. |
| `bull_thesis` | text | blank allowed | The Bull Agent's opening argument. |
| `bear_thesis` | text | blank allowed | The Bear Agent's opening argument. |
| `judge_reasoning` | text | blank allowed | The Judge Agent's explanation. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |

Indexes:
- `signal_asset_date_idx` on `(asset_id, created_at DESC)`.
