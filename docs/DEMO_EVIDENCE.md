# Demo Evidence Pack

This evidence pack gives a recruiter or reviewer a direct way to verify Agent Reliability Workbench end to end.

ARW is a local-first benchmark and governance workbench for tool-using agents. The public demo Agent Under Test is the external sample HTTP JSON agent in `examples/http-json-agent/`; the built-in `ReferenceIncidentAgent` remains available as a baseline/fallback.

## End-To-End Checklist

1. Start Postgres.

   ```bash
   docker compose up -d
   ```

2. Start the backend.

   ```bash
   cd apps/api
   python -m pip install -e .
   export OPENAI_API_KEY=your_key_here
   alembic upgrade head
   python -m app.cli.seed
   python -m uvicorn app.main:app --reload
   ```

3. Start the frontend in a second terminal.

   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

4. Start the external sample agent in a third terminal.

   ```bash
   cd examples/http-json-agent
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   python -m uvicorn server:app --host 0.0.0.0 --port 9000
   ```

5. Open `http://localhost:3000`.

6. Register `Local Sample HTTP Agent` in Agent Targets with endpoint `http://localhost:9000/agent`, then test the target.

7. Select `Local Sample HTTP Agent` for benchmarking.

8. Optionally run the default incident task to inspect trace/review behavior:

   ```text
   A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.
   ```

9. Inspect the run detail and confirm trace, validation, guardrail, approval, latency, token, cost, prompt, workflow, and Agent Under Test metadata are visible.

10. Run benchmark evals against the selected external Agent Under Test.

11. Open eval comparison and compare pass rate, score, latency, cost, guardrail failures, config metadata, and target identity across eval runs.

## Validation Commands

Backend:

```bash
cd apps/api
python -m pytest
```

Frontend:

```bash
cd apps/web
npm run typecheck
```

## API Proof Commands

These commands assume the backend is running at `http://localhost:8000`.

Health check:

```bash
curl http://localhost:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "service": "agent-reliability-workbench-api"
}
```

Confirm the sample external agent is healthy:

```bash
curl http://localhost:9000/health
```

Expected shape:

```json
{
  "status": "ok"
}
```

Test the sample external agent contract directly:

```bash
curl -X POST http://localhost:9000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "incident-triage-001",
    "task": "A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.",
    "input": {
      "incident_summary": "Kafka duplicate key retry exhaustion",
      "available_evidence": []
    }
  }'
```

Expected response shape:

```json
{
  "diagnosis": "... duplicate key ... retry exhaustion ...",
  "evidence": ["..."],
  "next_steps": ["..."],
  "confidence": "high",
  "sample_agent": "LocalSampleHttpJsonAgent",
  "matched_scenario": "incident-triage-001"
}
```

Create a reference agent run if you want to inspect the built-in baseline:

```bash
curl -X POST http://localhost:8000/agent-runs \
  -H "Content-Type: application/json" \
  -d '{
    "task": "A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.",
    "prompt_version": "v1"
  }'
```

Expected response shape:

```json
{
  "run_id": 101,
  "task": "...",
  "answer": "...",
  "structured_output": {
    "likely_cause": "...",
    "evidence": ["..."],
    "recommended_next_steps": ["..."],
    "prevention": ["..."],
    "confidence": "high"
  },
  "validation_status": "valid",
  "guardrail_result": {
    "passed": true,
    "checks": []
  },
  "approval_status": "approved",
  "requires_approval": false,
  "agent_under_test": {
    "name": "ReferenceIncidentAgent",
    "version": "v1",
    "type": "reference"
  }
}
```

List recent agent runs and inspect one run:

```bash
curl http://localhost:8000/agent-runs
curl http://localhost:8000/agent-runs/<run_id>
curl http://localhost:8000/agent-runs/<run_id>/approval
```

List Agent Targets:

```bash
curl http://localhost:8000/agent-targets
```

