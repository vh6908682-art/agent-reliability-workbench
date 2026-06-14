Ticket 035 — Add Sample External HTTP JSON Agent for Demo Benchmarking

Goal

Add a small deterministic sample external agent service that can be registered as an HTTP JSON Agent Target and benchmarked by Agent Reliability Workbench.

This ticket proves the core product story:

Agent Reliability Workbench can benchmark an agent it does not own, as long as the agent conforms to the platform’s HTTP JSON Agent Target contract.

Why this matters

The platform now has the Agent Under Test boundary, Agent Target registry, and HTTP JSON adapter. However, the repo still needs a working external agent example so demos can show:

1. Run the built-in ReferenceIncidentAgent.
2. Register a local external HTTP JSON agent.
3. Test the external target.
4. Run evals against the external target.
5. Compare benchmark results across agent targets.

Without this, the project supports external agents technically, but the demo story is less obvious.

Current project context

Recent implemented work includes:

* 032 — Agent Under Test boundary.
* 033A — Agent Target registry and backend APIs.
* 033B — HTTP JSON Agent adapter and target test endpoint.
* 034A — Frontend API methods and Agent Targets panel.
* 034B — Eval/Run UI support for agent target selection.
* Follow-up fix — Agent Targets fetch fallback and local DB migration issue fixed.

Latest verified state:

* /agent-targets returns the built-in ReferenceIncidentAgent.
* Alembic is at 009_add_agent_targets.
* Backend tests pass: 79 passed.
* Frontend typecheck passes.

Reference documents to inspect first

Before implementation, inspect these project docs so the example agent aligns with the product story:

* README.md
* DEMO_SCRIPT.md
* PROJECT_VISION.md
* BENCHMARK_SPEC.md
* EVAL_METHODOLOGY.md
* ROADMAP.md
* AGENTS.md
* docs/ directory if present
* Existing ticket docs under docs/tickets/ if present, especially tickets 032, 033A, 033B, 034A, and 034B

Do not rewrite these docs in this ticket except for small references if truly needed. Full demo-doc polish should be a separate ticket.

Source files to inspect first

Inspect the existing HTTP JSON adapter contract before writing the sample agent.

Likely relevant backend files:

* apps/api/app/agents/
* apps/api/app/services/
* apps/api/app/routes/agent_targets.py
* apps/api/app/evals/runner.py
* apps/api/app/schemas/
* apps/api/app/models/
* apps/api/tests/

Likely relevant frontend files for manual validation only:

* apps/web/src/lib/api.ts
* apps/web/src/components/AgentTargetsPanel.tsx
* apps/web/src/components/EvalRunnerPanel.tsx
* apps/web/src/components/EvalComparisonPanel.tsx

Important: use the actual existing adapter contract. Do not invent a new request/response shape if the backend already defines one.

Scope

Create a new example external agent under:

examples/http-json-agent/

Add these files:

examples/http-json-agent/server.py
examples/http-json-agent/requirements.txt
examples/http-json-agent/README.md

Optional only if useful:

examples/http-json-agent/.gitignore

This should be a small local FastAPI service.

Functional requirements

The sample external agent must expose:

POST /agent

The endpoint must accept the request shape currently sent by the existing HttpJsonAgent adapter.

The response must use the response shape currently expected by the existing HttpJsonAgent adapter.

If the adapter accepts flexible field names, prefer clear incident-triage fields such as:

{
  "final_answer": "The incident is likely caused by Kafka duplicate-key retry exhaustion after a re-migration.",
  "diagnosis": "Kafka duplicate-key retry exhaustion",
  "evidence": [
    "duplicate key errors",
    "Kafka consumer retries exhausted",
    "recent re-migration"
  ],
  "recommended_actions": [
    "Pause the affected consumer group if duplicate processing continues",
    "Inspect idempotency and migration replay safeguards",
    "Move poison messages to DLQ only after preserving evidence"
  ],
  "confidence": "medium"
}

But if the current adapter expects a different shape, follow the existing adapter.

Sample agent behavior

The sample agent should be deterministic.

