# Sample HTTP JSON Agent

This is a deterministic local external Agent Under Test for Agent Reliability Workbench.

It exposes `POST /agent`, accepts the `AgentTask` JSON posted by ARW's `HttpJsonAgent` adapter, and returns the structured response that adapter expects:

```json
{
  "diagnosis": "string",
  "evidence": ["string"],
  "next_steps": ["string"],
  "confidence": "high"
}
```

It does not call OpenAI, Anthropic, any LLM, or any external API. It only inspects the incoming incident text and returns fixed incident-triage responses.

## Run Locally

From the repo root:

```bash
cd examples/http-json-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 9000
```

The service runs at:

- `http://localhost:9000`
- `POST http://localhost:9000/agent`
- `GET http://localhost:9000/health`

## Test POST /agent

In another terminal:

```bash
curl -X POST http://localhost:9000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "manual-kafka-test",
    "task": "A Kafka consumer failed with duplicate key violation and retry exhaustion after re-migration.",
    "input": {
      "incident_summary": "Kafka duplicate key retry exhaustion after re-migration",
      "available_evidence": []
    },
    "expected_output_schema": {
      "diagnosis": "string",
      "evidence": ["string"],
      "next_steps": ["string"],
      "confidence": "low | medium | high"
    }
  }'
```

## Register In ARW

Start the ARW API first, usually from `apps/api`:

```bash
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
    "description": "Deterministic local sample external agent for ARW demos."
  }'
```

Note the returned `id`.

## Test The Target

Replace `<target_id>` with the `id` returned by registration:

```bash
curl -X POST http://localhost:8000/agent-targets/<target_id>/test
```

A successful response includes:

```json
{
  "ok": true,
  "message": "Agent target responded with a valid structured result."
}
```

## Run Evals Against It

Through the UI:

1. Open `http://localhost:3000`.
2. In Agent Targets, confirm `Local Sample HTTP Agent` is listed.
3. Click `Test Connection`.
4. In the eval runner, choose `Local Sample HTTP Agent` as the Agent Under Test.
5. Run evals.
6. Open the eval comparison view to compare it with `ReferenceIncidentAgent`.

Through the API:

```bash
curl -X POST http://localhost:8000/evals/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_target_id": <target_id>
  }'
```

## Deterministic Incident Patterns

The sample returns stable responses for:

- Kafka duplicate key / retry exhaustion
- DLQ poison message or schema contract mismatch
- secret rotation / authentication failure
- partial downstream outage
- rate limit / retry storm
- unknown fallback
