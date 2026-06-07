# Ticket 029 — Add End-to-End Smoke Test Flows

## Goal

Add a small but meaningful smoke test suite that proves the main Agent Reliability Workbench product loop works end to end.

The goal is not exhaustive unit testing. The goal is to validate the demo-critical paths:

> run → trace → validate → govern → evaluate → compare

This ticket should make the project feel more reliable and presentation-ready.

---

## Context

The project is positioned as an AI agent benchmarking, observability, and governance workbench.

The core demo depends on these flows working together:

1. Create an agent run from an incident prompt.
2. Persist the run.
3. Persist trace steps.
4. Return structured output.
5. Run validation.
6. Run guardrail checks.
7. Support approval/governance status.
8. Run evals against seeded benchmark cases.
9. Compare eval results across config metadata.

This ticket should add smoke/integration-style tests around those flows.

---

## Files likely involved

Backend-focused:

- apps/api/tests/
- Existing agent run tests
- Existing eval tests
- Existing comparison tests
- Existing seed loader tests
- Existing approval/guardrail tests
- Test fixtures/conftest if present

Do not add frontend E2E tooling in this ticket unless the project already has it configured.

---

## Required smoke test flows

### 1. Agent run creation smoke test

Add or confirm a test that:

- Creates an agent run through the API/service layer.
- Uses a realistic incident prompt, preferably the Kafka duplicate-key retry exhaustion scenario.
- Asserts the response includes:
  - run id
  - final answer or diagnosis
  - structured output if expected by the current API
  - validation status
  - guardrail result/status
  - cost/latency/token metadata if supported
  - config metadata:
    - model_name
    - prompt_version
    - workflow_type
    - toolset_name
    - guardrail_mode

Use actual field names from the current codebase.

---

### 2. Trace persistence smoke test

Add or confirm a test that:

- Creates an agent run.
- Fetches the run detail endpoint.
- Asserts trace steps were persisted.
- Asserts at least one trace step includes useful metadata such as:
  - step type
  - input/output/prompt content
  - retrieved context
  - timestamps
  - tool/context source information if present

Do not require brittle exact LLM wording.

---

### 3. Guardrail/governance smoke test

Add or confirm a test that:

- Verifies a safe recommendation can pass guardrails.
- Verifies an unsafe/destructive recommendation is flagged or blocked.
- Verifies approval state behavior still works:
  - pending review
  - approved
  - blocked

Use the current approval model/API behavior.

---

### 4. Eval runner smoke test

Add or confirm a test that:

- Runs seeded eval cases.
- Asserts the eval run returns results for all seeded cases.
- Asserts each result includes:
  - eval case id/name
  - pass/fail or score
  - diagnosis/evaluation signal
  - config metadata if supported
  - latency/cost fields if supported

Avoid brittle exact text matching. Prefer checking structured fields and expected signals.

---

### 5. Eval comparison smoke test

Add or confirm a test that:

- Creates or runs at least two eval result groups/configs if supported.
- Calls the eval comparison API/service.
- Asserts comparison output includes:
  - total cases
  - passed/failed counts or pass rate
  - average score
  - average latency
  - average cost
  - guardrail failures
  - config metadata

Use actual API names and field names.

---

## Acceptance criteria

- Backend test suite includes smoke coverage for:
  - agent run creation
  - trace persistence
  - structured validation metadata
  - guardrail/governance behavior
  - seeded eval execution
  - eval comparison output

- Tests avoid brittle assertions against exact LLM prose.

- Tests use deterministic paths/mocks where available.

- Tests pass locally with:

bash cd apps/api && python -m pytest 

- No frontend E2E framework is introduced unless already present.

- No production behavior is changed just to satisfy tests.

- No large refactors.

---

## Validation commands

bash cd apps/api && python -m pytest git diff --check git status --short 

Optional if frontend types are touched:

bash cd apps/web && npm run typecheck 

---

## Guardrails for Codex

- Keep this ticket focused on backend smoke/integration tests.
- Do not add Playwright/Cypress unless already configured.
- Do not rewrite the agent loop.
- Do not change app behavior unless fixing a real bug discovered by the tests.
- Prefer durable assertions over exact natural-language output.
- Use existing fixtures, factories, and seeded data where possible.
- If a test reveals a real bug, fix the smallest possible surface area and document it in the summary.