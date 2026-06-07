# Ticket 027 — Persist Eval Run Configuration Metadata

## Goal

Make eval comparison results accurately reflect the configuration used for an eval run, especially prompt_version, so the dashboard can honestly compare v1 vs v2.

## Context

Tickets 023–026 added:

- agent run configuration metadata
- eval comparison API
- comparison dashboard UI
- prompt version support for normal runs and eval execution

Current gap:

- eval execution accepts prompt_version
- normal agent runs persist config metadata
- but eval results are not clearly tied to a persisted eval config snapshot
- comparison rows may not fully represent the actual eval configuration used

## Inspect First

- apps/api/app/evals/runner.py
- apps/api/app/api/routes/evals.py
- apps/api/app/services/eval_comparison.py
- apps/api/app/models/eval_result.py
- apps/api/app/models/agent_run.py
- apps/api/app/schemas/evals.py
- apps/api/app/services/prompt_versions.py
- apps/api/tests/test_eval_comparison_api.py
- existing eval runner tests

## Task

Persist enough eval-run configuration metadata so GET /evals/comparison can group and display eval results by the actual config used during eval execution.

At minimum, comparison rows must correctly reflect:

- model_name
- prompt_version
- workflow_type
- toolset_name
- guardrail_mode

## Preferred Approach

Use the smallest clean design.

Prefer creating/reusing an AgentRun record as the eval run parent/config snapshot, then associate EvalResult rows to it, if that fits the current model.

If direct fields on EvalResult are cleaner with less churn, use that instead.

## Acceptance Criteria

- Running evals with prompt_version=v1 persists comparison metadata as v1.
- Running evals with prompt_version=v2 persists comparison metadata as v2.
- /evals/comparison returns separate rows for different prompt versions/configs.
- Existing normal agent run behavior remains unchanged.
- Existing eval runner behavior remains deterministic.
- Frontend comparison panel shows correct values without redesign.

## Guardrails

- Do not build a full eval-run management system.
- Do not add LangGraph.
- Do not add charts.
- Do not redesign the dashboard.
- Do not change benchmark seed cases.
- Do not add new dependencies.
- Do not make LLM calls in tests.
- Keep the fix small and MVP-level.
- Preserve existing API/UI contracts unless a tiny compatible extension is necessary.

## Validation

Run:

bash cd apps/api && python -m pytest 

If frontend files change:

bash cd apps/web && npm run typecheck 

## Summary Required

Report:

- files changed
- chosen persistence approach
- how v1 and v2 comparison rows are represented
- validation results
- assumptions