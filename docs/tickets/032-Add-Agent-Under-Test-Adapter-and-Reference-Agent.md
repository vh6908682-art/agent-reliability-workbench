# Ticket 032 — Add explicit Agent-Under-Test adapter and reference agent

## Goal

Make Agent Reliability Workbench clearly benchmark a pluggable agent under test, instead of appearing to evaluate its own internal workflow.

The current demo works, but the benchmark target is embedded inside the app flow. This can make the product story confusing because ARW is positioned as an agent benchmarking platform, yet there is no explicit “agent under test” boundary.

This ticket should introduce a small backend adapter/interface layer so the benchmark runner evaluates an explicit agent target. The existing incident workflow should become the default built-in reference implementation.

After this ticket, the product story should be:

> Agent Reliability Workbench owns the benchmark cases, trace capture, validation, guardrails, scoring, and comparison. The agent under test is a replaceable target. If no external agent is connected yet, ARW uses its built-in ReferenceIncidentAgent as the default sample agent.

Do not add external HTTP agent registration yet.  
Do not add LangGraph yet.  
Do not redesign the frontend yet.

This ticket is about making the internal product boundary correct and visible.

---

## Background / Current issue

ARW is positioned as:

> An eval/benchmarking tool for tool-using AI agents before production deployment.

Core loop:

text run → trace → validate → govern → evaluate → compare 

Incident investigation is the first benchmark environment.

Current concern:

- The current app can run benchmark cases.
- The current app can score outputs.
- But the “agent under test” is not explicit.
- It may look like ARW is evaluating itself.
- For a benchmark product, the subject being benchmarked must be clear.

This ticket fixes that by adding an explicit agent adapter layer.

---

## Desired architecture after this ticket

Add a simple abstraction:

text Benchmark case     ↓ AgentUnderTest     ↓ AgentResult     ↓ Validation / guardrails / scoring / comparison 

The eval runner should call an explicit agent target, even if that target is the built-in reference agent.

Example conceptual flow:

text Eval runner loads eval case Eval runner builds AgentTask Eval runner selects ReferenceIncidentAgent by default ReferenceIncidentAgent runs existing incident investigation behavior Eval runner receives AgentResult Existing validation/scoring/guardrail logic continues 

---

## Required implementation

### 1. Add AgentUnderTest adapter types

Create a small backend module for agent target abstractions.

Likely file:

text apps/api/app/agents/base.py 

Add types/classes similar to:

python from typing import Protocol, Literal from pydantic import BaseModel  class AgentTask(BaseModel):     case_id: str | None = None     task: str     input: dict     expected_output_schema: dict | None = None  class AgentResult(BaseModel):     diagnosis: str     evidence: list[str]     next_steps: list[str]     confidence: str | None = None     raw_output: dict | None = None     agent_name: str     agent_version: str | None = None     agent_type: Literal["reference", "http_json", "mock"] = "reference"  class AgentUnderTest(Protocol):     name: str     version: str | None     agent_type: str      def run(self, task: AgentTask) -> AgentResult:         ... 

Exact naming can be adjusted to match existing project style.

Keep this lightweight.

Do not over-engineer a plugin system yet.

---

### 2. Add ReferenceIncidentAgent

Create a built-in reference implementation that wraps the current incident workflow.

Likely file:

text apps/api/app/agents/reference_incident_agent.py 

This should be the default agent under test.

It should:

- use the existing incident run/triage behavior where reasonable
- return an AgentResult
- identify itself clearly as:
  - agent_name = "ReferenceIncidentAgent"
  - agent_type = "reference"
  - agent_version = "v1" or current default version

Important product meaning:

The ReferenceIncidentAgent is not an external customer agent. It is the bundled sample agent used for local demos and default evals.

It should represent:

> “This is the built-in sample incident-response agent under test.”

If the current eval runner uses deterministic responses for test stability, preserve test determinism. But make the boundary explicit so deterministic behavior belongs to the reference/test implementation, not the evaluator itself.

---

### 3. Make eval runner call AgentUnderTest

Update the eval runner so it evaluates through the agent adapter.

Likely file:

text apps/api/app/evals/runner.py 

The runner should select a default agent target:

text ReferenceIncidentAgent 

The runner should convert each eval case into an AgentTask.

The task should include enough benchmark context for a future external agent adapter to use the same shape.

Suggested AgentTask.input shape:

json {   "incident_summary": "...",   "available_evidence": [     {       "type": "log | config | runbook | document | payload",       "title": "...",       "content": "..."     }   ],   "metadata": {     "category": "...",     "difficulty": "...",     "risk_level": "...",     "expected_capability": "...",     "workflow_tags": []   } } 

