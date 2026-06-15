# Demo Script

This script is the interview and walkthrough version of the Agent Reliability Workbench demo.

The default public demo benchmarks the external sample HTTP JSON agent in `examples/http-json-agent/`. The built-in `ReferenceIncidentAgent` is still useful as a local baseline, but the main story is that ARW evaluates a pluggable Agent Under Test through a real HTTP boundary.

For verification commands, API examples, sample output links, and screenshot capture notes, see the [demo evidence pack](DEMO_EVIDENCE.md).

## Opening Pitch

I built Agent Reliability Workbench to test whether AI agents can reliably investigate incidents, cite evidence, produce structured outputs, avoid unsafe recommendations, and improve across prompt, model, and configuration changes.

It is not just a chatbot UI. The workbench shows the operational layer around an agent answer:

- what agent target was evaluated
- whether the target followed the AgentTask/AgentResult contract
- what the agent looked at
- whether the output matched the expected schema
- whether guardrails flagged risk
- whether review or approval was needed
- how the target performed in deterministic evals
- how one target or config compares with another

The core loop is:

> register -> test -> run -> trace -> validate -> govern -> evaluate -> compare

## Demo Flow

1. Start the local stack.

   ```bash
   docker compose up -d
   cd apps/api
   alembic upgrade head
   python -m app.cli.seed
   python -m uvicorn app.main:app --reload
   ```

   In a second terminal:

   ```bash
   cd apps/web
   npm run dev
   ```

   In a third terminal:

   ```bash
   cd examples/http-json-agent
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   python -m uvicorn server:app --host 0.0.0.0 --port 9000
   ```

2. Open the web UI at http://localhost:3000.

3. In Agent Targets, register the external sample:

   - Name: `Local Sample HTTP Agent`
   - Type: HTTP JSON
   - Endpoint: `http://localhost:9000/agent`
   - Auth: none
   - Version: `v1`

4. Click `Test Connection`.

   Explain that ARW sends an `AgentTask` payload to the external service and validates that the response is AgentResult-shaped JSON with diagnosis, evidence, next steps, and confidence.

5. Select `Local Sample HTTP Agent` with `Use for Benchmark`.

   This makes the external endpoint the Agent Under Test for the benchmark eval.

6. Run the Kafka duplicate-key incident prompt if you want to show the single-run trace/review path:

   > A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

7. Open the review and trace sections.

   Point out final diagnosis, structured output, validation, guardrail result, approval state, latency/token/cost metadata, trace steps, and Agent Under Test metadata.

8. Run benchmark evals with `Local Sample HTTP Agent` selected.

   Show the 12 seeded `incident_triage_v1` cases, the external Agent Under Test identity, per-case scores, and individual checks such as `structured_output_valid`, `evidence_present`, and `expected_keywords_present`.

9. Explain pass/fail checks.

   A passing case means the external target returned valid structured output, included diagnosis/evidence/next steps, and covered the expected benchmark concepts. A failing case is visible at the case/check level instead of being hidden by an aggregate score.

10. Open the eval comparison view.

   Explain that persisted eval runs can compare target identity, prompt/config metadata, pass rate, average score, latency, cost, and guardrail behavior. This is how teams compare an external candidate agent against a reference baseline or prior version.

11. Close with the pluggable benchmark story.

   ARW owns the benchmark tasks, target registry, validation, guardrail checks, scoring, traces, and comparison. The agent under test can be a separate HTTP JSON service, which matches how a company would evaluate its own agent before production.

## What To Emphasize

- This is a reliability workbench, not an incident triage chatbot.
- The external HTTP JSON sample is the main public demo target.
- The built-in reference agent is a baseline/fallback, not the product boundary.
- Agent Targets make the benchmark subject explicit.
- The benchmark checks contract compliance, evidence, safety, and expected incident concepts.
- Structured validation makes output contracts explicit.
- Guardrails and approval state make risky recommendations governable.
- Eval comparison supports benchmark-driven agent improvement.

## What Not To Overclaim

- The project is local/demo-focused today, not production hosted.
- It is not a replacement for LangSmith or a full observability suite.
- It is not fully multi-agent.
- LangGraph or workflow orchestration is roadmap work, not the current MVP.
- The current benchmark context uses deterministic local seed data, not real Kafka, production logs, or ticketing systems.
- The included `incident_triage_v1` cases are incident-specific, not a universal benchmark for every agent domain.
- The sample HTTP JSON agent is deterministic demo code, not a production LLM agent.

## Closing Line

Agent Reliability Workbench makes tool-using agent behavior observable, measurable, and governable before trusting it in higher-risk workflows.
