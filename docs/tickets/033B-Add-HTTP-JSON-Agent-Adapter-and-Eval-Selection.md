# Ticket 033B — Add HTTP JSON Agent adapter and eval runner selection

## Goal

Make Agent Reliability Workbench able to run benchmark evals against a registered external HTTP JSON Agent Target.

Ticket 032 added the AgentUnderTest adapter boundary and ReferenceIncidentAgent.

Ticket 033A added the persistent AgentTarget registry.

This ticket connects those pieces:

text AgentTarget registry     ↓ HttpJsonAgent adapter     ↓ eval runner accepts agent_target_id     ↓ external agent is benchmarked     ↓ validation / guardrails / scoring / comparison 

After this ticket, ARW should be able to evaluate either:

text ReferenceIncidentAgent 

or:

text registered external http_json agent endpoint 

Do not add the frontend UI yet.  
Do not add arbitrary code upload.  
Do not add LangGraph.  
Do not add SDK/CLI.

Frontend Agent Target UI and eval selector will come in Ticket 034.

---

## Current baseline

Already implemented:

### Ticket 032

- AgentTask
- AgentResult
- AgentIdentity
- AgentUnderTest
- ReferenceIncidentAgent
- eval runner calls default reference agent through adapter
- agent identity appears in run/eval output

### Ticket 033A

- AgentTarget model
- migration 009_add_agent_targets
- schemas
- service layer
- API routes:
  - GET /agent-targets
  - POST /agent-targets
  - GET /agent-targets/{target_id}
- default system-managed ReferenceIncidentAgent target
- auth token redaction
- tests passing: 73 passed

Now add execution support for http_json targets.

---

## Product behavior after this ticket

A backend/API caller should be able to:

1. Register an HTTP JSON agent target:

json {   "name": "My External Incident Agent",   "agent_type": "http_json",   "endpoint_url": "http://host.docker.internal:9000/run",   "auth_type": "none",   "version": "v1",   "description": "Local external agent for testing" } 

2. Run evals with that target:

json {   "agent_target_id": 2 } 

3. ARW should send benchmark cases to that endpoint.

4. The external agent should return structured incident diagnosis JSON.

5. ARW should validate, guardrail-check, score, persist, and return results just like it does for ReferenceIncidentAgent.

---

## Required implementation

## 1. Add HttpJsonAgent

Create an adapter implementation.

Likely file:

text apps/api/app/agents/http_json_agent.py 

It should implement the AgentUnderTest boundary from Ticket 032.

Conceptual shape:

python class HttpJsonAgent:     def __init__(self, target: AgentTarget, timeout_seconds: float = 10.0):         ...      def run(self, task: AgentTask) -> AgentResult:         ... 

Responsibilities:

- read config from AgentTarget
- require agent_type == "http_json"
- require endpoint_url
- send AgentTask JSON to endpoint_url
- include optional bearer token if configured
- use a reasonable timeout
- parse JSON response
- convert response into AgentResult
- preserve full external response in raw_output
- set agent identity from target:
  - name
  - version
  - type = http_json

Use the project’s existing HTTP client dependency if one exists.  
If no existing dependency exists, prefer a lightweight standard approach already available in the project. Do not add a large new dependency unless necessary.

---

## 2. HTTP request contract

When ARW calls an external agent, send a JSON payload shaped like the existing AgentTask.

Suggested request:

json {   "case_id": "kafka-duplicate-key-retry-exhaustion",   "task": "Investigate this incident and return a structured diagnosis.",   "input": {     "incident_summary": "Kafka consumer is retrying duplicate-key failures until exhaustion.",     "available_evidence": [       {         "type": "log",         "title": "consumer-error.log",         "content": "Duplicate key value violates unique constraint..."       }     ],     "metadata": {       "category": "incident_triage",       "difficulty": "medium",       "risk_level": "high",       "expected_capability": "root_cause_analysis",       "workflow_tags": ["kafka", "database", "retries"]     }   },   "expected_output_schema": {     "diagnosis": "string",     "evidence": ["string"],     "next_steps": ["string"],     "confidence": "low | medium | high"   } } 

Use the actual fields available from the existing AgentTask.

Do not invent large new task-shaping logic if Ticket 032 already created a structure.

