# AGENTS.md

This file gives implementation agents the minimum context needed to work safely in this repo.

For deeper product, architecture, benchmark, and workflow details, read the linked docs instead of adding long explanations here.

## Project Identity

This repo is **Agent Reliability Workbench**.

It is a benchmarking, observability, and governance platform for tool-using AI agents.

The current incident-investigation flow is the benchmark environment. It is used to evaluate whether an agent can investigate production-like incidents, use tools safely, produce evidence-backed diagnoses, pass validation, respect guardrails, and generate repeatable eval results.

Do not treat this project as only an incident triage demo.

## Source of Truth Docs

Read the most relevant docs before making changes:

- `README.md` — public project overview and local setup
- `docs/PROJECT_VISION.md` — product direction and positioning
- `docs/architecture/system-overview.md` — current system architecture
- `docs/architecture/data-model.md` — core entities and persistence model
- `docs/architecture/api-contract.md` — API shape and backend/frontend contract
- `docs/BENCHMARK_SPEC.md` — benchmark scenarios, tool-using agent task design, and incident environment
- `docs/EVAL_METHODOLOGY.md` — evaluation strategy, scoring, checks, and expected behavior
- `docs/ROADMAP.md` — staged development plan beyond MVP
- `docs/architecture/codex-workflow.md` — how implementation tickets should be executed
- `docs/architecture/demo-script.md` — demo flow and narrative

If a document does not exist yet, do not invent large architecture changes. Keep the implementation aligned with existing code and the current ticket.

## Working Rules

- Implement only the current ticket or explicit user request.
- Keep changes small and focused.
- Do not refactor unrelated files.
- Do not rename major concepts without explicit instruction.
- Do not silently change API contracts.
- Do not bloat `AGENTS.md`; add deeper explanations to the appropriate doc instead.
- Preserve the current MVP behavior unless the ticket explicitly changes it.
- Prefer deterministic behavior for benchmark, validation, guardrail, and eval logic.
- Treat eval cases and seed scenarios as product-critical, not test-only fixtures.

## Current Product Direction

The platform should support:

- repeatable agent benchmark scenarios
- traceable tool-using agent runs
- structured outputs
- validation and guardrails
- approval workflows for risky recommendations
- latency, token, and cost visibility
- recent run inspection
- deterministic eval runs
- future scenario expansion beyond the initial Kafka incident

The goal is to make agent behavior observable, comparable, and governable.

## Implementation Standards

Backend:

- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Deterministic services where possible
- Tests for API/service behavior when backend logic changes

Frontend:

- Next.js
- React
- TypeScript
- Tailwind
- Keep UI changes practical and demo-focused
- Preserve typed API contracts

General:

- Keep naming consistent.
- Prefer clear domain language over generic abstractions.
- Avoid speculative production features unless requested by the ticket.
- Favor simple implementation over cleverness.

## Verification

Run the relevant checks for the files changed.

Common commands:

Backend:

    cd apps/api
    python -m pytest

Frontend:

    cd apps/web
    npm run typecheck
    npm run build

If a command fails because of environment setup, report the exact failure and avoid unrelated fixes.

## Ticket Workflow

Each implementation ticket should be narrow.

A good ticket includes:

- goal
- files likely to change
- files that must not change
- exact expected behavior
- verification commands
- constraints and non-goals

Do not expand a ticket just because related improvements are visible.

## Documentation Rule

When adding durable project knowledge:

- use `README.md` only for public-facing summary and setup
- use `docs/PROJECT_VISION.md` for product direction
- use `docs/architecture/*` for technical design
- use `docs/BENCHMARK_SPEC.md` for benchmark scenario design
- use `docs/EVAL_METHODOLOGY.md` for scoring and checks
- use `docs/ROADMAP.md` for planned future phases
- keep `AGENTS.md` short

## Non-Goals Unless Explicitly Requested

Do not add or rewrite these unless the ticket asks for it:

- full multi-agent orchestration
- LangGraph migration
- authentication
- cloud deployment
- billing
- large UI redesign
- unrelated incident domains
- resume/blog/marketing copy
- broad refactors