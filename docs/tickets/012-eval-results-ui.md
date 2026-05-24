# Ticket 012 — Eval Results UI

## Goal

Create the first frontend UI for running and viewing eval results.

The user should be able to trigger the backend eval runner and see a pass/fail summary for the golden-path incident triage eval cases.

## Why this matters

AgentOps Workbench should show that agent quality can be tested before release.

This ticket makes evals visible as a product workflow, not just a backend script.

## Scope

Add an eval results section to the frontend.

The UI should allow the user to:

- Click a Run Evals button
- Call the backend eval runner endpoint
- Display total evals
- Display passed evals
- Display failed evals
- Display check-level details per eval case

## Non-goals

Do not build historical eval tracking yet.

Do not add charts.

Do not add LLM-as-judge.

Do not add dataset editing.

Do not build advanced filtering.

## Expected implementation shape

Add or update frontend files similar to:

    frontend/components/EvalRunnerPanel.tsx
    frontend/components/EvalResultCard.tsx
    frontend/lib/api.ts
    frontend/app/page.tsx

Use the backend endpoint from Ticket 008 if available, for example:

    POST /api/evals/run

The frontend should gracefully handle:

- Loading state
- Backend errors
- Empty eval result
- Failed eval checks

## Display expectations

Show a summary like:

    Total: 3
    Passed: 2
    Failed: 1

For each case, show:

- Case ID
- Passed or failed
- Check-level results
- Failure reasons, if available

Example check display:

    structured_output_valid: passed
    diagnosis_present: passed
    recommended_next_steps_present: failed

## Acceptance criteria

- User can trigger evals from the frontend
- Frontend calls the backend eval endpoint
- Eval summary is displayed clearly
- Each eval case result is displayed
- Check-level pass/fail details are visible
- Failed checks are easy to identify
- Loading and error states are handled
- Missing optional fields do not crash the UI
- Existing frontend checks still pass
- Existing backend tests still pass

## Suggested tests/checks

Manual checks are enough if no frontend test setup exists yet:

    cd frontend
    npm run dev

Then verify:

- Run Evals button is visible
- Clicking it calls the backend
- Summary counts render correctly
- Individual case results render correctly
- Backend-down scenario shows a useful error

## Codex guidance

Keep this ticket focused on UI integration.

Do not redesign the whole app.

Reuse the existing API helper.

Prefer simple cards and clear pass/fail labels.

Do not invent a new backend contract unless the implemented endpoint differs from the docs.

