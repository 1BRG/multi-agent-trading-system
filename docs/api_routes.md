# API Routes

## Overview

This document tracks the Django REST API route surface for the application.

## Authentication

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | No | Creates a new user account with `username`, `email`, `password`, optional `full_name`, and returns JWT tokens. |
| `POST` | `/auth/login` | No | Validates `identifier` plus `password`; `identifier` can be username or email. |
| `POST` | `/auth/social/{provider}/start` | No | Starts OAuth login for `google` or `github`; returns an authorization URL and state when provider credentials are configured. |
| `POST` | `/auth/social/{provider}/callback` | No | Exchanges an OAuth authorization code for app JWT tokens. |
| `GET` | `/auth/me` | Bearer token | Returns the currently authenticated user. |

## Users

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/users/me` | Bearer token | Returns the current user's profile. |
| `PATCH` | `/users/me` | Bearer token | Updates the current user's email or full name. |
| `PATCH` | `/users/me/password` | Bearer token | Changes the current user's password. |
| `DELETE` | `/users/me` | Bearer token | Deactivates the current user's account. |
| `GET` | `/users` | Admin bearer token | Lists users. |
| `GET` | `/users/{user_id}` | Admin bearer token | Returns a user by id. |
| `PATCH` | `/users/{user_id}` | Admin bearer token | Updates a user as admin. |
| `DELETE` | `/users/{user_id}` | Admin bearer token | Deactivates a user as admin. |

## Domain Routes

| Method | Route | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/assets` | No | Lists enabled assets prepared for stock, ETF, and commodity workflows. |
| `GET` | `/api/assets/{symbol}/prices?start=YYYY-MM-DD&end=YYYY-MM-DD` | No | Returns daily OHLCV price rows from PostgreSQL for charting and backtests. |

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
