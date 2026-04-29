# Architecture

## Overview

AI Stock Lab is a split frontend/backend application with a PostgreSQL database and local Ollama integration.

## Backend

The backend is implemented with Django REST Framework. PostgreSQL schema changes are managed through Django migrations. Authentication uses JWT access tokens and a custom Django user model that supports login with either username or email.

## Frontend

The frontend is a Next.js application that talks to the Django REST API through `NEXT_PUBLIC_API_BASE_URL`.

## TODO

- Define the frontend module boundaries.
- Define AI workflow orchestration.
