# Ticket 002 — Database Foundation

## Goal

Add the database foundation for the FastAPI backend.

This ticket should introduce SQLAlchemy, Alembic, Postgres connectivity, and a simple DB health check.

Do not implement product-specific tables yet.

## Why this matters

AgentOps Workbench needs durable storage for:

- agent runs
- trace steps
- tool calls
- structured validation results
- eval cases
- eval results

Before adding those models, the backend needs a clean and testable database layer.

## Scope

Work inside:

    apps/api/

Expected additions:

    apps/api/
      app/
        db/
          __init__.py
          base.py
          session.py
        api/
          routes/
            health.py
      alembic/
        env.py
        script.py.mako
        versions/
      alembic.ini

## Requirements

### 1. Dependencies

Update `apps/api/pyproject.toml` to include:

- sqlalchemy
- alembic
- psycopg[binary]

Keep existing dependencies from Ticket 001.

### 2. Database session module

Create:

    apps/api/app/db/session.py

It should expose:

- SQLAlchemy engine
- SessionLocal
- get_db dependency

Use `DATABASE_URL` from config.

### 3. Declarative base

Create:

    apps/api/app/db/base.py

It should expose a shared SQLAlchemy declarative Base.

No product models yet.

### 4. Alembic setup

Add Alembic config under:

    apps/api/alembic.ini
    apps/api/alembic/

Alembic should read the DB URL from app config.

No migration with product tables yet.

### 5. DB health endpoint

Extend health routing with:

    GET /health/db

It should attempt a simple database query:

    SELECT 1

Successful response:

    {
      "status": "ok",
      "database": "ok"
    }

Failure response should be clean JSON and should not expose secrets.

### 6. Tests

Add or update tests for:

- `/health`
- `/health/db`

For `/health/db`, use a safe approach.

If a real database is not available in test environment, mock the database dependency or session behavior.

Do not require local Postgres just to run unit tests.

## Out of scope

Do not add:

- agent run models
- trace models
- eval models
- seed loaders
- OpenAI calls
- frontend work
- Docker changes unless absolutely necessary

## Acceptance criteria

From `apps/api`:

    python -m pytest

should pass without requiring a live Postgres database.

If Postgres is running and `DATABASE_URL` is valid:

    python -m uvicorn app.main:app --reload

Then:

    curl http://localhost:8000/health
    curl http://localhost:8000/health/db

should both return healthy JSON.

## Codex instructions

Implement only this ticket.

Keep the diff small.

Preserve Ticket 001 behavior.

Do not jump ahead to product schema or agent logic.

After implementation, show:

1. files changed
2. commands run
3. test result
4. any assumptions made