It should inspect the incoming task/prompt/input text and return stable responses for at least these incident patterns:

1. Kafka duplicate key / retry exhaustion
2. DLQ poison message
3. secret rotation / authentication failure
4. partial downstream outage
5. rate limit / retry storm
6. unknown fallback incident

The sample agent does not need to be perfect. It should be intentionally simple but believable enough for a demo.

Example behavior:

* If input mentions duplicate key, Kafka, retry exhaustion, or re-migration, return a Kafka duplicate-key diagnosis.
* If input mentions DLQ, poison, or schema, return a poison message diagnosis.
* If input mentions secret, rotation, 401, or auth, return a secret rotation/auth failure diagnosis.
* If input mentions downstream, timeout, partial outage, or dependency, return a partial downstream outage diagnosis.
* If input mentions rate limit, 429, or retry storm, return a rate-limit retry storm diagnosis.
* Otherwise return a conservative unknown/fallback diagnosis with medium or low confidence.

Determinism requirements

The sample agent must not call:

* OpenAI
* Anthropic
* any external LLM
* any external API
* random/non-deterministic logic

The point is to provide a stable external agent target for local benchmarking.

README requirements

Create:

examples/http-json-agent/README.md

The README should explain:

* What this sample agent is.
* Why it exists.
* That it is a deterministic external Agent Under Test.
* How to install dependencies.
* How to run it.
* What endpoint it exposes.
* How to register it in Agent Reliability Workbench.
* How to test it through the Agent Targets UI/API.
* How to run an eval against it.
* How to compare it against the built-in ReferenceIncidentAgent.

Include exact commands.

Example setup:

cd examples/http-json-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 9000

Example local health/manual test command if a health endpoint is added:

curl http://localhost:9000/health

Example agent call:

curl -X POST http://localhost:9000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "input": "Kafka duplicate key retry exhaustion after re-migration"
    }
  }'

Example ARW registration command:

curl -X POST http://localhost:8000/agent-targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Sample HTTP Agent",
    "target_type": "http_json",
    "endpoint_url": "http://localhost:9000/agent"
  }'

The registration payload should be corrected if the actual API schema uses different field names.

Acceptance criteria

* A developer can run the sample agent locally from examples/http-json-agent/.
* The sample agent exposes POST /agent.
* The sample agent accepts the real request shape sent by the existing ARW HttpJsonAgent adapter.
* The sample agent returns the real response shape expected by the existing ARW HttpJsonAgent adapter.
* The sample agent can be registered as an HTTP JSON Agent Target.
* /agent-targets/{id}/test succeeds against the sample agent.
* /evals/run can run against the sample external target.
* The sample agent returns deterministic responses.
* The README includes clear local run, registration, test, and eval instructions.
* Existing backend tests still pass.
* Existing frontend typecheck still passes.

Validation commands

Run backend tests:

cd apps/api && python -m pytest

Run frontend typecheck:

cd apps/web && npm run typecheck

Run the sample external agent:

cd examples/http-json-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 9000

Verify the sample agent manually:

curl -X POST http://localhost:9000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "input": "Kafka duplicate key retry exhaustion after re-migration"
    }
  }'

Verify ARW backend is running and agent targets work:

curl http://localhost:8000/agent-targets

Register the sample target:

curl -X POST http://localhost:8000/agent-targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Sample HTTP Agent",
    "target_type": "http_json",
    "endpoint_url": "http://localhost:9000/agent"
  }'

Then verify manually through the UI:

Agent Targets → Create HTTP JSON target → Test target → Run eval against target → Compare results

Guardrails

* Do not call OpenAI.
* Do not add LangGraph.
* Do not add Docker unless absolutely necessary.
* Do not add new frontend UI in this ticket.
* Do not redesign the dashboard.
* Do not perform full README/DEMO_SCRIPT polish in this ticket.
* Do not change the HTTP JSON adapter contract unless there is a proven mismatch or bug.
* Do not make the sample agent non-deterministic.
* Do not add auth.
* Do not add new production dependencies to the main app.
* Keep this ticket small, local, deterministic, and demo-focused.

⸻
