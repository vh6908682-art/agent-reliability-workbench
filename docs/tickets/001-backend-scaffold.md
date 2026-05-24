# Ticket 001 — Backend Scaffold

## Goal

Create the initial FastAPI backend scaffold for AgentOps Workbench.

This ticket should only establish the backend application structure, health endpoint, config loading, and basic local run behavior.

Do not implement database models, agent logic, OpenAI calls, tracing, evals, or frontend work in this ticket.

## Why this matters

The backend is the control plane for the MVP.

Everything else will eventually connect through this service:

- agent runs
- trace capture
- structured output validation
- eval execution
- frontend dashboard APIs

## Scope

Create a backend app under:

    apps/api/

Expected structure:

    apps/api/
      app/
        __init__.py
        main.py
        core/
          __init__.py
          config.py
        api/
          __init__.py
          routes/
            __init__.py
            health.py
      tests/
        __init__.py
        test_health.py
      pyproject.toml

## Requirements

### 1. FastAPI app

Create a FastAPI app in:

    apps/api/app/main.py

The app should:

- have title `AgentOps Workbench API`
- register the health router
- expose `/health`

### 2. Health endpoint

Create:

    GET /health

Response:

    {
      "status": "ok",
      "service": "agentops-workbench-api"
    }

### 3. Config loading

Create:

    apps/api/app/core/config.py

Use Pydantic settings or a simple Pydantic model.

Config should support:

- `APP_ENV`
- `DATABASE_URL`
- `OPENAI_API_KEY`

Do not require real values yet.

The app should boot even if `OPENAI_API_KEY` is missing.

### 4. Tests

Add a basic test for `/health`.

Test should verify:

- HTTP status is `200`
- response status is `ok`
- service name is correct

### 5. Packaging

Create:

    apps/api/pyproject.toml

Minimal dependencies:

- fastapi
- uvicorn
- pydantic
- pydantic-settings
- pytest
- httpx

Use Python 3.11+.

## Out of scope

Do not add:

- SQLAlchemy
- Alembic
- Postgres connection logic
- OpenAI client
- agent loop
- eval runner
- frontend
- Docker changes unless absolutely necessary

## Acceptance criteria

This should work from `apps/api`:

    cd apps/api
    python -m pytest
    python -m uvicorn app.main:app --reload

Then this should return healthy JSON:

    curl http://localhost:8000/health

Expected output:

    {"status":"ok","service":"agentops-workbench-api"}

## Codex instructions

Implement only this ticket.

Keep the diff small.

Do not jump ahead to database, agent, eval, or frontend work.

After implementation, show:

1. files changed
2. commands run
3. test result
4. any assumptions made