---

## 3. HTTP response contract

The external agent should return:

json {   "diagnosis": "The Kafka consumer is repeatedly retrying a duplicate-key insert caused by missing idempotency during reprocessing.",   "evidence": [     "Logs show duplicate key violations for the same event ID.",     "Retry exhaustion occurs after repeated insert attempts."   ],   "next_steps": [     "Confirm whether the consumer checks existing processed event IDs before insert.",     "Add an idempotency guard or upsert behavior.",     "Replay only failed records after dedupe behavior is fixed."   ],   "confidence": "high" } 

Minimum required fields:

text diagnosis evidence next_steps 

confidence can be optional if current AgentResult allows it.

Extra fields should not fail the request. Preserve them in raw_output.

---

## 4. Error handling

Handle external agent failures cleanly.

Cases:

- missing endpoint URL
- unsupported target type
- timeout
- connection error
- non-2xx HTTP status
- invalid JSON response
- missing required fields
- wrong field types, such as evidence not being a list

Errors should not crash unexpectedly.

Use the existing project error style.

For eval runner behavior, choose the least disruptive existing pattern:

- either mark the eval case as failed with error details, if current runner supports per-case failures
- or raise a clear API error, if that is how existing eval failures are handled

Do not silently pass failing agent responses.

---

## 5. Add optional connection test endpoint

Add:

http POST /agent-targets/{target_id}/test 

This endpoint should:

- load the target
- reject unsupported target types if needed
- for reference, optionally return success without external HTTP call
- for http_json, call the endpoint with a tiny synthetic AgentTask
- validate that a structured response can be parsed into AgentResult
- return a simple success/error payload

Suggested synthetic task:

json {   "case_id": "connection-test",   "task": "Return a minimal structured incident diagnosis for connection testing.",   "input": {     "incident_summary": "Connection test incident.",     "available_evidence": []   },   "expected_output_schema": {     "diagnosis": "string",     "evidence": ["string"],     "next_steps": ["string"],     "confidence": "low | medium | high"   } } 

Suggested success response:

json {   "ok": true,   "agent_target_id": 2,   "agent_name": "My External Incident Agent",   "agent_type": "http_json",   "message": "Agent target responded with a valid structured result." } 

Suggested failure response:

json {   "ok": false,   "agent_target_id": 2,   "agent_name": "My External Incident Agent",   "agent_type": "http_json",   "message": "Agent target returned invalid JSON.",   "error": "..." } 

Keep this small. This endpoint is mainly for Ticket 034 UI.

---

## 6. Add adapter factory / resolver

Add a small helper that converts an AgentTarget into an AgentUnderTest.

Likely file:

text apps/api/app/agents/factory.py 

or inside the agent target service if that fits better.

Conceptual behavior:

python def build_agent_from_target(target: AgentTarget) -> AgentUnderTest:     if target.agent_type == "reference":         return ReferenceIncidentAgent(...)     if target.agent_type == "http_json":         return HttpJsonAgent(target)     raise ValueError(...) 

Keep it simple.

Do not build a plugin framework.

---

## 7. Update eval run request schema

Update eval run API request schema to accept optional:

json {   "agent_target_id": 2 } 

Rules:

- If agent_target_id is omitted, use the default ReferenceIncidentAgent.
- If provided, load that AgentTarget.
- If not found, return 404 or project-consistent validation error.
- If target is reference, use ReferenceIncidentAgent.
- If target is http_json, use HttpJsonAgent.

Existing frontend should continue working because it will not pass this field yet.

---

## 8. Update eval runner integration

Update:

text apps/api/app/evals/runner.py 

or the relevant eval service/route files.

The eval runner should:

1. accept selected agent target or resolved agent instance
2. build the AgentTask from each eval case
3. call the selected agent through the AgentUnderTest boundary
4. receive AgentResult
5. validate/guardrail/score as before
6. include selected agent identity in eval result output and persisted eval snapshot

Important separation:

text Agent generates candidate answer. Eval runner judges candidate answer. 

Do not move scoring logic into HttpJsonAgent.

Do not remove the default ReferenceIncidentAgent path.

---

## 9. Update docs with HTTP JSON contract

Update relevant docs:

text README.md docs/BENCHMARK_SPEC.md docs/architecture/api-contract.md 

