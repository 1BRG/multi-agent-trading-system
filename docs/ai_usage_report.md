# AI Tools Usage Report

The project was developed with AI assistance across planning, implementation, validation and documentation.

## Planning

- AI was used to break the trading system into backend, frontend, agent, strategy and backtesting responsibilities.
- AI helped define API contracts for strategy generation, debate outputs, portfolio holdings and backtest results.
- Product backlog and user stories are tracked in Linear and should be linked from `docs/grading_evidence.md`.

## Implementation

- AI-assisted coding was used for Django models, serializers, viewsets, frontend dashboard pages and validation flows.
- The product itself includes AI agents:
  - Bull analyst, Bear analyst and Judge agents for stock debates.
  - Strategy agent for turning natural language strategy ideas into deterministic JSON rules.

## Validation

- AI was used to identify missing validation paths and add automated backend tests.
- Agent eval coverage is implemented in `backend/conversations/tests.py`, using deterministic LLM mocks to verify debate orchestration and Judge JSON parsing.
- CI runs backend tests, Django checks, TypeScript and ESLint.

## Documentation

- AI was used to draft architecture notes, API route documentation, grading evidence and Mermaid diagrams.
- The documentation is intentionally linked from the README so the evaluator can map each grading requirement to a repository artifact.
