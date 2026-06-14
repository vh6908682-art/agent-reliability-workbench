# Demo Script

This script is the interview and walkthrough version of the Agent Reliability Workbench demo.

For the default demo, the benchmark target is the built-in reference `ReferenceIncidentAgent`. The important idea is that the workbench is not tied to this one agent: it can also benchmark registered external HTTP JSON agents through the Agent Target interface.

For verification commands, API examples, sample output links, and screenshot capture notes, see the [demo evidence pack](DEMO_EVIDENCE.md).
## Opening Pitch

I built Agent Reliability Workbench to test whether AI agents can reliably investigate incidents, cite evidence, produce structured outputs, avoid unsafe recommendations, and improve across prompt, model, and configuration changes.

It is not just a chatbot UI. The workbench shows the operational layer behind an agent answer:

- what the agent looked at
- which tool-like steps it used
- whether the output matched the expected schema
- whether guardrails flagged risk
- whether review or approval was needed
- how the run performed in deterministic evals
- how one config compares with another

The core loop is:

> run -> trace -> validate -> govern -> evaluate -> compare

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

2. Open the web UI at http://localhost:3000.

3. Run the Kafka duplicate-key retry exhaustion incident:

   > A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

4. Show the final diagnosis.

   Emphasize that the answer is structured around likely cause, evidence, recommendations, prevention, and confidence.

5. Open the trace viewer.

   Point out the captured investigation path: context retrieval, tool-like steps, validation, guardrail checks, latency, token, and estimated cost metadata.

6. Show retrieved context and evidence.

   Explain that the benchmark uses deterministic local seed data instead of live production systems.

7. Show validation and guardrail status.

   Explain that passing the schema is separate from having a plausible answer, and risky recommendations can require review.

8. Run evals against the selected Agent Under Test.

   Show the deterministic eval cases, the Agent Under Test identity, and pass/fail results. The goal is to evaluate repeatable behavior, not just one good-looking answer.

9. Open the eval comparison view.

   Explain how persisted agent target, prompt, and config metadata makes it possible to compare runs over the same benchmark cases.

10. Optionally register and test the sample HTTP JSON agent.

   Use `examples/http-json-agent/` to show that ARW is the benchmark platform and the Agent Under Test can be an external endpoint.

11. Close with the benchmark story.

   This workbench helps answer whether an agent used evidence, followed the output contract, respected guardrails, and improved or regressed across configuration changes.

## What To Emphasize

- This is a reliability workbench, not just an incident triage chatbot.
- Incident investigation is the first benchmark environment.
- The built-in reference agent is the default target, and HTTP JSON targets let external agents run through the same benchmark.
- The benchmark checks the process, not only the final answer.
- Traceability makes agent behavior inspectable.
- Structured validation makes output contracts explicit.
- Guardrails and approval state make risky recommendations governable.
- Eval comparison supports benchmark-driven agent improvement.

## What Not To Overclaim

- The project is local/demo-focused today, not production hosted.
- It is not a replacement for LangSmith or a full observability suite.
- It is not fully multi-agent.
- LangGraph or workflow orchestration is roadmap work, not the current MVP.
- The current benchmark context uses deterministic local seed data, not real Kafka, production logs, or ticketing systems.

## Closing Line

The goal is to make tool-using agent behavior observable, measurable, and governable before trusting it in higher-risk workflows.
