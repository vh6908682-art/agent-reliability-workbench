# Ticket 015 — Latency and Cost Tracking

## Goal

Add basic latency and cost tracking to agent runs so the platform can show operational metrics for each run.

This should make AgentOps Workbench feel more like a real production agent platform instead of only a demo agent runner.

## Why this matters

A production agent platform should answer:

- How long did this agent run take?
- How many model calls happened?
- How many tokens were used?
- What was the estimated cost?
- Which step was slow or expensive?

This ticket introduces the first version of that tracking.

## Scope

Track latency and estimated cost at the agent run level.

Also track basic per-step latency for tool calls and LLM calls if the current trace structure supports it cleanly.

## Backend requirements

Add fields to the agent run model if they do not already exist:

    started_at
    completed_at
    latency_ms
    model_name
    input_tokens
    output_tokens
    total_tokens
    estimated_cost_usd

Add fields to trace steps if appropriate:

    started_at
    completed_at
    latency_ms
    token_count
    estimated_cost_usd

The exact schema can be adjusted based on the existing models from earlier tickets.

## Cost calculation

Create a simple pricing utility.

Example location:

    backend/app/services/pricing.py

It should expose a function similar to:

    estimate_openai_cost(
        model_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float

For now, hardcode a small pricing map for the initial OpenAI model used by the project.

If the model is unknown, return 0.0 instead of failing.

## Agent loop changes

When an agent run starts:

    record started_at

When it finishes:

    record completed_at
    calculate latency_ms
    store token usage if available
    calculate estimated_cost_usd

If exact token usage is not available yet, store 0 and leave a clear TODO comment.

Do not block this ticket on perfect token accounting.

## API requirements

Update the run response DTO to include:

    latency_ms
    model_name
    input_tokens
    output_tokens
    total_tokens
    estimated_cost_usd

Update any run detail endpoint to return these fields.

## Frontend requirements

If a run detail page already exists, display a small metrics section showing:

    Latency
    Model
    Input tokens
    Output tokens
    Total tokens
    Estimated cost

Keep the UI simple.

Example labels:

    Latency: 1.42s
    Model: gpt-4.1-mini
    Tokens: 1,240 total
    Cost: $0.0021

If frontend run detail UI is not ready yet, expose the API fields only and leave UI display for Ticket 016.

## Acceptance criteria

- Agent runs store latency in milliseconds.
- Agent runs expose latency through the API.
- Agent runs store model name when available.
- Agent runs store token counts when available.
- Agent runs store estimated cost.
- Unknown models do not crash cost calculation.
- Frontend displays these metrics if run detail UI exists.
- Existing tests still pass.

## Out of scope

- Exact billing-grade cost accounting.
- Multi-provider pricing.
- Real-time streaming metrics.
- Advanced dashboards.
- Historical aggregate analytics.
- Alerts or budgets.

## Suggested Codex prompt

Implement Ticket 015 using the existing project structure.

Add basic latency, token, model, and estimated cost tracking for agent runs.

Use a small pricing utility with hardcoded OpenAI pricing for the current model. Unknown models should return 0.0 cost.

Update database models, schemas, API responses, and frontend display only where the existing structure makes sense.

Keep the implementation small and avoid introducing a full analytics system.
