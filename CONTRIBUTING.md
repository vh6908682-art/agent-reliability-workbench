# Contributing

Thanks for taking time to improve Agent Reliability Workbench. This project is a local-first MVP for benchmarking, tracing, evaluating, and governing tool-using AI agents. Keep changes focused and avoid changing product behavior unless the issue or PR explicitly calls for it.

## Local Setup

Prerequisites:

- Python 3.11+
- Node.js 20+
- Docker

Start the local database from the repo root:

```bash
docker compose up -d
```

Set up the API:

```bash
cd apps/api
python -m pip install -e .
alembic upgrade head
python -m app.cli.seed
python -m uvicorn app.main:app --reload
```

Set up the web app in another terminal:

```bash
cd apps/web
npm install
npm run dev
```

Copy `.env.example` when you need local environment variables. Do not commit real secrets.

## Backend Tests

Run API tests from `apps/api`:

```bash
python -m pytest
```

Add or update backend tests when changing API, service, validation, guardrail, eval, or adapter behavior.

## Frontend Typecheck

Run the web typecheck from `apps/web`:

```bash
npm run typecheck
```

Preserve typed API contracts between the frontend and backend.

## Eval Cases

The MVP eval seed file is:

```text
seed/eval_cases/incident-triage-evals.json
```

When adding or editing cases:

- Keep the file as one JSON array.
- Use stable, unique `id` and `name` values.
- Keep evidence and expected checks deterministic.
- Preserve the current structured output expectations unless the ticket explicitly changes eval contracts.
- Reseed locally with `cd apps/api && python -m app.cli.seed`.

See `docs/CUSTOM_BENCHMARK_SUITES.md` and `docs/EVAL_METHODOLOGY.md` for the supported case shape and scoring intent.

## External HTTP JSON Agents

You can test an external Agent Under Test through the HTTP JSON adapter.

1. Start the API.
2. Start the sample agent:

   ```bash
   cd examples/http-json-agent
   python -m pip install -r requirements.txt
   python -m uvicorn server:app --host 0.0.0.0 --port 9000
   ```

3. Register `http://localhost:9000/agent` in the Agent Targets UI or via the API.
4. Use the target test action before running benchmark evals.

External agent endpoints should be local or trusted unless you are intentionally testing remote integration behavior. See `examples/http-json-agent/README.md` for request and response examples.

## Pull Requests

Good PRs are narrow and easy to validate:

- Explain the goal and user-visible effect.
- Include screenshots for frontend UI changes when useful.
- List the checks you ran, including failures caused by local setup.
- Keep unrelated refactors out of the PR.
- Do not change API contracts, eval logic, database schema, or frontend product behavior without calling it out clearly.

Never commit API keys, tokens, credentials, database dumps with sensitive data, or real customer/production incident data.
