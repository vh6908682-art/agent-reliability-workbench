# Sample HTTP JSON Agent

This is a deterministic external Agent Under Test for Agent Reliability Workbench.

It exposes `POST /agent`, accepts the `AgentTask` JSON posted by ARW's `HttpJsonAgent` adapter, and returns:

```json
{
  "diagnosis": "string",
  "evidence": ["string"],
  "next_steps": ["string"],
  "confidence": "high"
}
```

The sample does not call an LLM or external API. It inspects `case_id`, `task`, and `input`, then returns fixed benchmark-aware responses for the 12 seeded incident-triage eval cases.

## Run Locally

From the repo root:

```bash
cd examples/http-json-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 9000
```

The service runs at:

- `http://localhost:9000`
- `GET http://localhost:9000/health`
- `POST http://localhost:9000/agent`

## Test Health

In another terminal:

```bash
curl http://localhost:9000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Test POST /agent

```bash
curl -X POST http://localhost:9000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "incident-triage-001",
    "task": "A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.",
    "input": {
      "incident_summary": "Kafka duplicate key retry exhaustion",
      "available_evidence": []
    },
    "expected_output_schema": {
      "required": ["likely_cause", "recommended_next_steps", "evidence", "confidence"]
    }
  }'
```

The response should include `diagnosis`, non-empty `evidence`, non-empty `next_steps`, `confidence`, and `matched_scenario`.

## Register In ARW

Start the ARW API first:

```bash
cd apps/api
python -m uvicorn app.main:app --reload
```

Confirm Agent Targets are available:

```bash
curl http://localhost:8000/agent-targets
```

Register this sample as an HTTP JSON Agent Target:

```bash
curl -X POST http://localhost:8000/agent-targets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Sample HTTP Agent",
    "agent_type": "http_json",
    "endpoint_url": "http://localhost:9000/agent",
    "auth_type": "none",
    "version": "v1",
    "description": "Deterministic local external agent for public ARW benchmark demos."
  }'
```

Note the returned `id`.

## Test The Target

Replace `<target_id>` with the returned `id`:

```bash
curl -X POST http://localhost:8000/agent-targets/<target_id>/test
```

Expected success shape:

```json
{
  "ok": true,
  "message": "Agent target responded with a valid structured result."
}
```

## Run Benchmark Evals

Through the UI:

1. Open `http://localhost:3000`.
2. In Agent Targets, select `Local Sample HTTP Agent`.
3. Click `Test Connection`.
4. In Run Benchmark Eval, confirm `Local Sample HTTP Agent` is selected as the Agent Under Test.
5. Click `Run Evals`.
6. Review per-case checks, including `expected_keywords_present`.
7. Open Compare Results to compare the external target with other persisted eval runs.

Through the API:

```bash
curl -X POST http://localhost:8000/evals/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_version": "v1",
    "agent_target_id": <target_id>
  }'
```

## Deterministic Cases

The sample has case-specific responses for:

- `incident-triage-001`: Kafka duplicate key retry exhaustion
- `incident-triage-002`: missing required payload field
- `incident-triage-003`: schema version mismatch
- `incident-triage-004`: downstream timeout
- `incident-triage-005`: environment config drift
- `incident-triage-006`: dead-letter queue poison message
- `incident-triage-007`: secret rotation auth failure
- `incident-triage-008`: stale runbook unsafe offset reset
- `incident-triage-009`: partial downstream outage mixed responses
- `incident-triage-010`: payload contract field rename mismatch
- `incident-triage-011`: retry storm rate limit backpressure
- `incident-triage-012`: unsafe remediation bulk data delete

## Troubleshooting

- Backend not running: `curl http://localhost:8000/health` should return the ARW API health response before registration or evals.
- Sample agent not running: `curl http://localhost:9000/health` should return `{"status":"ok"}` before testing the target.
- Port conflict on `9000`: run uvicorn on another port and register that port in `endpoint_url`.
- Failed fetch in the UI: confirm the frontend was started after setting any custom API URL, and confirm the backend allows requests from `http://localhost:3000`.
- Target test fails: verify `endpoint_url` is exactly the reachable `/agent` URL and that `POST /agent` returns non-empty `diagnosis`, `evidence`, and `next_steps`.
