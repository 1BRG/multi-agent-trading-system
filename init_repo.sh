#!/bin/bash

echo " Inițializare arhitectură repozitoriu Multi-Agent Trading..."

# 1. Crearea topologiei directoarelor
echo " Creare directoare..."
mkdir -p agents core tools tests/unit tests/evals docs .github/workflows .github/ISSUE_TEMPLATE

# Crearea fișierelor .gitkeep pentru a forța Git să urmărească directoarele goale
touch agents/.gitkeep core/.gitkeep tools/.gitkeep tests/unit/.gitkeep tests/evals/.gitkeep docs/.gitkeep

# 2. Generarea .gitignore
echo " Generare .gitignore..."
cat << 'EOF' > .gitignore
==========================================
Core Python Exclusions
==========================================
__pycache__/
*.py[cod]
*$py.class
*.so
dist/
build/
*.egg-info/
*.egg
==========================================
Virtual Environments and Dependencies
==========================================
venv/
env/
ENV/
.env/
.venv/
.tox/
==========================================
Testing, Coverage, and CI Artifacts
==========================================
htmlcov/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
==========================================
Jupyter and Data Science Artifacts
==========================================
.ipynb_checkpoints/
profile_default/
ipython_config.py
==========================================
AI, LLM, and Vector Database Local State
==========================================
# LangGraph state checkpoints and PostgreSQL local mounts
checkpoints/
pgdata/
*.db
*.sqlite3
# Local embedding caches (e.g., ChromaDB)
chroma_db/
.chroma/
# Ollama local model storage (if mounted locally during dev)
.ollama/
==========================================
Security and Environment Variables
==========================================
.env
.env.local
.env.*
*.pem
*.key
EOF

# 3. Generarea AGENTS.md
echo " Generare AGENTS.md..."
cat << 'EOF' > AGENTS.md
name: Multi-Agent Trading Architecture Assistant
description: You are an elite AI Systems Architect and DevSecOps Engineer specializing in LangGraph, Pydantic, and local LLM orchestration.

## Your Role
You are an expert Python engineer tasked with generating, reviewing, and refactoring source code for a highly sophisticated, autonomous multi-agent financial trading system. Your primary objective is to ensure deterministic execution, rigorous type-safety, and secure tool integration while strictly preventing context drift and hallucinations.

## Project Knowledge & Tech Stack
This project operates entirely on a local, privacy-first infrastructure. You must strictly adhere to the following technological boundaries and framework versions:
* **Language:** Python 3.11+
* **Orchestration:** LangGraph (Stateful graph architecture exclusively)
* **Local LLM Inference:** Ollama (utilizing llama3.1, smollm2, and granite models)
* **Data Validation:** Pydantic V2 (Strict schema enforcement required)
* **Database:** PostgreSQL 15+ with the pgvector extension for semantic similarity search
* **Tool Integration:** Model Context Protocol (MCP) utilizing JSON-RPC 2.0
* **Testing:** Pytest for deterministic functions, DeepEval for LLM-as-a-judge metrics
* **Frontend:** Streamlit (Utilizing Session State and real-time streaming capabilities)

## Execution Commands
When instructed to validate, format, or test your generated code, execute the following precise terminal commands from the project root:
* **Type Checking:** `poetry run mypy .`
* **Formatting:** `poetry run ruff format .`
* **Unit Testing:** `poetry run pytest tests/unit/ -v`
* **LLM Evaluation:** `poetry run deepeval test run tests/evals/`

## Architectural Boundaries

###  Always Do:
* Enforce structured outputs utilizing Pydantic models. Never rely on raw string matching or RegEx parsing for agent decisions.
* Implement explicit error handling and automated retry logic by utilizing LangChain's ToolStrategy for all external function calling.
* Write modular code strictly within the designated directory structure (`core/`, `agents/`, `tools/`).
* Ensure that any database connection object utilizing the LangGraph PostgresSaver checkpointer is explicitly instantiated with `autocommit=True` and `row_factory=dict_row` to prevent silent migration failures.

###  Ask First:
* Before modifying the global LangGraph state schema (defined conceptually in `core/state.py`).
* Before adding new external API dependencies to `pyproject.toml` or `requirements.txt`.
* Before attempting to alter the mathematical risk management guardrails or maximum portfolio drawdown limits.

###  Never Do:
* Never write or generate raw SQL queries via string formatting; you must exclusively interact with the database using the internal MCP server protocol.
* Never hardcode API keys, cryptographic credentials, or sensitive configurations into the source code; rely strictly on dynamically loaded environment variables.
* Never remove or comment out failing DeepEval or Pytest tests simply to pass the CI pipeline; instead, address the underlying prompt logic or algorithmic failure.
* Never utilize generalized conversational chat models for structured JSON generation tasks; explicitly route those tasks to highly deterministic, local models optimized for coding (e.g., Qwen or IBM Granite).

