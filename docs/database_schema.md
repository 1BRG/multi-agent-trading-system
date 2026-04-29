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
| `role` | varchar(50) | not null | Authorization role, currently `user` or `admin`. |
| `is_active` | boolean | not null | Soft-delete/deactivation flag. |
| `last_login` | timestamp with timezone | nullable | Last successful login timestamp. |
| `date_joined` | timestamp with timezone | not null | Django account creation timestamp. |
| `created_at` | timestamp with timezone | not null | Creation timestamp. |
| `updated_at` | timestamp with timezone | not null | Last update timestamp. |

## Market Data

Tables:
- `market_stock`: symbols, names, sector, exchange, currency, active flag.
- `market_stockprice`: local OHLCV historical prices, unique on `(stock_id, date)` and indexed on `(stock_id, date)`.

## User-Owned Domain Tables

- `strategies_strategy`: owner, name, description, JSON config, source `manual`/`ai`, public flag.
- `backtests_backtestrun`: user, strategy, stock, date range, initial cash, status, metrics JSON, equity curve JSON, trades JSON.
- `conversations_chatthread`: user chat sessions, optional stock context.
- `conversations_chatmessage`: chat messages with role and metadata JSON.
- `conversations_debatesession`: user AI debate sessions, optional stock context and status.
- `conversations_debatemessage`: debate agent messages with agent name, role and round number.
