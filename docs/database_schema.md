# Database Schema

## Overview

This document describes the PostgreSQL schema managed by Django migrations.

## Users

Table: `accounts_user`.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key, indexed | Internal user id. |
| `username` | varchar(150) | unique, case-insensitive unique constraint | Login identifier. |
| `email` | varchar(254) | unique, case-insensitive unique constraint | Normalized lowercase email address. |
| `password` | varchar(128) | not null | Django-managed password hash. |
| `full_name` | varchar(255) | blank allowed | Optional display name. |
| `profile_photo` | varchar(100) | blank allowed | Uploaded profile photo path under Django media storage. |
| `role` | varchar(50) | not null | Authorization role, currently `user` or `admin`. |
| `is_active` | boolean | not null | Soft-delete/deactivation flag. |
| `last_login` | timestamp with timezone | nullable | Last successful login timestamp. |
| `date_joined` | timestamp with timezone | not null | Django account creation timestamp. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

## Market Data

Tables:
- `assets`: symbols, names, asset type, sector, exchange, currency, active flag.
- `asset_prices`: local daily OHLCV historical prices from 2010-01-01 onward, unique on `(asset_id, date)` and indexed on `(asset_id, date)`.

Initial supported assets:
- Stocks: `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `NVDA`, `TSLA`, `META`, `JPM`, `KO`, `WMT`.
- ETFs: `SPY`, `QQQ`, `GLD`.
- Commodities: `GC=F`.

Table: `assets`.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key, indexed | Internal asset id. |
| `symbol` | varchar(24) | unique | Provider symbol, normalized uppercase. |
| `name` | varchar(255) | not null | Human-readable asset name. |
| `asset_type` | varchar(20) | `stock` / `etf` / `commodity` | Asset category. |
| `sector` | varchar(100) | blank allowed | Sector for equities when available. |
| `exchange` | varchar(50) | blank allowed | Listing exchange or source venue. |
| `currency` | varchar(10) | default `USD` | Quote currency. |
| `is_active` | boolean | not null | Whether the asset is enabled in the app. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

Table: `asset_prices`.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | integer | primary key, indexed | Internal price row id. |
| `asset_id` | integer | FK to `assets`, unique with `date` | Asset being priced. |
| `date` | date | unique with `asset_id`, indexed | Trading date. |
| `open` | decimal(18, 6) | not null | Daily open. |
| `high` | decimal(18, 6) | not null | Daily high. |
| `low` | decimal(18, 6) | not null | Daily low. |
| `close` | decimal(18, 6) | not null | Daily close. |
| `adjusted_close` | decimal(18, 6) | nullable | Adjusted daily close. |
| `volume` | bigint | default `0` | Daily volume. |
| `source` | varchar(50) | default `yahoo` | Data provider/source. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

## User-Owned Domain Tables

- `strategies_strategy`: owner, name, description, JSON config, source `manual`/`ai`, public flag.
- `backtests_backtestrun`: user, strategy, stock, date range, initial cash, status, metrics JSON, equity curve JSON, trades JSON.
- `conversations_chatthread`: user chat sessions, optional stock context.
- `conversations_chatmessage`: chat messages with role and metadata JSON.
- `conversations_debatesession`: user AI debate sessions, optional stock context and status.
- `conversations_debatemessage`: debate agent messages with agent name, role and round number.
