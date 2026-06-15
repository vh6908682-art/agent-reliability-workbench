# Agent Reliability Workbench

[![CI](https://github.com/vip-lade/agent-reliability-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/vip-lade/agent-reliability-workbench/actions/workflows/ci.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)

Agent Reliability Workbench is a local-first platform for benchmarking, tracing, validating, and governing tool-using AI agents.

Agent Reliability Workbench benchmarks a pluggable **Agent Under Test**. The public demo path registers a local external HTTP JSON sample agent and runs the benchmark/eval suite against that real endpoint boundary.

The backend tracks the benchmark subject as an **Agent Target**. The bundled `ReferenceIncidentAgent` remains a system-managed baseline/fallback target, while HTTP JSON targets let teams connect their own agents without changing the benchmark harness.

The current benchmark environment is incident investigation. The MVP focuses on a production-like Kafka duplicate-key retry exhaustion incident so agent behavior can be inspected end to end:

> run -> trace -> validate -> govern -> evaluate -> compare

## Architecture Flow

```mermaid
flowchart LR
  Reference[Reference incident agent] --> Adapter[Agent target adapter]
  External[External HTTP JSON agent] --> Adapter
  Adapter --> Runner[Eval runner]
  Runner --> Checks[Trace, validation, and guardrails]
  Checks --> Results[Results and comparison UI]
```

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
- Register, inspect, and test Agent Targets, including external HTTP JSON agents and the bundled reference baseline.
- Show agent runs, traces, evals, recent runs, approval state, and comparison views in the frontend.

This is not currently a hosted production system, a multi-agent orchestration platform, or a real production log/Kafka integration. Those belong on the roadmap unless a future ticket explicitly implements them.

## Core Benchmark Story

The golden-path benchmark starts with this incident prompt:

> A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

The agent investigates using local benchmark context, including seeded logs, runbooks, schemas, and configuration-like evidence. The system captures trace steps, retrieved context, structured diagnosis, validation result, guardrail status, approval state, cost/latency metadata, and eval score.

Eval comparison then makes it possible to compare prompt versions, model/config metadata, and Agent Targets over repeatable benchmark cases instead of judging a single final answer by feel.

## Benchmark Suites

ARW evaluates agents against domain-specific benchmark suites. The included default suite is `incident_triage_v1`, a 12-case incident-triage benchmark for agents that investigate production-like failures.

These cases are not intended to evaluate arbitrary agents. To adapt ARW for another domain, create domain-specific eval cases that use the supported seed JSON structure. See [Custom Benchmark Suites](docs/CUSTOM_BENCHMARK_SUITES.md) for the current template, a non-incident example, and LLM-assisted drafting guidance.

## Public Demo Flow

The recommended demo proves the pluggable Agent Under Test boundary:

1. Start Docker, the API, and the web app.
2. Start the sample external HTTP JSON agent in `examples/http-json-agent` on port `9000`.
3. Register `Local Sample HTTP Agent` as an Agent Target with endpoint `http://localhost:9000/agent`.
4. Test the target from the Agent Targets section.
5. Select that external target and run benchmark evals.
6. Open the eval details to inspect per-case checks, pass/fail outcomes, and keyword evidence.
7. Open the trace/review panels for individual runs and the comparison view for persisted eval results.

The key demo point is that ARW owns the benchmark, validation, guardrails, and comparison workflow while the agent under test can be an external service.

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

Start the external sample agent in a third terminal:

```bash
cd examples/http-json-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 9000
```

Then open the UI, register `http://localhost:9000/agent` in Agent Targets, test it, select it, and run benchmark evals against the external HTTP JSON Agent Under Test.

## Tech Stack

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Eval and agent layer: deterministic eval runner, Agent Targets, HTTP JSON agent adapter, prompt/config metadata, structured validation, guardrail checks
- Infrastructure: Docker Compose

## Example Outputs

Sample benchmark outputs are available in `docs/examples/`:

- [Sample agent run](docs/examples/sample-agent-run.json)
- [Sample trace](docs/examples/sample-trace.json)
- [Sample eval run](docs/examples/sample-eval-run.json)
- [Sample eval comparison](docs/examples/sample-eval-comparison.json)

For a walkthrough narrative, see the [demo script](docs/DEMO_SCRIPT.md).
For verifier-friendly commands and sample evidence, see the [demo evidence pack](docs/DEMO_EVIDENCE.md).

## Screenshots

Dashboard and run form:

![Dashboard and run form](docs/assets/dashboard.png)

Trace viewer and run details:

![Trace viewer and run details](docs/assets/trace-viewer.png)

Eval runner and results:

![Eval runner and results](docs/assets/eval-runner.png)

Eval comparison:

![Eval comparison](docs/assets/eval-comparison.png)

Agent targets:

![Agent targets](docs/assets/agent-targets.png)

Regenerate screenshots locally after starting the API, web app, and sample external agent:

```bash
cd apps/web
npx playwright install chromium
npm run screenshots
```

## Project Structure

```text
agent-reliability-workbench/
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

See [Project Vision](docs/PROJECT_VISION.md), [Benchmark Spec](docs/BENCHMARK_SPEC.md), [Eval Methodology](docs/EVAL_METHODOLOGY.md), [Custom Benchmark Suites](docs/CUSTOM_BENCHMARK_SUITES.md), and [Roadmap](docs/ROADMAP.md) for the deeper product direction.
