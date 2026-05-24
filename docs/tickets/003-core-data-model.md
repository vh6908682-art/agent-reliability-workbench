# Ticket 003 — Core Data Model

## Goal

Add the first product-specific database models for AgentOps Workbench.

This ticket should define the core persistence schema for agent runs, trace steps, eval cases, and eval results.

Do not implement the agent loop yet.

## Why this matters

The MVP needs to show the production layer behind an agent answer.

That means storing:

- what task was run
- what answer was produced
- what steps/tools/context were used
- whether structured output validation passed
- how eval cases performed

## Scope

Work inside:

    apps/api/

Expected additions or updates:

    apps/api/app/models/
      __init__.py
      agent_run.py
      trace_step.py
      eval_case.py
      eval_result.py

    apps/api/app/db/base.py

    apps/api/alembic/versions/
      initial_core_tables.py

## Requirements

### 1. AgentRun model

Create an `agent_runs` table.

Suggested fields:

- id
- task
- status
- final_answer
- structured_output
- validation_status
- latency_ms
- cost_usd
- created_at
- updated_at

Notes:

- `structured_output` should support JSON.
- `cost_usd` can be nullable for now.
- status can be a string for MVP.

### 2. TraceStep model

Create a `trace_steps` table.

Suggested fields:

- id
- agent_run_id
- step_index
- step_type
- name
- input
- output
- latency_ms
- created_at

Notes:

- `agent_run_id` should reference `agent_runs.id`.
- `input` and `output` should support JSON.
- This model represents tool calls, retrieval steps, validation steps, and LLM steps.

### 3. EvalCase model

Create an `eval_cases` table.

Suggested fields:

- id
- name
- task
- expected_signals
- tags
- is_active
- created_at
- updated_at

Notes:

- `expected_signals` should support JSON.
- `tags` should support JSON or an array-like JSON structure.

### 4. EvalResult model

Create an `eval_results` table.

Suggested fields:

- id
- eval_case_id
- agent_run_id
- score
- passed
- notes
- created_at

Notes:

- `eval_case_id` should reference `eval_cases.id`.
- `agent_run_id` should reference `agent_runs.id`.
- `score` can be nullable or numeric.

### 5. Alembic migration

Create an Alembic migration that creates these four tables.

The migration should be reversible.

### 6. Tests

Add basic model/import tests.

Tests should verify:

- models can be imported
- metadata includes the expected tables
- relationships do not break app startup

Do not require a live Postgres database for unit tests.

## Out of scope

Do not add:

- API CRUD endpoints
- seed data loader
- OpenAI integration
- agent loop
- eval runner logic
- frontend work

## Acceptance criteria

From `apps/api`:

    python -m pytest

should pass.

If Postgres is running and `DATABASE_URL` is valid:

    alembic upgrade head

should create:

- agent_runs
- trace_steps
- eval_cases
- eval_results

## Codex instructions

Implement only this ticket.

Keep the diff focused on models and migration.

Do not add business logic yet.

Do not implement APIs beyond what already exists.

After implementation, show:

1. files changed
2. commands run
3. test result
4. any assumptions made
