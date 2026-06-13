# Project Diagrams

These diagrams document the main architecture and workflows required for the MDS project evidence.

## Component Architecture

```mermaid
flowchart LR
  User[Authenticated user] --> Frontend[Next.js frontend]
  Frontend --> API[Django REST API]
  API --> Postgres[(PostgreSQL)]
  API --> Ollama[Local Ollama LLM]
  API --> MarketJobs[Market data import jobs]
  MarketJobs --> Yahoo[Yahoo Finance data source]
  MarketJobs --> Postgres

  subgraph Backend Apps
    Accounts[accounts]
    Market[market]
    Portfolios[portfolios]
    Conversations[conversations]
    Strategies[strategies]
    Backtests[backtests]
  end

  API --> Accounts
  API --> Market
  API --> Portfolios
  API --> Conversations
  API --> Strategies
  API --> Backtests
```

## AI Debate Workflow

```mermaid
sequenceDiagram
  participant U as User
  participant F as Frontend Debate Page
  participant A as Django API
  participant L as Ollama LLM
  participant DB as PostgreSQL

  U->>F: Select ticker and run debate
  F->>A: POST /debates/run_debate
  A->>DB: Create DebateSession
  A->>L: Bull opening prompt
  L-->>A: Bull thesis
  A->>DB: Save Bull message
  A->>L: Bear opening prompt
  L-->>A: Bear thesis
  A->>DB: Save Bear message
  A->>L: Bear rebuttal prompt
  L-->>A: Bear rebuttal
  A->>DB: Save Bear rebuttal
  A->>L: Bull rebuttal prompt
  L-->>A: Bull rebuttal
  A->>DB: Save Bull rebuttal
  A->>L: Judge JSON verdict prompt
  L-->>A: BUY/SELL/HOLD and conviction
  A->>DB: Save Judge message and StockSignal
  A-->>F: Debate transcript and signal
```

## Strategy Generation And Backtesting

```mermaid
flowchart TD
  Prompt[User natural language strategy idea] --> StrategyAPI[POST /strategies/generate_ai]
  StrategyAPI --> StrategyLLM[Strategy LLM agent]
  StrategyLLM --> RawJSON[Strict JSON strategy rules]
  RawJSON --> Serializer[DRF schema validation]
  Serializer --> Draft[Save strategy as DRAFT with raw LLM response]
  Draft --> Review[User reviews strategy JSON]
  Review --> Approve[PATCH /strategies/id/approve]
  Approve --> Backtest[POST /backtests]
  Backtest --> Prices[(Stored asset_prices)]
  Prices --> Engine[Deterministic backtest engine]
  Engine --> Results[Metrics, equity curve and trades]
  Results --> DB[(PostgreSQL)]
  Results --> UI[Backtesting dashboard]
```

## Portfolio Holding Workflow

```mermaid
flowchart TD
  Portfolio[Create portfolio container] --> PositionForm[Add position form]
  PositionForm --> Mode{Price mode}
  Mode -->|Previous close or exact close| Date[User enters purchase date]
  Date --> Resolve[GET /portfolio-holdings/resolve-price]
  Resolve --> StoredPrices[(asset_prices)]
  StoredPrices --> CostBasis[Server resolves buy price and price date]
  Mode -->|Custom price| Manual[User enters buy price]
  CostBasis --> Validate[Backend validation]
  Manual --> Validate
  Validate --> Holding[Save holding]
  Holding --> Metrics[Dynamic invested cost, current value and weight]
```

## CI And Test Workflow

```mermaid
flowchart LR
  Push[Push or pull request] --> CI[GitHub Actions]
  CI --> Ruff[Ruff backend lint]
  CI --> Django[Django checks and migrations]
  Django --> Tests[Backend tests and agent evals]
  CI --> TypeScript[Frontend TypeScript check]
  CI --> ESLint[Frontend ESLint]
  Ruff --> Result[Pass/fail signal]
  Tests --> Result
  TypeScript --> Result
  ESLint --> Result
```
