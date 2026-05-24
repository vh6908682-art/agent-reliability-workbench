# AGENTS.md

## Project

This repository is AgentOps Workbench: a developer platform for running, tracing, evaluating, debugging, and safely releasing tool-using LLM agents.

The project is intentionally scoped around one serious golden path:

Developer Support / Incident Triage Agent

A user submits an incident-like backend failure, such as:

> A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

The system should show not only the final answer, but the full reliability layer behind it:
- tool calls
- retrieved context
- structured output validation
- eval results
- trace events
- latency
- token usage
- estimated cost
- guardrail decisions
- approval requirements for risky actions

The project thesis is:

> Most AI agent demos show the answer. AgentOps Workbench shows the production layer behind the answer.

## Target positioning

This project is optimized for:
- AI Engineer
- LLM Application Engineer
- Agentic AI Engineer
- Applied AI Engineer
- AI Platform Engineer
- Backend Engineer, AI Products
- GenAI Engineer

It is not trying to be:
- a frontier ML research project
- a model training platform
- a full enterprise SaaS clone
- a generic chatbot app

## MVP philosophy

Build one cohesive platform, but implement it piece by piece.

Do not build the entire platform in one task.

The implementation order is:

1. Foundation
2. Runs and traces
3. Structured output validation
4. Typed tool registry
5. Mock incident triage agent
6. Guardrails and approval
7. Deterministic eval engine
8. RAG and pgvector
9. Frontend dashboard polish
10. Demo, README, screenshots, and resume assets

## Tech stack

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector later

Frontend:
- Next.js
- React
- TypeScript
- Tailwind
- shadcn/ui later

Local infrastructure:
- Docker Compose
- Postgres
- GitHub Actions

LLM provider:
- OpenAI first
- Anthropic later only if explicitly requested

Orchestration:
- Start with a simple custom agent loop.
- Add LangGraph later only if the core architecture is already clean.

## Engineering rules

Follow these rules for every code change:

- Keep diffs small and reviewable.
- Implement one ticket at a time.
- Do not modify unrelated files.
- Do not introduce new dependencies unless the ticket requires them.
- Explain any new dependency briefly.
- Prefer simple, explicit code over clever abstractions.
- Keep route handlers thin.
- Put business logic in service modules.
- Use typed schemas for request and response payloads.
- Validate tool inputs and outputs.
- Add or update tests for every behavior change.
- Do not silently change existing behavior.
- Do not add auth, billing, Kubernetes, real Slack/Jira integrations, or multi-tenancy unless explicitly requested.

## Safety and secrets

Never read, print, modify, or commit real secret files.

Do not commit:
- .env
- API keys
- database passwords
- private work code
- customer data
- proprietary company documents

Use `.env.example` for documented environment variables.

The MVP must use mock tools for external write actions.

High-risk actions such as `create_ticket_mock` must require approval.

## Backend structure

Backend code lives in:

```text
apps/api/app/