The response should include the system-managed `ReferenceIncidentAgent` target with `agent_type: "reference"` and `is_default: true`. After registration, it should also include `Local Sample HTTP Agent` with `agent_type: "http_json"`.

Create an external HTTP JSON Agent Target:

```bash
curl -X POST http://localhost:8000/agent-targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Sample HTTP Agent",
    "agent_type": "http_json",
    "endpoint_url": "http://localhost:9000/agent",
    "auth_type": "none",
    "version": "v1",
    "description": "Deterministic local sample external agent for ARW demos."
  }'
```

Test the external Agent Target:

```bash
curl -X POST http://localhost:8000/agent-targets/<target_id>/test
```

Expected success shape:

```json
{
  "ok": true,
  "agent_target_id": 2,
  "agent_name": "Local Sample HTTP Agent",
  "agent_type": "http_json",
  "message": "Agent target responded with a valid structured result.",
  "error": null
}
```

Run evals against the external Agent Target. Replace `2` with the `id` returned when the target was created.

```bash
curl -X POST http://localhost:8000/evals/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_version": "v1",
    "agent_target_id": 2
  }'
```

Fetch eval comparison results:

```bash
curl http://localhost:8000/evals/comparison
```

Expected comparison row fields include:

```json
{
  "eval_run_id": 204,
  "total_cases": 12,
  "passed": 12,
  "failed": 0,
  "pass_rate": 1.0,
  "avg_score": 1.0,
  "avg_latency": 1240.0,
  "avg_cost": 0.0018,
  "guardrail_failure_count": 0,
  "model_name": "gpt-4o-mini",
  "prompt_version": "v1",
  "workflow_type": "incident_triage",
  "toolset_name": "mock_incident_tools",
  "guardrail_mode": "standard",
  "agent_under_test": {
    "name": "Local Sample HTTP Agent",
    "version": "v1",
    "type": "http_json"
  }
}
```

## UI Proof Checklist

- Dashboard loads at `http://localhost:3000`.
- Agent run form can run the default Kafka duplicate-key incident.
- Run detail shows final diagnosis, structured output, context sources, trace steps, validation status, guardrail result, approval state, latency, token counts, estimated cost, prompt version, workflow type, and Agent Under Test.
- Agent Targets panel shows the built-in `ReferenceIncidentAgent` and the registered `Local Sample HTTP Agent`.
- External HTTP JSON target can be registered, tested, and selected.
- Eval runner supports Agent Under Test selection.
- Eval results identify `Local Sample HTTP Agent` as the target that was evaluated.
- Eval results show per-case checks and should not show a 0/12 reference-agent result as the main demo.
- Eval comparison table displays pass rate, average score, latency, cost, guardrail failures, config metadata, and Agent Under Test information.

## Sample Evidence In Repo

Reference sample outputs:

- `docs/examples/sample-agent-run.json`
- `docs/examples/sample-trace.json`
- `docs/examples/sample-eval-run.json`
- `docs/examples/sample-eval-comparison.json`

External target example:

- `examples/http-json-agent/README.md`
- `examples/http-json-agent/server.py`

Public screenshot assets:

- `docs/assets/dashboard.png`
- `docs/assets/trace-viewer.png`
- `docs/assets/eval-runner.png`
- `docs/assets/eval-comparison.png`
- `docs/assets/agent-targets.png`

Regenerate screenshots after running the seeded API, local frontend, and sample external agent:

```bash
cd apps/web
npx playwright install chromium
npm run screenshots
```

## Known Limitations

- The current demo is local-first, not a hosted SaaS product.
- Incident triage is currently the first benchmark environment.
- The seeded Kafka incident environment is deterministic local benchmark data, not live production Kafka, logs, or ticketing systems.
- External agents must follow the HTTP JSON contract shown in `examples/http-json-agent/README.md`.
- Agent Target registration supports create/list/read/test for the MVP; editing, deleting, and changing the default target are not implemented.
- This is not a large-scale multi-tenant production deployment.
- Full multi-agent orchestration and LangGraph migration remain roadmap work unless a future ticket implements them.
