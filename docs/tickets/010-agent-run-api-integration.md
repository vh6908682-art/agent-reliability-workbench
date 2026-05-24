# Ticket 010 — Agent Run API Integration

## Goal

Connect the frontend to the backend golden-path incident triage agent.

The frontend should allow a user to submit an incident prompt and receive the agent's structured triage result.

## Why this matters

This is the first real end-to-end product flow.

After this ticket, AgentOps Workbench should no longer be only separate backend and frontend pieces. A user should be able to run the incident triage agent from the UI.

## Scope

Add a frontend form for running the golden-path agent.

The user should be able to enter or use a default incident prompt such as:

    A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

The frontend should call the existing backend agent run endpoint.

Display the response in a readable format, including:

- Diagnosis
- Recommended next steps
- Evidence
- Confidence, if available
- Validation status, if available
- Run ID, if available

## Non-goals

Do not build full trace visualization yet.

Do not build eval UI yet.

Do not add authentication.

Do not add streaming.

Do not add complex state management.

Do not redesign the whole frontend.

## Expected implementation shape

Add or update frontend code similar to:

    frontend/app/page.tsx
    frontend/lib/api.ts
    frontend/components/AgentRunForm.tsx
    frontend/components/AgentRunResult.tsx

The API helper can use an environment variable such as:

    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

The frontend should gracefully handle:

- Loading state
- Backend errors
- Empty input
- Missing fields in the response

## Expected user flow

1. User opens the frontend
2. User sees a default incident triage prompt
3. User clicks Run Agent
4. Frontend calls the backend
5. Frontend displays the structured triage result

## Acceptance criteria

- User can submit an incident prompt from the frontend
- Frontend calls the backend agent run endpoint
- Loading state is visible while the request is running
- Error state is visible if the request fails
- Successful response is displayed clearly
- The default Kafka duplicate-key incident prompt is available
- No trace visualization is required yet
- Existing backend tests still pass
- Existing frontend checks still pass

## Suggested tests/checks

Manual checks are enough if no frontend test setup exists yet:

    cd frontend
    npm install
    npm run dev

In another terminal, run the backend.

Then verify:

- Default prompt appears
- Run Agent button sends request
- Successful backend response displays
- Backend-down scenario shows a useful error
- Empty prompt is blocked or handled cleanly

## Codex guidance

Keep this ticket small.

Use the backend API contract already documented in docs/architecture/api-contract.md.

If endpoint names differ from the docs, inspect the backend implementation and use the implemented route.

Do not invent a new backend contract unless absolutely necessary.