Add a concise section:

text External HTTP JSON Agent Contract 

Include:

- how ARW calls external agents
- request JSON shape
- response JSON shape
- required response fields
- note that ARW does not care whether the external agent is LangGraph, OpenAI, Claude, custom Python, internal tool chain, etc.
- ARW evaluates only the returned structured answer and captured metadata

Do not over-document.

---

## Non-goals

Do not implement these in Ticket 033B:

- frontend Agent Targets UI
- frontend eval agent selector
- arbitrary code upload
- Python file upload
- Docker sandbox
- LangGraph integration
- SDK
- CLI
- OAuth
- secret manager
- production-grade encryption
- streaming responses
- async job queue
- multi-agent orchestration

---

## Acceptance criteria

### Adapter

- HttpJsonAgent exists.
- HttpJsonAgent implements the AgentUnderTest boundary.
- It sends AgentTask JSON to the configured endpoint.
- It supports auth_type = none.
- It supports auth_type = bearer by sending an Authorization header.
- It parses valid external responses into AgentResult.
- It preserves external raw response in raw_output.
- It sets correct agent identity metadata.

### Eval runner

- Eval run request accepts optional agent_target_id.
- Omitting agent_target_id preserves existing reference-agent behavior.
- Passing a reference target uses ReferenceIncidentAgent.
- Passing an http_json target uses HttpJsonAgent.
- Eval results include selected agent identity.
- Existing eval tests still pass.
- Existing frontend behavior remains compatible.

### API

- POST /agent-targets/{target_id}/test exists.
- It can validate a working HTTP JSON target.
- It returns a clear success/failure response.
- It does not expose raw auth tokens.

### Errors

- Missing target returns project-consistent 404/error.
- Timeout returns clear error.
- Connection error returns clear error.
- Non-2xx response returns clear error.
- Invalid JSON returns clear error.
- Missing required fields returns clear error.

### Docs

- Docs explain the external HTTP JSON agent contract.
- Docs show request/response examples.
- Docs clarify that external agents are connected by endpoint, not uploaded as code.

---

## Testing guidance

Add backend tests for:

1. HttpJsonAgent converts a valid HTTP response into AgentResult.
2. HttpJsonAgent sends bearer token header when configured.
3. HttpJsonAgent handles non-2xx response.
4. HttpJsonAgent handles invalid JSON.
5. HttpJsonAgent handles missing required fields.
6. POST /agent-targets/{id}/test succeeds for a mocked valid target.
7. POST /agent-targets/{id}/test fails cleanly for invalid response.
8. Eval run without agent_target_id still uses reference agent and passes.
9. Eval run with http_json target calls the HTTP adapter.
10. Eval output includes selected external agent identity.
11. Existing tests continue passing.

Mock outbound HTTP calls.  
Do not require a real external server in automated tests.

---

## Validation commands

Run:

bash cd apps/api && python -m pytest 

Current baseline before this ticket:

text 73 passed 

After this ticket, all backend tests should pass.

Then run:

bash cd apps/web && npm run typecheck 

Expected:

text passes 

---

## Manual smoke test idea

After implementation, optionally run a tiny local fake agent server that returns:

json {   "diagnosis": "The incident is caused by duplicate Kafka event processing.",   "evidence": ["Duplicate-key errors appear in the consumer logs."],   "next_steps": ["Add idempotency or upsert behavior before replay."],   "confidence": "high" } 

Register it through the existing backend API as an http_json target.

Run eval with:

json {   "agent_target_id": "<created target id>" } 

Confirm:

- ARW calls the fake external agent
- eval result is scored
- selected agent identity is shown as the external target
- default reference agent path still works without agent_target_id

This is optional manual validation, not required for automated tests.

---

## Implementation guardrails for Codex

- Keep this backend-focused.
- Do not add frontend UI yet.
- Do not add arbitrary code upload.
- Do not add LangGraph.
- Do not overbuild the plugin system.
- Preserve current default eval behavior.
- Use the existing AgentUnderTest boundary.
- Use the existing AgentTarget registry.
- Do not expose raw auth tokens.
- Mock outbound HTTP in tests.
- Keep docs concise.
- Preserve frontend typecheck compatibility.

---

