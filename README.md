# AgentOps Workbench

AgentOps Workbench is a developer platform for running, tracing, evaluating, debugging, and safely releasing tool-using LLM agents.

Most AI agent demos show only the final answer. AgentOps Workbench shows the production layer behind the answer:

- What tools did the agent call?
- What context did it use?
- Did the output match the expected schema?
- Did evals pass?
- What did the run cost?
- How long did each step take?
- Did risky actions require approval?
- Why did a run fail?

The MVP focuses on one serious golden path: a Developer Support / Incident Triage Agent for backend incident diagnosis.

## Demo workflow

A user submits an incident-like task:

> A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

The agent should:

1. Classify the incident.
2. Search mock logs.
3. Look up mock service configuration.
4. Validate payload/schema if relevant.
5. Produce structured diagnosis JSON.
6. Store trace events for every major step.
7. Validate final output against a schema.
8. Run deterministic eval checks.
9. Require approval before mock high-risk actions.

## MVP features

- FastAPI backend
- Next.js frontend
- PostgreSQL database
- Agent run lifecycle
- Trace event storage
- Structured output validation
- Typed tool registry
- Mock incident triage tools
- Guardrail and approval model
- Deterministic eval engine
- Demo-friendly dashboard

## Tech stack

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL

Frontend:

- Next.js
- React
- TypeScript
- Tailwind CSS

Infrastructure:

- Docker Compose
- GitHub Actions
- PostgreSQL
- pgvector later

LLM provider:

- OpenAI first
- Other providers later only if useful

## Project structure

```text
agentops-workbench/
  apps/
    api/
      app/
        api/
        services/
        schemas/
        db/
        tools/
        agents/
        evals/
      tests/
    web/
      src/
        app/
        components/
        lib/
        types/
  docs/
    product/
    architecture/
    tickets/
  seed/
    documents/
    eval_cases/
    mock_logs/
```
