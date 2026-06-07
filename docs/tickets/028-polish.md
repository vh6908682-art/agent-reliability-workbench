# Ticket 028 — Polish README and Demo Story

## Goal

Update the public-facing project documentation so Agent Reliability Workbench is easy to understand, demo, and eventually open source.

The README should clearly explain the project as an AI agent benchmarking, observability, and governance workbench for tool-using agents. The demo story should make the golden-path incident investigation flow easy to present in interviews, GitHub, and resume conversations.

This ticket is documentation-only. Do not edit application code.

---

## Context

The project has evolved beyond a simple incident triage demo.

Current positioning:

> Agent Reliability Workbench is a benchmarking, observability, and governance platform for tool-using AI agents.

The first benchmark environment is incident investigation. The golden-path scenario is a Kafka duplicate-key retry exhaustion incident.

Core loop:

> run → trace → validate → govern → evaluate → compare

The project now includes agent runs, trace capture, structured output validation, guardrail checks, approvals, eval cases, benchmark metadata, prompt/config tracking, and eval comparison APIs/UI.

LangGraph/workflow orchestration is intentionally not part of the current MVP unless clearly marked as a future roadmap item.

---

## Files likely involved

- README.md
- docs/DEMO_SCRIPT.md
- docs/PROJECT_VISION.md
- docs/ROADMAP.md

Only edit these files if they already exist or are appropriate to create/update.

---

## README requirements

Update README.md so it includes the following sections:

### 1. Project title and one-line description

Use strong but honest positioning.

Example direction:

> Agent Reliability Workbench is a local-first platform for benchmarking, tracing, validating, and governing tool-using AI agents.

Do not overclaim production readiness.

---

### 2. Why this exists

Explain the problem clearly:

- AI agents can produce plausible but unsafe answers.
- Agent behavior needs to be evaluated across prompts, models, workflow types, tools, and guardrail modes.
- Observability alone is not enough; teams need repeatable benchmarks and governance checks.
- Incident investigation is used as the first benchmark environment because it tests evidence use, tool choice, diagnosis quality, and safe next-step recommendations.

Keep this section concise.

---

### 3. What the project does

Mention current implemented capabilities only:

- Create incident investigation agent runs.
- Retrieve relevant knowledge/context.
- Persist run traces and intermediate steps.
- Validate structured diagnosis output.
- Run guardrail checks.
- Support approval states for risky recommendations.
- Run deterministic eval cases.
- Compare eval results across run/config metadata.
- Show traces, evals, recent runs, and comparison views in the frontend.

Do not claim multi-agent orchestration, LangGraph workflows, enterprise deployment, or real production integrations unless marked as roadmap.

---

### 4. Core benchmark story

Explain the golden-path benchmark:

- Input: incident report involving Kafka duplicate-key retry exhaustion.
- Agent investigates using available benchmark context.
- System captures trace steps, retrieved docs, structured diagnosis, validation result, guardrail status, cost/latency metadata, and eval score.
- Eval comparison makes it possible to compare prompts/configs over the same benchmark cases.

Use the phrase:

> run → trace → validate → govern → evaluate → compare

---

### 5. Quickstart

Include local setup commands based on the current repo structure.

Expected shape:

bash docker compose up -d cd apps/api python -m pytest python -m app.seed uvicorn app.main:app --reload 

And frontend:

bash cd apps/web npm install npm run dev 

Only include commands that are accurate for the existing project. If the exact seed command differs, use the repo’s actual command.

Mention expected local URLs if known:

- API: http://localhost:8000
- Web: http://localhost:3000

---

### 6. Tech stack

Include a compact stack section:

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, Postgres
- Frontend: Next.js, React, TypeScript, Tailwind
- Eval/agent layer: deterministic eval runner, prompt/config metadata, structured validation, guardrail checks
- Infra: Docker Compose

---

### 7. Sample eval output

Add a small representative sample, not a huge blob.

Example fields:

json {   "total_cases": 4,   "passed": 3,   "failed": 1,   "pass_rate": 0.75,   "average_score": 0.82,   "average_latency_ms": 1240,   "average_cost_usd": 0.0018,   "guardrail_failures": 0,   "config": {     "model_name": "gpt-4o-mini",     "prompt_version": "v1",     "workflow_type": "single_agent",     "toolset_name": "incident_triage",     "guardrail_mode": "standard"   } } 

If real field names differ, use the actual API contract.

---

### 8. Screenshots / GIF placeholders

Add placeholders if screenshots are not ready yet.

Example:

md ## Screenshots  > TODO: Add screenshots of: > - Agent run form > - Trace viewer > - Eval runner > - Eval comparison dashboard 

Do not fabricate screenshots.

---

### 9. Roadmap

Clearly separate implemented features from future ideas.

Roadmap items may include:

- More benchmark incidents
- Better eval scoring rubric
- Screenshot/GIF demo assets
- LangGraph or workflow orchestration experiments
- More realistic tool simulation
- Hosted demo mode
- Exportable benchmark reports

Make sure roadmap items are not presented as already implemented.

---

## Demo script requirements

Create or update docs/DEMO_SCRIPT.md.

The demo script should be interview-ready and should include:

### 1. Opening pitch

A short explanation the user can say in interviews.

Example direction:

> I built Agent Reliability Workbench to test whether AI agents can reliably investigate incidents, cite evidence, avoid unsafe recommendations, and improve across prompt/model/config changes.

---

### 2. Demo flow

Write a clear step-by-step flow:

1. Start local backend/frontend.
2. Open the web UI.
3. Run the Kafka duplicate-key retry exhaustion incident.
4. Show the final diagnosis.
5. Open the trace viewer.
6. Point out retrieved context, reasoning steps, validation, guardrail status, latency/cost metadata.
7. Run evals.
8. Open eval comparison view.
9. Explain how this enables benchmark-driven agent improvement.

---

### 3. What to emphasize

Include concise talking points:

- This is not just a chatbot UI.
- It captures evidence and traceability.
- It validates structured outputs.
- It checks governance/guardrail behavior.
- It compares agent configurations over repeatable benchmark cases.
- It uses incident investigation as the first benchmark domain.

---

### 4. What not to overclaim

Add a small honesty section:

- Not production hosted yet.
- Not a replacement for LangSmith.
- Not fully multi-agent yet.
- LangGraph/workflow orchestration is roadmap, not current MVP.
- Current benchmark environment is local/demo-focused.

---

## Project vision / roadmap updates

If editing docs/PROJECT_VISION.md or docs/ROADMAP.md, keep changes small.

Make sure they align with:

- Benchmarking
- Observability
- Governance
- Repeatable evals
- Incident investigation as first benchmark environment
- Future workflow orchestration clearly marked as future

Do not rewrite the entire docs folder unless needed.

---

## Acceptance criteria

- README.md clearly explains:
  - what the project is
  - why it exists
  - how to run it locally
  - core implemented features
  - benchmark story
  - tech stack
  - sample eval/comparison output
  - roadmap vs implemented features

- docs/DEMO_SCRIPT.md exists and provides:
  - short pitch
  - step-by-step demo flow
  - talking points
  - honesty/limitations section

- Documentation does not overclaim unfinished features.

- LangGraph is either omitted or clearly marked as roadmap/future.

- Screenshots/GIF placeholders are acceptable if screenshots are not ready.

- No application code is changed.

---

## Validation commands

bash git status --short 

No tests are required for this ticket if it is markdown-only.

Optional checks:

bash find . -maxdepth 3 -name "*.md" | sort 

---

## Guardrails for Codex

- Do not edit backend code.
- Do not edit frontend code.
- Do not change database models, migrations, routes, or tests.
- Do not add dependencies.
- Do not turn README into a long essay.
- Keep the positioning strong but honest.
- Prefer concise sections and scannable bullets.
- Mark future features clearly as roadmap items.
- Use the current project name consistently.