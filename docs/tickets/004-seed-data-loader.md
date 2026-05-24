# Ticket 004 — Seed Data Loader

## Goal

Create a backend seed loader that imports the existing mock logs, runbooks, schemas, and eval cases into the local database.

This ticket should make the existing `seed/` folder useful to the backend.

Do not implement the agent loop yet.

## Why this matters

The MVP golden path depends on realistic context:

- mock Kafka consumer logs
- runbooks for retry/idempotency issues
- duplicate key violation guidance
- customer update event schema
- incident triage eval cases

This data will later be retrieved by the agent and evaluated.

## Scope

Work mainly inside:

    apps/api/

Also read from the existing repo-level folder:

    seed/

Expected additions:

    apps/api/app/models/
      knowledge_document.py

    apps/api/app/services/
      __init__.py
      seed_loader.py

    apps/api/app/cli/
      __init__.py
      seed.py

    apps/api/alembic/versions/
      add_knowledge_documents.py

## Requirements

### 1. KnowledgeDocument model

Create a `knowledge_documents` table.

Suggested fields:

- id
- source_path
- title
- document_type
- content
- metadata
- created_at
- updated_at

Notes:

- `source_path` should identify the original seed file path.
- `document_type` can be values like `runbook`, `schema`, or `mock_log`.
- `metadata` should support JSON.
- Make `source_path` unique so seed loading can be idempotent.

### 2. Alembic migration

Create a migration for the `knowledge_documents` table.

The migration should be reversible.

### 3. Seed loader service

Create:

    apps/api/app/services/seed_loader.py

It should:

- locate repo-level `seed/`
- load markdown files under `seed/documents/`
- load log files under `seed/mock_logs/`
- load eval cases from `seed/eval_cases/incident-triage-evals.json`
- insert or update records idempotently

For eval cases, use the `eval_cases` table from Ticket 003.

### 4. CLI entrypoint

Create:

    apps/api/app/cli/seed.py

It should be runnable as:

    python -m app.cli.seed

The command should print a short summary:

- knowledge documents loaded
- eval cases loaded
- skipped or updated records if applicable

### 5. Tests

Add tests for seed loading behavior.

Tests should cover:

- document type detection
- seed file discovery
- eval case parsing
- idempotency logic at the service level

Use temporary files and/or mocks where needed.

Do not require a live Postgres database for unit tests unless using an in-memory SQLite test setup.

## Out of scope

Do not add:

- retrieval/search logic
- embeddings
- OpenAI calls
- agent loop
- frontend work
- eval runner execution

## Acceptance criteria

From `apps/api`:

    python -m pytest

should pass.

If Postgres is running and migrations are applied:

    python -m app.cli.seed

should load the repo seed data and print a summary.

Running the seed command twice should not create duplicate records.

## Codex instructions

Implement only this ticket.

Keep the diff focused on seed loading and the knowledge document model.

Do not build retrieval, agent logic, or eval execution yet.

After implementation, show:

1. files changed
2. commands run
3. test result
4. any assumptions made
