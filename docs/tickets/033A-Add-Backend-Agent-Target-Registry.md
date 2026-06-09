# Ticket 033A — Add backend Agent Target registry

## Goal

Add a backend registry for Agent Targets so Agent Reliability Workbench can track which agent is being benchmarked.

Ticket 032 introduced the AgentUnderTest boundary and the built-in ReferenceIncidentAgent. This ticket adds persistence and API support for registering agent targets, without yet calling external HTTP agents.

After this ticket, ARW should have a backend concept of:

text Agent Target = the agent under test that ARW benchmarks 

The default target should be:

text ReferenceIncidentAgent 

This is the built-in sample incident-response agent used for local demos.

External HTTP execution will come in Ticket 033B.

Frontend UI will come in Ticket 034.

---

## Product reason

ARW is positioned as an agent benchmarking platform.

To make that believable, the system needs to clearly track the subject under test.

This ticket makes the benchmark target explicit in the backend:

text Benchmark case → selected Agent Target → AgentUnderTest adapter → validation / guardrails / scoring 

For now, this ticket only creates the registry and APIs.

It should not yet implement the HTTP agent adapter.

---

## Current state

Already implemented in Ticket 032:

- AgentTask
- AgentResult
- AgentIdentity
- AgentUnderTest
- ReferenceIncidentAgent
- eval runner calls the default reference agent through the adapter
- agent identity is exposed in run/eval output

Now we need persistent backend agent target records.

---

## Required implementation

### 1. Add AgentTarget database model

Add a SQLAlchemy model for registered agent targets.

Likely file:

text apps/api/app/models.py 

or wherever current app models are defined.

Suggested model:

python class AgentTarget(Base):     __tablename__ = "agent_targets"      id = Column(Integer, primary_key=True, index=True)     name = Column(String, nullable=False)     agent_type = Column(String, nullable=False)  # "reference" or "http_json"     endpoint_url = Column(String, nullable=True)     auth_type = Column(String, nullable=False, default="none")  # "none" or "bearer"     auth_token = Column(String, nullable=True)     version = Column(String, nullable=True)     description = Column(Text, nullable=True)     is_default = Column(Boolean, nullable=False, default=False)     created_at = Column(DateTime, nullable=False, ...)     updated_at = Column(DateTime, nullable=False, ...) 

Follow the project’s existing timestamp/database conventions.

Rules:

- reference targets do not require endpoint_url.
- http_json targets should require endpoint_url.
- auth_type should support:
  - none
  - bearer
- auth_token may be stored for future HTTP adapter use.
- Raw auth_token should not be returned in normal API responses.

---

### 2. Add Alembic migration

Add a migration for the agent_targets table.

Likely path:

text apps/api/alembic/versions/ 

The migration should create the table and indexes if consistent with project style.

Validation should run cleanly with existing test database setup.

---

### 3. Add Agent Target schemas

Add Pydantic schemas.

Likely file:

text apps/api/app/schemas.py 

or wherever existing API schemas live.

Suggested schemas:

python class AgentTargetCreate(BaseModel):     name: str     agent_type: Literal["http_json"]     endpoint_url: str     auth_type: Literal["none", "bearer"] = "none"     auth_token: str | None = None     version: str | None = None     description: str | None = None  class AgentTargetRead(BaseModel):     id: int     name: str     agent_type: Literal["reference", "http_json"]     endpoint_url: str | None = None     auth_type: Literal["none", "bearer"]     version: str | None = None     description: str | None = None     is_default: bool     created_at: datetime     updated_at: datetime 

Important:

- Do not allow users to create reference targets through the public create API.
- reference target should be system-managed.
- Do not expose raw auth_token in AgentTargetRead.
- If a token exists, optionally expose a boolean like:

python has_auth_token: bool 

Only add this if useful and easy.

---

### 4. Add Agent Target service

Create a small service module.

Likely file:

text apps/api/app/services/agent_targets.py 

Responsibilities:

- ensure default reference target exists
- list targets
- create HTTP JSON target
- get target by id
- validate target type
- validate endpoint_url is present for http_json
- prevent public creation of system reference targets
- avoid exposing raw auth token in responses

Suggested default reference target:

text name: ReferenceIncidentAgent agent_type: reference version: v1 description: Built-in sample incident-response agent used for local demos. is_default: true auth_type: none endpoint_url: null 

There should always be one default reference target.

