## Ticket 027 — Add LangGraph workflow mode

Goal  
Add a second workflow mode using LangGraph so the benchmark can compare baseline single-agent vs multi-node workflow behavior.

Files likely involved
- Backend agent workflow service
- LangGraph workflow module
- Agent loop orchestration
- Trace event emission
- Config/workflow type handling
- Tests
- Docs update

Acceptance criteria
- Existing single-agent mode still works.
- New langgraph workflow mode can be selected.
- Suggested nodes exist:
  - triage
  - evidence retrieval
  - root cause analysis
  - remediation planning
  - guardrail review
- Each node emits trace events.
- Run metadata records workflow type.
- Basic tests cover workflow selection and trace event creation.

Validation commands
- cd apps/api && python -m pytest
- cd apps/web && npm run typecheck if response types change.

Notes / guardrails for Codex
- Do not attempt this before comparison foundation exists.
- Keep LangGraph integration minimal.
- Do not rewrite existing single-agent logic.
- Do not make frontend changes unless needed to display workflow traces safely.
