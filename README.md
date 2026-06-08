# Agent Reliability Workbench

Agent Reliability Workbench is a local-first platform for benchmarking, tracing, validating, and governing tool-using AI agents.

The current benchmark environment is incident investigation. The MVP focuses on a production-like Kafka duplicate-key retry exhaustion incident so agent behavior can be inspected end to end:

> run -> trace -> validate -> govern -> evaluate -> compare

## Why This Exists

AI agents can produce plausible answers while skipping evidence, using the wrong tools, violating output contracts, or recommending unsafe actions.

Observability alone is not enough. Teams also need repeatable benchmarks and governance checks so they can compare prompts, models, workflow types, toolsets, and guardrail modes over the same tasks.

Incident investigation is the first benchmark domain because it tests practical agent reliability: evidence gathering, tool choice, diagnosis quality, structured output, and safe next-step recommendations.

## What It Does

Implemented capabilities include:

- Create incident investigation agent runs.
- Retrieve relevant seeded benchmark context.
- Persist run traces and intermediate steps.
- Store retrieved evidence and tool-like investigation steps.
- Validate structured incident diagnosis output.
- Run guardrail checks against risky recommendations.
- Track approval state for recommendations that need review.
- Capture latency, token, model, prompt, workflow, toolset, guardrail, and estimated cost metadata where available.
- Run deterministic eval cases.
- Compare eval results across persisted run and configuration metadata.
- Show agent runs, traces, evals, recent runs, approval state, and comparison views in the frontend.

This is not currently a hosted production system, a multi-agent orchestration platform, or a real production log/Kafka integration. Those belong on the roadmap unless a future ticket explicitly implements them.

## Core Benchmark Story

The golden-path benchmark starts with this incident prompt:

> A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

The agent investigates using local benchmark context, including seeded logs, runbooks, schemas, and configuration-like evidence. The system captures trace steps, retrieved context, structured diagnosis, validation result, guardrail status, approval state, cost/latency metadata, and eval score.

Eval comparison then makes it possible to compare agent configurations over repeatable benchmark cases instead of judging a single final answer by feel.

## Quickstart

Prerequisites:

- Python 3.11+
- Node.js 20+
- Docker
- An OpenAI API key for live agent runs

Start Postgres:

```bash
docker compose up -d
```

Set up and run the API:

```bash
cd apps/api
python -m pip install -e .
export OPENAI_API_KEY=your_key_here
alembic upgrade head
python -m app.cli.seed
python -m pytest
python -m uvicorn app.main:app --reload
```

The API runs at:

- http://localhost:8000
- http://localhost:8000/docs

Set up and run the web app in a second terminal:

```bash
cd apps/web
npm install
npm run dev
```

The web app runs at:

- http://localhost:3000

## Tech Stack

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Eval and agent layer: deterministic eval runner, prompt/config metadata, structured validation, guardrail checks
- Infrastructure: Docker Compose

## Example Outputs

Sample benchmark outputs are available in `docs/examples/`:

- [Sample agent run](docs/examples/sample-agent-run.json)
- [Sample trace](docs/examples/sample-trace.json)
- [Sample eval run](docs/examples/sample-eval-run.json)
- [Sample eval comparison](docs/examples/sample-eval-comparison.json)

## Screenshots

> TODO: Add screenshots or GIFs of:
>
> - Agent run form
> - Trace viewer
> - Eval runner
> - Eval comparison dashboard

## Project Structure

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
    architecture/
    tickets/
  seed/
    documents/
    eval_cases/
    mock_logs/
```

## Roadmap

Implemented work is intentionally focused on the local MVP. Future work may include:

- More production-like benchmark incidents.
- Better eval scoring rubrics and failure categories.
- Screenshot and GIF demo assets.
- LangGraph or workflow orchestration experiments.
- More realistic tool simulation.
- Hosted demo mode.
- Exportable benchmark reports.
- Additional benchmark domains after incident investigation is stronger.

See `docs/PROJECT_VISION.md`, `docs/BENCHMARK_SPEC.md`, `docs/EVAL_METHODOLOGY.md`, and `docs/ROADMAP.md` for the deeper product direction.