Use existing eval case fields and evidence fields. Do not invent large new data structures unless needed.

The eval runner should still perform:

- structured validation
- guardrail checks
- scoring
- metric capture
- result persistence

The agent should produce the candidate answer.  
The evaluator should judge the candidate answer.

Keep that separation clear.

---

### 4. Include agent identity in eval/run output where reasonable

Where existing response models allow it, include agent identity metadata.

Possible fields:

text agent_name agent_version agent_type agent_under_test 

Use whatever naming fits existing schemas.

The goal is that API responses and logs can clearly show:

json {   "agent_under_test": {     "name": "ReferenceIncidentAgent",     "version": "v1",     "type": "reference"   } } 

Do not force a large database migration unless it is clearly needed.

If persistence is already available through existing metadata/config fields, use that.  
If a small migration is necessary, keep it minimal.

---

### 5. Add default reference agent explanation to docs

Update relevant docs so the demo is no longer confusing.

Likely files:

text README.md docs/PROJECT_VISION.md docs/BENCHMARK_SPEC.md docs/DEMO_SCRIPT.md 

Only edit the files that actually exist and are relevant.

Add a concise explanation like:

text Agent Reliability Workbench benchmarks an explicit agent under test. The bundled ReferenceIncidentAgent is the default sample target used for local demos. It uses the built-in incident investigation workflow to respond to benchmark cases. In a real deployment, teams can replace this target with their own agent adapter, such as an HTTP JSON agent endpoint in a future ticket. 

Also clarify:

text The benchmark harness is the product. The ReferenceIncidentAgent is only the default demo subject. 

Do not bloat docs.

---

## Non-goals

Do not implement these in Ticket 032:

- HTTP external agent endpoint registration
- frontend “Add Agent” form
- file upload for agent code
- arbitrary code execution
- LangGraph integration
- SDK
- CLI
- authentication for external agents
- plugin marketplace
- Docker sandboxing
- major UI redesign

These should be future tickets.

Suggested future split:

text Ticket 033 — Add HTTP JSON AgentUnderTest adapter and backend agent target registry Ticket 034 — Add frontend Agent Targets UI and eval agent selector 

---

## Acceptance criteria

### Backend behavior

- There is an explicit AgentUnderTest adapter/protocol.
- There is a built-in ReferenceIncidentAgent.
- Eval runner calls the selected/default agent through the adapter boundary.
- Existing benchmark behavior still works.
- Existing deterministic eval tests still pass.
- The default eval path uses ReferenceIncidentAgent.
- The evaluator no longer directly owns the candidate answer generation without going through an agent target.
- Agent identity is visible in API output or persisted metadata where reasonable.

### Product clarity

- Docs explain that ARW benchmarks an explicit agent under test.
- Docs explain that ReferenceIncidentAgent is the default sample/demo target.
- Docs make clear that companies will later plug in their own agent through an adapter/endpoint.
- The product should no longer sound like it is “evaluating itself.”

### Compatibility

- Preserve all existing tests.
- Preserve existing API behavior unless a small additive response field is needed.
- Preserve existing frontend typecheck.
- Do not break current demo flow.
- Do not remove existing benchmark/eval functionality.

---

## Validation commands

Run:

bash cd apps/api && python -m pytest 

Expected:

text 67 passed 

Or all backend tests passing if count changes due to added tests.

Then run:

bash cd apps/web && npm run typecheck 

Expected:

text passes 

If docs only changed on frontend side, typecheck should still pass.

---

## Testing guidance

Add or update backend tests to verify:

1. ReferenceIncidentAgent can run an AgentTask and return an AgentResult.
2. Eval runner uses an agent adapter boundary.
3. Eval result includes agent identity metadata where implemented.
4. Existing seeded eval cases still run successfully.
5. Existing deterministic behavior remains stable.

Do not write brittle tests that depend on exact prose unless existing test style already does.

Prefer testing structure and key expected signals.

---

## Implementation guardrails for Codex

- Keep this small and MVP-focused.
- Prefer clean adapter boundary over large architecture.
- Reuse existing incident workflow logic.
- Do not duplicate scoring logic inside the agent.
- The agent generates the answer; the eval runner judges it.
- Do not add LangGraph.
- Do not add external HTTP endpoint support in this ticket.
- Do not add new frontend dependencies.
- Do not add arbitrary code upload.
- Preserve all existing behavior and tests.
- Update docs only enough to make the agent-under-test story clear.

---
