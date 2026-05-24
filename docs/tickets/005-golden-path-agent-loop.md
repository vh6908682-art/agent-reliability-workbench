# Ticket 005 — Golden Path Agent Loop

## Goal

Implement the first simple incident-triage agent loop for the MVP golden path.

The agent should take an incident task, use seeded context, call OpenAI, and return a diagnosis-style answer.

This ticket should keep orchestration simple and custom.

Do not add LangGraph yet.

## Why this matters

This is the first point where AgentOps Workbench becomes a working agent product instead of only infrastructure.

The golden path is:

    User submits incident task
    Backend retrieves relevant seed context
    Backend calls OpenAI
    Backend returns diagnosis and recommended next steps

Example task:

    A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

## Scope

Work inside:

    apps/api/

Expected additions:

    apps/api/app/services/
      agent_loop.py
      context_retriever.py
      llm_client.py

    apps/api/app/api/routes/
      agent_runs.py

Expected updates:

    apps/api/app/main.py
    apps/api/app/core/config.py
    apps/api/pyproject.toml

## Requirements

### 1. Request and response schema

Create a simple API endpoint:

    POST /agent-runs

Request body:

    {
      "task": "incident task text"
    }

Response body should include:

    {
      "task": "...",
      "answer": "...",
      "context_sources": [...]
    }

Keep this response simple for now.

Do not require persisted run storage in this ticket unless it is already easy from prior models.

Trace persistence comes in the next ticket.

### 2. Context retriever

Create:

    app/services/context_retriever.py

For MVP, use simple keyword matching over seeded knowledge documents.

No embeddings yet.

The retriever should return relevant content from:

- mock logs
- runbooks
- schemas

It should prefer context related to:

- Kafka consumer failures
- duplicate key violations
- retry exhaustion
- customer update events
- idempotency

### 3. LLM client

Create:

    app/services/llm_client.py

Use OpenAI first.

Requirements:

- read `OPENAI_API_KEY` from config
- fail cleanly if missing
- keep model configurable if simple
- avoid exposing secrets in errors

Suggested config:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`

Default model can be a small/current OpenAI chat model.

### 4. Agent loop

Create:

    app/services/agent_loop.py

The loop should:

1. accept a task
2. retrieve relevant context
3. build a concise incident-triage prompt
4. call the LLM
5. return answer and context source metadata

The answer should encourage a structured format:

- likely cause
- evidence
- recommended next steps
- prevention or guardrail suggestion

### 5. API route

Create:

    app/api/routes/agent_runs.py

Register it in `main.py`.

Endpoint:

    POST /agent-runs

### 6. Tests

Add unit tests for:

- context retrieval behavior
- prompt construction or agent loop with mocked LLM client
- API endpoint with mocked agent loop

Tests should not call OpenAI.

Tests should not require a live Postgres database unless already mocked or isolated.

## Out of scope

Do not add:

- streaming
- LangGraph
- embeddings/vector DB
- full trace persistence
- eval runner
- frontend UI
- approval workflows

## Acceptance criteria

From `apps/api`:

    python -m pytest

should pass without calling OpenAI.

With valid environment variables and seeded DB available, this should work:

    python -m uvicorn app.main:app --reload

Then:

    curl -X POST http://localhost:8000/agent-runs \
      -H "Content-Type: application/json" \
      -d '{"task":"A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps."}'

should return a diagnosis answer and context source list.

## Codex instructions

Implement only this ticket.

Keep the orchestration simple.

Do not add LangGraph.

Do not build tracing, evals, frontend, or approvals yet.

After implementation, show:

1. files changed
2. commands run
3. test result
4. any assumptions made