Do not overbuild default switching yet.

---

### 5. Add API routes

Add route file if project style supports it.

Likely file:

text apps/api/app/routes/agent_targets.py 

Required endpoints:

http GET /agent-targets POST /agent-targets GET /agent-targets/{id} 

Behavior:

### GET /agent-targets

Returns all agent targets.

Should include the default ReferenceIncidentAgent.

### POST /agent-targets

Creates an HTTP JSON agent target.

Example request:

json {   "name": "My Incident Agent",   "agent_type": "http_json",   "endpoint_url": "http://host.docker.internal:9000/run",   "auth_type": "none",   "version": "v1",   "description": "Local test agent endpoint" } 

Example response should omit auth_token.

### GET /agent-targets/{id}

Returns one target by id.

Should omit auth_token.

If target does not exist, return the project’s normal 404 response style.

---

### 6. Register routes in FastAPI app

Update the main app/router registration.

Likely file:

text apps/api/app/main.py 

or existing API router file.

Ensure the new endpoints are available.

---

### 7. Ensure default target exists

Make sure ReferenceIncidentAgent appears in the registry.

Possible approaches:

- seed it in existing seed loader
- create it lazily when listing targets
- create it in a service helper used by startup/seed flow

Use the approach that best matches existing project patterns.

Acceptance:

- fresh database should contain or automatically expose the default ReferenceIncidentAgent
- existing app behavior should still work even if no external targets are registered

---

### 8. Add docs update

Update only relevant docs.

Likely files:

text README.md docs/BENCHMARK_SPEC.md docs/DEMO_SCRIPT.md 

Add a short explanation:

text ARW tracks the agent being benchmarked as an Agent Target. The bundled ReferenceIncidentAgent is the default system-managed target for local demos. Future HTTP JSON targets allow teams to connect their own agents without changing the benchmark harness. 

Do not over-document.

The full HTTP contract belongs in Ticket 033B.

---

## Non-goals

Do not implement these in Ticket 033A:

- HttpJsonAgent
- outbound HTTP calls to external agents
- POST /agent-targets/{id}/test
- eval runner agent_target_id selection
- frontend Agent Target UI
- frontend eval agent selector
- arbitrary code upload
- LangGraph
- SDK
- CLI
- complex auth
- token encryption/key vault
- streaming
- async job queue

This ticket is only the backend registry.

---

## Acceptance criteria

### Backend

- AgentTarget model exists.
- Alembic migration exists.
- Agent Target schemas exist.
- Agent Target service exists.
- API supports:
  - GET /agent-targets
  - POST /agent-targets
  - GET /agent-targets/{id}
- Default ReferenceIncidentAgent target exists or is ensured.
- Public create API supports http_json targets only.
- http_json target requires endpoint_url.
- API responses do not expose raw auth_token.
- Existing backend behavior remains unchanged.
- Existing evals still use the reference agent path from Ticket 032.

### Docs

- Docs briefly explain Agent Targets.
- Docs identify ReferenceIncidentAgent as the default bundled sample target.
- Docs mention HTTP JSON external targets are coming next.

### Compatibility

- Existing frontend should not break.
- No frontend changes required except typecheck compatibility if generated types are touched.
- No changes to eval runner behavior required in this ticket.

---

## Testing guidance

Add backend tests for:

1. Listing agent targets returns the default ReferenceIncidentAgent.
2. Creating an http_json agent target succeeds with valid fields.
3. Creating an http_json target without endpoint_url fails.
4. Creating a reference target through public API fails.
5. Reading one agent target succeeds.
6. Reading a missing target returns 404.
7. API responses do not include raw auth_token.
8. Existing eval tests still pass.

Follow existing test style.

Do not require a real external HTTP agent.

---

## Validation commands

Run:

bash cd apps/api && python -m pytest 

Expected:

text all backend tests pass 

Current baseline before this ticket:

text 67 passed 

Then run:

bash cd apps/web && npm run typecheck 

Expected:

text passes 

---

## Implementation guardrails for Codex

- Keep this ticket backend-registry only.
- Do not implement HTTP execution yet.
- Do not update eval runner selection yet.
- Do not add frontend UI yet.
- Do not expose raw auth tokens.
- Reuse existing project patterns for models, migrations, schemas, services, routes, and tests.
- Preserve all existing tests and current demo behavior.
- Keep docs concise.

--