## Code Example: Pydantic Schema Enforcement
When generating agent output schemas, strictly follow this pattern to avoid conversational padding and markdown formatting artifacts:
```python
from pydantic import BaseModel, Field
from typing import Literal

class TradeDecision(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol representing the asset.")
    action: Literal["BUY", "SELL", "HOLD"] = Field(..., description="The calculated mathematical recommendation.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence probability strictly bounded between 0 and 1.")
    reasoning: str = Field(..., description="Concise justification completely devoid of conversational padding or markdown artifacts.")
EOF
# 4. Generarea Șabloanelor GitHub (Issue Templates)
echo "📝 Generare Issue Templates..."
cat << 'EOF' >.github/ISSUE_TEMPLATE/user_story.yml
name: "Agile User Story"
description: "Propose a new feature or agent capability using BDD syntax."
title: "[Epic Code] - <Short Description>"
labels: ["enhancement", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        ## User Story Definition
        A user story must clearly articulate the persona, the desired action, and the derived business value.
  - type: textarea
    id: user_story
    attributes:
      label: "User Story (As a... I want... so that...)"
      description: "Define the core requirement from the perspective of the end-user or system persona."
      placeholder: "As a Fundamental Analyst Agent, I want to fetch SEC 10-K filings via AlphaVantage so that..."
    validations:
      required: true
  - type: textarea
    id: acceptance_criteria
    attributes:
      label: "Acceptance Criteria (Gherkin Syntax)"
      description: "Define the exact conditions of satisfaction using Given/When/Then formats."
      value: |
        Given [precondition or state]
        When [action or trigger]
        Then [expected execution result]
        And [additional constraints or guardrails]
    validations:
      required: true
  - type: dropdown
    id: epic_link
    attributes:
      label: "Associated Epic"
      description: "Select the architectural pillar this story belongs to."
      options:
        - Foundational Infrastructure (INF)
        - Stateful Orchestration (ORC)
        - Specialized Agent Ecosystem (AGT)
        - Data Ingestion & MCP (DAT)
        - Continuous Evaluation (TST)
        - User Interface (UI)
    validations:
      required: true
  - type: input
    id: story_points
    attributes:
      label: "Estimated Story Points"
      description: "Fibonacci sequence estimation (1, 2, 3, 5, 8, 13)."
    validations:
      required: false
EOF

cat << 'EOF' >.github/ISSUE_TEMPLATE/bug_report.yml
name: "System Defect / LLM Failure Report"
description: "Report a deterministic crash, state corruption, or an unexpected AI reasoning failure."
title: " - <Short Description>"
labels: ["bug", "triage"]
body:
  - type: dropdown
    id: failure_type
    attributes:
      label: "Classification of Failure"
      options:
        - Deterministic Crash (Python Exception / Syntax Error)
        - LLM Hallucination (Factually incorrect market output)
        - State Corruption (LangGraph asynchronous routing failure)
        - Tool Execution Error (API timeout / MCP JSON-RPC failure)
        - Parsing Exception (Pydantic validation failure)
    validations:
      required: true
  - type: textarea
    id: reproduction_steps
    attributes:
      label: "Steps to Reproduce"
      description: "Exact sequence required to trigger the failure."
      placeholder: "1. Initialize the Bull Agent.\n2. Pass the ticker 'NVDA'.\n3. Observe the output of the Judge Agent."
    validations:
      required: true
  - type: textarea
    id: expected_vs_actual
    attributes:
      label: "Expected vs. Actual Behavior"
      description: "Contrast the intended algorithmic outcome with the erroneous result."
    validations:
      required: true
  - type: textarea
    id: system_logs
    attributes:
      label: "Execution Traces and LangGraph State"
      description: "Paste relevant backend logs, Ollama inference times, or DeepEval failure metrics."
      render: bash
    validations:
      required: false
EOF

# 5. Generarea CI/CD Pipeline
echo "⚙️ Generare CI/CD Workflow..."
cat << 'EOF' >.github/workflows/evaluate_agents.yml
name: Autonomous Agent Evaluation Pipeline

on:
  pull_request:
    branches:
      - main
      - develop
  push:
    branches:
      - develop

jobs:
  deterministic-tests:
    name: Execute Pytest (Mathematical & Unit Validation)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
      
      - name: Setup Python Environment
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          
      - name: Install Project Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run Deterministic Pytest Suite
        run: pytest tests/unit/ -v --junitxml=coverage.xml

  llm-evaluation:
    name: Execute DeepEval (Agent Reasoning & Guardrails Verification)
    needs: deterministic-tests
    runs-on: [actuated-8cpu-16gb, gpu]
    
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        
      - name: Setup Python Environment
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install DeepEval and Associated Integrations
        run: pip install deepeval langchain-openai psycopg-pool
        
      - name: Bootstrap Ollama Local Inference Server
        uses: ai-action/setup-ollama@v2
        
      - name: Pre-Pull Lightweight CI Evaluation Model
        run: ollama pull smollm2:1.7b
        
      - name: Verify Ollama Service Boot Status
        run: curl -I http://localhost:11434
        
      - name: Execute LLM-as-a-Judge Evaluation (DeepEval)
        run: deepeval test run tests/evals/ --verbose
        env:
          OLLAMA_HOST: "http://localhost:11434"
EOF

echo "Arhitectura a fost inițializată cu succes!"