# Ticket 009 — Minimal Frontend Scaffold

## Goal

Create the initial Next.js frontend scaffold for AgentOps Workbench.

The frontend should provide the first visible shell of the product: a clean developer workbench UI that can later display agent runs, traces, evals, validation results, and approvals.

## Why this matters

AgentOps Workbench needs to feel like a real developer platform, not only a backend API.

This ticket creates the frontend foundation without overbuilding the UI.

## Scope

Set up the frontend app using the existing repo structure and stack:

- Next.js
- React
- TypeScript
- Tailwind

Create a basic app shell with:

- Product title
- Short thesis/subtitle
- Left navigation or top navigation
- Main content area
- Placeholder cards for:
  - Run Agent
  - Trace Viewer
  - Eval Results
  - Structured Output
  - Guardrails
  - Approvals

## Non-goals

Do not build full trace visualization yet.

Do not connect every backend endpoint yet.

Do not add authentication.

Do not add complex component libraries unless already chosen.

Do not create a dashboard with fake complexity.

## Expected implementation shape

Create or complete frontend files similar to:

    frontend/package.json
    frontend/next.config.js
    frontend/tsconfig.json
    frontend/app/layout.tsx
    frontend/app/page.tsx
    frontend/app/globals.css

The first page should render a simple workbench landing screen.

Suggested UI sections:

    Header:
      AgentOps Workbench
      Production layer for tool-using LLM agents

    Main cards:
      Run incident triage agent
      Inspect tool-call traces
      Review structured output validation
      Run evals
      Check latency and cost
      Approve or block risky actions

## Acceptance criteria

- Frontend app can be installed and started from the frontend directory
- App renders without TypeScript errors
- Tailwind styles are working
- Home page clearly communicates the AgentOps Workbench thesis
- UI includes placeholders for the core MVP areas
- No backend integration is required yet
- Existing backend work remains untouched

## Suggested tests/checks

Manual checks are enough for this ticket:

    npm install
    npm run dev

Then verify:

- Page loads successfully
- No console errors on initial load
- Layout looks clean on desktop
- Core MVP areas are visible

## Codex guidance

Keep this ticket focused on frontend scaffolding only.

Do not implement business logic.

Do not wire real traces or evals yet.

Do not modify backend files unless absolutely necessary.

Prefer a clean, minimal UI that can be extended ticket by ticket.

